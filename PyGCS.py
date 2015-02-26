#!/usr/bin/python
# Cool stuff
import wxversion
print wxversion.getInstalled()
import wx
import socket
import yaml
import wx.lib.scrolledpanel as scrolled
import wx.lib.agw.floatspin as FS
from random import randrange
import numpy as np
import colorsys
class MyFrame(wx.Frame):
    
    def __init__(self, parent, id, title):
        self.parent=parent

        self.flagOnlyRTCC=True

        self.LRM_IP='192.168.1.200'
        self.LRM_TC_PORT=7131
        self.LRM_TM_PORT=7133
        self.LRM_TLM_PORT=7135
        self.LRM_TLM_TM_PORT=7136

        self.LRM_RTCC_IP='192.168.1.201'
        self.LRM_RTCC_TC_PORT=3333
        self.LRM_RTCC_ACK_PORT=3334
        self.LRM_RTCC_TLM_PORT=3335

        WINDOW_RATIO=4/5.
        self.BUFFER_SIZE = 1024
        self.commandCount=1
        self.TLM_OFFSET=20
        self.RTCC_OFFSET=30

        wx.Frame.__init__(self, parent, id, title, pos=(0,0), size=wx.DisplaySize())

        splitter = wx.SplitterWindow(self, -1)
        self.commandsPanel = wx.Panel(splitter, -1)
       
        self.commandsPanel.SetBackgroundColour(wx.LIGHT_GREY)
        self.consolePanel = Terminal(splitter)

        splitter.SplitHorizontally(self.commandsPanel, self.consolePanel,wx.DisplaySize()[1]*WINDOW_RATIO)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.config = yaml.load(open("config.yaml"))
        self.visualMatrix = []
        self.populateGUI(self.config["telecommand"])
        self.populateGUI(self.config["telemanipulation"])
        self.populateGUI(self.config["rtcc"])

        self.commandsPanel.SetSizer(self.vbox)
        self.connect()
        
        self.Centre()


    def connect(self):
        if not self.flagOnlyRTCC:
            self.upLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.downLink=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.upLinkTLM=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.downLinkTLM=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            
            self.upLink.connect((self.LRM_IP,self.LRM_TC_PORT))
            self.downLink.connect((self.LRM_IP,self.LRM_TM_PORT))
            self.upLinkTLM.connect((self.LRM_IP,self.LRM_TLM_PORT))
            self.downLinkTLM.connect((self.LRM_IP,self.LRM_TLM_TM_PORT))
        self.upLinkRTCC=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.upLinkRTCC.connect((self.LRM_RTCC_IP,self.LRM_RTCC_TC_PORT))
    
        
    def sendCommand (self,command):
        commandLine=str(self.commandCount)+' CSPFSTC TR PFS '+command+'\n'
        self.commandCount+=1
        print commandLine
        self.upLink.send(commandLine)
        data=self.downLink.recv(self.BUFFER_SIZE)
        print data
        self.consolePanel.append(command+" -> "+data)

    def sendCommandTLM (self,command):
        commandLine=str(self.commandCount)+' CSVFSTC TR VFS TLM_LRM_TC '+command+'\n'
        self.commandCount+=1
        print commandLine
        self.upLinkTLM.send(commandLine)
        # data=self.downLink.recv(self.BUFFER_SIZE)
        # print data
        # self.consolePanel.append(command+" -> "+data)

    def sendCommandRTCC (self,command):
        commandLine=str(self.commandCount)+' RTPFSTC TR PFS '+command+'\n'
        self.commandCount+=1
        print commandLine
        self.upLinkRTCC.send(commandLine)
        

    def populateGUI(self,commands):
        # print config
        for i in commands:
            hbox=wx.BoxSizer(wx.HORIZONTAL)
            button=wx.Button(self.commandsPanel,i["id"],i["code"],(-1,-1))
            hbox.Add(button,-1,wx.ALL,5)
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
                    paramFloatSpin=FS.FloatSpin(self.commandsPanel,id=100*i["id"]+idx,value=midValue,min_val=minLim,max_val=maxLim,agwStyle=FS.FS_LEFT,name=param)
                    if maxLim>1:
                        paramFloatSpin.SetFormat("%f")
                        paramFloatSpin.SetDigits(2)
                    # It's a decimal!:
                    else:
                        paramFloatSpin.SetFormat("%f")
                        paramFloatSpin.SetDigits(2)
                        paramFloatSpin.SetIncrement(0.01)
                    hbox.Add(paramText,-1,wx.ALL,5)
                    hbox.Add(paramFloatSpin,-1,wx.ALL,5)
            #TLM condition
            if (i["id"]>=self.RTCC_OFFSET): #isRTCC
                self.Bind(wx.EVT_BUTTON,self.buttonPressedRTCC,button)
                
            elif (i["id"]>=self.TLM_OFFSET): #isTLM
                self.Bind(wx.EVT_BUTTON,self.buttonPressedTM,button)

            else:
                self.Bind(wx.EVT_BUTTON,self.buttonPressed,button)
            self.vbox.Add(hbox,1,wx.ALL,5)

    def buttonPressed(self,event):
        commandLine=''
        commandLine+=self.config["telecommand"][event.GetId()]["code"]
        commandLine+=' '
        params=self.config["telecommand"][event.GetId()]["params"]
        if params==0:
            pass
        else:
            for idx,param in enumerate(params.split(',')):
                commandLine+= str(self.FindWindowById(100*event.GetId()+idx).GetValue())
                commandLine+=' '
        if not self.flagOnlyRTCC:
            self.sendCommand(commandLine)

    def buttonPressedTM(self,event):
        commandLine=''
        commandLine+=self.config["telemanipulation"][event.GetId()-self.TLM_OFFSET]["code"]
        commandLine+=' '
        params=self.config["telemanipulation"][event.GetId()-self.TLM_OFFSET]["params"]
        if params==0:
            pass
        else:
            for idx,param in enumerate(params.split(',')):
                commandLine+= str(self.FindWindowById(100*event.GetId()+idx).GetValue())
                commandLine+=' '
        if not self.flagOnlyRTCC:
            self.sendCommandTLM(commandLine)

    def buttonPressedRTCC(self,event):
        commandLine=''
        commandLine+=self.config["rtcc"][event.GetId()-self.RTCC_OFFSET]["code"]
        commandLine+=' '
        params=self.config["rtcc"][event.GetId()-self.RTCC_OFFSET]["params"]
        if params==0:
            pass
        else:
            for idx,param in enumerate(params.split(',')):
                commandLine+= str(self.FindWindowById(100*event.GetId()+idx).GetValue())
                commandLine+=' '

        self.sendCommandRTCC(commandLine)


class Terminal(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.first=True
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        text  = "Welcome to pyGCS"

        self.terminalBox = wx.TextCtrl(self,0,text,style=wx.TE_MULTILINE)

        colour=(randrange(255),randrange(255),randrange(255))
        colourHSV=colorsys.rgb_to_hsv(colour[0]/255.,colour[1]/255.,colour[2]/255.)
        
        inverseColourHSV= tuple((1-colourHSV[0],colourHSV[1],colourHSV[2]))        
        inverseColour= colorsys.hsv_to_rgb(inverseColourHSV[0],inverseColourHSV[1],inverseColourHSV[2])
        inverseColour=(inverseColour[0]*255,inverseColour[1]*255,inverseColour[2]*255)

        self.terminalBox.SetBackgroundColour(colour)
        self.terminalBox.SetForegroundColour(inverseColour)

        hbox.Add(self.terminalBox,1,wx.EXPAND|wx.TOP,5)
        self.SetSizer(hbox)

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