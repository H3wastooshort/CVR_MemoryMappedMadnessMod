import mmap, struct, math, curses
#from binascii import hexlify
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

mm_l = mmap.mmap(-1,1024,tagname="hand/left")
mm_r = mmap.mmap(-1,1024,tagname="hand/right")

stdscr = curses.initscr()

#struct hand_data
#  public float handPositionX;
#    public float handPositionY;
#    public float handPositionZ;

#    public float handRotationX;
#    public float handRotationY;
#    public float handRotationZ;
#    public float handRotationW;
#

def set_hand_pos(f, arg):
    x=0#arg[0]*10
    y=1#arg[1]*10
    z=1#arg[2]*10
    f.seek(0)
    f.write(struct.pack('fff',x,y,z))

def set_hand_rot(f, arg):
    conv=(2*math.pi)/360
    ex=-arg[2]+60#+180)*conv
    ey=arg[1]+90#+180)*conv
    ez=-arg[0]-90#+180)*conv
    f.seek(4*3)
    f.write(struct.pack('fff',ex,ey,ez))


def print_handler(address, *args):
    print(f"{address}: {args}")

def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

def left_pos_handler(addr, *arg):
    set_hand_pos(mm_l,arg)
    stdscr.addstr(0,0, "LP X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    stdscr.refresh()
def right_pos_handler(addr, *arg):
    set_hand_pos(mm_r,arg)
    stdscr.addstr(1,0, "RP X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    stdscr.refresh()

def left_rot_handler(addr, *arg):
    set_hand_rot(mm_l,arg)
    stdscr.addstr(2,0, "LR X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    stdscr.refresh()
def right_rot_handler(addr, *arg):
    set_hand_rot(mm_r,arg)
    stdscr.addstr(3,0, "RR X%+08.3f Y%+08.3f Z%+08.3f"%arg)
    stdscr.refresh()

dispatcher = Dispatcher()
dispatcher.map("/tracking/trackers/2/position", left_pos_handler)
dispatcher.map("/tracking/trackers/3/position", right_pos_handler)
dispatcher.map("/tracking/trackers/2/rotation", left_rot_handler)
dispatcher.map("/tracking/trackers/3/rotation", right_rot_handler)
#dispatcher.set_default_handler(default_handler)

ip = "127.0.0.1"
port = 9000

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever() 