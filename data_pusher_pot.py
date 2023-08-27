import mmap, struct, math, curses, serial, sys
from binascii import hexlify

mm_l = mmap.mmap(-1,1024,tagname="hand/left")
mm_r = mmap.mmap(-1,1024,tagname="hand/right")

scr = curses.initscr()
scr.addstr(7,0,"s")

#struct hand_data
#  public float handPositionX;
#    public float handPositionY;
#    public float handPositionZ;

#    public float handRotationX;
#    public float handRotationY;
#    public float handRotationZ;
#

def set_hand_pos(f, arg):
    conv = 127 #max adc value
    x=-((arg[0]-127) / conv)
    y=((arg[1]-127) / conv)+1
    z=-((arg[2]-127) / conv)
    f.seek(0)
    f.write(struct.pack('fff',x,y,z))

def set_hand_rot(f, arg):
    #conv=(2*math.pi)/255
    conv=360/255
    ex=-arg[2]*conv
    ey=-arg[1]*conv
    ez=-arg[0]*conv
    f.seek(4*3)
    f.write(struct.pack('fff',ex,ey,ez))


def left_pos_handler(*arg):
    set_hand_pos(mm_l,arg)
    scr.addstr(0,0, "LP X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    scr.refresh()
def right_pos_handler(*arg):
    set_hand_pos(mm_r,arg)
    scr.addstr(1,0, "RP X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    scr.refresh()

def left_rot_handler(*arg):
    set_hand_rot(mm_l,arg)
    scr.addstr(2,0, "LR X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    scr.refresh()
def right_rot_handler(*arg):
    set_hand_rot(mm_r,arg)
    scr.addstr(3,0, "RR X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    scr.refresh()


scr.addstr(7,0,"pre")
ser = serial.Serial(sys.argv[1], 115200)
scr.addstr(7,0,"ser")

def try_data():
    scr.addstr(7,0,"data")
    b = ser.read_until(b"END\n",16)
    scr.addstr(5,0,hexlify(b))
    if (len(b) != 11):
        return "Incorrect length: %d" % len(b)
    dat = struct.unpack('<BBBBBBB',b[0:7])
    if (dat[6] != 42):
        return "Incorrect magic: %d" % dat[6]
    right_pos_handler(dat[0],dat[1],dat[2])
    right_rot_handler(45,dat[3],60)
    return "OK"

print("starting")
while True:
    s = try_data()
    print(s)
    scr.addstr(4,0,"                ")
    scr.addstr(4,0,s)
