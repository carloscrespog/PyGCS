#!/usr/bin/python
# Cool stuff
import wxversion
print wxversion.getInstalled()
import wx
import socket
import yaml
import wx.lib.scrolledpanel as scrolled
from random import randrange

print wx.__version__
class MyFrame(wx.Frame):
    
    def __init__(self, parent, id, title):
        LRM_IP='192.168.1.200'
        LRM_TC_PORT=7131
        LRM_TM_PORT=7133
        self.BUFFER_SIZE = 1024

        wx.Frame.__init__(self, parent, id, title, pos=(0,0), size=wx.DisplaySize())

        splitter = wx.SplitterWindow(self, -1)
        self.commandsPanel = wx.Panel(splitter, -1)
       
        self.commandsPanel.SetBackgroundColour(wx.LIGHT_GREY)
        self.consolePanel = Terminal(splitter)
        # consolePanel.SetBackgroundColour(wx.WHITE)
        splitter.SplitHorizontally(self.commandsPanel, self.consolePanel,wx.DisplaySize()[1]*4/5)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.config = yaml.load(open("config.yaml"))
        self.visualMatrix = []
        self.populateGUI()

        # lostButton=wx.Button(self.commandsPanel,1,'LOST', (-1,-1))
        # lomaButton=wx.Button(self.commandsPanel,2,'LOMA', (-1,-1))

        # self.Bind(wx.EVT_BUTTON,self.sendCommand,id=1)
        # self.Bind(wx.EVT_BUTTON,self.sendCommand,id=2)  

        
        # self.vbox.Add(lostButton,0,wx.ALIGN_LEFT|wx.ALL,5)
        # self.vbox.Add(lomaButton,0,wx.ALIGN_LEFT|wx.ALL,5)
        self.commandsPanel.SetSizer(self.vbox)

        self.upLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.downLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.upLink.connect((LRM_IP,LRM_TC_PORT))
        self.downLink.connect((LRM_IP,LRM_TM_PORT))

        self.Centre()

        
        # print self.config


    def sendCommand (self,event):
        print event.GetId()
        command="1 CSPFSTC TR PFS ROSO 1\n"
        self.upLink.send(command)
        data=self.downLink.recv(self.BUFFER_SIZE)
        self.consolePanel.append(command+" -> "+data)

    def populateGUI(self):
        # print config
        for i in self.config["telecommand"]:
            hbox=wx.BoxSizer(wx.HORIZONTAL)
            button=wx.Button(self.commandsPanel,i["id"],i["code"],(-1,-1))
            hbox.Add(button,-1,wx.ALL,0)
            paramList=i["params"]
            if (paramList==0):
                pass
            else:
                for idx,param in enumerate(paramList.split(',')):
                    paramText=wx.StaticText(self.commandsPanel,-1,param,(100,20))
                    ranges=i["ranges"].split(',')
                    minLim=float(ranges[idx*2])
                    maxLim=float(ranges[(idx*2)+1])
                    midValue=((maxLim+minLim)/2.)
                    print param,minLim,midValue,maxLim
                    if maxLim>1:
                        paramSlider=wx.Slider(self.commandsPanel,-1,value=midValue,minValue=minLim,maxValue=maxLim,size=(200,20),style=wx.SL_HORIZONTAL|wx.SL_MIN_MAX_LABELS,name=param)
                    # It's a decimal!:
                    else:
                        # paramSlider.SetTickFreq((minLim-maxLim)/10.)
                        pass
                    # 
                    hbox.Add(paramText)
                    hbox.Add(paramSlider)


            self.vbox.Add(hbox,1,wx.ALL,0)


class Terminal(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.first=True
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        text  = "Welcome to pyGCS"

        self.terminalBox = wx.TextCtrl(self,0,text,style=wx.TE_MULTILINE)
        self.terminalBox.SetBackgroundColour((randrange(255),randrange(255),randrange(255)))
        # self.SetBackgroundColour((255,255,0))
        hbox.Add(self.terminalBox,1,wx.EXPAND|wx.TOP,5)
        self.SetSizer(hbox)
        # vbox.Add(hbox,1,wx.EXPAND,0)
        # self.SetSizer(vbox)
        self.SetAutoLayout(1) 
        self.SetupScrolling()

    def append(self,text):
        if(self.first):
            self.terminalBox.Clear()
            self.first=False
        self.terminalBox.AppendText(text)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'pyGCS')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()