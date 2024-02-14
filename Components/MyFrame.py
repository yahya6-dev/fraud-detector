## this is the toplevel window for managing all
## windows firstly it start with a login screen after successful login
## proceed to the main view else it display error either caused it locked
## or incorrect password and username

import wx,math,os
from wx.lib import sized_controls as size
import Components.utils as utils
# login panel which consist of a password and username field 
# with a submit button that popup in the initial loading


# license panel 
class LicensePanel(wx.Dialog):
    def __init__(self,parent):
        super(LicensePanel,self).__init__(parent)
        #x,y = self.TopLevelParent.GetSize()
        #self.SetInitialSize((x,y))
        # add our sizer here
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add child element here
        # we start with text and image "enter your activation key" and key image
        # text label that appear atop with its style
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.font = wx.Font()
        self.font.SetPointSize(12)
        self.font.MakeBold()
        # static text control
        self.textHeader = wx.StaticText(self,label="Enter Your Activation Key")
        self.textHeader.ForegroundColour = "rgb(255,255,255)"
        self.textHeader.SetFont(self.font)
        #self.textHeader.BackgroundColour = "rgb(31,31,31)"
        # add image key
        self.key = wx.StaticBitmap(self,bitmap=wx.Bitmap("./Components/assets/key.png"))
        headerSizer.Add(self.textHeader,1,wx.ALIGN_CENTRE_VERTICAL|wx.ALL,8)
        headerSizer.Add(self.key,1,wx.ALL|wx.ALIGN_TOP,0)
        # add Activation key input box
        #self.textError = wx.StaticText(self,label="")
        self.ctrlText = wx.TextCtrl(self) 
        # buttons sizer horizontal one
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # set trial and submit license key
        self.buttonTrial = wx.Button(self,label="Try Trial For 10 Days")
        self.buttonTrial.BackgroundColour = "rgb(38,124,254)"
        self.buttonTrial.ForegroundColour = "rgb(255,255,255)"
        self.buttonLicense = wx.Button(self,label="Submit")
        # add the two buttons
        buttonSizer.Add(self.buttonTrial,0,wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_LEFT,8)
        buttonSizer.AddStretchSpacer()
        buttonSizer.Add(self.buttonLicense,0,wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT,8)
        # set main layout sizer"""
        sizer.Add(headerSizer,0,wx.ALL|wx.EXPAND,0)
        sizer.Add(self.ctrlText,0,wx.EXPAND|wx.ALL,8)
        sizer.Add(buttonSizer,0,wx.EXPAND|wx.ALL,0)
        self.SetSizer(sizer)
        # event handler for trial button
        self.Bind(wx.EVT_BUTTON,self.OnTrial,self.buttonTrial)

    def OnTrial(self,event):
        # initialized trials day
        cursor,conn,result = utils.getTrialInfo()
        # insert statement
        stm = "insert into trial(days,istrial) values(1,1)"
        cursor.execute(stm)
        conn.commit()
        # start our app in new process
        self.TopLevelParent.Close()
        os.execlp("python3","python3","Components/MainWindow.py")

class MyPanel(wx.Panel):
    # an internal class to represent login field and text
    class _Login(size.SizedPanel):
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
            #self.passEntry.SetHint("Enter Password?")
            self.usernameEntry.SetHint("Enter Username?")
            # add login button
            # serve to show error in case of wrong input
            self.text = wx.StaticText(self,label="")
            self.button = wx.Button(self,label="Log In")
            self.button.SetSizerProp("halign","right")


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
        # bind evt to button to login
        self.Bind(wx.EVT_BUTTON,self.OnLogin,self.panel.login.button)
        # flag to decide whether a user start a trial
        self.flag = False
        # check if database exists before recreating another
        if not os.path.exists("Components/users.sqlite"):
            # initialized database
            utils.initDatabase("Components/users.sqlite")
        else:
            cur,conn,result = utils.getTrialInfo()
            if result:
                self.flag = True
        

    def OnLogin(self,event):
        # retrieve password and username
        username = self.panel.login.usernameEntry.Value
        password = self.panel.login.passEntry.Value
        print(username,password)
        # check login for validity
        if utils.checkLogin(username,password):
            if not self.flag:
                self.panel = LicensePanel(self)
                self.panel.ShowModal()
                self.Close()
            # user subscribed to trial version
            os.execlp("python3","python3","Components/MainWindow.py")
        else:
            self.panel.login.text.Label = "Error Login Please Check Your Details"
            self.panel.login.text.ForegroundColour  = "rgb(237,12,12)"

