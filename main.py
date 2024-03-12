import machine
import neopixel
import select
import sys
import time

serial_poll = select.poll()
serial_poll.register(sys.stdin, 1)

class NeopixelController:
    def __init__(self, pin_numbers: list[int], num_leds: list[int]) -> None:
        if len(pin_numbers) != len(num_leds):
            raise ValueError(f"pin_numbers and num_leds must have the same length. Current lengths are {len(pin_numbers)} and {len(num_leds)} respectively.")
        self.leds = [neopixel.NeoPixel(machine.Pin(pin), num) for pin, num in zip(pin_numbers, num_leds)]

    def clear(self) -> None:
        for pixel in self.leds:
            pixel.fill((0, 0, 0))
            pixel.write()

    def color_fade(self, color_1: tuple[int, int, int], color_2: tuple[int, int, int], mix: int, delay: float, current_char: str) -> None:
        for fade_step in range(mix + 1):
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(color_1, color_2))
            for led in self.leds:
                led.fill(intermediate_color)
                led.write()
            time.sleep(delay)
            if read_serial() != current_char:
                break

def read_serial():
    if serial_poll.poll(0):
        return sys.stdin.read(1)

np = NeopixelController([2, 3, 4, 5, 6], [26, 26, 44, 26, 12])
np.clear()
char = ""

while True:
    print("char: "+str(str(read_serial()).encode('unicode_escape')))
    if read_serial():
        char = read_serial()
    print(str(char).encode('unicode_escape'))
    print("still running")
    if char == "t":
        print("starting")
        np.color_fade(color_1 = (0, 0, 200), color_2 = (200, 0, 200), mix = 500, delay = 0.001, current_char = char)
        np.color_fade(color_1 = (200, 0, 200), color_2 = (0, 0, 200), mix = 500, delay = 0.001, current_char = char)
    elif char == "r":
        np.color_fade(color_1 = (255, 0, 0), color_2 = (0, 255, 0), mix = 500, delay = 0.001, current_char = char)
        np.color_fade(color_1 = (0, 255, 0), color_2 = (0, 0, 255), mix = 500, delay = 0.001, current_char = char)
        np.color_fade(color_1 = (0, 0, 255), color_2 = (255, 0, 0), mix = 500, delay = 0.001, current_char = char)
    time.sleep(1)