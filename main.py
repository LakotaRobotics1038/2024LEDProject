import uasyncio
import umachine
import neopixel
import usys
import uselect
import utime

class NeopixelController:

    def __init__(self, pin_numbers: "list[int]", pin_counts: "list[int]", leds: "list[list[dict[str, int]]]") -> None:
        if len(pin_numbers) != len(pin_counts):
            raise ValueError(f"Pin Numbers and Pin Counts must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(pin_counts)} LEDs.")
        self.leds = []
        self.led_starting_positions = []
        self.led_count = []
        self.led_strip = []
        for pin, count in zip(pin_numbers, pin_counts):
            self.leds.append(neopixel.NeoPixel(umachine.Pin(pin), count))
        for count, strip in enumerate(leds):
            for portion in strip:
                self.led_strip.append(count)
                self.led_starting_positions.append(portion["start"] - 1)
                self.led_count.append(portion["count"])

    def clear(self) -> None:
        for led in self.leds:
            led.fill((0, 0, 0))
            led.write()

    async def color_fade(self, strip: int, start_color: "tuple[int, int, int]", end_color: "tuple[int, int, int]", mix: int, delay: float) -> None:
        for fade_step in range(mix + 1):
            intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(start_color, end_color))
            for led in range(self.led_count[strip] - self.led_starting_positions[strip]):
                self.leds[self.led_strip[strip]][self.led_starting_positions[strip] + led] = intermediate_color
            self.leds[self.led_strip[strip]].write()
            await uasyncio.sleep(delay)

    async def team_colors(self, strip: int, start_color: "tuple[int, int, int]", end_color: "tuple[int, int, int]", mix: int, delay: float) -> None:
        while True:
            await np.color_fade(strip, start_color, end_color, mix, delay)
            await np.color_fade(strip, end_color, start_color, mix, delay)

    async def rainbow(self, strip: int, mix: int, delay: float) -> None:
        while True:
            await np.color_fade(strip, (255, 0, 0), (0, 255, 0), mix, delay)
            await np.color_fade(strip, (0, 255, 0), (0, 0, 255), mix, delay)
            await np.color_fade(strip, (0, 0, 255), (255, 0, 0), mix, delay)

    async def static_color(self, strip: int, color: "tuple[int, int, int]", delay: int, kill: bool, kill_mode: str) -> None:
        global character
        global tasks
        global mode
        global function

        for led in range(self.led_count[strip] - self.led_starting_positions[strip]):
            self.leds[self.led_strip[strip]][self.led_starting_positions[strip] + led] = color
            self.leds[self.led_strip[strip]].write()
        await uasyncio.sleep(delay)
        if kill:
            try:
                tasks[strip][0].cancel()
            except:
                pass
            tasks[strip] = [character, function[mode[kill_mode][strip]]]
            print(tasks[strip])

                

    async def racing(self, strip: int, baseColor: "tuple[int, int, int]", racingColor: "tuple[int, int, int]", length: int, delay: float) -> None:
        while True:
            for led in range(self.led_starting_positions[strip], self.led_count[strip]):
                self.leds[self.led_strip[strip]][led] = racingColor
                if led - length >= self.led_starting_positions[strip]:
                    self.leds[self.led_strip[strip]][led - length] = baseColor
                if led - length < self.led_starting_positions[strip]:
                    self.leds[self.led_strip[strip]][self.led_count[strip] - self.led_starting_positions[strip] + led - length] = baseColor
                self.leds[self.led_strip[strip]].write()
                await uasyncio.sleep(delay)

async def set_mode() -> None:
    global character
    global tasks
    global mode
    global function

    select_poll = uselect.poll()
    select_poll.register(usys.stdin, 1)

    while True:
        if select_poll.poll(0):
            received_input = usys.stdin.read(1)
            if received_input != "\n":
                character = received_input
        for count, task in enumerate(tasks):
            if task[0] != character and mode[character][count] != "":
                try:
                    task[1].cancel()
                except:
                    pass
                tasks[count] = [character, eval(function[mode[character][count]], globals(), {"count":count})]
        await uasyncio.sleep(0.01)

np = NeopixelController(pin_numbers=[2, 3, 4, 5], pin_counts=[44, 26, 12, 26], leds=[
    [{"start":1, "count":26}, {"start":27, "count":44}],
    [{"start":1, "count":26}],
    [{"start":1, "count":12}],
    [{"start":1, "count":26}]
])

character = "D"
tasks = []
for _ in np.leds:
    tasks.append(["", None])
mode = {
    "D":["Racing", "Team Colors", "Racing", "Team Colors", "Team Colors"],
    "E":["Rainbow", "Rainbow", "Rainbow", "Rainbow", "Rainbow"],
    "N":["Detected Note", "", "Detected Note", "", ""],
    "G":["Possessed Note", "", "Possessed Note", "", ""]
}
function = {
    "Team Colors":"uasyncio.create_task(np.team_colors(strip=count, start_color=(0, 0, 200), end_color=(200, 0, 200), mix=128, delay=0.01))",
    "Rainbow":"uasyncio.create_task(np.rainbow(strip=count, mix=128, delay=0.01))",
    "Detected Note":"uasyncio.create_task(np.static_color(strip=count, color=(255, 40, 0), delay=1, kill=False, kill_mode=''))",
    "Possessed Note":"uasyncio.create_task(np.static_color(strip=count, color=(0, 255, 0), delay=2, kill=True, kill_mode='D'))",
    "Racing":"uasyncio.create_task(np.racing(strip=count, baseColor=(0, 0, 200), racingColor=(200, 0, 200), length=3, delay=0.1))"
}


try:
    uasyncio.run(set_mode())
except Exception as e:
    usys.print_exception(e)
    utime.sleep(1)
finally:
    np.clear()
    umachine.reset()