import machine, neopixel
import asyncio

np = [
    neopixel.NeoPixel(machine.Pin(2), 31), #26
    neopixel.NeoPixel(machine.Pin(3), 26),
    neopixel.NeoPixel(machine.Pin(4), 44),
    neopixel.NeoPixel(machine.Pin(5), 26),
    neopixel.NeoPixel(machine.Pin(6), 12)
]

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

async def Rainbow(np, H, S, V, HueStart, HueEnd, interval, delay, direction):
    while True:
        if (H >= HueEnd):
            direction = "back"
        elif (H <= HueStart):
            direction = "forward"
      
        for i in range(len(np)):
            np[i] = HSVtoRGB(H, S, V)
        np.write()
        if (direction == "forward"):
            H += interval
        elif (direction == "backward"):
            H-= interval
        await asyncio.sleep(delay)

async def OverlappingRainbow(np, H = 0, S = 0, V = 0, individualDelay = 0.05, delay = 0.1):
    while True:
      if (H >= 1):
          H = 0
      
      for i in range(len(np)):
          np[i] = HSVtoRGB(H, S, V)
          await asyncio.sleep(individualDelay)
          np.write()
      H += 0.1
      await asyncio.sleep(delay)

async def OverlappingValues(np, colList, individualDelay, direction):
    while True:
        for i in colList:
            for j in range(len(np)):
                if (direction == "up"):
                    np[j] = i
                elif (direction == "down"):
                    np[npNum - j - 1] = i
                await asyncio.sleep(individualDelay)
                np.write()

async def Flashing(np, colList, delay):
    while True:
        for i in colList:
            for j in range(len(np)):
                np[j] = i
                np.write()
            await asyncio.sleep(delay)

async def main():
    await asyncio.gather(
        Rainbow(np[0], 0.6666666648, 1, 0.7843, 0.6666666648, 0.833333331, 0.01, 0.05, "forward")
    )


asyncio.run(main())

