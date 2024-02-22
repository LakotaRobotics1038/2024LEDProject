import machine, neopixel
import asyncio

np0Num = 26
np0 = neopixel.NeoPixel(machine.Pin(0), np0Num)
np1Num = 26
np1 = neopixel.NeoPixel(machine.Pin(1), np1Num)
np2Num = 44
np2 = neopixel.NeoPixel(machine.Pin(2), np2Num)
np3Num = 26
np3 = neopixel.NeoPixel(machine.Pin(3), np3Num)
np4Num = 12
np4 = neopixel.NeoPixel(machine.Pin(4), np4Num)

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

async def Rainbow(np, npNum, H, S, V, interval, delay):
    while True:
      if (H >= 1):
          H = 0
      
      for i in range(npNum):
          np[i] = HSVtoRGB(H, S, V)
      np.write()
      H += interval
      await asyncio.sleep(delay)

async def OverlappingRainbow(np, npNum, H = 0, S = 0, V = 0, individualDelay = 0.05, delay = 0.1):
    while True:
      if (H >= 1):
          H = 0
      
      for i in range(npNum):
          np[i] = HSVtoRGB(H, S, V)
          await asyncio.sleep(individualDelay)
          np.write()
      H += 0.1
      await asyncio.sleep(delay)

async def OverlappingValues(np, npNum, colList = [], individualDelay = 0.05, delay = 0.1, direction = "up"):
    while True:
      for i in colList:
          for j in range(npNum):
              if (direction == "up"):
                  np[j] = i
              elif (direction == "down"):
                  np[npNum - j - 1] = i
              await asyncio.sleep(individualDelay)
              np.write()
          await asyncio.sleep(delay)

async def Flashing(np, npNum, colList = [], delay = 1):
    while True:
        for i in colList:
            for j in range(npNum):
                np[j] = i
                np.write()
            await asyncio.sleep(delay)
            for j in range(npNum):
                np[j] = (0, 0, 0)
                np.write()
            await asyncio.sleep(delay)
async def main():
  await asyncio.gather(
    Rainbow(np0, np0Num, 0, 1, 1, 0.05, 0.25),
    Rainbow(np1, np1Num, 0, 1, 1, 0.05, 0.25),
    OverlappingRainbow(np2, np2Num, 0, 1, 1, 0.05, 0.1),
    OverlappingValues(np3, np3Num, [(200, 0, 200), (0, 0, 200), (0, 255, 0)], 0.05, 0.1, "up"),
    Flashing(np4, np4Num, [(200, 0, 200), (0, 0, 200), (0, 255, 0)], 0.5)
  )


asyncio.run(main())
