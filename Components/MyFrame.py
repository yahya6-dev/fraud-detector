## this is the toplevel window for managing all
## windows firstly it start with a login screen after successful login
## proceed to the main view else it display error either caused it locked
## or incorrect password and username

import wx,math

class MyFrame(wx.Frame):
    def __init__(self,parent=None,title=""):
        """ construct our base class constructor appropriately inspite super has some side effect"""
        super(MyFrame,self).__init__(parent,title=title)
        # get the main display size
        _,_,x,y = wx.Display().GetClientArea()
        # calculate the center of our rect
        centerX = math.floor(x/2)
        centerY = math.floor(y/2)
        # determine our login window size by subtracting from centerX and centerY
        self.SetInitialSize((centerX,centerY))
        # background color
        self.BackgroundColour = "rgb(51,51,51)"
        # center our login window
        self.Centre()
        print(self.DoGetPosition())