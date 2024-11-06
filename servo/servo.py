#https://wokwi.com/projects/413761246743497729
from machine import Pin, PWM
from utime import sleep, sleep_ms

sensor = Pin(34, Pin.IN)
led = Pin(2, Pin.OUT)
buzzer = Pin(21, Pin.OUT)
servo = PWM(Pin(33), freq=50)

while True:
    
    if(sensor.value()==1):
        print("Motion",sensor.value())
        led.value(1)
        buzzer.value(1)
        for i in range(1800, 8000):
            servo.duty_u16(i)
            sleep_ms(1)
        print("Motion Detected")
    else:
        led.value(0)
        buzzer.value(0)
        print("Motion Not Detected")
    sleep(0.5)