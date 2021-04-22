#!/usr/bin/env python

'''
This file generates a user interface for using a touchscreen to generate distributions. 
This file interfaces with ROS over a websocket. Make sure the ip settings below match your config!
If you want to debug this file without using ROS, just flip the "DEUBG_MODE" flag below to True.
'''

# kivy imports
from kivy.config import Config
Config.set('graphics', 'resizable', 'False')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as kvImage 
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Line 
from kivy.uix.textinput import TextInput
from kivy.properties import OptionProperty, ListProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase

# other python imports
import numpy as np # not currently used anywhere uncommented
import cv2 # not currently used anywhere uncommented
# import matplotlib.pyplot as plt # for debugging
import os
import roslibpy # to interface with ros
from scipy.ndimage import gaussian_filter # to smooth data
import sys

# Arg parsing
import argparse
TEAM = 'None'                      # what team are you controlling?
HOST = 'None'                      # are you hosting the testbed server/game?
ADDRESS = 'None'                   # if HOST=no, what ip address will you be connecting to?

#config
DRAWING_MODE = False
DEBUG_MODE = False  # set to true to run without ROS

background_map_name = "ros_game_env.png"
background_map_width = 50
background_map_height = 50

#setup (note: you may want to comment out "fullscreen lines below if using an external monitor")
cwd = os.path.dirname(os.path.realpath(__file__))

## The interface works better on a computer (with external monitors attached) if you comment out the lines below (the screen won't jump around when matplotlib plots are open)
#Window.fullscreen = 'auto'
# Config.set('graphics', 'fullscreen', 'auto') # this might work depending on your system
Window.size = (850, 668)
max_height = Window.height*0.88


class ros_interface(object):
    """ Sets up the ros interface. """
    def __init__(self): 
        # self.client = roslibpy.Ros(host='192.168.1.217',port=9090) # manually change this if you have a different setup (wifi)
        # self.client = roslibpy.Ros(host='192.168.137.2',port=9090) # manually change this if you have a different setup (hardwired)
        # self.client = roslibpy.Ros(host='10.0.1.84',port=9090) # manually change this if you have a different setup (rover)

        if (HOST == 'yes' or not HOST): #(not HOST means if the HOST variable has not been set from the command line)
            self.client = roslibpy.Ros(host='localhost', port=9090)
        elif (HOST == 'no'):
            if (not ADDRESS): #we may not need to enter an ADDRESS if both the red and blue player are on the same network
                sys.exit("Address should not be set to None if you are not host=no (you are not hosting the game, and therefore need to specify an ip address to connect to")
            else:
                self.client = roslibpy.Ros(host=ADDRESS, port=9090)
        else:
            print('HOST value is not valid, did you enter yes/no for HOST?')

        self.publisher = roslibpy.Topic(self.client,'/tablet_comm','ergodic_humanswarmcollab_sim/tablet')
        
        self.client.run()

        # initiate the connection service (will be different for red/blue players)
        if (TEAM == 'red'):
            self.connection_service = roslibpy.Service(self.client, 'red_connection_service', 'Empty')
        elif (TEAM == 'blue'):
            self.connection_service = roslibpy.Service(self.client, 'blue_connection_service', 'Empty')
        else:
            print('TEAM value not valid, did you enter red/blue?')
            sys.exit("TEAM needs to be red/blue")
        self.request = roslibpy.ServiceRequest()

    # call the connection service
    def call_connection_service(self):
        print('Calling service...')
        result = self.connection_service.call(self.request)

    def publish(self,msg):
        if self.client.is_connected:
            print('Publishing data')
            self.publisher.publish(msg)
            
    
    def __del__(self):
        self.client.terminate()
        

# Main GUI interface
class MainLayout ( BoxLayout ) :
        
    # Resize array
    mapProperties = { 'kivy_x_offset':0 , 
                      'kivy_y_offset':0 ,
                      'kivy_map_width':0 ,
                      'kivy_map_height':0 , 
                      'map_width':0 , 
                      'map_height':0 }
    
    
    infoText = StringProperty () 
    
    coordsAttract = ListProperty ( [] ) 
    coordsAttract = [ 'x.y' ] 

    outputX = ListProperty ( [] ) 
    outputX = []
    outputY = ListProperty ( [] ) 
    outputY = []
    
    coordsRepel = ListProperty ( [] ) 
    coordsRepel = [ 'x.y' ] 

    coordsRestricted = ListProperty ( [] ) 
    coordsRestricted = [ 'x.y' ] 
    
    global CURRENT_DRAW 
    CURRENT_DRAW = 'none'
    
    global DRAW_AERIAL 
    DRAW_AERIAL = False 

    DRAW_GROUND = BooleanProperty ( defaultvalue = False ) 
    DRAW_RESTRICTED = BooleanProperty ( defaultvalue = False ) 
    
    draw_weight_attract = 10 #original default=5
    draw_weight_repel = 10   #original default=5

    
    def build ( self ):
        Clock.schedule_once ( lambda *args: self.print_pos() )
        
    def print_pos ( self ) :
        print ( "Position:" + str ( MainLayout.mainScreen.pos ) )
    
    # Initialize and build interface
    def __init__ ( self , **kwargs ) :
        
        super ( MainLayout , self ).__init__ ( **kwargs ) 
        
        # Main-level window settings
        self.orientation = 'vertical'
        self.padding = 10 
        
        # Container for top UI widgets
        self.topLayout = BoxLayout ( orientation = 'horizontal' , padding = 2 ) 
        self.topLayout.size_hint = ( 1.0 , 0.1 ) 
        
        # Top container widgets
        self.btnLoadMap = Button ( text = "Load Map" , font_size = 25 )
        self.topLayout.add_widget ( self.btnLoadMap ) 
        self.btnSaveMap = Button ( text = "Save Map" , font_size = 25 )
        self.topLayout.add_widget ( self.btnSaveMap ) 
        self.btnSaveMap.bind(on_press = self.callbackSave) 
        self.btnROSConfig = Button ( text = "Distribution Overlay" , font_size = 25 )
        self.topLayout.add_widget ( self.btnROSConfig )
        ## Add button for connecting the player
        self.btnConnectService = Button(text = "Connect Player", font_size = 25)
        self.btnConnectService.bind(on_press = self.callbackConnectService)
        self.topLayout.add_widget(self.btnConnectService) 
        
        # Container for middle UI widgets        
        self.middleLayout = BoxLayout ( orientation = 'horizontal' , padding = 5  )# , size = (max_height,max_height), pos = (10,10)) 
        # self.middleLayout.size_hint = ( 1.0 , 0.90 ) 
        
        # Main drawing widget
        self.mainScreen = DrawingWidget () 
        self.middleLayout.add_widget ( self.mainScreen )
        
        # Container for side panel UI widgets
        
        self.middleSideLayout = BoxLayout ( orientation = 'vertical' ) 
        self.middleSideLayout.size_hint_x = ( 0.4 ) 
        self.middleLayout.add_widget ( self.middleSideLayout )
        
        # Side panel widgets
        self.attractButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 )  
        self.middleSideLayout.add_widget ( self.attractButtonContainer  ) 
        self.attracttoggle = ToggleButton ( text = "Draw\nAttract" , font_size = 25  , halign = 'center' , group = 'mode_selection' ) 
        self.attractButtonContainer.add_widget ( self.attracttoggle ) 
        self.attracttoggle.bind ( on_press = self.toggleDrawState ) 
        
        self.attractRow2 = BoxLayout ( orientation = 'horizontal'  , padding = 10 , size_hint_y = 0.75 ) 
        self.attractClear =  Button ( text = "Clear\n Map" , font_size = 25)
        self.attractClear.bind ( on_press = self.callbackClear ) 
        self.attractRow2.add_widget ( self.attractClear ) 
        self.attractDeploy = Button ( text = "Deploy/\n Export", font_size = 25 ) 
        self.attractDeploy.bind ( on_press = self.callbackPublish ) 
        self.attractRow2.add_widget ( self.attractDeploy ) 
        # self.attractButtonContainer.add_widget ( self.attractRow2 ) #MOVED BELOW
        
        self.attractRow3 = BoxLayout ( orientation = 'vertical' ,  padding = 5 , size_hint_y = 0.5 ) 
        self.attractWeight = Slider ( min=1, max=20, value=self.draw_weight_attract )                  #original min,max = 1,10
        self.attractWeight.bind ( on_touch_move = self.callbackSlider_attract ) 
        self.attractRow3.add_widget(self.attractWeight)
        self.attractWeightDisp = Label(text = str(self.attractWeight.value))
        self.attractRow3.add_widget(self.attractWeightDisp)
        self.middleSideLayout.add_widget ( self.attractRow3 ) 

        self.repelButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        self.middleSideLayout.add_widget ( self.repelButtonContainer  ) 
        self.repeltoggle = ToggleButton ( text = "Draw\n Repel" , font_size = 25  , halign = 'center' , group = 'mode_selection' ) 
        self.repelButtonContainer.add_widget ( self.repeltoggle )
        self.repeltoggle.bind ( on_press = self.toggleDrawState ) 
        
        # self.repelRow2 = BoxLayout ( orientation = 'horizontal' , size_hint_y = 0.75 ) 
        # self.repelRow2.add_widget ( Button ( text = "CLEAR"  , color = [0.5,0.,0.]) ) 
        # self.repelRow2.add_widget ( Button ( text = "DEPLOY / EXPORT" , color = [0.5,0.,0.] ) ) 
        # self.repelButtonContainer.add_widget ( self.repelRow2  ) 
        
        self.repelRow3 = BoxLayout ( orientation = 'vertical' ,  padding = 5 , size_hint_y = 0.5 ) 
        self.repelWeight = Slider ( min=1, max=20, value=self.draw_weight_repel )                       #original min,max = 1,10
        self.repelWeight.bind ( on_touch_move = self.callbackSlider_repel ) 
        self.repelRow3.add_widget(self.repelWeight)
        self.repelWeightDisp = Label(text = str(self.repelWeight.value))
        self.repelRow3.add_widget(self.repelWeightDisp)
        self.middleSideLayout.add_widget ( self.repelRow3 ) 


        self.middleSideLayout.add_widget ( self.attractRow2 )  # FROM ABOVE

        # self.restrictedButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        # self.middleSideLayout.add_widget ( self.restrictedButtonContainer  ) 
        # self.restrictedtoggle = ToggleButton ( text = "DRAW RESTRICTED AREA" , font_size = 25  , halign = 'center' , group = 'mode_selection' ) 
        # self.restrictedButtonContainer.add_widget ( self.restrictedtoggle ) 
        # self.restrictedtoggle.bind ( on_press = self.toggleDrawState )
        
        # self.restrictedRow2 = BoxLayout ( orientation = 'horizontal' , size_hint_y = 0.75 ) 
        # self.restrictedRow2.add_widget ( Button ( text = "CLEAR" , color = [0.5,0.,0.]) )
        # self.restrictedRow2.add_widget ( Button ( text = "DEPLOY / EXPORT" , color = [0.5,0.,0.]) ) 
        # self.restrictedButtonContainer.add_widget ( self.restrictedRow2   ) 


        # self.DeployAllButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        
        # self.DeployAllButtonContainer.add_widget ( Button ( text = "DEPLOY ALL UNITS" , font_size = 25 , halign = 'center' , color = [0.5,0.,0.] ) ) 
        # self.middleSideLayout.add_widget ( Label ( text = "" ) ) 
        # self.middleSideLayout.add_widget ( self.DeployAllButtonContainer) 
       
        # self.emergencyButtonContainer = BoxLayout ( orientation = 'horizontal' , padding = 10 , size_hint_y = 0.75 )          
        # self.middleSideLayout.add_widget ( self.emergencyButtonContainer  ) 
        # self.emergencyButtonContainer.add_widget ( Button ( text = "STOP\nALL UNITS" , font_size = 25  , halign = 'center' , color = [0.5,0.,0.] ) ) 
        # self.emergencyButtonContainer.add_widget ( Button ( text = "RECALL\nALL UNITS" , font_size = 25 , halign = 'center', color = [0.5,0.,0.] ) ) 

        self.bottomLayout = BoxLayout ( orientation = 'horizontal' ) 
        self.bottomLayout.size_hint = ( 1.0 , 0.05 ) 
        self.infoPanel = Label ( text = self.infoText ) 
        self.bottomLayout.add_widget ( self.infoPanel )
        
        # Add containers to main GUI interface
        self.add_widget ( self.topLayout ) 
        self.add_widget ( self.middleLayout ) 
        # self.add_widget ( self.bottomLayout ) 
        
        # Build ROS configuration popup
        self.rosBox = BoxLayout ( orientation = 'vertical' ) 
        self.distPlaceholder = kvImage ()
        self.rosBox.add_widget(self.distPlaceholder)
        self.btnCloseRos = Button ( text = "CLOSE" , font_size = 25, size_hint = (0.1, 0.1))
        self.btnCloseRos.bind ( on_press = self.callbackRosConfigClose ) 
        self.rosBox.add_widget ( self.btnCloseRos ) 
        self.rosConfigPopup = Popup ( title = 'Distribution Overlay' , content = self.rosBox , auto_dismiss=False)
        self.rosConfigPopup.size_hint = ( 0.8 , 0.8 ) 
        self.btnROSConfig.bind ( on_press = self.callbackRosConfig ) 
        
        # Build map load popup
        self.mapBox = BoxLayout ( orientation = 'vertical' ) 

        self.mapNameBox = BoxLayout ( orientation = 'horizontal'  )
        
        #self.mapName = TextInput ( text = 'shelby_raw.png', multiline=False )
        self.mapName = TextInput ( text = 'game_env.png', multiline=False )
        
        self.mapNameBox.add_widget(Label( text = 'Map File Name (.png)'))
        self.mapNameBox.add_widget(self.mapName)
        self.mapBox.add_widget ( self.mapNameBox ) 

        self.mapWidthBox = BoxLayout ( orientation = 'horizontal'  )
        
        #self.mapWidth = TextInput ( text = '450' , multiline=False)
        self.mapWidth = TextInput ( text = '50' , multiline=False)
        
        self.mapWidthBox.add_widget( Label( text = 'Map Width (in points)'))
        self.mapWidthBox.add_widget(self.mapWidth)
        self.mapBox.add_widget ( self.mapWidthBox ) 

        self.mapHeightBox = BoxLayout ( orientation = 'horizontal'  )
        
        #self.mapHeight = TextInput ( text = '225' , multiline=False )
        self.mapHeight = TextInput ( text = '50' , multiline=False )
        
        self.mapHeightBox.add_widget(Label( text = 'Map Height (in points)'))
        self.mapHeightBox.add_widget(self.mapHeight)
        self.mapBox.add_widget ( self.mapHeightBox ) 

        self.btnSaveMapName = Button ( text = "OK" , font_size = 25)
        self.btnSaveMapName.bind ( on_press = self.callbackChooseMap ) 
        self.mapBox.add_widget ( self.btnSaveMapName ) 

        self.mapConfigPopup = Popup ( title = "Map Details", content = self.mapBox , auto_dismiss=False)
        self.mapConfigPopup.size_hint = ( 0.4 , 0.3 ) 
        self.btnLoadMap.bind ( on_press = self.callbackMap) 
            
        Clock.schedule_interval(self.updateDisplay, 0.1)
        
        
    #def on_infotext ( self , instance , value ) :
        
    def callbackConnectService(self, event):
        self.mainScreen.attemptPlayerConnect()
    
    def toggleDrawState ( self , event ) :
        global CURRENT_DRAW
        if self.attracttoggle.state == 'down' :
            CURRENT_DRAW = 'attract'
            self.infoPanel.text = "DRAWING AERIAL"
        elif self.repeltoggle.state == 'down' : 
            CURRENT_DRAW = 'repel'
        # elif self.restrictedtoggle.state == 'down' :
        #     CURRENT_DRAW = 'restricted'
        else :
            CURRENT_DRAW = 'none'
    
    # def toggleAttractState ( self , event ) :
    #     global CURRENT_DRAW
    #     if self.attracttoggle.state == 'down' :
    #         CURRENT_DRAW = 'attract'
    #     else:
    #         CURRENT_DRAW = 'none'
        

    # def toggleRepelState ( self , event ) :
    #     global CURRENT_DRAW
    #     if self.repeltoggle.state == 'down' :
    #         CURRENT_DRAW = 'repel'
    #     else:
    #         CURRENT_DRAW = 'none'
    
    def updateDisplay ( self , event ) :
        self.infoPanel.text = self.infoText 
        MainLayout.mapProperties["kivy_x_offset"] = int ( self.mainScreen.x ) 
        MainLayout.mapProperties["kivy_y_offset"] = int ( self.mainScreen.y ) 
        MainLayout.mapProperties["kivy_map_width"] = int ( self.mainScreen.width ) 
        MainLayout.mapProperties["kivy_map_height"] = int ( self.mainScreen.height ) 
        MainLayout.mapProperties["map_width"] = int ( self.mainScreen.width - self.mainScreen.x )
        MainLayout.mapProperties["map_height"] = int ( self.mainScreen.height - self.mainScreen.y )
        if DEBUG_MODE:
            print ( "x: " , MainLayout.mapProperties["kivy_x_offset"]  , ", y: " , MainLayout.mapProperties["kivy_y_offset"]  )
            print ( "kw: " , MainLayout.mapProperties["kivy_map_width"]  , ", kh: " , MainLayout.mapProperties["kivy_map_height"]  )
            print ( "mw: " , MainLayout.mapProperties["map_width"]  , ", mh: " , MainLayout.mapProperties["map_height"]  )
            print(Window.size)
        
                
    # Method to export display as image 
    def callbackSave ( self , event ) :
        self.mainScreen.attemptExportSave() 
        self.infoPanel.text = self.infoText
        print ("Success" ) 
    
    # Method to export display as image 
    def callbackMap ( self , event ) :
        self.mapConfigPopup.open() 
        return True

    def callbackChooseMap ( self , event ) :
        self.mapConfigPopup.dismiss() 
        global background_map_name, background_map_width, background_map_height
        background_map_name = self.mapName.text
        background_map_width = int(self.mapWidth.text)
        background_map_height = int(self.mapHeight.text)
        self.mainScreen.background.source = background_map_name
        self.mainScreen.attemptPublish() # make sure params are correct (rviz/ccast should through an error if not?)
        return True

    def callbackRosConfig ( self, event ) :
        self.distPlaceholder.source = 'dist.png'
        self.distPlaceholder.reload()
        self.rosConfigPopup.open() 
        return True
    
    def callbackRosConfigClose ( self, event ) :
        self.rosConfigPopup.dismiss() 
        return True

    # Callback functions for attract buttons
    def callbackPublish( self , event ) : 
        self.mainScreen.attemptPublish()

    def callbackClear( self , event ) : 
        self.mainScreen.attemptClear()
    
    def callbackSlider_attract( self , event, location ) :
        MainLayout.draw_weight_attract = int(self.attractWeight.value)
        self.attractWeightDisp.text = str(MainLayout.draw_weight_attract)

    def callbackSlider_repel( self , event, location ) :
        MainLayout.draw_weight_repel = int(self.repelWeight.value)
        self.repelWeightDisp.text = str(MainLayout.draw_weight_repel)

# def changeStatusText ( self ) :
#     self.infopanel.text = self.textInput 
#     self.infoPanel.text = self.infoText 
    
    
    

class DrawingWidget ( Widget ) :
    
    
    def __init__ ( self , **kwargs ) :
        
        super ( DrawingWidget , self ).__init__ ()
        if DEBUG_MODE == False: 
            self.ros = ros_interface()

        with self.canvas:
            self.background = Rectangle ( source = background_map_name, size = (max_height,max_height), pos = (10,10) ) #size = self.size, pos = self.pos
        
        # self.bind ( pos = self.updateBackground , size = self.updateBackground )         

        self.objects = []

    def attemptPlayerConnect(self):
        self.ros.call_connection_service()

    def attemptExport ( self ) :
        self.export_to_png( "source.png" )
        
        
    def attemptExportSave ( self ) :
        self.export_to_png( "combined_output.png" )
        # source = cv2.imread ( "source.png" ) 
        # update = cv2.imread ( "overlay_output.png" )
        # diff = cv2.absdiff ( source , update ) 
        # mask = cv2.cvtColor ( diff , cv2.COLOR_BGR2GRAY )
        # thresh = 1 
        # imask = mask > thresh 
        # result = np.zeros_like(update, np.uint8 )
        # result[imask] = update [ imask ]
        
        # cv2.imwrite ( "rgb_output.png" , result)
        
    def attemptPublish ( self ) :
        # remove background to save drawing then redraw
        self.background.source = ""
        self.export_to_png( "drawing.png" )
        self.background.source = background_map_name

        # load figures
        background = cv2.imread( background_map_name , 1) # 1 = color, 0 = grayscale
        draw = cv2.imread("drawing.png",1) # color order BGR
        attract = draw[:,:,0] # blue
        repel = cv2.bitwise_not(draw[:,:,1]) # green, invert image (hvt/ee instead of ied/dd)
        total = cv2.addWeighted(attract,0.5,repel,0.5,0) # sum again

        # resize figures to match
        h,w,_ = background.shape 
        update = cv2.resize(total,(w,h))

        # smooth out
        down_sample = cv2.resize(update,(int(w/5),int(h/5)))
        smooth = gaussian_filter(down_sample,sigma=2)
        up_sample = cv2.resize(smooth,(background_map_width,background_map_height)) # manually updated to match shelby map

        # normalize to send to ros
        val = np.array(up_sample.copy(),dtype = np.float32)
        if np.sum(val) > 0: # error handling for empty page
            val /= np.sum(val)

        # scale back up for cv2 
        target_dist = val.copy()
        target_dist -= np.min(target_dist) # shift min to 0
        if np.max(target_dist) > 0: # error handling for empty map
            target_dist /= np.max(target_dist) # normalize max to 1
        target_dist *= 255 # rescale to 255 (RGB range)
        target_dist = np.array(target_dist,dtype=np.uint8) 

        # colormap
        up_sample_vis = cv2.resize(target_dist,(w,h))
        heatmap = cv2.applyColorMap(up_sample_vis,9) # heatmaps are 0-12

        # overlap and save
        out = cv2.addWeighted(background,0.5,heatmap,0.8,0)
        cv2.imwrite('dist.png',out)

        # save message
        val = np.flipud(val)
        width,height = val.shape
        val = val.ravel()

        #val = val * 1000 #trying to make sure all info values are > 10^4 (does not work otherwise)
        #val = val*100000  #val needs to be this big for the gridmap msg to visually appear in rviz
        val = val*10
        
        msg = dict(
            name = 'attract data',
            team = TEAM,
            data = val.tolist(),
            map_width = width, 
            map_height = height
            )
        if DEBUG_MODE == False:
            self.ros.publish(msg)
        else:
            MainLayout.infoText = str ('NOTE: Not publishing to ros because DEBUG_MODE is enabled') 
            

    def attemptClear ( self ) :
        MainLayout.outputX = []
        MainLayout.outputY = []
        while len(self.objects) > 0: 
            item = self.objects.pop(-1)
            self.canvas.remove(item)
        if DEBUG_MODE: 
            MainLayout.infoText = str ('Screen successfully cleared') 

    def updateBackground ( self , instance , value ) :
        self.background.pos = self.pos
        self.background.size = self.size
        # self.MainLayout.infoPanel.text = "Update Background" 

    def on_touch_down ( self , touch ) :
        

        super ( DrawingWidget , self ).on_touch_down( touch ) 
              

        if self.collide_point ( touch.pos[0] , touch.pos[1] ) :
            
            global DRAWING_MODE 
            DRAWING_MODE = True 
            
            global CURRENT_DRAW 
                
            with self.canvas :
                # print (  ) 
                if CURRENT_DRAW == 'none' :
                    pass
                elif CURRENT_DRAW == 'repel':
                    Color ( 0.0 , 1.0 , 0.0 ) #currently green, maybe change to red?
                    self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = MainLayout.draw_weight_repel )
                    self.objects.append(self.line)
                    MainLayout.infoText = str ( 'Repel: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                elif CURRENT_DRAW == 'attract':
                    Color ( 0.0 , 0.0 , 1.0 )
                    self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = MainLayout.draw_weight_attract )
                    self.objects.append(self.line)
                    MainLayout.infoText = str ( 'Attract: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                # if CURRENT_DRAW == 'restricted':
                #     Color ( 1.0 , 0.0 , 0.0 )
                #     self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = 2 )
                #     self.objects.append(self.line)
                #     MainLayout.infoText = str ( 'Restricted: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                    

                
    def on_touch_move ( self , touch ) :
        global CURRENT_DRAW
        
        if CURRENT_DRAW == 'none' :
            pass
        elif CURRENT_DRAW == 'attract' :
            if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
                self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
                MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                MainLayout.outputX.append( int ( touch.pos[0] - MainLayout.mapProperties["kivy_x_offset"] ) )
                MainLayout.outputY.append( int ( touch.pos[1] - MainLayout.mapProperties["kivy_y_offset"] )  )              
                #  MainLayout.coordsAttract.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )   
        elif CURRENT_DRAW == 'repel' :
            if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
                self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
                MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                MainLayout.coordsRepel.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )
        # elif CURRENT_DRAW == 'restricted' :
        #     if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
        #         self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
        #         MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
        #         MainLayout.coordsRestricted.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )
                
                
    def on_touch_up ( self , touch ) :
        
        file = open ( cwd+'/coord_output.txt' , 'w' ) 
        file.write ( str ( MainLayout.mapProperties["map_width"] ) )  
        file.write ( str ( "\n" ) ) 
        file.write ( str ( MainLayout.mapProperties["map_height"] ) ) 
        file.write ( str ( "\n" ) ) 
        file.write ( str ( MainLayout.outputX ) ) 
        file.write ( str ( "\n" ) ) 
        file.write ( str ( MainLayout.outputY ) ) 
        
        
        file.close()
        
        # print ( MainLayout.coordsAttract ) 

         

        
class Interface ( App ) :
    def build ( self ) :
        
        return MainLayout () 

    def on_stop( self ):
        return True
    
if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('team', help='input the team you are controlling (blue or red)', type=str)
    parser.add_argument('-host', help='Needed for 2-player games: are you hosting the game? (yes/no)', type=str)
    parser.add_argument('-address', help='Needed for 2-player games:  if you are not hosting the game, enter the ip address of the host', type=str)
    args = parser.parse_args()
    
    TEAM = args.team
    print('Your team is: {}'.format(TEAM))

    HOST = args.host

    ADDRESS = args.address

    print('Inputted arguments: {}'.format(vars(args)))
    
    try: 
        Interface().run()
    except KeyboardInterrupt: 
        pass
