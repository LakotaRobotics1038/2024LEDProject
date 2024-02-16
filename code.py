import time
import machine, neopixel

time.sleep(0.1)

npNum = 7
np = neopixel.NeoPixel(machine.Pin(0), npNum)

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

def Rainbow(H = 0, S = 0, V = 0, delay = 0.001):
    while True:
        if (H >= 1):
            H = 0
        
        for i in range(npNum):
            np[i] = HSVtoRGB(H, S, V)
        np.write()
        H += 0.001
        time.sleep(delay)

def OverlappingRainbow(H = 0, S = 0, V = 0, individualDelay = 0.05, delay = 0.1):
    while True:
        if (H >= 1):
            H = 0
        
        for i in range(npNum):
            np[i] = HSVtoRGB(H, S, V)
            time.sleep(individualDelay)
            np.write()
        H += 0.1
        time.sleep(delay)

def OverlappingValues(colList = [], individualDelay = 0.05, delay = 0.1, direction = "up"):
    LEDDir = "up"
    while True:
        for i in colList:
            if (direction == "alternating"):
                if (LEDDir == "up"):
                    LEDDir = "down"
                elif (LEDDir == "down"):
                    LEDDir = "up"
            for j in range(npNum):
                if (direction == "up"):
                    np[j] = i
                elif (direction == "down"):
                    np[npNum - j - 1] = i
                elif (direction == "alternating"):
                    if (LEDDir == "up"):
                        np[j] = i
                    elif (LEDDir == "down"):
                        np[npNum - j - 1] = i
                time.sleep(individualDelay)
                np.write()
            time.sleep(delay)

def Flashing(colList = [], delay = 1):
    while True:
        for i in colList:
            for j in range(npNum):
                np[j] = i
                np.write()
            time.sleep(delay)
            for j in range(npNum):
                np[j] = (0, 0, 0)
                np.write()
            time.sleep(delay)
# Rainbow(0, 1, 1, 0.01)
# OverlappingRainbow(0, 1, 1, 0.05, 0.1)
# OverlappingValues([(200, 0, 200), (0, 0, 200), (0, 255, 0)], 0.05, 0.1, "up")
# Flashing([(200, 0, 200), (0, 0, 200), (0, 255, 0)], 0.5)
