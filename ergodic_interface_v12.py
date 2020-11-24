
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color , Rectangle , Line
from kivy.uix.label import Label
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.properties import OptionProperty 
from kivy.properties import ListProperty
from kivy.properties import StringProperty 
from kivy.properties import BooleanProperty

from kivy.properties import ObjectProperty
from kivy.uix.image import Image as kvImage 
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup

from kivy.clock import Clock
import numpy as np

import os
cwd = os.path.dirname(os.path.realpath(__file__))

import cv2

DRAWING_MODE = False

Config.set('graphics', 'fullscreen', 'auto')


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
    
    coordsAerial = ListProperty ( [] ) 
    coordsAerial = [ 'x.y' ] 

    outputX = ListProperty ( [] ) 
    outputX = []
    outputY = ListProperty ( [] ) 
    outputY = []
    
    coordsGround = ListProperty ( [] ) 
    coordsGround = [ 'x.y' ] 

    coordsRestricted = ListProperty ( [] ) 
    coordsRestricted = [ 'x.y' ] 
    
    global CURRENT_DRAW 
    CURRENT_DRAW = 'none'
    
    global DRAW_AERIAL 
    DRAW_AERIAL = False 

    DRAW_GROUND = BooleanProperty ( defaultvalue = False ) 
    DRAW_RESTRICTED = BooleanProperty ( defaultvalue = False ) 
    
    
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
        self.topLayout.size_hint = ( 1.0 , 0.05 ) 
        
        # Top container widgets
        self.btnLoadMap = Button ( text = "Load Map" , font_size = 20 )
        self.topLayout.add_widget ( self.btnLoadMap ) 
        self.btnLoadMap.bind ( on_press = self.callback ) 
        self.btnSaveMap = Button ( text = "Save Map" , font_size = 20 )
        self.topLayout.add_widget ( self.btnSaveMap ) 
        self.btnSaveMap.bind ( on_press = self.callbackSave ) 
        self.btnROSConfig = Button ( text = "ROS Configuration" , font_size = 20 )
        self.topLayout.add_widget ( self.btnROSConfig ) 
       
        
        
        # Container for middle UI widgets        
        self.middleLayout = BoxLayout ( orientation = 'horizontal' , padding = 5 ) 
        self.middleLayout.size_hint = ( 1.0 , 0.90 ) 
        
        # Main drawing widget
        self.mainScreen = DrawingWidget () 
        self.middleLayout.add_widget ( self.mainScreen )
        
        # Container for side panel UI widgets
        self.middleSideLayout = BoxLayout ( orientation = 'vertical' ) 
        self.middleSideLayout.size_hint_x = ( 0.3 ) 
        self.middleLayout.add_widget ( self.middleSideLayout )
        
        # Side panel widgets
        self.aerialButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 )  
        self.middleSideLayout.add_widget ( self.aerialButtonContainer  ) 
        self.aerialtoggle = ToggleButton ( text = "DRAW AERIAL AOI" , font_size = 20  , halign = 'center' , group = 'mode_selection' ) 
        self.aerialButtonContainer .add_widget ( self.aerialtoggle ) 
        self.aerialtoggle.bind ( on_press = self.toggleDrawState ) 
        
        self.aerialRow2 = BoxLayout ( orientation = 'horizontal' , size_hint_y = 0.75 ) 
        self.aerialRow2.add_widget ( Button ( text = "CLEAR" ) ) 
        self.aerialRow2.add_widget ( Button ( text = "DEPLOY / EXPORT" ) ) 
        self.aerialButtonContainer .add_widget ( self.aerialRow2 ) 
        
        self.groundButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        self.middleSideLayout.add_widget ( self.groundButtonContainer  ) 
        self.groundtoggle = ToggleButton ( text = "DRAW GROUND AOI" , font_size = 20  , halign = 'center' , group = 'mode_selection'  ) 
        self.groundButtonContainer.add_widget ( self.groundtoggle )
        self.groundtoggle.bind ( on_press = self.toggleDrawState ) 
        
        self.groundRow2 = BoxLayout ( orientation = 'horizontal' , size_hint_y = 0.75 ) 
        self.groundRow2 .add_widget ( Button ( text = "CLEAR" ) ) 
        self.groundRow2 .add_widget ( Button ( text = "DEPLOY / EXPORT" ) ) 
        self.groundButtonContainer .add_widget ( self.groundRow2  ) 
        
        self.restrictedButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        self.middleSideLayout.add_widget ( self.restrictedButtonContainer  ) 
        self.restrictedtoggle = ToggleButton ( text = "DRAW RESTRICTED AREA" , font_size = 20  , halign = 'center' , group = 'mode_selection' ) 
        self.restrictedButtonContainer .add_widget ( self.restrictedtoggle ) 
        self.restrictedtoggle.bind ( on_press = self.toggleDrawState )
        
        self.restrictedRow2 = BoxLayout ( orientation = 'horizontal' , size_hint_y = 0.75 ) 
        self.restrictedRow2  .add_widget ( Button ( text = "CLEAR" ) )
        self.restrictedRow2  .add_widget ( Button ( text = "DEPLOY / EXPORT" ) ) 
        self.restrictedButtonContainer.add_widget ( self.restrictedRow2   ) 
       
        self.DeployAllButtonContainer = BoxLayout ( orientation = 'vertical' , padding = 10 ) 
        
        self.DeployAllButtonContainer .add_widget ( Button ( text = "DEPLOY ALL UNITS" , font_size = 20 , halign = 'center' ) ) 
        self.middleSideLayout.add_widget ( Label ( text = "" ) ) 
        self.middleSideLayout.add_widget ( self.DeployAllButtonContainer) 
       
        
        self.emergencyButtonContainer = BoxLayout ( orientation = 'horizontal' , padding = 10 , size_hint_y = 0.75 )  
        self.middleSideLayout.add_widget ( self.emergencyButtonContainer  ) 
        self.emergencyButtonContainer.add_widget ( Button ( text = "STOP\nALL UNITS" , font_size = 20  , halign = 'center' ) ) 
        self.emergencyButtonContainer.add_widget ( Button ( text = "RECALL\nALL UNITS" , font_size = 20 , halign = 'center' ) ) 

        self.bottomLayout = BoxLayout ( orientation = 'horizontal' ) 
        self.bottomLayout.size_hint = ( 1.0 , 0.05 ) 
        self.infoPanel = Label ( text = self.infoText ) 
        self.bottomLayout.add_widget ( self.infoPanel )
        
        # Add containers to main GUI interface
        self.add_widget ( self.topLayout ) 
        self.add_widget ( self.middleLayout ) 
        self.add_widget ( self.bottomLayout ) 
        
        # Build ROS configuration popup
        self.rosConfigPopup = Popup ( title = 'ROS Configuration' , content = Label ( text = 'Placeholder for ROS' ) )
        self.rosConfigPopup.size_hint = ( 0.5 , 0.5 ) 
        #self.rosConfigPopup.bind ( on_dismiss = self.callbackRosConfig )
        #self.rosConfigPopup.open() 
        self.btnROSConfig.bind ( on_press = self.callbackRosConfig ) 
        
        
        
        Clock.schedule_interval(self.updateDisplay, 0.1)
        
        
    #def on_infotext ( self , instance , value ) :
        
    
    
    def toggleDrawState ( self , event ) :
        global CURRENT_DRAW
        if self.aerialtoggle.state == 'down' :
            CURRENT_DRAW = 'aerial'
            self.infoPanel.text = "DRAWING AERIAL"
        elif self.groundtoggle.state == 'down' : 
            CURRENT_DRAW = 'ground'
        elif self.restrictedtoggle.state == 'down' :
            CURRENT_DRAW = 'restricted'
        else :
            CURRENT_DRAW = 'none'
    
    # def toggleAerialState ( self , event ) :
    #     global CURRENT_DRAW
    #     if self.aerialtoggle.state == 'down' :
    #         CURRENT_DRAW = 'aerial'
    #     else:
    #         CURRENT_DRAW = 'none'
        

    # def toggleGroundState ( self , event ) :
    #     global CURRENT_DRAW
    #     if self.groundtoggle.state == 'down' :
    #         CURRENT_DRAW = 'ground'
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
        print ( "x: " , MainLayout.mapProperties["kivy_x_offset"]  , ", y: " , MainLayout.mapProperties["kivy_y_offset"]  )
        print ( "kw: " , MainLayout.mapProperties["kivy_map_width"]  , ", kh: " , MainLayout.mapProperties["kivy_map_height"]  )
        print ( "mw: " , MainLayout.mapProperties["map_width"]  , ", mh: " , MainLayout.mapProperties["map_height"]  )
        
        

        
    # Method to export display as image 
    def callbackSave ( self , event ) :
        self.mainScreen.attemptExportSave() 
        self.infoPanel.text = self.infoText
        print ("Success" ) 
    
    # Method to export display as image 
    def callback ( self , event ) :
        self.infoPanel.text = "Click!" 
        
    def callbackRosConfig ( self, event ) :
        self.rosConfigPopup.open() 
        print('Popup', self , 'is being dismissed but is prevented!')
        return True
    
# def changeStatusText ( self ) :
#     self.infopanel.text = self.textInput 


#     self.infoPanel.text = self.infoText 
    
    
    

class DrawingWidget ( Widget ) :
    
    
    def __init__ ( self , **kwargs ) :
        
        super ( DrawingWidget , self ).__init__ ()
        

        
        with self.canvas:
            self.background = Rectangle ( source = 'raw.png' , size = self.size, pos = self.pos ) 
        
        self.bind ( pos = self.updateBackground , size = self.updateBackground ) 
        
        

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
                print (  ) 
                if CURRENT_DRAW == 'none' :
                    pass
                elif CURRENT_DRAW == 'ground':
                    Color ( 0.0 , 1.0 , 0.0 )
                    self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = 4 )
                    MainLayout.infoText = str ( 'Ground: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                elif CURRENT_DRAW == 'aerial':
                    Color ( 0.0 , 0.0 , 1.0 )
                    self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = 4 )
                    MainLayout.infoText = str ( 'Aerial: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                if CURRENT_DRAW == 'restricted':
                    Color ( 1.0 , 0.0 , 0.0 )
                    self.line = Line ( points = [ touch.pos [0] , touch.pos [ 1 ] ] , width = 4 )
                    MainLayout.infoText = str ( 'Restricted: x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                    

                
    def on_touch_move ( self , touch ) :
        global CURRENT_DRAW
        
        if CURRENT_DRAW == 'none' :
            pass
        elif CURRENT_DRAW == 'aerial' :
            if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
                self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
                MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                MainLayout.outputX.append( int ( touch.pos[0] - MainLayout.mapProperties["kivy_x_offset"] ) )
                MainLayout.outputY.append( int ( touch.pos[1] - MainLayout.mapProperties["kivy_y_offset"] )  )              
                #  MainLayout.coordsAerial.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )   
        elif CURRENT_DRAW == 'ground' :
            if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
                self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
                MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                MainLayout.coordsGround.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )
        elif CURRENT_DRAW == 'restricted' :
            if self.collide_point ( touch.pos [ 0 ] , touch.pos [ 1 ] ) :
                self.line.points = self.line.points + [ touch.pos [ 0 ] , touch.pos [ 1 ] ] 
                MainLayout.infoText = str ( 'x = ' ) + str ( int ( touch.pos [ 0 ] )  ) + str ( ', y = ' ) + str ( int ( touch.pos [ 1 ] ) ) 
                MainLayout.coordsRestricted.append (  ( int ( touch.pos [ 0 ] )  )  + (  (  ( touch.pos [ 1 ] / 1000 ) ) )  )
                
                
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
        
        print ( MainLayout.coordsAerial ) 
    


        
class Interface ( App ) :
    def build ( self ) :
        
        return MainLayout () 
    
    
if __name__ == '__main__' :
    Interface().run()