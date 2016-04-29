import requests
import socket
import threading
import logging
import mraa
from PyMata.pymata import PyMata

# change this to the values from MCS web console
DEVICE_INFO = {
    'device_id' : 'DgntFX7Y',
    'device_key' : 'KeaqpQbiIe3TBUjt'
}

# change 'INFO' to 'WARNING' to filter info messages
logging.basicConfig(level='INFO')

heartBeatTask = None
"""
def request_device_info():
        logging.basicConfig(level = logging.INFO)
        logging.info("[Gerald]: request_device_info start")
        requestAPI = 'https://api.mediatek.com/mcs/v2/devices/%(device_id)s/firmwares/available
        r = requests.get(requestAPI % DEVICE_INFO,
                 headers = {'deviceKey' : DEVICE_INFO['device_key'],
                            'Content-Type' : 'application/json'})
        logging.info("[Gerald]: %s" % r.status_code)
        logging.info("[Gerald]: %s" % r.text)
"""

def establishCommandChannel():
    # Query command server's IP & port
    connectionAPI = 'https://api.mediatek.com/mcs/v2/devices/%(device_id)s/connections.csv'
    r = requests.get(connectionAPI % DEVICE_INFO,
                 headers = {'deviceKey' : DEVICE_INFO['device_key'],
                            'Content-Type' : 'text/csv'})
    logging.info("Command Channel IP,port=" + r.text)
    logging.info("Command Channel IP,port=" + r.text)
    (ip, port) = r.text.split(',')

    # Connect to command server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))
    s.settimeout(None)

    # Heartbeat for command server to keep the channel alive
    def sendHeartBeat(commandChannel):
        keepAliveMessage = '%(device_id)s,%(device_key)s,0' % DEVICE_INFO
        commandChannel.sendall(keepAliveMessage)
        logging.info("beat:%s" % keepAliveMessage)

    def heartBeat(commandChannel):
        sendHeartBeat(commandChannel)
        # Re-start the timer periodically
        global heartBeatTask
        heartBeatTask = threading.Timer(40, heartBeat, [commandChannel]).start()

    heartBeat(s)
    return s

def waitAndExecuteCommand(commandChannel):
    while True:
        command = commandChannel.recv(1024)
        logging.info("recv:" + command)
        # command can be a response of heart beat or an update of the LED_control,
        # so we split by ',' and drop device id and device key and check length
        fields = command.split(',')[2:]

        if len(fields) > 1:
            timeStamp, dataChannelId, commandString1, commandString2 = fields
            #timeStamp, dataChannelId, commandString1 = fields
            if dataChannelId == 'LED_PWM_Control':
                logging.info("[Gerald] LED_PWM_Control")
                # check the value - it's either 0 or 1
                commandValue1 = int(commandString1)
                commandValue2 = int(commandString2)
                logging.info("[Gerald]led value1:%d" % commandValue1)
                logging.info("[Gerald]led value2:%d" % commandValue2)
                setLED(commandValue1)
                                                             
pin = None
def setupLED():
  global PWM_pin
  global board
  PWM_pin = 5
  # use pin D5 as pwm to adjest LED.
  board = PyMata('/dev/ttyS0', verbose = True)
  board.set_pin_mode(PWM_pin, board.PWM, board.DIGITAL)
  print "Start PWM test by pin D5"

def setLED(PWM_value):
  # Note the LED is "reversed" to the pin's GPIO status.
  # So we reverse it here.

  board.analog_write(PWM_pin, PWM_value)

if __name__ == '__main__':
  setupLED()
  channel = establishCommandChannel()
  #request_device_info()
  waitAndExecuteCommand(channel)
