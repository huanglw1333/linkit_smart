# LCD module HD44780
import time
import sys
import signal
import pymata_pwm

from PyMata.pymata import PyMata

board = PyMata('/dev/ttyS0', verbose = True)

###### 4-bits mode bit config ######
# bit7 ---------------------- bit0 #
#  d7  d6  d5  d4  bl  en  rw  rs  #
####################################

device_addr = 0x27  # device address
bl_bit = 0x08       # backlight bit
en_bit = 0x04       # read/write enable bit
rw_bit = 0x02       #
rs_bit = 0x01       #

DATA    = 0x01
COMMAND = 0x00

setBackLight = 1

def delay_ms(time_ms):
    time.sleep(time_ms/1000)

# def i2c_send(value, mode):

def i2c_send_4bits(value, mode):
    high_byte = value & 0xF0
    low_byte  = value << 4

    # check mode is data or command
    if mode == DATA:
        high_byte |= rs_bit
        low_byte  |= rs_bit

    # check backlight
    if setBackLight == 1:
        high_byte |= bl_bit
        low_byte  |= bl_bit

    i2c_send_enable(high_byte)
    i2c_send_enable(low_byte)

def i2c_send_enable(value):
    board.i2c_write(device_addr, value | en_bit)
    board.i2c_write(device_addr, value & ~en_bit)

def lcd_init():
    # setup i2c pin, D2: SDA, D3: SCL
    board.i2c_config(0, board.DIGITAL, 3, 2)
    print "i2c config end, send data begin"

    # start LCD init sequence
    board.i2c_write(0x27, 0x00)
    delay_ms(100)

    # function set
    i2c_send_enable(0x30)
    delay_ms(5)
    i2c_send_enable(0x30)
    delay_ms(1)
    i2c_send_enable(0x30)
    delay_ms(1)
    i2c_send_enable(0x20)
    delay_ms(1)

    # function set command
    i2c_send_4bits(0x28, COMMAND)
    delay_ms(1)

    # display on/off control
    i2c_send_4bits(0x08, COMMAND)
    delay_ms(1)

    # clear display
    i2c_send_4bits(0x01, COMMAND)
    delay_ms(5)

    # entry mode set
    i2c_send_4bits(0x06, COMMAND)
    delay_ms(1)
    # end LCD init

def setCursor_pos(col, row):
    row_offsetDef = [0x00, 0x40]                      # DDRAM start address line-1: 0x00 line-2: 0x40
    cursor_data = (0x80 | (col + row_offsetDef[row])) # 0x08: set ddram address
    i2c_send_4bits(cursor_data, COMMAND)

def lcd_print(input_string):
    for i in range(len(input_string)):
        # convert string to ASCII and show on LCD
        input_char = ord(input_string[i])
        i2c_send_4bits(input_char, DATA)

# if __name__ == "__main__":
# lcd init sequence
lcd_init()

# set cursor blink
i2c_send_4bits(0x0F, COMMAND)
delay_ms(1)

# set first col and row
setCursor_pos(0, 0)
lcd_print("LED breath...")
setCursor_pos(0, 1)
lcd_print("!!!START!!!")
time.sleep(1)

pymata_pwm.pwm_start(board)

board.close()
