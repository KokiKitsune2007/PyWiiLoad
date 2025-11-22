import sys
import os
import wx
from wx import App, Frame, Panel, BoxSizer, Button, TextCtrl, StaticText, EVT_BUTTON, ID_ANY

class WiiloadForm(wx.Frame):
    def __init__(self, parent, title):
        # Calling the parent 
        super(WiiloadForm, self).__init__(parent, title=title, size=(400, 300))
        self.panel = wx.Panel(self)
        self.st = wx.StaticText(self.panel, label="Target IP Address:")

if __name__ == "__main__":
    app = wx.App()
    frame = WiiloadForm(None, "PyWiiLoad GUI")
    frame.Show()
    app.MainLoop()