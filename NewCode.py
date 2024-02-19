import time
import machine, neopixel

time.sleep(0.1)

npNum = {
    "npNum0" : 26,
    "npNum1" : 26,
    "npNum2" : 44,
    "npNum3" : 26,
    "npNum4" : 12
}

np = {
    "np0" : neopixel.NeoPixel(machine.Pin(0), npNum["npNum0"]),
    "np1" : neopixel.NeoPixel(machine.Pin(1), npNum["npNum1"]),
    "np2" : neopixel.NeoPixel(machine.Pin(2), npNum["npNum2"]),
    "np3" : neopixel.NeoPixel(machine.Pin(3), npNum["npNum3"]),
    "np4" : neopixel.NeoPixel(machine.Pin(4), npNum["npNum4"])
}

npMode = [
    "Rainbow",
    "Rainbow",
    "Rainbow",
    "Rainbow",
    "Rainbow"
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


RainbowH = 0
RainbowS = 1
RainbowV = 1
while True:
    for i in range(0, len(np)):
        if (npMode[i] == "Rainbow"):
            if (RainbowH >= 1):
                RainbowH = 0
            for j in range(0, npNum["npNum"+str(i)]):
                np["np"+str(i)][j] = HSVtoRGB(RainbowH, RainbowS, RainbowV)
            np["np"+str(i)].write()
            RainbowH += 0.01
            time.sleep(0.01)
        elif (npMode[i] == "AlternatingRainbow"):
            pass
