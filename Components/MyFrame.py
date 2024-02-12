## this is the toplevel window for managing all
## windows firstly it start with a login screen after successful login
## proceed to the main view else it display error either caused it locked
## or incorrect password and username

import wx,math
from wx.lib import sized_controls as size
#import utils
# login panel which consist of a password and username field 
# with a submit button that popup in the initial loading

class MyPanel(wx.Panel):
    # an internal class to represent login field and text
    class _Login(size.SizedScrolledPanel):
        def __init__(self,parent):
            # initialize our super class
            super(MyPanel._Login,self).__init__(parent)
            # set sizer type
            self.SetSizerType("form")
            # password field and entry
            self.usernameLabel  = wx.StaticText(self,label="Username:")
            self.usernameEntry = wx.TextCtrl(self)
            self.usernameEntry.SetSizerProp("expand",True)
            self.usernameLabel.SetSizerProp("valign","center")
            # password section allows it to expand
            self.passLabel  = wx.StaticText(self,label="Password:")
            self.passEntry = wx.TextCtrl(self,style=wx.TE_PASSWORD)
            self.passEntry.SetSizerProp("expand",True)
            self.passLabel.SetSizerProp("valign","center")
            # set entries hint text like placeholder in html
            self.passEntry.SetHint("Enter Password?")
            self.usernameEntry.SetHint("Enter Username?")
            # add login button
            # serve to show error in case of wrong input
            self.text = wx.StaticText(self,label="")
            self.button = wx.Button(self,label="Log In")
            self.button.SetSizerProp("halign","right")
            # bind evt to button to login
            self.Bind(wx.EVT_BUTTON,self.OnLogin,self.button)

        def OnLogin(self,event):
            self.text.Label = "Error Login Please Check Your Details"
            self.text.ForegroundColour  = "rgb(220,0,0)"


    def __init__(self,parent):
        """ main login panel"""
        # call our super class constructor
        super(MyPanel,self).__init__(parent)
        # create a sizer vertical one for all the placement
        self.configSizer()

    def configSizer(self):
        # header image
        self.imageHeader = wx.StaticBitmap(self,bitmap=wx.Bitmap("./Components/assets/person.png"))
        # set foreground colour to  close to white color
        self.ForegroundColour = "rgb(225,225,225)"
        # we use sans serif font
        self.font = wx.Font()
        # set font size to 16 px
        self.font.SetPointSize(16)
        # set font weight to bold
        self.font.MakeBold()
        _,_,x,y = wx.Display().GetClientArea()
        # calculate image header size
        xPos,yPos = x // 3, y // 2.5
        # set size imageheader
        self.imageHeader.SetInitialSize((xPos,-1))
        # our main panel sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # header sizer which assume horizontal 
        imagesizer = wx.BoxSizer(wx.HORIZONTAL)
        # add image as our header
        imagesizer.Add(self.imageHeader,1,wx.ALL|wx.ALIGN_CENTRE_HORIZONTAL,4)
        # add image sizer to our main sizer
        sizer.Add(imagesizer,0,wx.ALL,0)
        self.text = wx.StaticText(self,label="To Continue Log In")
        self.text.SetFont(self.font)
        sizer.Add(self.text,0,wx.ALL|wx.ALIGN_CENTRE_HORIZONTAL,4)
        # login section
        self.login = MyPanel._Login(self)
        sizer.Add(self.login,1,wx.ALL|wx.EXPAND,4)
        self.SetSizer(sizer)

class MyFrame(wx.Frame):
    def __init__(self,parent=None,title=""):
        """ construct our base class constructor appropriately inspite super has some side effect"""
        super(MyFrame,self).__init__(parent,title=title,style=wx.CLOSE_BOX  | wx.CAPTION)
        # get the main display size
        _,_,x,y = wx.Display().GetClientArea()
        # calculate the center of our rect
        centerX = math.floor(x/3)
        centerY = math.floor(y/2.5)
        # determine our login window size by subtracting from centerX and centerY
        self.SetInitialSize((centerX,centerY))
        # background color
        self.BackgroundColour = "rgb(51,51,51)"
        # center our login window
        self.Centre()
        print(self.DoGetPosition())
        # our login panel
        self.panel = MyPanel(self)

