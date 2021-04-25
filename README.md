# Touch Screen Interface Setup
## Installation

Install Kivy:
Add the Kivy repo: sudo add-apt-repository ppa:kivy-team/kivy
Install Kivy: sudo apt-get install python3-kivy

Install OpenCV:
pip install opencv-python

## Networking Setup
Both players must be on the same local network. The hosting player may have to add a ufw rule to allow incoming connections from the ip address of the non-hosting player.

For example, if you are the host and the ip address of the other player is 192.168.1.1, add the ufw rule as follows:
`sudo ufw allow from 192.168.1.1`

To delete the ufw rule when you are done using the testbed, run:
`sudo delete allow from 192.168.1.1`

If you are using a physical touch screen interface, you may have to add a ufw rule for the ip address of the physical interface. You may also use an ethernet connection.

## Running the Touch Screen Interface

Run from the command-line:
`python3 ergodic_interface_v12 <team> -host <yes/no> -address <ip_address>` where:
- team argument should be `red` or `blue` depending upon which team you would like to control
- host argument should be `yes` or `no` depending upon if you are the player that is hosting the virtual testbed 
- if you are not the host (host=no), the address argument denotes the ip address of the hosting player on the local network both players are on 

Once the touch screen interface has launched:
- Click/touch "Draw Attract" to draw attraction regions for your team
- Click/touch "Draw Repel" to draw repulsion regions for your team
- Click/touch "Save Map" (along the top) to save png to current directory
- Click/touch "Deploy / Export" to send messages containing the drawing to your team via ROS
- Click/touch "Clear Map" to erase the current drawing and return to a blank canvas (note this currently clears both attract and repel regions)
- Click/touch "ROS Configuration" to view target distribution being explored by agents
- Click/touch "Connect Player" to confirm that you can see both teams of agents in Rviz and that you are ready to play
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