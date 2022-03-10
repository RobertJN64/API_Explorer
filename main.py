import TKinterModernThemes as TKMT
import tkinter as tk
import requests
from json_tools import make_treeview, udpate_treeview
from functools import partial
import json

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("API_Explorer")

        with open('savedata.json') as f:
            savedata = json.load(f)

        self.reqDB = {}

        self.baseURL = tk.StringVar(value=savedata['baseurl'])
        self.reqURL = tk.StringVar(value=savedata['requrl'])

        self.headers = savedata['headers']
        self.params = savedata['params']

        #Request Config Frame
        self.rqConfigFrame = self.addLabelFrame("Request Config")
        self.rqConfigFrame.Text("Base URL:")
        self.rqConfigFrame.Entry(self.baseURL, validate='none', col=1, widgetkwargs={"width": 50})
        self.rqConfigFrame.Text("Request URL:")
        self.rqConfigFrame.Entry(self.reqURL, validate='none', col=1)
        self.rqConfigFrame.AccentButton("Make Request", self.makeRequest, colspan=2)

        self.notebookFrame = self.addFrame("NotebookFrame", padx=10, pady=10)
        self.notebook = self.notebookFrame.Notebook("")

        #Parameter Frame
        self.pNameVar = tk.StringVar()
        self.pValueVar = tk.StringVar()
        self.paramTab = self.notebook.addTab("Request Parameters")

        self.paramTab.Text("Parameter Name", col=0)
        self.paramTab.Entry(self.pNameVar, col=1)
        self.paramTab.Button("Add/Update Parameter", command=self.add_param, col=2)

        self.paramTab.Text("Parameter Value", col=0)
        self.paramTab.Entry(self.pValueVar, col=1)
        self.paramTab.Button("Delete Selected Parameter", command=self.del_param, col=2)

        self.paramTreeview = self.paramTab.Treeview(["Name", "Value"], [60,100], 5, {}, "subentry", colspan=3)

        #Header Frame
        self.hNameVar = tk.StringVar()
        self.hValueVar = tk.StringVar()
        self.headerTab = self.notebook.addTab("Request Headers")

        self.headerTab.Text("Header Name", col=0)
        self.headerTab.Entry(self.hNameVar, col=1)
        self.headerTab.Button("Add/Update Header", command=self.add_header, col=2)

        self.headerTab.Text("Header Value", col=0)
        self.headerTab.Entry(self.hValueVar, col=1)
        self.headerTab.Button("Delete Selected Header", command=self.del_header, col=2)

        self.headerTreeview = self.headerTab.Treeview(["Name", "Value"], [60, 100], 5, {}, "subentry", colspan=3)


        self.codeGen = self.notebook.addTab("Code Generator")
        self.codeGen.Text("CODE GEN")

        self.nextCol()
        self.respFrame = self.addLabelFrame("Response", rowspan=2)
        self.treeviewwidget = self.respFrame.Treeview(['key', 'value', 'type'], [400, 120, 80], 15, {},
                                                      'subentry', openkey='open', colspan=2)

        self.treeviewwidget.bind('<KeyRelease>', self.update)
        self.treeviewwidget.bind('<ButtonRelease>', self.update)
        self.paramTreeview.bind('<KeyRelease>', self.param_update)
        self.paramTreeview.bind('<ButtonRelease>', self.param_update)
        self.headerTreeview.bind('<KeyRelease>', self.header_update)
        self.headerTreeview.bind('<ButtonRelease>', self.header_update)

        self.keyVar = tk.StringVar()
        self.valueVar = tk.StringVar()
        self.respFrame.Text("Selected Key:")
        self.respFrame.Entry(self.keyVar, col=1, widgetkwargs={'width': 60})
        self.respFrame.Text("Selected Value:")
        self.respFrame.Entry(self.valueVar, col = 1, widgetkwargs={'width': 60})

        self.menu = tk.Menu(self.master)
        self.respFrame.MenuButton(self.menu, "Load previous request:", colspan=2)

        for key, value in self.headers.items():
            self.headerTreeview.insert('', 'end', text=key, values=[value])

        for key, value in self.params.items():
            self.paramTreeview.insert('', 'end', text=key, values=[value])

        self.debugPrint()
        self.root.state("zoomed")
        self.run()


    def makeRequest(self):
        baseurl = self.baseURL.get()
        requrl = self.reqURL.get()
        if len(requrl) > 0 and requrl[0] == '/':
            requrl = requrl[1:]

        r = requests.get(baseurl + '/' + requrl, headers=self.headers)
        data = r.json()
        udpate_treeview(self.treeviewwidget, make_treeview(data))
        self.reqDB[requrl] = data

        self.menu.add_command(label=requrl, command=partial(self.load_prev_req, requrl))

    def load_prev_req(self, name):
        udpate_treeview(self.treeviewwidget, make_treeview(self.reqDB[name]))

    def add_param(self):
        if self.pNameVar.get() in self.params:
            children = self.paramTreeview.get_children()
            for child in children:
                if self.paramTreeview.item(child)['text'] == self.pNameVar.get():
                    self.paramTreeview.delete(child)

        self.params[self.pNameVar.get()] = self.pValueVar.get()
        self.paramTreeview.insert('', 'end', text=self.pNameVar.get(), values=[self.pValueVar.get()])
        self.pNameVar.set("")
        self.pValueVar.set("")

    def del_param(self):
        sel = self.paramTreeview.selection()
        if len(sel) > 0:
            self.params.pop(self.paramTreeview.item(sel[0])['text'])
            self.paramTreeview.delete(sel[0])

    def add_header(self):
        if self.hNameVar.get() in self.headers:
            children = self.headerTreeview.get_children()
            for child in children:
                if self.headerTreeview.item(child)['text'] == self.hNameVar.get():
                    self.headerTreeview.delete(child)

        self.headers[self.hNameVar.get()] = self.hValueVar.get()
        self.headerTreeview.insert('', 'end', text=self.hNameVar.get(), values=[self.hValueVar.get()])
        self.hNameVar.set("")
        self.hValueVar.set("")

    def del_header(self):
        sel = self.headerTreeview.selection()
        if len(sel) > 0:
            self.headers.pop(self.headerTreeview.item(sel[0])['text'])
            self.headerTreeview.delete(sel[0])


    def update(self, _=None):
        sel = self.treeviewwidget.selection()
        if len(sel) > 0:
            self.keyVar.set(self.treeviewwidget.item(sel[0])['text'])
            self.valueVar.set(self.treeviewwidget.item(sel[0])['values'][0])

    def param_update(self, _=None):
        if self.pNameVar.get() == "" and self.pValueVar.get() == "":
            sel = self.paramTreeview.selection()
            if len(sel) > 0:
                self.pNameVar.set(self.paramTreeview.item(sel[0])['text'])
                self.pValueVar.set(self.paramTreeview.item(sel[0])['values'][0])

    def header_update(self, _=None):
        if self.hNameVar.get() == "" and self.hValueVar.get() == "":
            sel = self.headerTreeview.selection()
            if len(sel) > 0:
                self.hNameVar.set(self.headerTreeview.item(sel[0])['text'])
                self.hValueVar.set(self.headerTreeview.item(sel[0])['values'][0])

    def handleExit(self):
        savedata = {
            'baseurl': self.baseURL.get(),
            'requrl': self.reqURL.get(),
            'params': self.params,
            'headers': self.headers
        }
        with open('savedata.json', 'w+') as f:
            json.dump(savedata, f, indent=4)
        TKMT.ThemedTKinterFrame.handleExit(self)

if __name__ == '__main__':
    app = App()