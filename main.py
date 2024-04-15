from uasyncio import sleep, run, create_task
from umachine import Pin, UART, soft_reset
from neopixel import NeoPixel
from usys import stdin, print_exception
from uselect import poll, POLLIN
from gc import enable
from micropython import const
from rp2 import bootsel_button

enable()

class NeopixelController:

    def __init__(self, pin_numbers: "list[int]", pin_counts: "list[int]", leds: "list[list[dict[str, int]]]") -> None:
        if len(pin_numbers) != len(pin_counts):
            raise ValueError(f"Pin Numbers and Pin Counts must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(pin_counts)} leds.")
        self.leds = []
        self.led_starting_positions = []
        self.led_count = []
        self.led_strip = []
        for pin, count in zip(pin_numbers, pin_counts):
            self.leds.append(NeoPixel(Pin(pin), count))
        for count, strip in enumerate(leds):
            for portion in strip:
                self.led_strip.append(count)
                self.led_starting_positions.append(portion["start"] - 1)
                self.led_count.append(portion["count"])

    async def color_fade(self, strip: int, colors: "list[tuple[int, int, int]]", mix: int, step_delay: float, delay: float) -> None:
        while True:
            for count in range(len(colors)):
                for fade_step in range(mix + 1):
                    intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(colors[count], colors[count + 1] if len(colors) > count + 1 else colors[0]))
                    for led in range(self.led_count[strip] - self.led_starting_positions[strip]):
                        self.leds[self.led_strip[strip]][self.led_starting_positions[strip] + led] = intermediate_color
                    self.leds[self.led_strip[strip]].write()
                    await sleep(step_delay)
            await sleep(delay)

    async def static_color(self, strip: int, color: "tuple[int, int, int]", delay: int, kill: bool, kill_mode: str) -> None:
        global tasks
        global MODES
        global FUNCTIONS
        global character

        for led in range(self.led_count[strip] - self.led_starting_positions[strip]):
            self.leds[self.led_strip[strip]][self.led_starting_positions[strip] + led] = color
        self.leds[self.led_strip[strip]].write()
        await sleep(delay)
        if kill:
            if kill_mode in MODES:
                tasks[strip] = [character, eval(FUNCTIONS[MODES[kill_mode][strip]], globals(), {"count": strip})]
            else:
                raise ValueError(f"Unknown mode. '{kill_mode}'. Available modes are: {MODES}")

    async def racing(self, strip: int, baseColor: "tuple[int, int, int]", racingColor: "tuple[int, int, int]", length: int, delay: float) -> None:
        for led in range(self.led_starting_positions[strip], self.led_count[strip]):
            self.leds[self.led_strip[strip]][led] = baseColor
        while True:
            for led in range(self.led_starting_positions[strip], self.led_count[strip]):
                self.leds[self.led_strip[strip]][led] = racingColor
                if led - length >= self.led_starting_positions[strip]:
                    self.leds[self.led_strip[strip]][led - length] = baseColor
                if led - length < self.led_starting_positions[strip]:
                    self.leds[self.led_strip[strip]][self.led_count[strip] - self.led_starting_positions[strip] + led - length] = baseColor
                self.leds[self.led_strip[strip]].write()
                await sleep(delay)

async def set_mode() -> None:
    global tasks
    global MODES
    global FUNCTIONS
    global character

    uart = UART(0, 9600, parity=None, stop = 1, bits = 8, tx=Pin(0), rx=Pin(1), timeout=10)
    select_poll = poll()
    select_poll.register(stdin, POLLIN)
    mode_names = []
    for mode, _ in MODES.items():
        mode_names.append(mode)

    while True:
        if bootsel_button() == 1:
            soft_reset()
        
        if uart.any() > 0:
            received_input = uart.read(1).decode("utf-8")
            if received_input != "\n":
                if received_input in mode_names:
                    character = received_input
                else:
                    print("Unknown Character")
        
        if select_poll.poll(0):
            received_input = stdin.read(1)
            if received_input != "\n":
                if received_input in mode_names:
                        if character != "D" and character != "E" or received_input == "A":
                            character = received_input
                else:
                    print("Unknown Character")

        for count, task in enumerate(tasks):
            if character in MODES:
                if task[0] != character and MODES[character][count] != "":
                    try:
                        task[1].cancel()
                    except:
                        pass
                    tasks[count] = [character, eval(FUNCTIONS[MODES[character][count]], globals(), {"count":count})]
        await sleep(0.1)

np = NeopixelController(pin_numbers=[2, 3, 4, 5], pin_counts=[44, 26, 12, 26], leds=[
    [{"start":1, "count":26}, {"start":27, "count":44}],
    [{"start":1, "count":26}],
    [{"start":1, "count":12}],
    [{"start":1, "count":26}]
])

tasks = []
for _ in np.led_count:
    tasks.append(["", None])
MODES = {
    "A": [const(""), const(""), const(""), const(""), const("")],
    "D": [const("Racing"), const("Team Colors"), const("Racing"), const("Team Colors"), const("Team Colors")],
    "E": [const("Rainbow"), const("Rainbow"), const("Rainbow"), const("Rainbow"), const("Rainbow")],
    "X": [const("Racing"), const("Team Colors"), const("Racing"), const("Team Colors"), const("Team Colors")],
    "N": [const("Detected Note"), const("Team Colors"), const("Detected Note"), const("Team Colors"), const("Team Colors")],
    "G": [const("Possessed Note"), const("Possessed Note"), const("Possessed Note"), const("Possessed Note"), const("Possessed Note")]
}
FUNCTIONS = {
    "Team Colors": const("create_task(np.color_fade(strip=count, colors=[(0, 0, 200), (200, 0, 200)], mix=128, step_delay=0.01, delay=0.8))"),
    "Rainbow": const("create_task(np.color_fade(strip=count, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], mix=128, step_delay=0.01, delay=0))"),
    "Detected Note": const("create_task(np.static_color(strip=count, color=(255, 40, 0), delay=1, kill=False, kill_mode=''))"),
    "Possessed Note": const("create_task(np.static_color(strip=count, color=(0, 255, 0), delay=2, kill=True, kill_mode='X'))"),
    "Racing": const("create_task(np.racing(strip=count, baseColor=(0, 0, 200), racingColor=(200, 0, 200), length=12, delay=0.15))")
}
character = "D"

try:
    run(set_mode())
except Exception as e:
    print_exception(e)
    sleep(1)
finally:
    for led in np.leds:
        led.fill((0, 0, 0))
        led.write()
    soft_reset()
