#coding:utf-8
from pinpong.board import Board
from maqueenplusv2 import DFRobot_MaqueenPlusV2
import time

Board().begin()

robot = DFRobot_MaqueenPlusV2()

print("init")
robot.sys_init()

time.sleep(3)

# Version check
print("Version:", robot.read_version())
# Simple motor test

#robot.motor_run(robot.LEFT, robot.CW, 200)
#time.sleep(1)
#robot.motor_run(robot.RIGHT, robot.CCW, 200)
#time.sleep(1)
#robot.motor_stop(robot.ALL)
#time.sleep(1)
# Line sensor test
#print("Line sensor:", robot.read_patrol(robot.L2),robot.read_patrol(robot.L1),robot.read_patrol(robot.M),robot.read_patrol(robot.R1),robot.read_patrol(robot.R2))
#print("Line sensor v:", robot.read_patrol_voltage(robot.L1),robot.read_patrol_voltage(robot.L2),robot.read_patrol_voltage(robot.M),robot.read_patrol_voltage(robot.R2),robot.read_patrol_voltage(robot.R1))
#L=1,R=0
#print("light",robot.get_light(1),robot.get_light(0))
#L=1,R=0
#print("speed",robot.get_speed(1),robot.get_speed(0))
#L=1,R=0,ALL=2
#robot.set_rgb_led(1,0xFF0000)
#robot.set_rgb_led(0,0x00FF00)

robot.line_tracking(1)
#speed1-5
robot.line_speed(2)
#Go straight = 3, turn left = 1, turn right = 2, stop = 4
#Crossroads
#robot.cross1(2)
#T-intersection
#robot.cross2(2)
#Left turn and straight intersection
#robot.cross3(2)
#Right turn and straight intersection
#robot.cross4(2)
#Query intersection, 1 = intersection, 2 = T-junction, 3 = left turn and straight ahead intersection, 4 = right turn and straight ahead intersection
#print(robot.inquire_cross())

while 1:
    inqCrs = robot.inquire_cross()
    #print("Line sensor:", robot.read_patrol(robot.L2),robot.read_patrol(robot.L1),robot.read_patrol(robot.M),robot.read_patrol(robot.R1),robot.read_patrol(robot.R2))
    #print(inqCrs)
    if inqCrs==1:
        print(1)
    elif inqCrs==2:
        print(2)
    elif inqCrs==3:
        print(3)
    elif inqCrs==4:
        print(4)


