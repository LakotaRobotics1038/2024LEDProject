from uasyncio import sleep, run, create_task
from asyncio import Task
from umachine import Pin, UART, soft_reset
from neopixel import NeoPixel
from usys import stdin, print_exception
from uselect import poll, POLLIN
from rp2 import bootsel_button
from math import sin

class NeopixelController:
    def __init__(
        self,
        pin_numbers: "tuple[int, ...]",
        pin_counts: "tuple[int, ...]",
        leds: "tuple[tuple[dict[str, int], ...], ...]",
        modes: "dict[str, tuple[str, ...]]",
        character: str,
        brightness: float,
    ) -> None:
        if len(pin_numbers) != len(pin_counts):
            raise ValueError(f"Pin Numbers and Pin Counts must be the same length. Current lengths are {len(pin_numbers)} pin numbers and {len(pin_counts)} leds.")
        self.leds: list[NeoPixel] = [NeoPixel(Pin(pin), count) for pin, count in zip(pin_numbers, pin_counts)]
        self.start: list[int] = []
        self.end: list[int] = []
        self.led_strip: list[int] = []
        self.led_count: list[int] = []
        for count, strip in enumerate(leds):
            for portion in strip:
                self.led_strip.append(count)
                self.start.append(portion["start"] - 1)
                self.end.append(portion["end"])
                self.led_count.append(portion["end"] - portion["start"] - 1)
        self.tasks: "list[tuple[str, None | Task[None]]]" = [("", None) for _ in self.end]
        self.modes: "dict[str, tuple[str, ...]]" = modes
        self.character: str = character
        self.brightness: float = brightness

    def get_function(self, count: int, pattern: str) -> Task[None]:
        if pattern == "Team Colors":
            return create_task(self.color_fade(strip=count, colors=[(0, 0, 200), (200, 0, 200)], mix=128, step_delay=0.01, delay=0.8))
        elif pattern == "Rainbow":
            return create_task(self.color_fade(strip=count, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], mix=128, step_delay=0.01, delay=0))
        elif pattern == "Detected Note":
            return create_task(self.static_color(strip=count, color=(255, 40, 0), delay=1, kill=False, kill_mode=""))
        elif pattern == "Possessed Note":
            return create_task(self.static_color(strip=count, color=(0, 255, 0), delay=2, kill=True, kill_mode="X"))
        elif pattern == "Chasing":
            return create_task(self.chasing(strip=count, base_color=(0, 0, 200), chasing_color=(200, 0, 200), mix=100, step_delay=0.1, length=10, frequency=1))
        else:
            raise ValueError("Pattern not recognized")

    def choose_pattern(self) -> None:
        for count, task in enumerate(self.tasks):
            if self.character in self.modes:
                if task[0] != self.character and self.modes[self.character][count] != "":
                    if task[1] is not None:
                        try:
                            task[1].cancel()
                        except:
                            pass
                    self.tasks[count] = (self.character, self.get_function(count, self.modes[self.character][count]))

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
                    intermediate_color = tuple(int(((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) * self.brightness) for rgb_1, rgb_2 in zip(colors[count], colors[(count + 1) % len(colors)]))
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
        for led in range(self.led_count[strip]):
            self.leds[self.led_strip[strip]][self.start[strip] + led] = tuple([int(value * self.brightness) for value in color])
        self.leds[self.led_strip[strip]].write()
        await sleep(delay)
        if kill:
            if kill_mode in self.modes:
                self.character = kill_mode
                self.choose_pattern()
            else:
                raise ValueError(f"Unknown mode. '{kill_mode}'. Available modes are: {self.modes}")

    async def chasing(
        self,
        strip: int,
        base_color: "tuple[int, int, int]",
        chasing_color: "tuple[int, int, int]",
        mix: int,
        step_delay: float,
        length: int,
        frequency: int,
    ) -> None:
        intermediate_colors: "list[list[int]]" = [[int(((1 - fade_step / mix) * rgb_1 + fade_step / mix * rgb_2) * self.brightness) for rgb_1, rgb_2 in zip(base_color, chasing_color)] for fade_step in range(mix + 1)]
        position: int = 0
        while True:
            for led in range(self.led_count[strip]):
                self.leds[self.led_strip[strip]][self.start[strip] + led] = intermediate_colors[int((len(intermediate_colors) - 1) / (abs(sin(frequency * min(abs(position - led) / length, (self.led_count[strip] - abs(position - led)) / length))) + 1))]
            position = position + 1 if position < self.led_count[strip] else 0
            self.leds[self.led_strip[strip]].write()
            await sleep(step_delay)


async def set_mode(controller: NeopixelController) -> None:
    uart = UART(0, 9600, parity=None, stop=1, bits=8, tx=Pin(0), rx=Pin(1), timeout=10)
    select_poll: poll = poll()
    select_poll.register(stdin, POLLIN)
    mode_names: "list[str]" = [mode for mode, _ in controller.modes.items()]

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
                    controller.character = received_input
                else:
                    print("Unknown Character")

        if select_poll.poll(0):
            received_input = stdin.read(1)
            if received_input != "\n":
                if received_input in mode_names:
                    controller.character = received_input
                else:
                    print("Unknown Character")

        controller.choose_pattern()
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
    modes={
        "A": (
            "",
            "",
            "",
            "",
            "",
        ),
        "D": (
            "Chasing",
            "Team Colors",
            "Chasing",
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
            "Chasing",
            "Team Colors",
            "Chasing",
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
    },
    character="D",
    brightness=1,
)

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
