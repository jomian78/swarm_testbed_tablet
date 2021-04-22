# SwarmInterface

Install Kivy:
Add the Kivy repo: sudo add-apt-repository ppa:kivy-team/kivy
Install Kivy: sudo apt-get install python3-kivy

Install OpenCV:
pip install opencv-python


To run:
`python3 ergodic_interface_v12 <team> <host> <address>` where:
- team should be `red` or `blue` depending upon which team you would like to control
- host should be `yes` or `no` depending upon if you are hosting the virtual testbed
- address is an optional argument (only needed if you are not hosting the game, and need to connect remotely) denoting the ip address you are remotely connecting to 

Use:
- Click/touch "Draw Attract" to draw attraction regions for your team
- Click/touch "Draw Repel" to draw repulsion regions for your team
- Click/touch "Save Map" (along the top) to save png to current directory
- Click/touch "Deploy / Export" to send messages containing the drawing to your team via ROS
- Click/touch "Clear Map" to erase the current drawing and return to a blank canvas (note this currently clears both attract and repel regions)
- Click/touch "ROS Configuration" to view target distribution being explored by agents
- Adjust the sliders under "Draw Attract" and "Draw Repel" to change the line width of your drawing tool 
- Press "Esc" on your keyboard to exit the program

Outputs:
- coord_output.txt: text file that outputs the dimensions of the map image 
  and the x-y coordinates of drawn inputs in real time 
  (appending as new inputs are added)
- combined_output.png: image file that combines the drawn attraction and repulsion regions onto the original map


## Copyright and License
The implementations of SwarmInterface contained herein are copyright (C) 2021 - 2022 by Joel Meyer and Allison Pinosky and are distributed under the terms of the GNU General Public License (GPL) version 3 (or later). Please see the LICENSE for more information.

Contact: joelmeyer@u.northwestern.edu

Lab Info: Todd D. Murphey https://murpheylab.github.io/ Northwestern University