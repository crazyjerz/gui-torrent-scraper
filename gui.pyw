from tkinter import *
from tkinter import ttk
import tksheet
import requester
import qbit
config = qbit.loadJSON("gui") #loads the configs for this part of the app (for now only config['debug'])
def floatCommaConv(input: str) -> float: #converts a string into float regardless of the decimal separator used 
    if "," not in input: #if it's a standard float-convertable string (with a .), calls float()
        return float(input)
    else: #if it contains a comma, converts it to float without the float() function
        inputList = input.split(',')
        return float(inputList[0]) + (float(inputList[1]) / 10**len(inputList[1]))
def kize(input: int) -> str: #turns large numbers (>9999) into shortened forms with letters to signify thousands etc.
    if input < 10000:
        return str(input)
    else:
        letterDict = {'T': 1000000000000, 'B': 1000000000, 'M': 1000000, 'k': 1000}
        for l in letterDict:
            if input > letterDict[l]:
                outputList = [str(input/letterDict[l]), l]
                break
        if len(outputList[0]) > 3:
            outputList[0] = outputList[0][:3]
            if outputList[0][-1] == '.':
                outputList[0] = outputList[0][:2]
        return outputList[0]+outputList[1]
def delcomma(input: str) -> str: #deletes comma from scraped file sizes between 1000 and 1024
    if input[1] == ',': # that contain a comma as the thousands separator
        input = input[0] + input[2:]
    return input
class App(Tk): #class inheriting from the root tkinter.Tk class
    def __init__(self): #creation of the window
        super().__init__()
        self.title("Torrenting Tool Alpha") #basic settings
        self.geometry('450x400+120+120')
        self.resizable(False, False)
        self.iconbitmap(default="assets\\logo.ico")

        #creating the frame and buttons to set the desired resolution of results
        self.resVar = {"1080p": BooleanVar(), "720p": BooleanVar(), "304p": BooleanVar(), "2160p": BooleanVar()}
        self.resFrame = self.styledFrame("Resolution")

        self.resBL = []
        self.resTL = []
        self.resBL.append(ttk.Checkbutton(self.resFrame, variable=self.resVar['1080p'], onvalue=True, offvalue=False))
        self.resBL.append(ttk.Checkbutton(self.resFrame, variable=self.resVar['720p'], onvalue=True, offvalue=False))
        self.resBL.append(ttk.Checkbutton(self.resFrame, variable=self.resVar['304p'], onvalue=True, offvalue=False))
        self.resBL.append(ttk.Checkbutton(self.resFrame, variable=self.resVar['2160p'], onvalue=True, offvalue=False))
        self.resTL.append(self.styledLabel(self.resFrame, "1080p"))
        self.resTL.append(self.styledLabel(self.resFrame, "720p"))
        self.resTL.append(self.styledLabel(self.resFrame, "XviD"))
        self.resTL.append(self.styledLabel(self.resFrame, "2160p (4K)"))
        self.resSpace = ttk.Label(self.resFrame, text="") 

        #creating the frame and buttons to set the desired encoding of results
        self.encodeVar = {"H264": BooleanVar(), "H265": BooleanVar(), "XviD": BooleanVar(), "AV1": BooleanVar(), "REMUX": BooleanVar(), "HSBS": BooleanVar()}
        self.encodeFrame = self.styledFrame("Encoding")

        self.encodeBL = []
        self.encodeTL = []
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["H264"], onvalue=True, offvalue=False))
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["H265"], onvalue=True, offvalue=False))
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["XviD"], onvalue=True, offvalue=False))
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["AV1"], onvalue=True, offvalue=False))
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["REMUX"], onvalue=True, offvalue=False))
        self.encodeBL.append(ttk.Checkbutton(self.encodeFrame, variable=self.encodeVar["HSBS"], onvalue=True, offvalue=False))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "H264"))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "H265"))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "XviD"))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "AV1"))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "REMUX"))
        self.encodeTL.append(self.styledLabel(self.encodeFrame, "3D"))

        #creating the frame and entry fields to set the desired size of results
        self.sizeMin = StringVar()
        self.sizeMax = StringVar()
        self.sizeUnit = StringVar()
        self.sizeFrame = self.styledFrame("Size")

        self.sizeMinEntry = ttk.Entry(self.sizeFrame, textvariable=self.sizeMin, width=5)
        self.sizeMaxEntry = ttk.Entry(self.sizeFrame, textvariable=self.sizeMax, width=5)
        self.sizeMyslnik = ttk.Label(self.sizeFrame, text="—")
        self.sizeSpace = ttk.Label(self.sizeFrame, text="")
        self.sizeUnitEntry = ttk.Combobox(self.sizeFrame, textvariable=self.sizeUnit, values=("B", "kB", "MB", "GB", "TB"), width=4, state="readonly") #units
        self.sizeUnitEntry.set("GB") #default unit is GB

        #creating the frame and buttons to set the desired category of results
        self.categoryVar = StringVar()
        self.categoryFrame = self.styledFrame("Category", 'ne')

        self.categoryBL = []
        self.categoryTL = []
        self.categoryBL.append(ttk.Radiobutton(self.categoryFrame, variable=self.categoryVar, value="Movies"))
        self.categoryBL.append(ttk.Radiobutton(self.categoryFrame, variable=self.categoryVar, value="TV"))
        self.categoryTL.append(self.styledLabel(self.categoryFrame, "Movies"))
        self.categoryTL.append(self.styledLabel(self.categoryFrame, "Shows"))

        #creating the frame and buttons to search for results
        self.searchVar = StringVar()
        self.searchFrame = self.styledFrame("Search", 'ne')
        self.searchEntry = ttk.Entry(self.searchFrame, textvariable=self.searchVar, width=20)
        self.searchButton = ttk.Button(self.searchFrame, text="Search", command=lambda: self.torrents()) #weird syntax required by tkinter
        self.searchSpace = ttk.Label(self.searchFrame, text="")

        #grid column and row configuration to keep the widgets from expanding
        self.grid_columnconfigure(5, weight = 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(4, weight=3)
        self.grid_rowconfigure(5, weight=255)
        #grid - positioning of widgets on the window area
        self.resFrame.grid(column=0, row=0, columnspan=6, rowspan=2, sticky="nw")
        self.resBL[0].grid(column=0, row=0, columnspan=1)
        self.resBL[1].grid(column=0, row=1, columnspan=1)
        self.resBL[2].grid(column=2, row=0, columnspan=1)
        self.resBL[3].grid(column=2, row=1, columnspan=1)
        self.resTL[0].grid(sticky=W, column=1, row=0, columnspan=1)
        self.resTL[1].grid(sticky=W, column=1, row=1, columnspan=1)
        self.resTL[2].grid(sticky=W, column=3, row=0, columnspan=1)
        self.resTL[3].grid(sticky=W, column=3, row=1, columnspan=1)
        self.resSpace.grid(column=4, row=1, columnspan=2, rowspan=2)

        self.encodeFrame.grid(column=0, row=2, columnspan=6, rowspan=2, sticky="nw")
        self.encodeBL[0].grid(column=0, row=2, columnspan=1)
        self.encodeBL[1].grid(column=0, row=3, columnspan=1)
        self.encodeBL[2].grid(column=2, row=2, columnspan=1)
        self.encodeBL[3].grid(column=2, row=3, columnspan=1)
        self.encodeBL[4].grid(column=4, row=2, columnspan=1)
        self.encodeBL[5].grid(column=4, row=3, columnspan=1)
        self.encodeTL[0].grid(sticky=W, column=1, row=2, columnspan=1)
        self.encodeTL[1].grid(sticky=W, column=1, row=3, columnspan=1)
        self.encodeTL[2].grid(sticky=W, column=3, row=2, columnspan=1)
        self.encodeTL[3].grid(sticky=W, column=3, row=3, columnspan=1)
        self.encodeTL[4].grid(sticky=W, column=5, row=2, columnspan=1)
        self.encodeTL[5].grid(sticky=W, column=5, row=3, columnspan=1)

        self.sizeFrame.grid(column=0, row=4, columnspan=5, rowspan=1, sticky="nw")
        self.sizeMinEntry.grid(column=0, row=4)
        self.sizeMyslnik.grid(column=1, row=4)
        self.sizeMaxEntry.grid(column=2, row=4)
        self.sizeSpace.grid(column=3, row=4, padx=5)
        self.sizeUnitEntry.grid(column=4, row=4)

        self.categoryFrame.grid(column=6, row=0, columnspan=4, sticky="ne")
        self.categoryBL[0].grid(column=6, row=0)
        self.categoryBL[1].grid(column=8, row=0)
        self.categoryTL[0].grid(column=7, row=0)
        self.categoryTL[1].grid(column=9, row=0)

        self.searchFrame.grid(column=6, row=1, columnspan=4, rowspan=3, sticky="ne")
        self.searchEntry.grid(column=6, row=1, columnspan=4)
        self.searchSpace.grid(column=6, row=2, columnspan=4, pady=1)
        self.searchButton.grid(column=7, row=3, columnspan=2)

    def styledFrame(self, label: str, labelpos = 'nw') -> ttk.Labelframe: #function used to reduce repeating code in creating ttk.Labelframes
        return ttk.Labelframe(self, text=label, padding="5 5 5 5", labelanchor=labelpos)
    def styledLabel(self, framesroot: Frame, display: str) -> ttk.Label: #as above
        return ttk.Label(framesroot, text=display, anchor='w', justify=LEFT)
    def openPopup(self, display = "An unknown error occurred.", title = "Error!"):
        pop = Toplevel(self)
        pop.geometry(f"200x80+{self.winfo_x()+125}+{self.winfo_y()+160}")
        pop.title(title)
        pop.wm_transient(self)
        ttk.Label(pop, text=display).place(x=100, y=20, anchor="center")
    def download(self, input: list[requester.Torrent]): #function to download the torrent chosen from results
        self.selected = self.choiceSheet.get_currently_selected(get_coords = False, return_nones_if_not = False)
        if len(self.selected) > 1 and self.selected[0] == "row": #checks if there is a selected torrent
            try: #if the qbittorrent app doesn't respond, opens an error popup (important: the exception is only raised after some time)
                if not qbit.torrentAdd(input[self.selected[1]].getMagnetLink()): 
                    self.openPopup("Torrent cannot be added.")
                    return None #if the app is configured correctly, but it doesn't add the torrent, opens an error popup
            except: #see 4 lines before
                self.openPopup("Torrent cannot be added. Check your login credentials in config.")
                return None
            self.openPopup("Torrent added successfully.", "Success!") #if none of the errors are detected, opens a popup
        else: #if no selected torrent, opens an error popup
            self.openPopup("No torrent selected! Try again.") 
    def torrents(self): #function to search for torrents and show the results
        def sizeBool(compared: float) -> bool: #checks if a scraped torrent's size is between the limits set by the user
            checkDict = {'B': 1.0, 'kB': 1024.0, 'MB': 1048576.0, 'GB': 1073741824.0, 'TB': 1099511627776.0}
            minval = self.sizeMin.get()
            maxval = self.sizeMax.get()
            unit = self.sizeUnit.get()
            if minval: #checks if there is a min value set by the user
                minval = floatCommaConv(minval) * checkDict[unit]
                minvalCond = (compared >= minval)
            else: #if not, the condition will be always true
                minvalCond = True
            if maxval: #as in minval
                maxval = floatCommaConv(maxval) * checkDict[unit]
                maxvalCond = (compared <= maxval)
            else:
                maxvalCond = True
            return (minvalCond and maxvalCond) #if both the minval and maxval conditions are true, returns true
        def internalGet(page = 1) -> list[requester.Torrent]: #scrapes the torrents and checks for errors using requester.getTorrents()
            try:
                pafy = requester.getTorrents(requester.getLink(self.searchVar.get(), self.categoryVar.get(), page))
            except TypeError:
                self.openPopup("No search input! Try again.")
                self.progressBar['value'] = 6.0
                return False
            except ValueError:
                self.openPopup("No category! Try again.")
                self.progressBar['value'] = 6.0
                return False
            except Exception:
                self.openPopup()
                self.progressBar['value'] = 6.0
                return False
            else:
                self.progressBar['value'] += 1.0
                return pafy

        self.progressFrame = ttk.Frame(self) #progressbar is not working for now, work in progress
        self.progressBar = ttk.Progressbar(self.progressFrame, maximum=6.0, length=120)
        self.progressBar['value'] = 0.0
        self.progressFrame.grid(column=6, row=4, columnspan=4, rowspan=1, sticky="ne")
        self.progressBar.grid(column=6, row=4, columnspan=4, rowspan=1)

        resolutions = {i for i in self.resVar if self.resVar[i].get()} #gets a set of resolutions that were checked by the user
        encodes = {j for j in self.encodeVar if self.encodeVar[j].get()} #as above
        if not resolutions: #if no resolutions are checked, ignores it and allows all resolutions
            resolutions = set(self.resVar.keys())
        if not encodes: #as above
            encodes = set(self.encodeVar.keys())
        if (self.sizeMin.get() and self.sizeMax.get() and not self.sizeUnit.get()): #if no size unit due to a program bug, opens an error popup
            self.openPopup("Wrong size input! Try again.")
            return None
        foundTorrents = 0
        page = 0
        outputList = []
        while True: #loop that scrapes 1337x pages one by one to find torrents fulfilling criteria set by the user
            page += 1 
            if page == 1: #if it's the 1st page, gets all results
                torrentList = internalGet(page)
            else: #on 1337x for pages 2+ only the second half of results is new, the first 20 are repeated from the previous page
                torrentList = internalGet(page)[20:]
            if not torrentList: #if there are no more torrents (either no results at all or no more pages)
                if page > 1 and not foundTorrents: #if no torrents at all, stops the function with an error popup
                    self.openPopup("No results for this query.")
                    return None
                elif page > 1 and foundTorrents: #if less than 5 torrents were found before running out of them, stop the loop
                    self.progressBar['value'] = 6.0
                    break
            for t in torrentList: #loop that runs through all found torrents to find those fulfilling set criteria
                sizeCond = sizeBool(t.getByteSize()) #checks if the size condition is true for the torrent's size
                if config['debug']: #debug
                    print(t.findResolution(), t.findEncoding(), t.seed, t.rawsize, t.getByteSize(), sizeCond)
                    print(resolutions, encodes)
                if t.findResolution() in resolutions and t.findEncoding() in encodes and sizeCond:
                    outputList.append(t)
                    foundTorrents += 1
                    self.progressBar['value'] += 1.0
                    if config['debug']: print(f"Torrents found: {foundTorrents}")
                if foundTorrents >= 5: #maximum number: 5 torrents
                    break
            if foundTorrents >= 5:
                break
        
        #display of found torrents in a tksheet.Sheet
        sheetDisplayList = [[qbit.getShortname(i.name), kize(i.seed), kize(i.leech), delcomma(i.rawsize)] for i in outputList]
        self.choiceFrame = self.styledFrame("Found torrents:", 'n')
        self.choiceSheet = tksheet.Sheet(self.choiceFrame, font=("Arial", 9, "normal"))
        self.choiceSheet.set_sheet_data(sheetDisplayList)
        self.choiceSheet.headers(["Name", "Seed", "Leech", "Size"])
        self.choiceSheet.set_column_widths([235, 40, 40, 70])
        self.choiceFrame.grid(column=0, row=5, columnspan=10, rowspan=5, pady=(0, 20))
        self.choiceSheet.grid(column=0, row=5, sticky = "nwe", rowspan=5)
        self.choiceSheet.enable_bindings("single_select","row_select")
        
        #the download button
        self.downloadFrame = ttk.Frame(self)
        self.downloadButton = ttk.Button(self.downloadFrame, text="Download", command=lambda: self.download(outputList))
        self.downloadFrame.grid(column=0, row=10, columnspan=10, sticky="n", pady=(0, 20))
        self.downloadButton.grid(column=4, row=10, columnspan=2)

if __name__ == '__main__': #runs the app
    app = App()
    app.mainloop()

