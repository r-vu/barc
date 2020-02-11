#!/usr/bin/env python

import rospy
import time
from barc.msg import ECU
import sys, tty, termios
from math import pi

class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

# def getKey():
#         inkey = _Getch()
#         while(1):
#                 k=inkey()
#                 if k!='':break
#         if k=='\x1b[A':
#                 print "up"
#         elif k=='\x1b[B':
#                 print "down"
#         elif k=='\x1b[C':
#                 print "right"
#         elif k=='\x1b[D':
#                 print "left"
#         else:
#                 print "not an arrow key!"

def teleop_control():
    rospy.init_node("teleop_control", anonymous=True)
    state_pub = rospy.Publisher('ecu', ECU, queue_size = 10)

    # set node rate
    loop_rate = 50
    dt = 1.0 / loop_rate
    rate = rospy.Rate(loop_rate)
    t0 = time.time()

    # set initial conditions
    d_f = 0
    acc = 0

    find_key = _Getch()

    while not rospy.is_shutdown():
        k = find_key()
        if k == '\x1b[A':
            acc += 0.2
        elif k == '\x1b[B':
            acc -= 0.2
        elif k == '\x1b[C':
            d_f -= pi/12
        elif k == '\x1b[D':
            d_f += pi/12
        elif k == '':
            # Add artificial acceleration decay to make user control easier
            if acc > 0:
                acc -= 0.5
            elif acc < 0:
                acc += 0.5
            elif abs(acc) < 1: # fix floating point errors just in case
                acc = 0
        
        

        # Add limitations to the vehicle
        if acc > 1:
            acc = 1
        elif acc < -1:
            acc = -1
        
        if d_f > pi/4:
            d_f = pi/4
        elif d_f < -pi/4:
            d_f = -pi/4
        
        state_pub.publish(ECU(acc, d_f))
        rate.sleep()
    

if __name__=='__main__':
        try:
            teleop_control()
        except rospy.ROSInterruptException:
            pass

