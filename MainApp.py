## This is the main entry level of fraud and face tracker software
## every other component is attached here to reduce redundancy.
## it start our servers each in a new process and record PID in case user need to shut them down
## load wx modules and necessary modules
import wx

class MyApp(wx.App):
        def OnInit(self):
            """ this hold our main Component """
            return True

if __name__=="__main__":
    # instantiate our app
    myapp = MyApp(False)
    # run forever
    myapp.MainLoop()