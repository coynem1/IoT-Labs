import gpiozero as gpz

button = gpz.Button(17)
led = gpz.LED(2)

while True:
    button.wait_for_press()
    led.toggle()