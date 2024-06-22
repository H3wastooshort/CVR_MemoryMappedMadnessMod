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

hand_offset = (0,0.5,0.3)
mag=(1,3,1)

max_adc_angle = 4000
max_angle = 45

dist_between_balls = 0.135

max_adc_len=4075 # adc reading with cables fully retracted
max_len = 3.2 #cable length when reading 0
min_len = 0.1 # how many meters out from swivel point does length get detected

def set_hand_pos(f, arg):
    x=arg[0]*mag[0] + hand_offset[0]
    y=arg[1]*mag[1] + hand_offset[1]
    z=arg[2]*mag[2] + hand_offset[2]
    f.seek(0)
    f.write(struct.pack('fff',x,y,z))

def set_hand_rot(f, arg):
    conv=360/(2*math.pi)
    ex=-arg[0]*conv
    ey=-arg[1]*conv
    ez=-arg[2]*conv
    f.seek(4*3)
    f.write(struct.pack('fff',ex,ey,ez))


def left_pos_handler(arg):
    set_hand_pos(mm_l,arg)
    scr.addstr(0,0, "LP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0] - (dist_between_balls/2),arg[1],arg[2]))
    scr.refresh()
def right_pos_handler(arg):
    set_hand_pos(mm_r,arg)
    scr.addstr(1,0, "RP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0] + (dist_between_balls/2),arg[1],arg[2]))
    scr.refresh()

def left_rot_handler(arg):
    set_hand_rot(mm_l,arg)
    scr.addstr(2,0, "LR X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()
def right_rot_handler(arg):
    set_hand_rot(mm_r,arg)
    scr.addstr(3,0, "RR X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    scr.refresh()

def fix_int_sign(integer,bits):
    sign_mask = 1 << bits-1 #can be ANDed with the int to select only the sign
    sign = (integer & sign_mask) >> bits-1 # get sign bit (0 or 1)
    integer = integer & ~sign_mask #cut sign bit from the int's bits
    if (sign==1):
        integer -= ((2**(bits))/2)
    return integer

def deg2rad(deg):
    return (deg/360) * 2*math.pi

def calc_3d(hor,ver,dist): #trigonometry time
    max_angle_rad = deg2rad(max_angle)
    hor_rad = (2*(hor / max_adc_angle)-1) * max_angle_rad
    ver_rad = (2*(ver / max_adc_angle)-1) * max_angle_rad
    dist_m = ((max_adc_len-dist) / max_adc_len) * (max_len - min_len)
    dist_m += min_len
    #print("Hor=%.3frad Ver=%.3frad Len=%04.2fm"%(hor_rad,ver_rad,dist_m))
    
    x = dist_m * math.sin(hor_rad)
    z = dist_m * math.sin(ver_rad)
    # len = sqrt(x**2 + y**2 + z **2) <=> len**2 = ... <=> y**2 = len**2 - (x**2 + z**2) <=>
    y = dist_m#math.sqrt(dist_m**2 - (x**2 + z**2))
    return (x,y,z)

last_pos_l = (0,0,0)
last_pos_r = (0,0,0)
ofst_pos_l = (0,0,0)
ofst_pos_r = (0,0,0)
btn_was_down = False

def triple_sub(a,b):
    return (a[0]-b[0],a[1]-b[1],a[2]-b[2])

def parse_game_trak(b):
    global btn_was_down, last_pos_l, last_pos_r, ofst_pos_l, ofst_pos_r
    
    (left_hor, left_ver, left_len, right_hor, right_ver, right_len, buttons) = struct.unpack("<HHHHHHBxxx",b)
    
    #print(left_hor, left_ver, left_len, right_hor, right_ver, right_len)
    
    l_pos = calc_3d(left_hor, left_ver, left_len)
    r_pos = calc_3d(right_hor, right_ver, right_len)
    
    if buttons>0:
        btn_was_down = True
    else:
        if btn_was_down:
            btn_was_down = False
            ofst_pos_l = triple_sub(l_pos,last_pos_l)
            ofst_pos_r = triple_sub(r_pos,last_pos_r)
            print(ofst_pos_l,ofst_pos_r)
        last_pos_l = l_pos
        last_pos_r = r_pos
        
        left_pos_handler(triple_sub(l_pos,ofst_pos_l))
        #left_rot_handler(l_rot)
        right_pos_handler(triple_sub(r_pos,ofst_pos_r))
        #right_rot_handler(r_rot)

with hid.Device(0x0982, 0x0982) as dev:
    print(f'Device manufacturer: {dev.manufacturer}')
    print(f'Product: {dev.product}')
    print(f'Serial Number: {dev.serial}')
    print("starting")
    
    scr = curses.initscr()
    
    while True:
        d=dev.read(16, 1000)
        #print(hexlify(d, ' '))
        parse_game_trak(d)
