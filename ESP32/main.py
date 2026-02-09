import machine 
import time

pin = machine.Pin(2, machine.Pin.OUT)
while True:
    pin.value(1)
    print("LED ON")
    time.sleep(1)
    pin.value(0)
    print("LED OFF")
    time.sleep(1)
