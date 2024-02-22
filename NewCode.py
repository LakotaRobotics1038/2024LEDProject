import time
import machine, neopixel

time.sleep(0.1)

npNum = [
    26,
    26,
    44,
    26,
    12
]

np = [
    neopixel.NeoPixel(machine.Pin(0), npNum[0]),
    neopixel.NeoPixel(machine.Pin(1), npNum[1]),
    neopixel.NeoPixel(machine.Pin(2), npNum[2]),
    neopixel.NeoPixel(machine.Pin(3), npNum[3]),
    neopixel.NeoPixel(machine.Pin(4), npNum[4])
]

npMode = [
    ["AlternatingRainbow", 0, 1, 1],
    ["AlternatingRainbow", 0, 1, 1],
    ["AlternatingRainbow", 0, 1, 1],
    ["AlternatingRainbow", 0, 1, 1],
    ["Rainbow", 0, 1, 1]
]

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

while True:
    for i in range(0, len(np)):
        if (npMode[i][0] == "Rainbow"):
            if (npMode[i][1] >= 1):
                npMode[i][1] = 0
            for j in range(0, npNum[i]):
                np[i][j] = HSVtoRGB(npMode[i][1], npMode[i][2], npMode[i][3])
            np[i].write()
            npMode[i][1] += 0.001
            time.sleep(0.001)
        elif (npMode[i][0] == "AlternatingRainbow"):
            if (npMode[i][1] >= 1):
                npMode[i][1] = 0
            for j in range(0, npNum[i]):
                np[i][j] = HSVtoRGB(npMode[i][1], npMode[i][2], npMode[i][3])
                time.sleep(0.025)
                np[i].write()
            npMode[i][1] += 0.1
            time.sleep(0.1)
