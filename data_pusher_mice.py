import mmap, struct, math, curses, sys
import usb.core,usb.util #PyUSB
from binascii import hexlify

mm_l = mmap.mmap(-1,64,tagname="hand/left")
mm_r = mmap.mmap(-1,64,tagname="hand/right")
mm_ctrl = mmap.mmap(-1,64,tagname="ctrl")

#struct hand_data
#  public float handPositionX;
#    public float handPositionY;
#    public float handPositionZ;

#    public float handRotationX;
#    public float handRotationY;
#    public float handRotationZ;
#

max_distance = 5
max_rotation = 360 * 2

mag = 0.3
def set_hand_pos(f, arg):
    x=arg[2]*mag
    y=arg[1]*mag*2+1
    z=-arg[0]*mag+0.1
    f.seek(0)
    f.write(struct.pack('fff',x,y,z))

def set_hand_rot(f, arg):
    #conv=(2*math.pi)/255
    conv=360/2000
    ex=-arg[2]*conv
    ey=-arg[1]*conv*2
    ez=-arg[0]*conv
    f.seek(4*3)
    f.write(struct.pack('fff',ex,ey,ez))


def left_pos_handler(arg):
    set_hand_pos(mm_l,arg)
    scr.addstr(0,0, "LP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()
def right_pos_handler(arg):
    set_hand_pos(mm_r,arg)
    scr.addstr(1,0, "RP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()

def left_rot_handler(arg):
    set_hand_rot(mm_l,arg)
    scr.addstr(2,0, "LR X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()
def right_rot_handler(arg):
    set_hand_rot(mm_r,arg)
    scr.addstr(3,0, "RR X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()

mouse_map=[2,0,1]
mouse_maps=[[2,0,1],[2,1,0],[0,1,2]]
next_mouse_map=1

l_pos = [0,0,0]
l_rot = [0,0,0]
r_pos = [0,0,0]
r_rot = [0,0,0]

rot_en = False

def fix_int_sign(integer,bits):
    sign_mask = 1 << bits-1 #can be ANDed with the int to select only the sign
    sign = (integer & sign_mask) >> bits-1 # get sign bit (0 or 1)
    integer = integer & ~sign_mask #cut sign bit from the int's bits
    if (sign==1):
        integer -= ((2**(bits))/2)
    return integer

def not_moving(*argv):
    for a in argv:
        if a != 0:
            return False
    return True

gesture=[1,1]
move_mag=[0,0]
def handle_mouse_data_default(btns,right,left,x,y,wheel,p,r,e):
    global move_mag, gesture, mouse_map, mouse_maps, next_mouse_map
    if (not_moving(x,y)):
        if (btns == 4):
            r[0]=0
            r[1]=0
            r[2]=0
            p[0]=0
            p[1]=0
            p[2]=0
            move_mag[0]=0
            move_mag[1]=0
            for i in range(0,1):
                gesture[i]=0
        elif (btns==3):
            for i in range(0,3):
                mouse_map[i]=mouse_maps[next_mouse_map][i]
            next_mouse_map+=1
            next_mouse_map %= 3
        elif (btns==left):
            if (wheel != 0):
                if (wheel>0):
                    gesture[e]+=1
                else:
                    gesture[e]-=1
                wheel=0
                gesture[0]=max(min(gesture[0],7),-1)
                gesture[1]=max(min(gesture[1],7),-1)
                mm_ctrl.seek(0)
                mm_ctrl.write(struct.pack('ff',gesture[0],gesture[1]))
        else:
            move_mag[0]=0
            move_mag[1]=0
    if (btns==left):
        move_mag[0] += x/500
        move_mag[1] += -y/500
        for m in move_mag:
            m=max(min(m,1),-1)
    elif (btns == right):
        #print("ROTATE ",end="")
        r[mouse_map[0]] += wheel * 10 #arm axis rottation
        r[mouse_map[1]] += -y #up dn
        r[mouse_map[2]] += -x # left right
        #r[mouse_map[1]] += wheel * 10
        #print(r)
    else:
        #print("TRANSLATE ",end="")
        p[mouse_map[0]] += x / 2000
        p[mouse_map[1]] += y / 2000
        p[mouse_map[2]] += wheel / 50
        #print(p)
    mm_ctrl.seek(4*2)
    mm_ctrl.write(struct.pack('ff',move_mag[0],move_mag[1]))

def parse_mouse(b):
    if (len(b) != 6):
        print("wrong len")
        return
    d = struct.unpack('<BBL',b)
    if (d[0] != 1):
        print("wrong magic")
        return
        
    btns = d[1] #00000MRL
    #posdat contains two 12bit numbers and one 8bit one for the mousewheel like this [8 W][12  Y][12  X]
    posdat = d[2]
    #bitshift cut out int
    x = (posdat>>0) & 0x0FFF
    y = (posdat>>12) & 0x0FFF
    wheel = (posdat>>24) & 0x00FF
    #convert sign
    x = fix_int_sign(x,12)
    y = fix_int_sign(y,12)
    wheel = fix_int_sign(wheel,8)
    
    return (btns,x,y,wheel)
    

def parse_left_mouse(b):
    #d = struct.unpack('<BBL',b)
    #print('{:032b}'.format(d[2]))
    (btns,x,y,wheel) = parse_mouse(b)
    
    handle_mouse_data_default(btns,1,2,x,y,wheel,l_pos,l_rot,0)
    left_pos_handler(l_pos)
    left_rot_handler(l_rot)

def parse_right_mouse(b):
    (btns,x,y,wheel) = parse_mouse(b)
    handle_mouse_data_default(btns,2,1,x,y,wheel,r_pos,r_rot,1)
    right_pos_handler(r_pos)
    right_rot_handler(r_rot)

mice = list(usb.core.find(find_all=True, bDeviceClass=0))
for i,m in enumerate(mice):
    mf = "?M?"
    prd = "?P?"
    try:
        mf = m.manufacturer
    except:
        pass
    try:
        prd = m.product
    except:
        pass
    print('[%d] %s %s @ BUS%d ADDR%d'%(i,mf,prd,m.bus,m.address))#m.product))
if (len(mice)==0):
    print("what? no usb mice?")
i_l = int(input("which of these is your left mouse? "))
i_r = int(input("which of these is your right mouse? "))
l_mouse = mice[i_l]
r_mouse = mice[i_r]

def init_mouse(m):
    m.reset()
    m.set_configuration()
    cfg = m.get_active_configuration()
    intf = cfg[(0,0)]
    print(intf)
    ep = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    #print(ep)
    return ep

l_ep = init_mouse(l_mouse)
r_ep = init_mouse(r_mouse)

assert l_ep is not None
assert r_ep is not None

print("starting")

scr = curses.initscr()

def left_loop():
    d=[]
    try:
        d=l_ep.read(6, timeout=9)
    except usb.core.USBTimeoutError:
        pass
    except IOError:
        exit("Left Mouse IO Error. Have you installed the WinUSB driver using Zadig?")
    else:
        parse_left_mouse(d)

def right_loop():
    d=[]
    try:
        d=r_ep.read(6, timeout=9)
    except usb.core.USBTimeoutError:
        pass
    except IOError:
        exit("Right Mouse IO Error. Have you installed the WinUSB driver using Zadig?")
    else:
        parse_right_mouse(d)

while True:
    left_loop()
    right_loop()
