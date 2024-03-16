<h1 align="center">2024LEDProject</h1>
<h3 align="center">The LED project for FRC team 1038.</h3>
<br />
<br />
<h4>Modes:</h4>
<p>The program provides 4 modes that are able to be changed through a serial interface. Disabled (d) causes an alternating blue and purple color. E-Stop (e) causes a cycling rainbow color. When the robot sees a node (n), it causes a static orange color. When the robot picks up a node (g), it causes a static green color for 2 seconds and after, resets to the default value.</p>
<br />
<h4>It is possable to simulate micropython on the pico using <a href="https://wokwi.com/projects/new/micropython-pi-pico">this link</a>.</h4>
<br />
<h4>Additional Notes:</h4>
<p>If you are having connectivity issues with the pico, it may be to the main.py file running while attempting to make changes to the code. To erase the file, hold down the bootcel while plugging in the pico and drag the file flash_nuke.uf2 into the drive. The pico should completely reset.</p>
