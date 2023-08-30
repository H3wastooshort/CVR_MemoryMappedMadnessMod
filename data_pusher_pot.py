import mmap, struct, math, curses, serial, sys
from binascii import hexlify

mm_l = mmap.mmap(-1,1024,tagname="hand/left")
mm_r = mmap.mmap(-1,1024,tagname="hand/right")

#struct hand_data
#  public float handPositionX;
#    public float handPositionY;
#    public float handPositionZ;

#    public float handRotationX;
#    public float handRotationY;
#    public float handRotationZ;
#

mag = 0.3
def set_hand_pos(f, arg):
    adc = 512 #max adc value / 2 
    x=mag*((arg[0]-adc) / adc)
    y=mag*2*((arg[1]-adc) / adc)+1
    z=-mag*((arg[2]-adc) / adc)+0.1
    f.seek(0)
    f.write(struct.pack('fff',x,y,z))

def set_hand_rot(f, arg):
    #conv=(2*math.pi)/255
    conv=360/1023
    ex=-arg[2]*conv
    ey=-arg[1]*conv
    ez=-arg[0]*conv
    f.seek(4*3)
    f.write(struct.pack('fff',ex,ey,ez))


def left_pos_handler(*arg):
    set_hand_pos(mm_l,arg)
    scr.addstr(0,0, "LP X%+09.3f Y%+09.3f Z%+09.3f"%arg)
    scr.refresh()
def right_pos_handler(*arg):
    set_hand_pos(mm_r,arg)
    scr.addstr(1,0, "RP X%+09.3f Y%+09.3f Z%+09.3f"%arg)
    scr.refresh()

def left_rot_handler(*arg):
    set_hand_rot(mm_l,arg)
    scr.addstr(2,0, "LR X%+09.3f Y%+09.3f Z%+09.3f"%arg)
    scr.refresh()
def right_rot_handler(*arg):
    set_hand_rot(mm_r,arg)
    scr.addstr(3,0, "RR X%+09.3f Y%+09.3f Z%+09.3f"%arg)
    scr.refresh()

ser = serial.Serial(sys.argv[1], 115200)

def try_data():
    b = ser.read_until(b"EndOfPkg\n",64)
    scr.addstr(5,0,hexlify(b))
    if (len(b) != 22):
        return "Incorrect length: %d" % len(b)
    dat = struct.unpack('<HHHHHHB',b[0:13])
    if (dat[6] != 42):
        return "Incorrect magic: %d" % dat[6]
    right_pos_handler(dat[0],dat[1],dat[2])
    left_pos_handler(dat[0],dat[1],dat[2])
    right_rot_handler(dat[3],dat[4],dat[5])
    left_rot_handler(dat[3],dat[4],dat[5])
    #left_pos_handler(dat[3],dat[4],dat[5])
    return "OK"

print("starting")

scr = curses.initscr()
#scr.addstr(5,0,"waiting for data")
while True:
    s = try_data()
    #print(s)
    scr.addstr(4,0,"                ")
    scr.addstr(4,0,s)
