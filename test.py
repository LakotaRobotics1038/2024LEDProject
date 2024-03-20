import uasyncio
import umachine
import neopixel
import utime
import _thread
import usys
import math
import gc

gc.enable()

class NeopixelController:
    def __init__(self, pin_numbers: list, leds: list) -> None:
        if len(pin_numbers) != len(leds):
            print(f"Pin Numbers and LEDs must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(leds)} LEDs.")
        self.leds = []
        self.led_starting_positions = []
        for pin, strip in zip(pin_numbers, leds):
            for portion in strip:
                self.leds.append(neopixel.NeoPixel(umachine.Pin(pin), portion["count"]))
                self.led_starting_positions.append(portion["start"] - 1)

    def clear(self) -> None:
        for led in self.leds:
            led.fill((0, 0, 0))
            led.write()

    async def color_fade(self, strip: int, color_1: tuple, color_2: tuple, mix: int, current_character: str) -> None:
        global character
        for fade_step in range(mix + 1):
            if character != current_character:
                break
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(color_1, color_2))
            for led in range(len(self.leds[strip]) - self.led_starting_positions[strip]):
                self.leds[strip][self.led_starting_positions[strip] + led] = intermediate_color
            self.leds[strip].write()
            await uasyncio.sleep(0.01)
        for fade_step in range(mix + 1):
            if character != current_character:
                break
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_2 + fade_step / mix * rgb_1) for rgb_1, rgb_2 in zip(color_1, color_2))
            for led in range(len(self.leds[strip]) - self.led_starting_positions[strip]):
                self.leds[strip][self.led_starting_positions[strip] + led] = intermediate_color
            self.leds[strip].write()
            await uasyncio.sleep(0.01)
            
    async def rainbow(self, strip:int, frequency: float, mix: int, width:int, center:int, current_character: str) -> None:
        global character
        for fade_step in range(mix, 0, -1):
            if character != current_character:
                break
            rainbow_color = (int(math.sin(frequency * fade_step + 1) * width + center), int(math.sin(frequency * fade_step + 3) * width + center), int(math.sin(frequency * fade_step + 5) * width + center))
            for led in range(len(self.leds[strip]) - self.led_starting_positions[strip]):
               self.leds[strip][self.led_starting_positions[strip] + led] = rainbow_color
            self.leds[strip].write()
            await uasyncio.sleep(0.01)

    async def static_color(self, strip: int, color: tuple, delay: int, current_character: str) -> None:
        global character
        for led in range(len(self.leds[strip]) - self.led_starting_positions[strip]):
            self.leds[strip][self.led_starting_positions[strip] + led] = color
        self.leds[strip].write()
        for _ in range(delay):
            if character != current_character:
                break
            await uasyncio.sleep(0.01)

    async def racing(self, strip: int, baseColor: tuple, racingColor: tuple, length: int, current_character: str):
        global character
        for led in range(self.led_starting_positions[strip], len(self.leds[strip])):
            if character != current_character:
                break
            self.leds[strip][led] = racingColor
            if led - length >= self.led_starting_positions[strip]:
                self.leds[strip][led - length] = baseColor
            if led - length < self.led_starting_positions[strip]:
                self.leds[strip][len(self.leds[strip]) - self.led_starting_positions[strip] + led - length] = baseColor
            self.leds[strip].write()
            await uasyncio.sleep(0.05)

def get_input():
    global character
    global terminate_thread
    while terminate_thread != True:
        recieved_input = usys.stdin.read(1)
        if recieved_input != "\n":
            character = recieved_input

async def set_mode():
    global character
    
    while True:
        if character == "D":
            for task in tasks:
                if task == "D1":
                    continue
                elif task.find("1") != -1:
                    try:
                        tasks[task].cancel()
                    except:
                        pass
                    del tasks[task]
                    tasks.update({"D1":uasyncio.create_task(np.color_fade(strip=2, color_1=(0, 0, 200), color_2=(200, 0, 200), mix=128, current_character="D"))})
        elif character == "E":
            for task in tasks:
                if task == "E1":
                    continue
                elif task.find("1") != -1:
                    try:
                        tasks[task].cancel()
                    except:
                        pass
                    del tasks[task]
                    tasks.update({"E1":uasyncio.create_task(np.rainbow(strip=1, frequency=0.1, mix=127, width=127, center=128, current_character="E"))})
        elif character == "N":
            pass
            # np.static_color(strip=2, color=(255, 40, 0), delay=1, current_character="N")
        elif character == "Q":
            pass
            # np.racing(strip=0, baseColor=(0, 0, 200), racingColor=(200, 0, 200), length=3, current_character="Q")
        elif character == "G":
            # np.static_color(strip=0, color=(0, 255, 0), delay=200, current_character="G")
            if character == "G":
                character = "D"
        await uasyncio.sleep(0.1)

np = NeopixelController(pin_numbers=[2, 3, 4, 5], leds=[[{"start":1, "count":10}, {"start":11, "count":20}, {"start":21, "count":26}], [{"start":0, "count":25}], [{"start":0, "count":11}], [{"start":0, "count":25}]])

np.clear()

character = "D"
terminate_thread = False
tasks = {"1":0, "2":0}

_thread.start_new_thread(get_input, ())

try:
    uasyncio.run(set_mode())
except Exception as e:
    usys.print_exception(e)
finally:
    terminate_thread = True
    np.clear()
    utime.sleep(0.5)
    umachine.reset()
