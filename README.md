# SwarmInterface

Install Kivy:
Add the Kivy repo: sudo add-apt-repository ppa:kivy-team/kivy
Install Kivy: sudo apt-get install python3-kivy


Install OpenCV:
pip install opencv-python


To run:
python3 ergodic_interface_v12


Use:
- Click/Touch "Draw Aerial AOI" 
  (note: only Aerial AOI is outputting data in this version)
- Draw on the screen
- Click/touch "Save Map" (along the top)


Outputs:
- coord_output.txt: text file that outputs the dimensions of the map image 
  and the x-y coordinates of drawn inputs in Aerial AOI in real time 
  (appending as new inputs are added)
- combined_output.png: image file that combines the drawn AOIs onto the original map

