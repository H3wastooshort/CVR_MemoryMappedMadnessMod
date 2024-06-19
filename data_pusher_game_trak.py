import mmap, struct, math, curses, sys
import hid
from binascii import hexlify

mm_l = mmap.mmap(-1,64,tagname="hand/left")
mm_r = mmap.mmap(-1,64,tagname="hand/right")

#struct hand_data
#  public float handPositionX;
#    public float handPositionY;
#    public float handPositionZ;

#    public float handRotationX;
#    public float handRotationY;
#    public float handRotationZ;
#

mag=1

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

def parse_game_trak(b):
    (left_hor, left_ver, left_len, right_hor, right_ver, right_len, buttons) = struct.unpack("HHHHHHBxxx",b)
    
    print(left_hor, left_ver, left_len, right_hor, right_ver, right_len)
    
    #handle_mouse_data_default(btns,1,2,x,y,wheel,l_pos,l_rot,0)
    #left_pos_handler(l_pos)
    #left_rot_handler(l_rot)
    #right_pos_handler(r_pos)
    #right_rot_handler(r_rot)

#scr = curses.initscr()

with hid.Device(0x0982, 0x0982) as dev:
    print(f'Device manufacturer: {dev.manufacturer}')
    print(f'Product: {dev.product}')
    print(f'Serial Number: {dev.serial}')
    print("starting")

    while True:
        d=dev.read(16, 1000)
        print(hexlify(d, ' '))
        parse_game_trak(d)
