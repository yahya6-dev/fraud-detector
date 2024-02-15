
import wx

class GroupSizer(wx.StaticBox):
	def __init__(self,parent,orient,label):
		super(GroupSizer,self).__init__(parent,label=label)
		# our actual Sizer
		self._sizer = wx.StaticBoxSizer(self,orient)
		self.ForegroundColour = "rgb(255,255,255)"
	def AddItem(self,item,proportion,flag=wx.ALL,border=0):
		"""
			Add item giving closed to same signature to the sizer item
		"""
		self._sizer.Add(item,proportion,flag,border)

	@property
	def sizer(self):
		return self._sizer
