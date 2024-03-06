import machine
import neopixel
import asyncio
import select
import sys

poll_obj = select.poll()
poll_obj.register(sys.stdin, 1)

np = [
    neopixel.NeoPixel(machine.Pin(2), 26),
    neopixel.NeoPixel(machine.Pin(3), 26),
    neopixel.NeoPixel(machine.Pin(4), 44),
    neopixel.NeoPixel(machine.Pin(5), 26),
    neopixel.NeoPixel(machine.Pin(6), 12)
]
def Clear():
    for i in range(len(np)):
        for j in range(len(np[i])):
            np[i][j] = (0, 0, 0)
        np[i].write()

def HSVtoRGB(H, S, V):
    if (S == 0):
        R = V * 255
        G = V * 255
        B = V * 255
    else:
        var_h = H * 6
        if (var_h == 6):
            var_h = 0
        var_i = int(var_h)
        var_1 = V * (1 - S )
        var_2 = V * (1 - S * (var_h - var_i))
        var_3 = V * (1 - S * (1 - (var_h - var_i)))

        if (var_i == 0):
            var_r = V
            var_g = var_3
            var_b = var_1
        elif (var_i == 1):
            var_r = var_2
            var_g = V
            var_b = var_1
        elif (var_i == 2):
            var_r = var_1
            var_g = V
            var_b = var_3
        elif (var_i == 3):
            var_r = var_1
            var_g = var_2
            var_b = V
        elif ( var_i == 4 ):
            var_r = var_3
            var_g = var_1
            var_b = V
        else:
            var_r = V
            var_g = var_1
            var_b = var_2

        R = var_r * 255
        G = var_g * 255
        B = var_b * 255

        return (int(R), int(G), int(B))

async def Fade(np, h, s, v, currentH, interval, delay, direction, directionSwitchDelay):
    while True:
        if (currentH >= h["end"]):
            direction = "backward"
            await asyncio.sleep(directionSwitchDelay)
        elif (currentH <= h["start"]):
            direction = "forward"
            await asyncio.sleep(directionSwitchDelay)
      
        for i in range(len(np)):
            np[i] = HSVtoRGB(currentH, s, v)
        np.write()
        if (direction == "forward"):
            currentH += interval
        elif (direction == "backward"):
            currentH -= interval
        await asyncio.sleep(delay)

async def OverlappingValues(np, colList, individualDelay, direction):
    while True:
        for i in colList:
            for j in range(len(np)):
                if (direction == "up"):
                    np[j] = i
                elif (direction == "down"):
                    np[len(np) - j - 1] = i
                await asyncio.sleep(individualDelay)
                np.write()

async def Flashing(np, colList, delay):
    while True:
        for i in colList:
            for j in range(len(np)):
                np[j] = i
                np.write()
            await asyncio.sleep(delay)

async def Main(mode):
    Clear()
    if (mode == 't'):
        await asyncio.gather(
            Fade(np[0], {"start":0.6666666648, "end":0.833333331}, 0.6666666648, 1, 0.7843, 0.001, 0.005, "forward", 1),
            Fade(np[1], {"start":0.6666666648, "end":0.833333331}, 0.6666666648, 1, 0.7843, 0.001, 0.005, "forward", 1),
            Fade(np[2], {"start":0.6666666648, "end":0.833333331}, 0.6666666648, 1, 0.7843, 0.001, 0.005, "forward", 1),
            Fade(np[3], {"start":0.6666666648, "end":0.833333331}, 0.6666666648, 1, 0.7843, 0.001, 0.005, "forward", 1),
            Fade(np[4], {"start":0.6666666648, "end":0.833333331}, 0.6666666648, 1, 0.7843, 0.001, 0.005, "forward", 1)
        )
Clear()
while True:
    if poll_obj.poll(0):
        char = sys.stdin.read(1)
        asyncio.run(Main(char))
