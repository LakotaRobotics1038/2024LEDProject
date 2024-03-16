import time
import board
import digitalio
import busio
import usb_cdc
import neopixel
from rainbowio import colorwheel
from digitalio import DigitalInOut, Direction, Pull

ORDER = neopixel.GRB
Alliance = "" # "R"ed or "B"lue or "" Unknown 
AnimationFrame = 0

ColorMode_1038 = 0
ColorMode_Cone = 1
ColorMode_Cube = 2
ColorMode_Confirmed = 3
ColorMode_Rainbow = 4

Nothing = 0
Confirmed = 1
Cone = 2
Cube = 3

IndicatorMode = Nothing
ColorMode = ColorMode_1038 # Initialize
BluePurpleLength = 16

serial = usb_cdc.data
uart = busio.UART(board.GP0, board.GP1, baudrate=9600)

switch = DigitalInOut(board.GP11)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

xAnimationFrame = 0
topRightAnimationFrame = 0
bottomRightAnimationFrame = 0
bottomLeftAnimationFrame = 0
topLeftAnimationFrame = 0
nichKnackAnimationFrame = 0
mainAnimationFrame = 0

# Define the number of pixels in the LED strips.
RIGHT_SIDE = 100
NICH_KNACK = 100
LEFT_SIDE = 100
LEFT_SIDE_FIX = 100
X_FRAME = 42

pixels1 = neopixel.NeoPixel(board.GP6, LEFT_SIDE_FIX, brightness=0.8, auto_write=False)
pixels2 = neopixel.NeoPixel(board.GP7, LEFT_SIDE_FIX, brightness=0.8, auto_write=False)
pixels3 = neopixel.NeoPixel(board.GP4, LEFT_SIDE_FIX, brightness=0.8, auto_write=False)
pixels4 = neopixel.NeoPixel(board.GP5, LEFT_SIDE_FIX, brightness=0.8, auto_write=False)
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

def GetChar():                   # Get any color change requests from the USB or RoboRio serial port
   Result = ""
   if serial and serial.in_waiting > 0:
      byte = serial.read(1)
      print("USB: ", byte)
      Result = byte
   if uart.in_waiting > 0:        
       byte = uart.read(1)
       print("RoboRio: ", byte)
       Result = byte
   return Result if Result else ""

def SetLeftFixHighHeight(pixels, x,r,g,b):
   if (x <=7):
      pixels[x + 90] = (r,g,b)
      pixels[91 - x] = (r,g,b)
   else:
      pixels[x - 9] = (r,g,b)
      pixels[92 - x] = (r,g,b)

ledState = True

while True: 
   #print(topRightAnimationFrame)
   # print(switch.value)
   Incoming = GetChar()
   if Incoming != "":
      if (Incoming == b'R'):
         print("Red")
         Alliance = "R"
      if (Incoming == b'B'):
         print("Blue")
         Alliance = "B"
      if (Incoming == b'G'):
         print("Green")
         IndicatorMode = Confirmed
      if (Incoming == b'Y'):
         print("Cone")
         IndicatorMode = Cone
      if (Incoming == b'P'):
         print("Cube")
         IndicatorMode = Cube
      if (Incoming == b'#'):
         print("1038")
         ColorMode = ColorMode_1038
      if (Incoming == b'!'):
         print("Rainbow")
         ColorMode = ColorMode_Rainbow
      if (Incoming == b'D'):
         print("Disabled")
         ColorMode = ColorMode_1038
         IndicatorMode = Nothing

   if (ColorMode == ColorMode_1038):
      time.sleep(0.05)
      ledState = not ledState
      led.value=ledState
      for i in range(LEFT_SIDE_FIX):
            pixels1[i] = (0, 0, 200) # Assume everything is blue
            pixels2[i] = (0, 0, 200) # Assume everything is blue
            pixels3[i] = (0, 0, 200) # Assume everything is blue
            pixels4[i] = (0, 0, 200) # Assume everything is blue
      for i in range (topLeftAnimationFrame, topLeftAnimationFrame+25):
            if i <=49:
               SetLeftFixHighHeight(pixels1, i,200, 0, 200)
               SetLeftFixHighHeight(pixels2, i,200, 0, 200)
               SetLeftFixHighHeight(pixels3, i,200, 0, 200)
               SetLeftFixHighHeight(pixels4, i,200, 0, 200)
            else:
               SetLeftFixHighHeight(pixels1, i-49, 200, 0, 200)
               SetLeftFixHighHeight(pixels2, i-49, 200, 0, 200)
               SetLeftFixHighHeight(pixels3, i-49, 200, 0, 200)
               SetLeftFixHighHeight(pixels4, i-49, 200, 0, 200)
      topLeftAnimationFrame = topLeftAnimationFrame + 1
      if topLeftAnimationFrame > 49:
         topLeftAnimationFrame = 0
         
   # if (ColorMode == ColorMode_Rainbow):
   #    time.sleep(0.05)
   #    for i in range(0, 149):                  
   #       rc_index = (i * 256 // RIGHT_SIDE) + AnimationFrame * 16
   #       pixels1[i] = colorwheel(rc_index & 255)
   #    for i in range(0, NICH_KNACK):                  
   #       rc_index = (i * 256 // NICH_KNACK) + AnimationFrame * 16
   #       pixels2[i] = colorwheel(rc_index & 255)
   #    for i in range(0, LEFT_SIDE):                  
   #       rc_index = (i * 256 // LEFT_SIDE) + AnimationFrame * 16
   #       pixels3[i] = colorwheel(rc_index & 255)
   #    for i in range(0, LEFT_SIDE_FIX):                  
   #       rc_index = (i * 256 // LEFT_SIDE_FIX) + AnimationFrame * 16
   #       pixels4[i] = colorwheel(rc_index & 255)

   # FillAllianceColor()
   
   pixels1.show()
   pixels2.show()
   pixels3.show()
   pixels4.show()

   AnimationFrame = AnimationFrame + 1
   if AnimationFrame > 63:
      AnimationFrame = 0
   #time.sleep(0.05)