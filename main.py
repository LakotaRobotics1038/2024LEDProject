import machine
import neopixel
import time
import _thread
import sys

class NeopixelController:
    def __init__(self, pin_numbers: list[int], num_leds: list[int]) -> None:
        if len(pin_numbers) != len(num_leds):
            raise ValueError(f"pin_numbers and num_leds must have the same length. Current lengths are {len(pin_numbers)} and {len(num_leds)} respectively.")
        self.leds = [neopixel.NeoPixel(machine.Pin(pin), num) for pin, num in zip(pin_numbers, num_leds)]

    def clear(self) -> None:
        for pixel in self.leds:
            pixel.fill((0, 0, 0))
            pixel.write()

    def color_fade(self, color_1: tuple[int, int, int], color_2: tuple[int, int, int], mix: int, delay: float, current_character: str) -> None:
        global character
        for fade_step in range(mix + 1):
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(color_1, color_2))
            for led in self.leds:
                led.fill(intermediate_color)
                led.write()
            time.sleep(delay)
            if character != current_character:
                break

def buffer_stdin():
    global character, terminate_thread
    while terminate_thread != True:
        recieved_input = sys.stdin.read(1)
        if recieved_input != "\n":
            character = recieved_input

np = NeopixelController(pin_numbers=[2, 3, 4, 5, 6], num_leds=[26, 26, 44, 26, 12])
np.clear()

character = " "
terminate_thread = False

buffer_stdin_thread = _thread.start_new_thread(buffer_stdin, ())

try:
    while True:
        if character == "d":
            np.color_fade(color_1=(0, 0, 200), color_2=(200, 0, 200), mix=250, delay=0.001, current_character="d")
            np.color_fade(color_1=(200, 0, 200), color_2=(0, 0, 200), mix=250, delay=0.001, current_character="d")
        elif character == "e":
            np.color_fade(color_1=(255, 0, 0), color_2=(0, 255, 0), mix=375, delay=0.001, current_character="e")
            np.color_fade(color_1=(0, 255, 0), color_2=(0, 0, 255), mix=375, delay=0.001, current_character="e")
            np.color_fade(color_1=(0, 0, 255), color_2=(255, 0, 0), mix=375, delay=0.001, current_character="e")
        elif character == "n":
            np.color_fade(color_1=(255, 165, 0), color_2=(255, 165, 0), mix=1, delay=0.001, current_character="n")
        elif character == "g":
            np.color_fade(color_1=(0, 255, 0), color_2=(0, 255, 0), mix=1, delay=0.001, current_character="g")
            time.sleep(2)
            if character == "g":
                character = "d"
except KeyboardInterrupt:
    terminate_thread = True
    np.clear()
    machine.reset()

