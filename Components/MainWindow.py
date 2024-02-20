# main camera app screen
import wx,math
from utils import getTrialInfo
from GroupSizer import GroupSizer
from wx.lib import sized_controls as sized

# simple panel for representing play and stop camera functionalities
class PlayPausedPanel(wx.Panel):
    def __init__(self,parent,label,image):
        super(PlayPausedPanel,self).__init__(parent)
        # add sizer that default to vertical
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add controls image and label
        self.label = wx.StaticText(self,label=label)
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap(image))
        # add controls to the sizer
        sizer.Add(self.label,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,4)
        sizer.Add(self.image,0,wx.EXPAND|wx.ALL,4)
        # add sizer as layout sizer
        self.SetSizer(sizer)

class LabelAndImageHorizontal(wx.Panel):
    def __init__(self,parent,image):
        super(LabelAndImageHorizontal,self).__init__(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # add controls image 
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap(image))
        # add radio button
        self.radio = wx.CheckBox(self,size=(-1,32))
        # add image to the hsizer
        sizer.Add(self.image,0,wx.ALL,0)
        sizer.Add(self.radio,0,wx.LEFT,4)
        self.SetSizer(sizer)

# panel containing controls for choosing either color image or gray image
class FrameType(wx.Panel):
    def __init__(self,parent):
        super(FrameType,self).__init__(parent)
        # config appearance 
        self.BackgroundColour = "rgb(31,31,31)"
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(self,label="Frame Type")
        # add choice option
        self.options = wx.RadioBox(self,choices=["Gray","Color"],style=wx.RA_SPECIFY_ROWS)
        sizer.Add(self.label,0,wx.TOP|wx.LEFT|wx.RIGHT,4)
        sizer.Add(self.options,0,wx.ALL,4)
        # add sizer to the main layout
        self.SetSizer(sizer)

# AI enhancement section
class AIEnhancer(wx.Panel):
    def __init__(self,parent,label,image):
        super(AIEnhancer,self).__init__(parent)
         # add sizer that default to vertical
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(self,label=label)
        imagePanel = LabelAndImageHorizontal(self,image)
        # add controls to the sizer
        sizer.Add(self.label,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.LEFT|wx.RIGHT|wx.TOP,4)
        sizer.Add(imagePanel,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.BOTTOM,4)
        # add sizer as layout sizer
        self.SetSizer(sizer)


        
# our window for camera tools
class CameraTools(wx.Panel):
    def __init__(self,parent):
        super(CameraTools,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # target label
        self.titleLabel = wx.StaticText(self,label="Camera Tools")
        # config label font
        font = wx.Font()
        font.SetPointSize(16)
        self.titleLabel.SetFont(font)
        # set title appearance
        self.titleLabel.ForegroundColour = "rgb(235,235,235)"
        sliderSize,_ = self.titleLabel.GetSize()
        # add slider to a panel
        self.sliderPanel = wx.Panel(self,size=(sliderSize,-1))
        # add slider to the panel
        self.slider = wx.Slider(self.sliderPanel,minValue=0,maxValue=100)
        # set slider appearance
        self.sliderPanel.BackgroundColour = "rgb(31,31,31)"
        # slider panel box sizer
        sliderBoxSizer = wx.BoxSizer(wx.VERTICAL)
        #sliderBoxSizer.Add(self.slider,1,wx.EXPAND)
        # add slider title
        self.sliderTitle = wx.StaticText(self.sliderPanel,label="Zoom")
        sliderBoxSizer.Add(self.sliderTitle,0,wx.LEFT|wx.RIGHT|wx.TOP,4)
        sliderBoxSizer.Add(self.slider,0,wx.EXPAND|wx.ALL,4)
        # config slider panel sizer
        self.sliderPanel.SetSizer(sliderBoxSizer)
        # add play pause control
        self.play = PlayPausedPanel(self,"Play/Paused","Components/assets/play.png")
        sizer.Add(self.titleLabel,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        self.enhancer = AIEnhancer(self,"AI Enhancer","Components/assets/eyeglasses.png")
        # frame type controls
        self.frameType = FrameType(self)
        # add panel to the main sizer
        sizer.Add(self.sliderPanel,0,wx.ALL|wx.EXPAND,8)
        # add play control to the sizer
        sizer.Add(self.play,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        sizer.Add(self.enhancer,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        sizer.Add(self.frameType,1,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        self.SetSizer(sizer)
        # bind paint event to draw a line atop of title
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.titleLabel.GetRect()
        color = "rgb(200,200,200)" 
        dc.SetPen(wx.Pen(color,1))
        dc.DrawLine(x,y,w+50,y)
    
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
        dc.DrawRectangle(x,y-32,w-32-1,h)

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
        self.images = ["Components/assets/pic1.jpg","Components/assets/pick4.jpg",
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
                # custom utility to delete the image
        self.imageList.childs = results
        self.imageList.Refresh()
        self.imageList.Update()
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

# this panel contain various UI for controlling the target
class MainControl(wx.Panel):
    def __init__(self,parent):
        super(MainControl,self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.targetControl = TargetControl(self)
        # target control to the sizer
        sizer.Add(self.targetControl,0,wx.ALL,8)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.GetRect()
        # pencil and brush color
        dc.SetBrush(wx.Brush("rgb(200,220,200)"))
        dc.SetPen(wx.Pen("rgb(220,220,220)"))
        # draw rectangle
        print("I cant see anymore")
        dc.DrawRectangle(x,y,w,h)

# Target Control UI, for setting and moving frame
class TargetControl(wx.Panel):
    def __init__(self,parent):
        super(TargetControl,self).__init__(parent)
        # buttons for moving around target
        self.btLeft = wx.StaticBitmap(self,bitmap=wx.Bitmap("Components/assets/left.png"))
        self.btRight = wx.StaticBitmap(self,bitmap=wx.Bitmap("Components/assets/right.png"))
        self.btTop = wx.StaticBitmap(self,bitmap=wx.Bitmap("Components/assets/up.png"))
        self.btBottom = wx.StaticBitmap(self,bitmap=wx.Bitmap("Components/assets/down.png"))
        # main layout sizer
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # hsizer for vertical alignment
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        # vsizer as the main sizer
        self.SetSizer(vsizer)

        # bind to paint event to draw the rectangle
        #self.Bind(wx.EVT_PAINT,self.OnPaint)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y = self.GetSize()
        x1,y1,w,_h = self.GetRect()
        normalizedHeight = y - 16 - 32 - 64
        # rectangle starting offset
        startYOffset = y1 - 28
        startXOffset = x1 - 8
        endYOffset = startYOffset
        endXOffset =  w // 10
        # set pencil color
        dc.SetPen(wx.Pen("rgb(220,220,220)",2))
        dc.SetBrush(wx.Brush("rgb(51,255,255)"))
        dc.DrawRectangle(startXOffset,startYOffset,endXOffset,endYOffset)

class MainWindowPanel(wx.Panel):
    def __init__(self,parent):
        # get our superclass ready
        super(MainWindowPanel,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add group sizer
        self.groupsizer = GroupSizer(self,wx.HORIZONTAL,"")
        self.bottomSection = MainControl(self)
        # add item to the top sizer
        self.targetScreen = TargetScreen(self)
        self.topRight = CameraTools(self)
        # add camera component panel
        self.cameraComponent = CamPanel(self)
        # section to our main box sizer
        self.groupsizer.AddItem(self.targetScreen,1,wx.ALL|wx.EXPAND,8)
        self.groupsizer.AddItem(self.cameraComponent,3,wx.ALL|wx.EXPAND,8)
        self.groupsizer.AddItem(self.topRight,1,wx.ALL|wx.EXPAND,8)
        # add image list to our topleft screen
        #self.imageList = MyImageList(topLeft,["Components/assets/other.jpeg"])
        #topLeft.AddItem(self.imageList,1,wx.EXPAND|wx.ALL,8)
        # add toplevel section to main sizer
        sizer.Add(self.groupsizer.sizer,3,wx.EXPAND|wx.ALL,8)
        sizer.Add(self.bottomSection,1,wx.EXPAND|wx.ALL,8)
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