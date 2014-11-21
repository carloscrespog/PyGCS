#!/usr/bin/python
# Cool stuff
import wx
import socket
import yaml

class MyFrame(wx.Frame):
    
    def __init__(self, parent, id, title):
        LRM_IP='192.168.1.200'
        LRM_TC_PORT=7131
        LRM_TM_PORT=7133
        self.BUFFER_SIZE = 1024

        wx.Frame.__init__(self, parent, id, title, pos=(0,0), size=wx.DisplaySize())

        splitter = wx.SplitterWindow(self, -1)
        commandsPanel = wx.Panel(splitter, -1)
       
        commandsPanel.SetBackgroundColour(wx.LIGHT_GREY)
        consolePanel = wx.Panel(splitter, -1)
        consolePanel.SetBackgroundColour(wx.WHITE)
        splitter.SplitHorizontally(commandsPanel, consolePanel,wx.DisplaySize()[1]*2/3)
        
        lostButton=wx.Button(commandsPanel,1,'LOST', (-1,-1))
        lomaButton=wx.Button(commandsPanel,2,'LOMA', (-1,-1))

        self.Bind(wx.EVT_BUTTON,self.sendCommand,id=1)
        self.Bind(wx.EVT_BUTTON,self.sendCommand,id=2)  

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(lostButton,0,wx.ALIGN_LEFT|wx.ALL,5)
        self.vbox.Add(lomaButton,0,wx.ALIGN_LEFT|wx.ALL,5)
        commandsPanel.SetSizer(self.vbox)

        self.upLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.downLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.upLink.connect((LRM_IP,LRM_TC_PORT))
        self.downLink.connect((LRM_IP,LRM_TM_PORT))

        self.Centre()

        self.config = yaml.load(open("config.yaml"))
        print self.config


    def sendCommand (self,event):
        print event.GetId()
        self.upLink.send("1 CSPFSTC TR PFS ROSO 1\n")
        data=self.downLink.recv(self.BUFFER_SIZE)
        print data      

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'pyGCS')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()