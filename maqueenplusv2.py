#coding:utf-8
#Transplanted from DFRobot_MaqueenPlusV2.h in MindPlus
#Only applicable to unihiker M10 (install pinpong 0.6 and above), used to control McQueen plus V2/V3
#Not all functions have been tested

import time
from pinpong.board import gboard, I2C

class DFRobot_MaqueenPlusV2:
    def __init__(self, bus_num=0, address=0x10):
        try:
            self.bus = I2C(bus_num)
        except Exception as e:
            print(f"\nError:PinPong not begin")
            print(f"Error:{e}\n")
            sys.exit("Exit")
        self.address = address

        # Motor speed tracking
        self._speedLeft = 0
        self._speedRight = 0
        
        # Constants from original header
        self.LEFT = 1
        self.RIGHT = 2
        self.ALL = 3
        
        self.CW = 0
        self.CCW = 1
        
        self.L1 = 1
        self.M = 2
        self.R1 = 3
        self.L2 = 4
        self.R2 = 5
        
        self.OFF = 0
        self.ON = 1
    
    def _i2c_write_buffer(self, reg, data):
        #print("write:",hex(reg),(data))
        if isinstance(data, int):
            self.bus.writeto_mem(self.address,reg,data)
        else:
            self.bus.writeto(self.address,data)
    
    def _i2c_read_buffer(self, reg, length):
        #print("read:",hex(reg),length)
        read_l =  self.bus.readfrom_mem(self.address,reg,length)
        #print("read_l=",read_l)
        return read_l

    
    def motor_run(self, index, direction, speed):
        """Control motor movement"""
        speed = min(abs(speed), 255)
        
        if index == self.LEFT:
            buf = [0x00, direction, speed]
            self._i2c_write_buffer(0x10, buf)
            self._speedLeft = speed
        elif index == self.RIGHT:
            buf = [0x02, direction, speed]
            self._i2c_write_buffer(0x10, buf)
            self._speedRight = speed
        elif index == self.ALL:
            buf = [0x00, direction, speed, direction, speed]
            self._i2c_write_buffer(0x10, buf)
            self._speedLeft = speed
            self._speedRight = speed
    
    def motor_stop(self, index):
        """Stop motor"""
        self.motor_run(index, self.CW, 0)
    
    def set_rgb(self, rgb, color):
        """Control RGB LEDs"""
        if rgb == self.LEFT:
            self._i2c_write_buffer(0x0B, color)
        elif rgb == self.RIGHT:
            self._i2c_write_buffer(0x0C, color)
        elif rgb == self.ALL:
            self._i2c_write_buffer(0x0B, color)
            self._i2c_write_buffer(0x0C, color)
    
    def read_patrol(self, patrol):
        """Read line patrol sensors"""
        y = self._i2c_read_buffer(0x1D, 1)[0]
        #print("y=",y)
        
        if patrol == self.L1: return (y & 0x08) == 0x08
        elif patrol == self.M: return (y & 0x04) == 0x04
        elif patrol == self.R1: return (y & 0x02) == 0x02
        elif patrol == self.L2: return (y & 0x10) == 0x10
        elif patrol == self.R2: return (y & 0x01) == 0x01
        return 0
    
    def read_patrol_voltage(self, patrol):
        """Read patrol sensor voltage values"""
        if patrol == self.L1:
            y = self._i2c_read_buffer(0x24, 2)
        elif patrol == self.M:
            y = self._i2c_read_buffer(0x22, 2)
        elif patrol == self.R1:
            y = self._i2c_read_buffer(0x20, 2)
        elif patrol == self.L2:
            y = self._i2c_read_buffer(0x26, 2)
        elif patrol == self.R2:
            y = self._i2c_read_buffer(0x1E, 2)
        else:
            return 0
            
        return y[0] | (y[1] << 8)
    
    def read_version(self):
        """Read firmware version"""
        length = self._i2c_read_buffer(0x32, 1)
        version = self._i2c_read_buffer(0x33, length[0])
        return bytes(version).decode('ascii')
        

    def sys_init(self):
        """Initialize system"""
        self._i2c_write_buffer(73, 0x01)  # Reset state
        time.sleep(0.2)
        
        version = self._i2c_read_buffer(0x32, 1)
        while version == 0:
            time.sleep(0.5)
            version = self._i2c_read_buffer(0x32, 1)

    def line_tracking(self, enable):
        """Enable/disable line tracking"""
        if enable:
            self._i2c_write_buffer(60, 0x04 | 0x01)
        else:
            self._i2c_write_buffer(60, 0x08)

    def motor_select(self, enable):
        """Select motor control mode"""
        self._i2c_write_buffer(62, 0x01 if enable else 0x00)

    def line_speed(self, speed):
        """Set line tracking speed"""
        self._i2c_write_buffer(63, speed)
        self.mode_cmd = 0x01  # User line tracking mode

    def distance_control(self, direction, distance, interrupt=True):
        """Control movement by distance"""
        speed = 2
        self.mode_cmd = 0x02  # Precision control mode
        distance = min(distance, 60000)
        
        self._i2c_write_buffer(64, direction)
        self._i2c_write_buffer(85, speed)
        self._i2c_write_buffer(65, distance >> 8)
        self._i2c_write_buffer(66, distance & 0xFF)
        self._i2c_write_buffer(60, 0x04 | 0x02)
        
        if not interrupt:
            flag = self._i2c_read_buffer(87, 1)
            while flag == 1:
                time.sleep(0.01)
                flag = self._i2c_read_buffer(87, 1)

    def angle_control(self, angle, interrupt=True):
        """Control movement by angle"""
        speed = 2
        self.mode_cmd = 0x02  # Precision control mode
        
        self._i2c_write_buffer(67, 1 if angle >= 0 else 2)
        self._i2c_write_buffer(86, speed)
        self._i2c_write_buffer(68, abs(angle))
        self._i2c_write_buffer(60, 0x04 | 0x02)
        
        if not interrupt:
            flag = self._i2c_read_buffer(87, 1)
            while flag == 1:
                time.sleep(0.01)
                flag = self._i2c_read_buffer(87, 1)

    def pid_stop(self):
        """Stop precision control"""
        self._i2c_write_buffer(60, 0x10)

    def inquire_cross(self):
        """Check crossroad status"""
        return self._i2c_read_buffer(61, 1)[0]

    def cross1(self, cmd):
        """Control crossroad type 1"""
        self._i2c_write_buffer(69, cmd)

    def cross2(self, cmd):
        """Control crossroad type 2"""
        if cmd != 3:  # Skip invalid command
            self._i2c_write_buffer(70, cmd)

    def cross3(self, cmd):
        """Control crossroad type 3"""
        if cmd != 2:  # Skip invalid command
            self._i2c_write_buffer(71, cmd)

    def cross4(self, cmd):
        """Control crossroad type 4"""
        if cmd != 1:  # Skip invalid command
            self._i2c_write_buffer(72, cmd)

    def get_speed(self, left=True):
        """Get motor speed (cm/s)"""
        buf = self._i2c_read_buffer(76, 2)
        return buf[0 if left else 1] / 5.0

    def get_light(self, left=True):
        """Get light sensor reading (0-1023)"""
        buf = self._i2c_read_buffer(78, 4)
        if left:
            return (buf[0] << 8) | buf[1]
        else:
            return (buf[2] << 8) | buf[3]

    def set_rgb_led(self, side, color):
        """Set RGB LED color"""
        color_map = {
            0xFF0000: 1,
            0x00FF00: 2,
            0xFFFF00: 3,
            0x0000FF: 4,
            0xFF00FF: 5,
            0x00FFFF: 6,
            0xFFFFFF: 7,
            0x000000: 0
        }
        value = color_map.get(color, 0)
        
        if side == 2:  # Both sides
            self._i2c_write_buffer(11, value)
            self._i2c_write_buffer(12, value)
        elif side == 1:  # Left
            self._i2c_write_buffer(11, value)
        else:  # Right
            self._i2c_write_buffer(12, value)

    def enable_ir(self, recv_pin, callback=None):
        """Enable IR receiver (requires RPi.GPIO)
        
        Args:
            recv_pin: GPIO pin number (BCM numbering)
            callback: Function to call when IR code received
        """
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.recv_pin = recv_pin
            self.ir_callback = callback
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(recv_pin, GPIO.IN)
            GPIO.add_event_detect(recv_pin, GPIO.RISING, 
                                callback=self._ir_handler)
        except ImportError:
            raise RuntimeError("RPi.GPIO required for IR support")

    def _ir_handler(self, channel):
        """Internal IR signal handler"""
        if not hasattr(self, 'last_ir_time'):
            self.last_ir_time = 0
            
        current_time = time.time()
        interval = current_time - self.last_ir_time
        self.last_ir_time = current_time
        
        if interval > 0.003:  # 3ms gap resets
            self.ir_counter = 0
            self.ir_tmp = 0
            return
            
        bit = 1 if (0.002 < interval < 0.0025) else 0
        self.ir_tmp = (self.ir_tmp << 1) | bit
        self.ir_counter += 1
        
        if self.ir_counter == 32:  # Complete code
            self._decode_ir(self.ir_tmp)
            self.ir_counter = 0

    def _decode_ir(self, code):
        """Decode received IR code"""
        self.ir_data = code & 0xFFFFFFFF
        if self.ir_callback:
            decoded = self._trans_mind(self.ir_data)
            if decoded >= 0:
                self.ir_callback(decoded)

    def _trans_mind(self, data):
        """Translate IR code to button value"""
        code_map = {
            255: 0, 127: 1, 191: 2, 223: 4, 95: 5,
            159: 6, 239: 8, 111: 9, 175: 10, 207: 12,
            79: 13, 143: 14, 247: 16, 119: 17, 183: 18,
            215: 20, 87: 21, 151: 22, 231: 24, 103: 25,
            167: 26
        }
        return code_map.get(data, -1)

    def get_ir_data(self):
        """Get last received IR code"""
        data = getattr(self, 'ir_data', 0)
        self.ir_data = 0
        return self._trans_mind(data)

    def set_ir_callback(self, callback):
        """Set IR callback function"""
        self.ir_callback = callback
        if not hasattr(self, 'ir_task_init'):
            self.ir_task_init = True

    def __del__(self):
        """Clean up GPIO on deletion"""
        if hasattr(self, 'GPIO'):
            self.GPIO.cleanup()

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.__del__()
