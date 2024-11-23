from uasyncio import sleep, run, create_task
from umachine import Pin, UART, soft_reset
from neopixel import NeoPixel
from usys import stdin, print_exception
from uselect import poll, POLLIN
from micropython import const
from rp2 import bootsel_button
from math import sin


class NeopixelController:
    def __init__(
        self,
        pin_numbers: "tuple[int, ...]",
        pin_counts: "tuple[int, ...]",
        leds: "tuple[tuple[dict[str, int], ...], ...]",
    ) -> None:
        if len(pin_numbers) != len(pin_counts):
            raise ValueError(f"Pin Numbers and Pin Counts must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(pin_counts)} leds.")
        self.leds: list[NeoPixel] = []
        self.start: list[int] = []
        self.end: list[int] = []
        self.led_strip: list[int] = []
        self.led_count: list[int] = []
        for pin, count in zip(pin_numbers, pin_counts):
            self.leds.append(NeoPixel(Pin(pin), count))
        for count, strip in enumerate(leds):
            for portion in strip:
                self.led_strip.append(count)
                self.start.append(portion["start"] - 1)
                self.end.append(portion["end"])
                self.led_count.append(portion["end"] - portion["start"] - 1)

    async def color_fade(
        self,
        strip: int,
        colors: "list[tuple[int, int, int]]",
        mix: int,
        step_delay: float,
        delay: float,
    ) -> None:
        while True:
            for count in range(len(colors)):
                for fade_step in range(mix + 1):
                    intermediate_color = tuple(int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(colors[count], colors[(count + 1) % len(colors)]))
                    for led in range(self.led_count[strip]):
                        self.leds[self.led_strip[strip]][self.start[strip] + led] = intermediate_color
                    self.leds[self.led_strip[strip]].write()
                    await sleep(step_delay)
            await sleep(delay)

    async def static_color(
        self,
        strip: int,
        color: "tuple[int, int, int]",
        delay: int,
        kill: bool,
        kill_mode: str,
    ) -> None:
        global tasks
        global MODES
        global FUNCTIONS
        global character

        for led in range(self.led_count[strip]):
            self.leds[self.led_strip[strip]][self.start[strip] + led] = color
        self.leds[self.led_strip[strip]].write()
        await sleep(delay)
        if kill:
            if kill_mode in MODES:
                tasks[strip] = [character, eval(FUNCTIONS[MODES[kill_mode][strip]], globals(), {"count": strip})]
            else:
                raise ValueError(f"Unknown mode. '{kill_mode}'. Available modes are: {MODES}")

    async def chasing(
        self,
        strip: int,
        base_color: "tuple[int, int, int]",
        racing_color: "tuple[int, int, int]",
        mix: int,
        step_delay: float,
        length: int,
        frequency: int,
    ) -> None:
        intermediate_colors: "list[list[int]]" = [[int((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) for rgb_1, rgb_2 in zip(base_color, racing_color)] for fade_step in range(mix + 1)]
        position: int = 0
        while True:
            for led in range(self.led_count[strip]):
                self.leds[self.led_strip[strip]][self.start[strip] + led] = intermediate_colors[int((len(intermediate_colors) - 1) / (abs(sin(frequency * min(abs(position - led) / length, (self.led_count[strip] - abs(position - led)) / length))) + 1))]
            position = position + 1 if position < self.led_count[strip] else 0
            self.leds[self.led_strip[strip]].write()
            await sleep(step_delay)


async def set_mode(controller: NeopixelController) -> None:
    global tasks
    global MODES
    global FUNCTIONS
    global character

    uart = UART(0, 9600, parity=None, stop=1, bits=8, tx=Pin(0), rx=Pin(1), timeout=10)
    select_poll = poll()
    select_poll.register(stdin, POLLIN)
    mode_names = []
    for mode, _ in MODES.items():
        mode_names.append(mode)

    while True:
        if bootsel_button() == 1:
            for led in controller.leds:
                led.fill((0, 0, 0))
                led.write()
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
                    tasks[count] = [character, eval(FUNCTIONS[MODES[character][count]], globals(), {"count": count})]
        await sleep(0.1)


controller = NeopixelController(
    pin_numbers=(2, 3, 4, 5),
    pin_counts=(44, 26, 12, 26),
    leds=(
        (
            {"start": 1, "end": 26},
            {"start": 27, "end": 44},
        ),
        (
            {"start": 1, "end": 26},
        ),
        (
            {"start": 1, "end": 12},
        ),
        (
            {"start": 1, "end": 26},
        ),
    ),
)

tasks = [["", None] for _ in controller.end]

MODES = {
    "A": (
        "",
        "",
        "",
        "",
        "",
    ),
    "D": (
        "Racing",
        "Team Colors",
        "Racing",
        "Team Colors",
        "Team Colors",
    ),
    "E": (
        "Rainbow",
        "Rainbow",
        "Rainbow",
        "Rainbow",
        "Rainbow",
    ),
    "X": (
        "Racing",
        "Team Colors",
        "Racing",
        "Team Colors",
        "Team Colors",
    ),
    "N": (
        "Detected Note",
        "Team Colors",
        "Detected Note",
        "Team Colors",
        "Team Colors",
    ),
    "G": (
        "Possessed Note",
        "Possessed Note",
        "Possessed Note",
        "Possessed Note",
        "Possessed Note",
    ),
}
FUNCTIONS = {
    "Team Colors": const("create_task(controller.color_fade(strip=count, colors=[(0, 0, 200), (200, 0, 200)], mix=128, step_delay=0.01, delay=0.8))"),
    "Rainbow": const("create_task(controller.color_fade(strip=count, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], mix=128, step_delay=0.01, delay=0))"),
    "Detected Note": const("create_task(controller.static_color(strip=count, color=(255, 40, 0), delay=1, kill=False, kill_mode=''))"),
    "Possessed Note": const("create_task(controller.static_color(strip=count, color=(0, 255, 0), delay=2, kill=True, kill_mode='X'))"),
    "Racing": const("create_task(controller.chasing(strip=count, base_color=(0, 0, 200), racing_color=(200, 0, 200), mix=100, step_delay=0.1, length=10, frequency=1))"),
}
character = "D"

try:
    run(set_mode(controller))
except Exception as e:
    print_exception(e)
    sleep(1)
finally:
    for led in controller.leds:
        led.fill((0, 0, 0))
        led.write()
    soft_reset()
