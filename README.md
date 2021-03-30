# SwarmInterface

Install Kivy:
Add the Kivy repo: sudo add-apt-repository ppa:kivy-team/kivy
Install Kivy: sudo apt-get install python3-kivy

Install OpenCV:
pip install opencv-python


To run:
`python3 ergodic_interface_v12 <team>` where <team> is `red` or `blue` depending upon which team you would like to control 

Use:
- Click/Touch "Draw Aerial AOI" 
  (note: only Aerial AOI is outputting data in this version)
- Draw on the screen
- Click/touch "Save Map" (along the top) to save png to current directory
- Click/touch "Deploy / Export" under "Draw Aerial AOI" to send messages via ROS
- Click/touch "Clear" under "Draw Aerial AOI" to clear map (note this currently clears all types)
- Click/touch "ROS Configuration" to view target distribution being explored by agents
- Adjust slider to change drawing line width 
- Press "Esc" on your keyboard to exit the program

Outputs:
- coord_output.txt: text file that outputs the dimensions of the map image 
  and the x-y coordinates of drawn inputs in Aerial AOI in real time 
  (appending as new inputs are added)
- combined_output.png: image file that combines the drawn AOIs onto the original map


Notes: 
- changed color of all un-implemented buttons to be red (easier for me to remember)
- commented out numpy and cv2 as they aren't currently used
- added import roslibpy to send array to the ergodic controller stuff 
  - on the ergodic controller side, I added a script to subscribe to the outputs, smooth out the outputs, and send the processed results to the ergodic planner. The coupling between the tablet and the space is a little finicky, so we'll have to make sure we manually set the same inputs for the controller that match the size of the tablet screen. No biggie but something to be aware of 
  - I also wrote a custom message to take the outputs you were saving to the text file. This is actually part of the ergodic controller package, but I've uploaded a copy to this repository for reference
  - the ip address is manually input, so if the network isn't set up for that ip address you'll have to change that (I also put a DEBUG_MODE in to allow you to comment out the ROS stuff while you mess with the gui itself)
  - the tablet interface stuff is on the "tablet" branch https://github.com/atulletaylor/HumanSwarmCollab/tree/tablet

## Copyright and License
The implementations of SwarmInterface contained herein are copyright (C) 2021 - 2022 by Joel Meyer, Allison Pinosky, and Thomas Trzpit and are distributed under the terms of the GNU General Public License (GPL) version 3 (or later). Please see the LICENSE for more information.

Contact: joelmeyer@u.northwestern.edu

Lab Info: Todd D. Murphey https://murpheylab.github.io/ Northwestern University