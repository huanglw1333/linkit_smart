import time
import sys
import signal

from PyMata.pymata import PyMata
#from PyMata.pymata_serial import PyMataSerial

board = PyMata('/dev/ttyS0', verbose = True)
device_addr = 0x27  # device address
bl_bit = 0x08       # backlight bit
en_bit = 0x04       # read/write enable bit
rw_bit = 0x02       # 
rs_bit = 0x01       # 

def delay_ms(time_ms):
    time.sleep(time_ms/1000)

def i2c_send_4bits(data):
    high_byte = data >> 4
    low_byte  = data & 0x0F
    i2c_send(high_byte | bl_bit)
    i2c_send(low_byte  | bl_bit)

def i2c_send(data):
    board.i2c_write(device_addr, data | en_bit)
    board.i2c_write(device_addr, data & ~en_bit)

def lcd_init():
    # setup i2c pin, D2: SDA, D3: SCL
    board.i2c_config(0, board.DIGITAL, 3, 2)
    print "i2c config end, send data begin"

    # start LCD init sequence
    board.i2c_write(0x27, 0x00)
    delay_ms(100)

    # function set
    i2c_send(0x30 | bl_bit)
    delay_ms(5)
    i2c_send(0x30 | bl_bit)
    delay_ms(1)
    i2c_send(0x30 | bl_bit)
    delay_ms(1)
    i2c_send(0x20 | bl_bit)
    delay_ms(1)

    # function set command
    i2c_send(0x20 | bl_bit)
    i2c_send(0x80 | bl_bit)
    delay_ms(1)

    # display on/off control
    i2c_send(0x00 | bl_bit)
    i2c_send(0x80 | bl_bit)
    delay_ms(1)

    # clear display
    i2c_send(0x00 | bl_bit)
    i2c_send(0x10 | bl_bit)
    delay_ms(5)

    # entry mode set
    i2c_send(0x00 | bl_bit)
    i2c_send(0x60 | bl_bit)
    # end LCD init

def setCursor(col, row):
    row_offsetDef = [0x00, 0x40]
    cursor_data = 0x80 | (col + row_offsetDef[row])
    i2c_send_4bits(cursor_data)

# lcd
lcd_init()
setCursor(0, 0)    

time.sleep(10)

board.close()
