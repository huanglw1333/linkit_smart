# pwm first test #

import time
# from PyMata.pymata import PyMata

def pwm_start(board_id):
    # pwm_init_para()
    PWM_pin = 5
    PWM_value = 0
    PWM_step = 17
    PWM_interval = 0.1
    board_id.set_pin_mode(PWM_pin, board_id.PWM, board_id.DIGITAL)
    print "Start PWM test by pin D23..."

    while True:
        board_id.analog_write(PWM_pin, PWM_value)
        time.sleep(0.1)
        PWM_value += PWM_step
        if PWM_value >= 255:
            while True:
                board_id.analog_write(PWM_pin, PWM_value)
                time.sleep(0.1)
                PWM_value -= PWM_step
                if PWM_value <= 0:
                    break





#board.close()
