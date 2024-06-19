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

hand_offset = (0,0,0.2)

mag=1

max_adc_angle = 4000
max_angle = 45

max_adc_len=4075 # adc reading with cables fully retracted
max_len = 3.2 #cable length when reading 0
min_len = 0.1 # how many meters out from swivel point does length get detected

def set_hand_pos(f, arg):
    x=arg[0]*mag + hand_offset[0]
    y=arg[1]*mag + hand_offset[1]
    z=arg[2]*mag + hand_offset[2]
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
    #scr.addstr(0,0, "LP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    #scr.refresh()
def right_pos_handler(arg):
    set_hand_pos(mm_r,arg)
    #scr.addstr(1,0, "RP X%+09.3f Y%+09.3f Z%+09.3f"%(arg[0],arg[1],arg[2]))
    #scr.refresh()

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
    print("Hor=%.3frad Ver=%.3frad Len=%04.2fm"%(hor_rad,ver_rad,dist_m))
    
    x = dist_m * math.sin(hor_rad)
    z = dist_m * math.sin(ver_rad)
    # len = sqrt(x**2 + y**2 + z **2) <=> len**2 = ... <=> y**2 = len**2 - (x**2 + z**2) <=>
    y = math.sqrt(dist_m**2 - (x**2 + z**2))
    
    print("X%06.3f Y%06.3f Z%06.3f" % (x,y,z))
    return (x,y,z)

def parse_game_trak(b):
    (left_hor, left_ver, left_len, right_hor, right_ver, right_len, buttons) = struct.unpack("<HHHHHHBxxx",b)
    
    print(left_hor, left_ver, left_len, right_hor, right_ver, right_len)
    
    l_pos = calc_3d(left_hor, left_ver, left_len)
    r_pos = calc_3d(right_hor, right_ver, right_len)
    
    left_pos_handler(l_pos)
    #left_rot_handler(l_rot)
    right_pos_handler(r_pos)
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
