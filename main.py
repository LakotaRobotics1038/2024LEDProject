import machine
import neopixel
import time
import _thread
import sys

class NeopixelController:
    def __init__(self, pin_numbers: list, num_leds: list) -> None:
        if len(pin_numbers) != len(num_leds):
            raise ValueError(f"pin_numbers and num_leds must have the same length. Current lengths are {len(pin_numbers)} and {len(num_leds)} respectively.")
        for pin, num in zip(pin_numbers, num_leds):
            self.leds = [neopixel.NeoPixel(machine.Pin(pin), num)]

    def clear(self) -> None:
        for led in self.leds:
            led.fill((0, 0, 0))
            led.write()

    def color_fade(self, color_1: tuple, color_2: tuple, mix: int, current_character: str) -> None:
        global character
        for fade_step in range(mix + 1):
            if character != current_character:
                break
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(color_1, color_2))
            for led in self.leds:
                led.fill(intermediate_color)
                led.write()
            time.sleep(0.01)

    def static_color(self, strip: int, color: tuple, delay: int, current_character: str):
        global character
        self.leds[strip].fill(color)
        self.leds[strip].write()
        for i in range(int(delay / 10)):
            if current_character != character:
                break
            time.sleep(0.01)

    
    def overlapping_values(self, strip, baseColor, chasingColor, length, current_character):
        global character
        self.leds[strip].fill(baseColor)
        self.leds[strip].write()
        for num in range(len(self.leds[strip]) + length):
            if character != current_character:
                break
            if num < len(self.leds[strip]):
                self.leds[strip][num] = chasingColor
                self.leds[strip].write()
            if 0 < num:
                self.leds[strip][num - length] = baseColor
                self.leds[strip].write()
            time.sleep(0.05)


def get_input():
    global character, terminate_thread
    while terminate_thread != True:
        recieved_input = sys.stdin.read(1)
        if recieved_input != "\n":
            character = recieved_input

np = NeopixelController(pin_numbers=[2, 3, 4, 5], num_leds=[[[0, 26], [27, 35], [36, 44]], [[0, 26]], [[0, 12]], [[0, 26]]])
np.clear()

character = "D"
terminate_thread = False

_thread.start_new_thread(get_input, ())

try:
    while True:
        if character == "D":
            np.color_fade(color_1=(0, 0, 200), color_2=(200, 0, 200), mix=128, current_character="D")
            np.color_fade(color_1=(200, 0, 200), color_2=(0, 0, 200), mix=128, current_character="D")
        elif character == "E":
            np.color_fade(color_1=(255, 0, 0), color_2=(0, 255, 0), mix=190, current_character="E")
            np.color_fade(color_1=(0, 255, 0), color_2=(0, 0, 255), mix=190, current_character="E")
            np.color_fade(color_1=(0, 0, 255), color_2=(255, 0, 0), mix=190, current_character="E")
        elif character == "N":
            np.static_color(strip=0, color=(255, 40, 0), delay=1, current_character="N")
        elif character == "Q":
            np.overlapping_values(strip=0, baseColor=(0, 0, 200), chasingColor=(200, 0, 200), length=7, current_character="Q")
        elif character == "G":
            np.static_color(strip=0, color=(0, 255, 0), delay=2000, current_character="G")
            if character == "G":
                character = "D"
except Exception as exception:
    print(sys.print_exception(exception))
    terminate_thread = True
    np.clear()
    sys.exit()
