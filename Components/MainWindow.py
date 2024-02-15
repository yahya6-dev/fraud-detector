# main camera app screen
import wx
from utils import getTrialInfo
from GroupSizer import GroupSizer

# our list box section for displaying list of target
class MyImageList(wx.ListBox):
    def __init__(self,parent,imagelists):
        # init our super class
        super(MyImageList,self).__init__(parent,style=wx.LC_REPORT)
        # utility to add images to  list 
        self.AddImages(imagelists)

    # images to the list
    def AddImages(self,images):
        for image in images:
            print(wx.Bitmap(image))

class CamPanel(wx.Panel):
    def __init__(self,parent):
        super(CamPanel,self).__init__(parent)
        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # slit cam screen into two
        # buttons for switching
        self.bt1 = wx.ToggleButton(self,label="Playback")
        self.bt2 = wx.ToggleButton(self,label="Live Camera")
        # set bts colour
        self.bt1.ForegroundColour = "rgb(255,255,255)"
        self.bt2.ForegroundColour = "rgb(255,255,255)"
        self.BackgroundColour = "rgb(200,200,200)"
        # get panel size
        x,y = self.TopLevelParent.GetSize()
        print(x,y,"toplevel")
        # image window
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap("./Components/assets/other.jpeg"),size=(x*2,y))
        # buttons sizer
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.bt1,1,wx.LEFT|wx.BOTTOM,16)
        buttonSizer.Add(self.bt2,1,wx.RIGHT|wx.BOTTOM,16)
        # add buttonsizer to the mainsizer
        sizer.Add(buttonSizer,1,wx.ALL|wx.EXPAND,0)
        sizer.Add(self.image,9,wx.TOP|wx.EXPAND,0)
        self.SetSizer(sizer)


class MainWindowPanel(wx.Panel):
    def __init__(self,parent):
        # get our superclass ready
        super(MainWindowPanel,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add group sizer
        self.groupsizer = GroupSizer(self,wx.HORIZONTAL,"")
        bottomSizer = GroupSizer(self,wx.HORIZONTAL,"")
        # add item to the top sizer
        topLeft = GroupSizer(self,wx.VERTICAL,"")
        #camScreen = GroupSizer(self,wx.VERTICAL,"")
        topRight = GroupSizer(self,wx.VERTICAL,"")
        # add camera component panel
        self.cameraComponent = CamPanel(self)
        # section to our main box sizer
        self.groupsizer.AddItem(topLeft,1,wx.ALL,8)
        self.groupsizer.AddItem(self.cameraComponent,3,wx.ALL|wx.EXPAND,8)
        self.groupsizer.AddItem(topRight,1,wx.ALL,8)
        # add image list to our topleft screen
        self.imageList = MyImageList(topLeft,["Components/assets/other.jpeg"])
        topLeft.AddItem(self.imageList,1,wx.EXPAND|wx.ALL,8)
        # add toplevel section to main sizer
        sizer.Add(self.groupsizer.sizer,3,wx.EXPAND|wx.ALL,8)
        sizer.Add(bottomSizer,1,wx.EXPAND|wx.ALL,8)
        self.SetSizer(sizer)

class MyWindow(wx.Frame):
    def __init__(self,parent,title):
        """ this is the main window of our camera
            where everything happened
        """
        super(MyWindow,self).__init__(parent,title=title)
        # set our frame background
        self.BackgroundColour = "rgb(51,51,51)"
        # our main layout panel
        self.panel = MainWindowPanel(self)

class MyApp(wx.App):
    def OnInit(self):
        cursor,db,status = getTrialInfo()
        # our camera main window title
        title = status[-1]
        title = "AI Camera App Trial" if title == 1 else "AI Camera App"
        self.frame = MyWindow(None,title)
        self.frame.ShowFullScreen(True)
        return True


if __name__=="__main__":
    myapp = MyApp(False)
    myapp.MainLoop() 