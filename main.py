import TKinterModernThemes as TKMT
import tkinter as tk
import requests
from json_tools import make_treeview, update_treeview, SearchManager
from code_gen import generate_request_segment, CodeGenInfo
from functools import partial
import json

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("API_Explorer")

        #VARIABLES
        #GLOBAL INFO
        self.reqDB = {}
        self.codeGenInfo = None
        self.searchManager: SearchManager = SearchManager([])

        #ACTIVE REQUEST
        with open('savedata.json') as f:
            savedata = json.load(f)

        self.baseURL = tk.StringVar(value=savedata['baseurl'])
        self.reqURL = tk.StringVar(value=savedata['requrl'])
        self.headers = savedata['headers']
        self.params = savedata['params']

        #Response Search Feature
        self.keyStringVar = tk.StringVar()
        self.keyVar = tk.StringVar()
        self.valueVar = tk.StringVar()

        #PARAM CONFIG
        self.pNameVar = tk.StringVar()
        self.pValueVar = tk.StringVar()

        #HEADER CONFIG
        self.hNameVar = tk.StringVar()
        self.hValueVar = tk.StringVar()

        #Request Config Frame
        rqConfigFrame = self.addLabelFrame("Request Config")
        rqConfigFrame.Text("Base URL:")
        rqConfigFrame.Entry(self.baseURL, validate='none', col=1, widgetkwargs={"width": 50})
        rqConfigFrame.Text("Request URL:")
        rqConfigFrame.Entry(self.reqURL, validate='none', col=1)
        rqConfigFrame.AccentButton("Make Request", self.makeRequest, colspan=2)

        notebook = self.addFrame("NotebookFrame", padx=10, pady=10).Notebook("")

        #Parameter Tab
        paramTab = notebook.addTab("Request Parameters")
        paramTab.Text("Parameter Name", col=0)
        paramTab.Entry(self.pNameVar, col=1)
        paramTab.Button("Add/Update Parameter", command=self.add_param, col=2)
        paramTab.Text("Parameter Value", col=0)
        paramTab.Entry(self.pValueVar, col=1)
        paramTab.Button("Delete Selected Parameter", command=self.del_param, col=2)
        self.paramTreeview = paramTab.Treeview(["Name", "Value"], [60,100], 5, {}, "subentry", colspan=3)

        #Header Tab
        headerTab = notebook.addTab("Request Headers")
        headerTab.Text("Header Name", col=0)
        headerTab.Entry(self.hNameVar, col=1)
        headerTab.Button("Add/Update Header", command=self.add_header, col=2)
        headerTab.Text("Header Value", col=0)
        headerTab.Entry(self.hValueVar, col=1)
        headerTab.Button("Delete Selected Header", command=self.del_header, col=2)
        self.headerTreeview = headerTab.Treeview(["Name", "Value"], [60, 100], 5, {}, "subentry", colspan=3)

        #Code Gen Tab
        codeGenTab = notebook.addTab("Code Generator")
        codeGenTab.Label("Generated Code: ", sticky='w')
        self.codeGenBox = tk.Text(codeGenTab.master, height=15, width=70)
        self.codeGenBox.grid()

        self.nextCol()
        respFrame = self.addLabelFrame("Response", rowspan=2)
        self.treeviewwidget = respFrame.Treeview(['key', 'value', 'type'], [400, 120, 80], 15, {},
                                                      'subentry', openkey='open', colspan=3)

        self.treeviewwidget.bind('<KeyRelease>', self.update)
        self.treeviewwidget.bind('<ButtonRelease>', self.update)
        self.paramTreeview.bind('<KeyRelease>', self.param_update)
        self.paramTreeview.bind('<ButtonRelease>', self.param_update)
        self.headerTreeview.bind('<KeyRelease>', self.header_update)
        self.headerTreeview.bind('<ButtonRelease>', self.header_update)

        respFrame.Text("Selected Key:")
        respFrame.Entry(self.keyVar, col=1, widgetkwargs={'width': 40})
        respFrame.Button("Search / Next", self.search_by_key, col=2)
        respFrame.Text("Selected Value:")
        respFrame.Entry(self.valueVar, col = 1, widgetkwargs={'width': 40})
        respFrame.Button("Search / Next", self.search_by_value, col=2)
        respFrame.Text("Key String: ")
        respFrame.Entry(self.keyStringVar, col = 1, widgetkwargs={'width': 60}, colspan=2)

        self.menu = tk.Menu(self.master)
        respFrame.MenuButton(self.menu, "Load previous request:", colspan=3)

        for key, value in self.headers.items():
            self.headerTreeview.insert('', 'end', text=key, values=[value])

        for key, value in self.params.items():
            self.paramTreeview.insert('', 'end', text=key, values=[value])

        #self.debugPrint()
        self.root.state("zoomed")
        self.run()


    def makeRequest(self):
        baseurl = self.baseURL.get()
        requrl = self.reqURL.get()
        if len(requrl) > 0 and requrl[0] == '/':
            requrl = requrl[1:]

        if len(self.params) > 0:
            for key, value in self.params.items():
                if "?" in requrl:
                    requrl += "&" + key + "=" + value
                else:
                    requrl += "?" + key + "=" + value

        r = requests.get(baseurl + '/' + requrl, headers=self.headers)
        data = r.json()
        self.searchManager = update_treeview(self.treeviewwidget, make_treeview(data))
        self.codeGenInfo = CodeGenInfo(self.baseURL.get(), self.reqURL.get(),
                                       self.params.copy(), self.headers.copy(), data)
        self.reqDB[requrl] = self.codeGenInfo

        self.menu.add_command(label=requrl, command=partial(self.load_prev_req, requrl))
        self.valueVar.set("")
        self.keyStringVar.set("")
        self.keyVar.set("")
        self.update_codegen()

    def load_prev_req(self, name):
        self.codeGenInfo = self.reqDB[name]
        self.searchManager = update_treeview(self.treeviewwidget, make_treeview(self.codeGenInfo.data))
        self.update_codegen()

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
        parent = self.treeviewwidget.selection()
        if len(parent) > 0:
            parent = parent[0]
            valueText = self.treeviewwidget.item(parent)['values'][0]
            self.valueVar.set(valueText)
            self.keyVar.set(self.treeviewwidget.item(parent)['text'])
            self.codeGenInfo.searchValue = valueText
            self.keyStringVar.set(parent)
            self.codeGenInfo.searchKey = parent
            self.searchManager.set_index_by_keystring(parent)
            self.update_codegen()

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

    def update_codegen(self):
        if self.codeGenInfo is not None:
            retval = generate_request_segment(self.codeGenInfo)
            self.codeGenBox.delete(1.0, tk.END)
            self.codeGenBox.insert(1.0, retval)

    def search_by_key(self):
        item = self.searchManager.get_next_key_match(self.keyVar.get())
        if item is not None:
            self.keyVar.set(item.key)
            self.valueVar.set(item.value)
            self.keyStringVar.set(item.keystring)
            self.codeGenInfo.searchKey = item.keystring
            self.codeGenInfo.searchValue = item.value
            self.treeviewwidget.selection_set([item.keystring])
            self.update_codegen()

    def search_by_value(self):
        item = self.searchManager.get_next_value_match(self.valueVar.get())
        if item is not None:
            self.keyVar.set(item.key)
            self.valueVar.set(item.value)
            self.keyStringVar.set(item.keystring)
            self.codeGenInfo.searchKey = item.keystring
            self.codeGenInfo.searchValue = item.value
            self.treeviewwidget.selection_set([item.keystring])
            self.update_codegen()

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