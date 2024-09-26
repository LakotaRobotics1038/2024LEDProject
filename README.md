# 2024LEDProject

The LED project for FRC team 1038

## Simulation Website

<https://wokwi.com/projects/new/circuitpython-pi-pico>

## Setting up the project

1. Clone the project
2. Install MicroPico extension from the workspace recommended
3. `CTRL+SHFT+P` and run `MicroPico: Configure project`

## Troubleshooting

- If this is not the first time that program has been flashed, empty the flash memory [here](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory/) and re-flash the program.
- If the animation does not start, disconnect the Pico from all sources of power and plug it back in. This includes the USB port and GPIO pins.

## Modes

The program provides 4 modes that are able to be changed through a serial interface.

* Disabled (`D`) causes an alternating blue and purple color.
* E-Stop (`E`) causes a cycling rainbow color.
* When the robot sees a node (`N`), it causes a static orange color.
* When the robot picks up a node (`G`), it causes a static green color for 2 seconds and after, resets to the default value.
