# 2024LEDProject

The LED project for FRC team 1038

## Simulation Website

<https://wokwi.com/projects/new/circuitpython-pi-pico>

## Setting up the project

1. Clone the project
2. Install MicroPico extension from the workspace recommended
3. `CTRL+SHFT+P` and run `MicroPico: Configure project`

## Modes

The program provides 4 modes that are able to be changed through a serial interface.

* Disabled (d) causes an alternating blue and purple color.
* E-Stop (e) causes a cycling rainbow color.
* When the robot sees a node (n), it causes a static orange color.
* When the robot picks up a node (g), it causes a static green color for 2 seconds and after, resets to the default value.
