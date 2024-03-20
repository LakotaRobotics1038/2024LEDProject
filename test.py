import uasyncio
import umachine
import neopixel
import usys
import uselect

class NeopixelController:
    def __init__(self, pin_numbers: "list[int]", pin_counts: "list[int]", leds: "list[list[dict[str, int]]]") -> None:
        if len(pin_numbers) != len(pin_counts):
            raise ValueError(f"Pin Numbers and Pin Counts must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(pin_counts)} LEDs.")
        self.leds = []
        self.led_starting_positions = []
        self.led_count = []
        for pin, count in zip(pin_numbers, pin_counts):
            self.leds.append(neopixel.NeoPixel(umachine.Pin(pin), count))
        for strip in leds:
            for portion in strip:
                self.led_starting_positions.append(portion["start"] - 1)
                self.led_count.append(portion["count"] - 1)

    def clear(self) -> None:
        for led in self.leds:
            led.fill((0, 0, 0))
            led.write()

    async def color_fade(self, strip: int, color_1: "tuple[int, int, int]", color_2: "tuple[int, int, int]", mix: int, delay: float) -> None:
        while True:
            for fade_step in range(mix + 1):
                intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(color_1, color_2))
                for led in range(self.led_count[strip - 1] - self.led_starting_positions[strip - 1]):
                    self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = intermediate_color
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)
            for fade_step in range(mix + 1):
                intermediate_color = tuple(int((1 - fade_step / mix) * rgb_2 + fade_step / mix * rgb_1) for rgb_1, rgb_2 in zip(color_1, color_2))
                for led in range(self.led_count[strip - 1] - self.led_starting_positions[strip - 1]):
                    self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = intermediate_color
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)

    async def rainbow(self, strip: int, mix: int, delay: float) -> None:
        while True:
            for fade_step in range(mix + 1):
                intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip((255, 0, 0), (0, 255, 0)))
                for led in range(self.led_count[strip - 1] - self.led_starting_positions[strip - 1]):
                    self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = intermediate_color
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)
            for fade_step in range(mix + 1):
                intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip((0, 255, 0), (0, 0, 255)))
                for led in range(self.led_count[strip - 1] - self.led_starting_positions[strip - 1]):
                    self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = intermediate_color
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)
            for fade_step in range(mix + 1):
                intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip((0, 0, 255), (255, 0, 0)))
                for led in range(len(self.leds[strip - 1]) - self.led_starting_positions[strip - 1]):
                    self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = intermediate_color
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)

    async def static_color(self, strip: int, color: "tuple[int, int, int]", delay: int, exit_after_delay: bool) -> None:
        while True:
            for led in range(len(self.leds[strip - 1]) - self.led_starting_positions[strip - 1]):
                self.leds[strip - 1][self.led_starting_positions[strip - 1] + led] = color
            self.leds[strip - 1].write()
            await uasyncio.sleep(delay)
            if exit_after_delay:
                return

    async def racing(self, strip: int, baseColor: "tuple[int, int, int]", racingColor: "tuple[int, int, int]", length: int, delay: float) -> None:
        while True:
            for led in range(self.led_starting_positions[strip - 1], len(self.leds[strip - 1])):
                self.leds[strip - 1][led] = racingColor
                if led - length >= self.led_starting_positions[strip - 1]:
                    self.leds[strip - 1][led - length] = baseColor
                if led - length < self.led_starting_positions[strip - 1]:
                    self.leds[strip - 1][len(self.leds[strip - 1]) - self.led_starting_positions[strip - 1] + led - length] = baseColor
                self.leds[strip - 1].write()
                await uasyncio.sleep(delay)

async def set_mode():
    character = "D"
    select_poll = uselect.poll()
    select_poll.register(usys.stdin, 1)
    while True:
        if select_poll.poll(0):
            recieved_input = usys.stdin.read(1)
            if recieved_input != "\n":
                character = recieved_input
        if character == "D":
            for name, task in tasks.items():
                if name == "D2":
                    continue
                elif name.find("2") != -1:
                    try:
                        task.cancel()
                    except:
                        pass
                    del tasks[name]
                    tasks.update({"D2":uasyncio.create_task(np.color_fade(strip=2, color_1=(0, 0, 200), color_2=(200, 0, 200), mix=128, delay=0.01))})
        elif character == "E":
            for name, task in tasks.items():
                if name == "E1":
                    continue
                elif name.find("1") != -1:
                    try:
                        task.cancel()
                    except:
                        pass
                    del tasks[name]
                    tasks.update({"E1":uasyncio.create_task(np.rainbow(strip=1, mix=128, delay=0.01))})
        elif character == "N":
            for name, task in tasks.items():
                if name == "N2":
                    continue
                elif name.find("2") != -1:
                    try:
                        task.cancel()
                    except:
                        pass
                    del tasks[name]
                    tasks.update({"N2":uasyncio.create_task(np.static_color(strip=2, color=(255, 40, 0), delay=1, exit_after_delay=False))})
        elif character == "Q":
            for name, task in tasks.items():
                if name == "Q3":
                    continue
                elif name.find("3") != -1:
                    try:
                        task.cancel()
                    except:
                        pass
                    del tasks[name]
                    tasks.update({"Q3":uasyncio.create_task(np.racing(strip=3, baseColor=(0, 0, 200), racingColor=(200, 0, 200), length=3, delay=0.1))})
        elif character == "G":
            for name, task in tasks.items():
                if name == "G1":
                    continue
                elif name.find("1") != -1:
                    try:
                        task.cancel()
                    except:
                        pass
                    del tasks[name]
                    tasks.update({"G1":uasyncio.create_task(np.static_color(strip=1, color=(0, 255, 0), delay=2, exit_after_delay=True))})
        await uasyncio.sleep(0.1)

np = NeopixelController(pin_numbers=[2, 3, 4, 5], pin_counts=[26, 44, 12, 26], leds=[[{"start":1, "count":10}, {"start":11, "count":20}, {"start":21, "count":26}], [{"start":1, "count":44}], [{"start":1, "count":12}], [{"start":1, "count":26}]])
tasks = {"1":"", "2":"", "3":"", "4":"", "5":"", "6":""}

try:
    uasyncio.run(set_mode())
except Exception as e:
    usys.print_exception(e)
finally:
    np.clear()
    umachine.reset()