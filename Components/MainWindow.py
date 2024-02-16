# main camera app screen
import wx,math
from utils import getTrialInfo
from GroupSizer import GroupSizer
from wx.lib import sized_controls as sized

# our image for displaying a single target
class MyImage(wx.Panel):
    def __init__(self,parent,image,size,deleteButton,images):
        super(MyImage,self).__init__(parent)
        self.imageName = image
        # layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # main image display control
        # delete button reference
        self.deleteButton = deleteButton
        # reference to original images
        self.images = images
        self.image = wx.Image(image)
        self.image.Rescale(250-32-24-8,200-32)
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap(self.image))
        # set cursor image on hovering
        self.image.SetCursor(wx.Cursor("Components/assets/cursor.png"))
        sizer.Add(self.image,0,wx.ALL,8)
        
        self.SetSizer(sizer)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.image.SetEvtHandlerEnabled(True)
        self.image.Bind(wx.EVT_LEFT_UP,self.OnLeftClick,self.image)
        self.isSelected = False

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.image.GetRect()
        color = "rgb(237,12,12)" if self.isSelected else "rgb(38,124,254)"
        dc.SetPen(wx.Pen(color,2))
        dc.SetBrush(wx.Brush("rgb(51,51,51)"))
        dc.DrawRectangle(x-2,y-2,w+4,h+4)
        

    def OnLeftClick(self,event):
        self.isSelected = not self.isSelected
        # this hold the states of the images
        allImages = [image.isSelected for image in self.images]

        if not self.deleteButton.IsShown() and self.isSelected:
            self.deleteButton.Show()
        elif self.deleteButton.IsShown() and not self.isSelected and not any(allImages):
            self.deleteButton.Hide()

        self.Refresh()
        print("Hello What happened")
    

# our main image list
class MyImageList(sized.SizedScrolledPanel):
    def __init__(self,parent,imageList,size,deleteButton):
        super(MyImageList,self).__init__(parent)
        self.size = size
        self.config(imageList,self.size,deleteButton)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.ShowScrollbars(False,True)

    # add images as MyImage instance
    def config(self,images,size,deleteButton):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.childs = []
        for image in images:
            print(image)
            targetContainer = MyImage(self,image,size,deleteButton,self.childs)
            self.childs.append(targetContainer)
            self.sizer.Add(targetContainer,0,wx.LEFT|wx.RIGHT,8)
        self.SetSizer(self.sizer)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        # our main window total size
        x,y,w,h = self.GetRect()
        dc.SetBrush(wx.Brush("rgb(51,51,51)"))
        dc.SetPen(wx.Pen("rgb(200,200,200)",1))
        dc.DrawRectangle(x,y-32,w-32,h)

# class that hold left screen that targets image list
class TargetScreen(wx.Panel):
    def __init__(self,parent):
        # init our base class
        super(TargetScreen,self).__init__(parent)
        # add a layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # target label
        self.titleLabel = wx.StaticText(self,label="Targets")
        # button to delete target from target list
        self.deleteButton = wx.BitmapButton(self,bitmap=wx.Bitmap("Components/assets/trash.png"))
        # hide event
        self.deleteButton.Hide()
        # config label font
        font = wx.Font()
        font.SetPointSize(24)
        font.MakeBold()
        self.titleLabel.SetFont(font)
        # image panel add to it
        self.images = ["Components/assets/pic1.jpg","Components/assets/pic2.jpg",
            "Components/assets/pic3.jpg","Components/assets/pick4.jpg"]
        x,y = self.TopLevelParent.GetSize()
        print(x,y,"of the parent")
        self.imageList = MyImageList(self,self.images,(x-16,math.floor(y/1.2)),self.deleteButton)
        # add label to the main sizer
        sizer.Add(self.titleLabel,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,4)
        # add image list to our sizer
        sizer.Add(self.imageList,1,wx.EXPAND|wx.ALL,8)    
        self.SetSizer(sizer)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        # listen in case delete was issued
        self.deleteButton.Bind(wx.EVT_BUTTON,self.OnDelete,self.deleteButton)

    def OnDelete(self,event):
        print("here get called")
        results = []
        for child in self.imageList.childs:
            if  not child.isSelected: 
                results.append(child)
            else:
                child.isSelected = False
                child.Destroy()
        self.imageList.childs = results
        self.imageList.Refresh()
        self.deleteButton.Hide()
        self.images = results
        self.Refresh()

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.titleLabel.GetRect()
        dc.SetPen(wx.Pen("rgb(220,220,220)",1,wx.PENSTYLE_DOT))
        targetMargin = 8
        lengthOfDot = self.GetRect()[2]
        print(self.GetRect(),w,h)
        dc.DrawLine(x-targetMargin,y,w+lengthOfDot,y)
        

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
        # topLeft = GroupSizer(self,wx.VERTICAL,"")
        #topLeft.AddItem(self.titleLabel,1,wx.ALL|wx.ALIGN_RIGHT,8)
        #camScreen = GroupSizer(self,wx.VERTICAL,"")
        self.targetScreen = TargetScreen(self)
        topRight = GroupSizer(self,wx.VERTICAL,"")
        # add camera component panel
        self.cameraComponent = CamPanel(self)
        # section to our main box sizer
        self.groupsizer.AddItem(self.targetScreen,1,wx.ALL|wx.EXPAND,8)
        self.groupsizer.AddItem(self.cameraComponent,3,wx.ALL|wx.EXPAND,8)
        self.groupsizer.AddItem(topRight,1,wx.ALL,8)
        # add image list to our topleft screen
        #self.imageList = MyImageList(topLeft,["Components/assets/other.jpeg"])
        #topLeft.AddItem(self.imageList,1,wx.EXPAND|wx.ALL,8)
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