# main camera app screen
import wx,math
from utils import getTrialInfo,playSound
from GroupSizer import GroupSizer
from wx.lib import sized_controls as sized
import os,socket,zlib
import sys,time,pickle
import _thread as thread
import cv2
sys.path.append("server1")
from server1 import Server1
from multiprocessing import Process, Pipe
import wx.adv as adv
import cv2.dnn_superres as superres
from PIL import Image

# simple panel for representing play and stop camera functionalities
class PlayPausedPanel(wx.Panel):
    def __init__(self,parent,label,image):
        super(PlayPausedPanel,self).__init__(parent)
        # add sizer that default to vertical
        sizer = wx.BoxSizer(wx.VERTICAL)
        # check if is playing
        self.flag = False
        # add controls image and label
        self.label = wx.StaticText(self,label=label)
        self.pausedImage = wx.Image(image)
        self.playImage = wx.Image("Components/assets/pause.png")
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap(self.playImage))
        # add controls to the sizer
        sizer.Add(self.label,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,4)
        sizer.Add(self.image,0,wx.EXPAND|wx.ALL,4)
        self.soundFilename = "Components/assets/info.wav" 
        # add sizer as layout sizer
        self.SetSizer(sizer)
        self.image.SetEvtHandlerEnabled(True)
        self.image.Bind(wx.EVT_LEFT_UP,self.OnLeftClick)

    def OnLeftClick(self,event):
        self.flag = not self.flag
        # alternate btw playing and paused image
        if self.flag:
            self.image.SetBitmap(wx.Bitmap(self.pausedImage))
            self.enhancer.imagePanel.radio.Enable()
            # send special request to stop receiving data
        else:
            self.image.SetBitmap(wx.Bitmap(self.playImage))
            # send special request to continue receiving data
            self.enhancer.imagePanel.radio.Disable()
        playSound(self.soundFilename)
        self.Refresh()
        print("Why Dont Run")

# simple class with label and image vertically aligned
class LabelAndImageVertical(wx.Panel):
    def __init__(self,parent,label,image,image2):
        super(LabelAndImageVertical,self).__init__(parent)
        # add vertical sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # images list reference
        self.images = []
        # add controls
        self.label = wx.StaticText(self,label=label)
        font = wx.Font()
        font.SetPointSize(8)
        self.label.SetFont(font)
        self.image = wx.Image(image)
        self.image.Rescale(48,48)
        self.imageSel = wx.Image(image2)
        self.imageSel.Rescale(48,48)
        self.bitmap = wx.Bitmap(self.image)
        self.imageCtrl = wx.StaticBitmap(self,bitmap=self.bitmap)
        # indicator of wheher it is selected
        self.flag = False
        # ad controls to the sizer
        sizer.Add(self.label,0,wx.ALL,2)
        sizer.Add(self.imageCtrl,0,wx.ALL,2)
        self.SetSizer(sizer)
        self.imageCtrl.SetEvtHandlerEnabled(True)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP,self.OnLeftClick)

    def OnLeftClick(self,event):
        self.flag = not self.flag
        if self.flag:
            # deselect all other images
            for image in self.images:
                image.flag = False
                image.imageCtrl.SetBitmap(image.bitmap)
                image.Refresh()
            self.imageCtrl.SetBitmap(wx.Bitmap(self.imageSel))
        else:
            self.imageCtrl.SetBitmap(wx.Bitmap(self.image))
        self.Refresh()
        # apropriate handlers for such event

# Panel representing tracking type
class TrackingTypePanel(wx.Panel):
    def __init__(self,parent):
        super(TrackingTypePanel,self).__init__(parent)
        # layout sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # add controls
        self.fullBody = LabelAndImageVertical(self,"Full Body","Components/assets/person-fill3.png","Components/assets/person-fill3-sel.png")
        self.upperBody = LabelAndImageVertical(self,"Top Body","Components/assets/person-fill1.png","Components/assets/person-fill1-sel.png")
        self.face = LabelAndImageVertical(self,"Face","Components/assets/person-fill2.png","Components/assets/person-fill2-sel.png")
        self.offTracking = LabelAndImageVertical(self,"Off","Components/assets/power-sel.png","Components/assets/power.png")
        # fields to store reference to all images
        self.images = [self.fullBody,self.upperBody,self.face,self.offTracking]
        # pass the images reference to the images
        self.fullBody.images = self.upperBody.images = self.face.images = self.offTracking.images = self.images 
        # add controls to the sizer
        sizer.Add(self.fullBody,0,wx.LEFT,8)
        sizer.Add(self.upperBody,0,wx.LEFT,8)
        sizer.Add(self.face,0,wx.LEFT,8)
        sizer.Add(self.offTracking,0,wx.LEFT,8)

        self.SetSizer(sizer)

# main panel carrying target options such as search
class TargetOption(wx.Panel):
    def __init__(self,parent):
        super(TargetOption,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.searchBottom = wx.Button(self,label="Search Target")
        font = wx.Font()
        font.MakeBold()
        self.searchBottom.SetFont(font)
        self.searchBottom.ForegroundColour = "rgb(250,250,250)"
        self.liveRecognition = wx.Button(self,label="Add To Live Recognition")
        self.liveRecognition.BackgroundColour ="rgb(38,124,254)"
        self.liveRecognition.ForegroundColour = "rgb(250,250,250)"
        # add controls to the sizer
        sizer.Add(self.searchBottom,0,wx.ALL|wx.ALIGN_CENTRE_HORIZONTAL,4)
        sizer.Add(self.liveRecognition,0,wx.ALL|wx.EXPAND,4)
        # set panel appearance
        self.BackgroundColour = "rgb(31,31,31)"
        # set layout sizer
        self.SetSizer(sizer)

# parent panel carrying targetoption and label
class TargetOptionPanel(wx.Panel):
    def __init__(self,parent):
        super(TargetOptionPanel,self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add controls
        self.targetOptions = TargetOption(self)
        self.label = wx.StaticText(self,label="Target Options")
        # add all of the controls
        sizer.Add(self.label,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,4)
        sizer.Add(self.targetOptions,0,wx.ALL,4)

        self.SetSizer(sizer)
        
# main panel containing tracking panel
class TrackingPanel(wx.Panel):
    def __init__(self,parent):
        super(TrackingPanel,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add controls
        self.label = wx.StaticText(self,label="Tracking Type")
        self.label.ForegroundColour = "rgb(255,255,255)"
        font = wx.Font()
        font.SetPointSize(14)
        self.label.SetFont(font)
        # add main TrackingTypePanel
        self.tracking = TrackingTypePanel(self)
        # add them to the sizer
        sizer.Add(self.label,0,wx.ALL|wx.ALIGN_CENTRE_HORIZONTAL,8)
        sizer.Add(self.tracking,0,wx.EXPAND|wx.ALL,8)

        self.SetSizer(sizer)

class LabelAndImageHorizontal(wx.Panel):
    def __init__(self,parent,image):
        super(LabelAndImageHorizontal,self).__init__(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # add controls image 
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap(image))
        # add radio button
        self.radio = wx.CheckBox(self,size=(-1,32))
        self.radio.Disable()
        # add image to the hsizer
        sizer.Add(self.image,0,wx.ALL,0)
        sizer.Add(self.radio,0,wx.LEFT,4)
        self.SetSizer(sizer)
        self.radio.Bind(wx.EVT_CHECKBOX,self.OnCheck)
    
    def OnCheck(self,event):
        print("HERE=>FOR WHAT?")
        if  self.radio.IsChecked():
            self.camPanel.updateImage()
            self.radio.SetValue(False)
            
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
        self.options.SetSelection(1)
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
        self.imagePanel = LabelAndImageHorizontal(self,image)
        # add controls to the sizer
        sizer.Add(self.label,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.LEFT|wx.RIGHT|wx.TOP,4)
        sizer.Add(self.imagePanel,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.BOTTOM,4)
        # add sizer as layout sizer
        self.SetSizer(sizer)


# selected target panel
class SelectedTargetPanel(wx.Panel):
    def __init__(self,parent):
        super(SelectedTargetPanel,self).__init__(parent)
        # main layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add controls
        self.label = wx.StaticText(self,label="Selected Target")
        self.image = wx.Image("Components/assets/no-selection.png")
        # rescale image size
        self.image.Rescale(100,100)
        self.imageCtrl = wx.StaticBitmap(self,bitmap=wx.Bitmap(self.image))
        # set label font
        font = wx.Font()
        font.MakeBold()
        #font.SetPointSize(16)
        self.label.SetFont(font)
        # add controls to the main sizer
        sizer.Add(self.label,0,wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,8)
        sizer.Add(self.imageCtrl,0,wx.ALL,8)
        self.SetSizer(sizer)
        # bind to Paint Event
        self.Bind(wx.EVT_PAINT,self.OnPaint)
       

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.label.GetRect()
        # draw line
        dc.SetBrush(wx.Brush("rgb(51,51,51)"))
        dc.SetPen(wx.Pen("rgb(180,180,180)",2))
        dc.DrawLine(x,y,x+150,y)
        x,y,w,h = self.imageCtrl.GetRect()
        w,h = self.imageCtrl.GetSize()
        dc.SetPen(wx.Pen("rgb(237,12,12)"))
        dc.DrawRectangle(x-1,y-1,w+2,h+2)
        self.Refresh()

# our window for camera tools
class CameraTools(wx.Panel):
    def __init__(self,parent,):
        super(CameraTools,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # target label
        self.titleLabel = wx.StaticText(self,label="Camera Tools")
        img = wx.Image("Components/assets/power1.png")
        img.Rescale(20,20)
        self.close = wx.BitmapButton(self,name="Exit",bitmap=wx.Bitmap(img))
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
        # pass a reference of enhancer to the play
        self.play.enhancer = self.enhancer
        # frame type controls
        self.frameType = FrameType(self)
        # add a control for selecting target selection rectangle
        self.targetRect = wx.RadioBox(self,choices=["1","2","3","4","5","6"],label="Target Select Rect Size")
        # add panel to the main sizer
        sizer.Add(self.sliderPanel,0,wx.ALL|wx.EXPAND,8)
        # add play control to the sizer
        sizer.Add(self.play,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        sizer.Add(self.enhancer,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        sizer.Add(self.frameType,1,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        sizer.Add(self.targetRect,1,wx.ALIGN_CENTRE_HORIZONTAL|wx.ALL,8)
        self.SetSizer(sizer)
        # bind paint event to draw a line atop of title
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.close.Bind(wx.EVT_BUTTON,lambda event: self.TopLevelParent.Close())
        self.sliderPanel.Bind(wx.EVT_COMMAND_SCROLL_THUMBRELEASE,self.OnSlider,source=self.slider)

    
    def OnSlider(self,event):
        self.play.OnLeftClick(None)
        zoomFactor = int( (100 / self.slider.GetValue()) * 10 )
        event.Veto()

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
        self.bitmap = wx.Bitmap(self.image)
        self.image = wx.StaticBitmap(self,bitmap=self.bitmap)
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
        self.images = ["Components/assets/targets/"+target for target in os.listdir("Components/assets/targets")]
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
                child.Hide()
                # custom utility to delete the image
        self.imageList.Layout()
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
    NO_DATA_MSG = b"NO_DATA"
    RECT_CHOICES = {"1":25,"2":50,"3":75,"4":100,"5":150,"6":250}    

    def __init__(self,parent,targetRectSize,targetControl):
        super(CamPanel,self).__init__(parent)

        # DNN Model for super image resolution
        self.superres = superres.DnnSuperResImpl.create()
        self.superres.setModel("fsrcnn",3)        
        self.superres.readModel("Components/assets/models/FSRCNN-small_x3.pb")

        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # slit cam screen into two
        self.targetControl = targetControl
        # buttons for switching
        self.bt1 = wx.ToggleButton(self,label="Playback")
        self.bt2 = wx.ToggleButton(self,label="Live Camera 0")
        self.bt3 = wx.ToggleButton(self,label="Live Camera 1")
        self.bt4 = wx.ToggleButton(self,label="Main View")
        # this hold a reference to the choices of target selection size
        self.targetRectSize = targetRectSize
        # set bts colour
        self.bt1.ForegroundColour = "rgb(255,255,255)"
        self.bt2.ForegroundColour = "rgb(255,255,255)"
        self.bt3.ForegroundColour = "rgb(255,255,255)"
        self.bt4.ForegroundColour = "rgb(255,255,255)"
        self.BackgroundColour = "rgb(200,200,200)"
        # get panel size
        x,y = self.TopLevelParent.GetSize()
        print(x,y,"toplevel")
        # server address
        self.serverAddr = ("",8000)
        self.MAXBUFF = 1024 * 6
        # image window
        self.image = wx.StaticBitmap(self,bitmap=wx.Bitmap("./Components/assets/other.jpeg"),size=(x*2,y))
        self.WIDTH,self.HEIGHT = x*2,y
        # buttons sizer
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.bt1,1,wx.LEFT|wx.BOTTOM,16)
        buttonSizer.Add(self.bt2,1,wx.BOTTOM,16)

        buttonSizer.Add(self.bt3,1,wx.BOTTOM,16)
        buttonSizer.Add(self.bt4,1,wx.RIGHT|wx.BOTTOM,16)
        # add buttonsizer to the mainsizer
        sizer.Add(buttonSizer,1,wx.ALL|wx.EXPAND,0)
        sizer.Add(self.image,9,wx.TOP|wx.EXPAND,0)
        self.SetSizer(sizer)
        self.frame = None
        self.imageObject = None
        # add event listener to the live camera and playback button
        self.Bind(wx.EVT_TOGGLEBUTTON,self.OnButton1Click,self.bt1)
        self.Bind(wx.EVT_TOGGLEBUTTON,self.OnButton2Click,self.bt2)
        
        self.lock = thread.allocate_lock()
        proc = thread.start_new_thread(self.readMessage,())

    def readMessage(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect(self.serverAddr)
        # choices of target rect size
        choices = list(CamPanel.RECT_CHOICES.keys())
        # current selection of the current target selection rect
        current_size = CamPanel.RECT_CHOICES.get(choices[self.targetRectSize.GetSelection()])
        x,y,targetSelected = self.targetControl.rect_position
        reply = pickle.dumps([Server1.GET_CAMERA_1,current_size,x,y,targetSelected])   
        client.sendto(reply,self.serverAddr)
        reply,addr = client.recvfrom(1024*2)
        print(reply,"from the server")
        # send server camera query

        while True:
            # current selection of the current target selection rect
            current_size = CamPanel.RECT_CHOICES.get(choices[self.targetRectSize.GetSelection()])
            x,y,targetSelected = self.targetControl.rect_position
            print(x,y,"XY Direction")
            frame = b""
            print("server loop")
            if self.playPaused.flag:
                reply = Server1.SERVER_STOP

            elif self.frameType.GetSelection() == 0:
                reply = Server1.SERVER_FRAME_TYPE_GRAY_CAM_1
            
            else:
                # reply from the main process
                reply = Server1.GET_CAMERA_1

            msg = pickle.dumps([reply,current_size,x,y,targetSelected])
            print(msg,"reply from main process")
            client.sendto(msg,self.serverAddr)

            # if server stop receive ok message from the server
            if self.playPaused.flag:
                data,addr = client.recvfrom(1024)
        
            while True and  reply != Server1.SERVER_STOP:
                data,addr = client.recvfrom(1024*6)
                if data == Server1.START_OF_FRAME:
                    print("server start frame")
                    frame = b""
                    # childEnd.send(CamPanel.NO_DATA_MSG)
                
                elif data == Server1.END_OF_FRAME:
                    print("server end frame")
                    try:
                        frame = zlib.decompress(frame)
                        frame = pickle.loads(frame)
                        print(frame,"from END FRAME")
                        if reply == Server1.SERVER_FRAME_TYPE_GRAY_CAM_1:
                            frame = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR)
                            width,height,_ = frame.shape
                            self.imageObject = wx.Image(height,width,frame)
                            self.imageObject.Rescale(self.WIDTH,self.HEIGHT*3)
                        else:
                            width,height,_ = frame.shape
                            self.imageObject = wx.Image(height,width,frame)
                            self.imageObject.Rescale(self.WIDTH,self.HEIGHT*3)
                            print(frame,_)
                        self.frame = frame
                        self.bitmap = wx.Bitmap(self.imageObject)
                        self.lock.acquire()
                        self.image.SetBitmap(self.bitmap)
                        self.image.Refresh()
                        self.lock.release()

                        frame = b""
                        break
                    except Exception as e:
                        frame = b""
                        print("exception happened",e)
                        break
                if data  != Server1.START_OF_FRAME and data != Server1.SUCCESS:
                    frame += data
            #time.sleep(0.0001)

    def updateImage(self):
        self.imageObject = self.imageObject.BlurHorizontal(20)
        self.bitmap = wx.Bitmap(self.imageObject)
        self.image.SetBitmap(self.bitmap)
        self.image.Refresh()
        print("RUN AGAIN")
        for i in range(10):
            time.sleep(0.5)
            wx.GetApp().Yield()
        self.frame = self.superres.upsample(self.frame)
        print(self.frame,"OUTPUT")
        width,height,_ = self.frame.shape
        self.imageObject = wx.Image(height,width,self.frame)
        self.imageObject.Rescale(self.WIDTH,self.HEIGHT*3)
        self.bitmap = wx.Bitmap(self.imageObject)
        self.image.SetBitmap(self.bitmap)
        self.image.Refresh()

    def OnButton1Click(self,event):
        print(event.EventObject.Value,"Button 1")
        self.bt2.Value = False
        self.bt3.Value = False
        self.bt4.Value = False

    def OnButton2Click(self,event):
        print(event.EventObject.Value,"Button 2")
        self.bt1.Value = False
        self.bt3.Value = False
        self.bt4.Value = False

    
    def UpdateImage(self,event):
        self.lock.acquire()
        print(self.frame)
        self.lock.release()

        

        
# panel containing detect motion options
class TrackingOption(wx.Panel):
    def __init__(self,parent):
        super(TrackingOption,self).__init__(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # add radio box 
        self.radioBox = wx.RadioBox(self,choices=["Detect Motion","Track Target","None"],label="Tracking Options")
        # add box to the sizer
        sizer.Add(self.radioBox,0,wx.ALIGN_CENTRE_VERTICAL|wx.ALL,8)

        self.SetSizer(sizer)

# main control panel
class MainControlPanel(wx.Panel):
    def __init__(self,parent):
        super(MainControlPanel,self).__init__(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainControl = MainControl(self)
        self.selectedTarget = SelectedTargetPanel(self)
        # add a reference to selected target
        self.mainControl.targetControl.selectedTargetImg = self.selectedTarget
        self.trackingPanel = TrackingPanel(self)
        self.targetOption = TargetOptionPanel(self)
        sizer.Add(self.mainControl,0,wx.EXPAND,0)
        # tracking options
        self.trackingOption = TrackingOption(self)
        sizer.AddSpacer(10)
        # add selectedTarget panel to the main sizer
        sizer.Add(self.selectedTarget,0,wx.TOP|wx.EXPAND,8)
        sizer.AddSpacer(8)
        sizer.Add(self.trackingOption,0,wx.TOP|wx.EXPAND,8)
        sizer.AddStretchSpacer()
        sizer.Add(self.trackingPanel,0,wx.ALIGN_RIGHT|wx.ALL,8)
        sizer.Add(self.targetOption,0,wx.ALIGN_RIGHT|wx.ALL,8)
        
        # add sizer
        self.SetSizer(sizer)


# this panel contain various UI for controlling the position target
class MainControl(wx.Panel):
    def __init__(self,parent):
        super(MainControl,self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(self,label="Set Target Position")
        # label atop of targetControl 
        sizer.Add(self.label,0,wx.LEFT|wx.TOP,8)
        self.targetControl = TargetControl(self)
        # target control to the sizer
        sizer.Add(self.targetControl,0,wx.ALL,8)
        self.label = wx.StaticText(self,label="")
        sizer.Add(self.label,0,wx.ALL,8)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        """x,y,w,h = self.GetRect()
        x,y,_,_ = self.label.GetRect()
        # pencil and brush color
        dc.SetBrush(wx.Brush("rgb(51,51,51)"))
        dc.SetPen(wx.Pen("rgb(220,220,220)"))
        # draw rectangle
        print("I cant see anymore",x,y,w,h)
        dc.DrawRectangle(x-8,y-120-32-16,w+200,h-8)
        """
        x,y,w,h = self.targetControl.GetRect()
        # set pencil color
        dc.SetPen(wx.Pen("rgb(180,180,180)",1))
        dc.SetBrush(wx.Brush("rgb(31,31,31)"))
        dc.DrawRectangle(x,y-6,120,120)
        # refresh the panel
        self.Refresh()

# Target Control UI, for setting and moving frame
class TargetControl(wx.Panel):
    def __init__(self,parent,targetRectSize=None,selectedTargetImg=None):
        super(TargetControl,self).__init__(parent)
        self.serverAddr = ("",8000)
        self.selectedTargetImg = selectedTargetImg
        self.targetRectSize = targetRectSize
        # rectangle position for target selection
        self.rect_position = [0,0,False]
        self.WIDTH = self.HEIGHT = 80
        # buttons for moving around target
        self.btLeft = wx.BitmapButton(self,bitmap=wx.Bitmap("Components/assets/left.png"),size=(32,32),id=1)
        self.btRight = wx.BitmapButton(self,bitmap=wx.Bitmap("Components/assets/right.png"),size=(32,32),id=2)
        self.btTop = wx.BitmapButton(self,bitmap=wx.Bitmap("Components/assets/up.png"),size=(32,32),id=3)
        self.btBottom = wx.BitmapButton(self,name="choice",bitmap=wx.Bitmap("Components/assets/down.png"),size=(32,32),id=4)
        self.plus = wx.Bitmap("Components/assets/plus.png")
        self.minus = wx.Bitmap("Components/assets/minus.png")   
        self.setTarget = wx.BitmapButton(self,bitmap=self.plus,size=(32,32),id=5)
        self.SetInitialSize((120,120))
        # main layout sizer
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.btTop,0,wx.ALL|wx.ALIGN_TOP|wx.ALIGN_CENTRE_HORIZONTAL,2)
        # hsizer for vertical alignment
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        # add items horixontally 
        hsizer.Add(self.btLeft,0,wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_LEFT,2)
        hsizer.Add(self.setTarget,0,wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTRE_HORIZONTAL,2)
        hsizer.Add(self.btRight,0,wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_RIGHT,2)
        vsizer.Add(hsizer,0,wx.ALIGN_CENTRE_HORIZONTAL,0)
        vsizer.Add(self.btBottom,0,wx.ALIGN_CENTRE_HORIZONTAL|wx.TOP,4)
        # vsizer as the main sizer
        self.SetSizer(vsizer)
        # flag to indicate target locking
        self.targetLock = False
        # bind to all the button
        self.Bind(wx.EVT_BUTTON,self.OnClick)

        
    def OnClick(self,event):
        target = event.EventObject

        # calculate the rect size
        if target.Id == 1:
            self.rect_position[0] -= 2
        elif target.Id == 2:
            self.rect_position[0] += 2

        elif target.Id == 3:
            self.rect_position[1] -= 2 

        elif target.Id == 4:
            self.rect_position[1] += 2

        elif target.Id == 5:
            playSound("Components/assets/info.wav")
            self.targetLock = not self.targetLock
            if self.targetLock:
                target.SetBitmap(self.minus)
                self.rect_position[2] = True
                thread.start_new_thread(self.fetchTarget,())
            else:
                target.SetBitmap(self.plus)
                self.rect_position[2] = False
            self.setTarget.Refresh()            
            # do the rest

    def fetchTarget(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect(self.serverAddr)
        # choices of target rect size
        choices = list(CamPanel.RECT_CHOICES.keys())
        # current selection of the current target selection rect
        current_size = CamPanel.RECT_CHOICES.get(choices[self.targetRectSize.GetSelection()])
        x,y,targetSelected = self.rect_position
        reply = pickle.dumps([Server1.SERVER_TARGET_REQUEST,current_size,x,y,targetSelected])   
        client.sendto(reply,self.serverAddr)
        reply,addr = client.recvfrom(1024*2)
        print(reply,"from the server")
        # send server camera query

        while True:
            # current selection of the current target selection rect
            current_size = CamPanel.RECT_CHOICES.get(choices[self.targetRectSize.GetSelection()])
            x,y,targetSelected = self.rect_position
            print(x,y,"XY Direction")
            frame = b""
            reply = Server1.SERVER_TARGET_REQUEST
            msg = pickle.dumps([reply,current_size,x,y,targetSelected])
            print(msg,"reply from main process")
            client.sendto(msg,self.serverAddr)

            while True and  reply != Server1.SERVER_STOP:
                time.sleep(0.0001)
                data,addr = client.recvfrom(1024*6)
                if data == Server1.START_OF_FRAME:
                    print("server start frame")
                    frame = b""
                    # childEnd.send(CamPanel.NO_DATA_MSG)
                
                elif data == Server1.END_OF_FRAME:
                    print("server end frame")
                    try:
                        frame = zlib.decompress(frame)
                        frame = pickle.loads(frame)
                        print(frame,"from END FRAME SPECIAL FRAME")
                        width,height,_ = frame.shape
                        self.imageObject = wx.Image(height,width,frame)
                        self.imageObject.Rescale(100,100)
                        self.bitmap = wx.Bitmap(self.imageObject)
                        self.selectedTargetImg.imageCtrl.SetBitmap(self.bitmap)
                        print(self.imageObject)
                        frame = b""
                        break
                    except Exception as e:
                        frame = b""
                        print("exception happened",e)
                        break
                if data  != Server1.START_OF_FRAME and data != Server1.SUCCESS:
                    frame += data
                
            break
        
    
class MainWindowPanel(wx.Panel):
    def __init__(self,parent):
        # get our superclass ready
        super(MainWindowPanel,self).__init__(parent)
        # add layout sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add group sizer
        self.groupsizer = GroupSizer(self,wx.HORIZONTAL,"")
        self.bottomSection = MainControlPanel(self)
        # add item to the top sizer
        self.targetScreen = TargetScreen(self)
        self.topRight = CameraTools(self)
        # pass the reference of rectsize to the targetControl
        self.bottomSection.mainControl.targetControl.targetRectSize = self.topRight.targetRect
        # add camera component panel
        self.cameraComponent = CamPanel(self,self.topRight.targetRect,self.bottomSection.mainControl.targetControl)
        # pass play button so that it can be used in message
        self.cameraComponent.playPaused = self.topRight.play
        self.cameraComponent.frameType = self.topRight.frameType.options
        # add reference of CamPanel to cameraTools
        self.topRight.enhancer.imagePanel.camPanel = self.cameraComponent
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
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        x,y,w,h = self.bottomSection.GetRect()
        dc.SetPen(wx.Pen("rgb(180,180,180)"))
        dc.SetBrush(wx.Brush("rgb(51,51,51)"))
        dc.DrawRectangle(x,y,w,h)
        self.Refresh()

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