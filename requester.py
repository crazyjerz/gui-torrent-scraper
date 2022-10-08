import re
import json
import qbit
import httpx
# from emoji import demojize
config = qbit.loadJSON("requester")
client = httpx.Client()
class Torrent:
    def __init__(self, index: int, name: str, seed: int, leech: int, link: str, rawsize: str):
        self.index = index
        self.name = name
        self.seed = seed
        self.leech = leech
        self.link = link
        self.rawsize = rawsize
    def findResolution(self): # finds resolution in a full name using regex
        specialCases = {"xvid":"304p", "3d": "3D"}
        self.foundResolution = False # variable for printDName() to know whether the resolution has been found
        regex = re.search("[0-9]+p", self.name) # regex for resolution - number of any length followed by "p" is valid
        if regex:
            self.foundResolution = True # lets printDName() know it found the resolution
            self.resolution = regex.group() # loads the regex-matching text into self.resolution attribute
            return self.resolution
        else:
            for i in specialCases:
                if i in self.name.lower():
                    self.resolution = specialCases[i]
                    self.foundResolution = True
                    return self.resolution
    def findEncoding(self): # searches for encoding
        change = {"remux":"REMUX", "265":"H265", "hevc": "H265", "av1":"AV1", "xvid":"XviD", "hsbs": "HSBS", "3d": "HSBS"}
        for i in change: # checks if any text in full name matches the encodings on the list
            if i in self.name.lower():
                self.encoding = change[i]
                break
            self.encoding = "H264" # if it hasn't found an encoding, set to h264 (most common, if not given, it's most likely 264)
        return self.encoding
    def getDName(self) -> str: # generates dname (detailed name) - shortname with details (resolution, encoding, seeders, size)
        res = ""
        self.findResolution() # four methods to get the required info to print dname 
        self.findEncoding()
        if self.foundResolution: # checks if resolution has been found - prevents useless []s in dname
            res = f" [{self.resolution}]"
        self.dname = f"{self.index}. {qbit.getShortname(self.name)}{res} [{self.encoding}] | {self.seed} | {self.leech} | {self.getPSize()}"
        return self.dname
    def getPSize(self): # gets the size as displayed on site (PSize stands for Printed Size)
        sizeli = self.rawsize.split(' ') # splits the found size into the actual value and unit (MB/GB)
        if sizeli[1] == "MB": # if it's in MB
            output = f"{round(float(sizeli[0])/1024, 3)} GB (~{sizeli[0]} MB)"
        elif sizeli[1] == "GB":
            output = f"{sizeli[0]} GB (~{int(round(float(sizeli[0])*1024, 0))} MB)"
        else: # if it's in something else (B, kB, TB) it just prints the value found w/o formatting
            output = self.rawsize
        return output
    def getByteSize(self) -> float:
        sizeli = self.rawsize.lower().split(' ')
        try:
            if sizeli[1][1] == 'i':
                sizeli[1] = sizeli[1][0] + sizeli[1][2:] # deleting "i" from potential "GiB"/"MiB"/etc.
        except IndexError:
            pass
        try:
            if sizeli[0][1] == ',':
                sizeli[0] = sizeli[0][0] + sizeli[0][2:]
        except IndexError:
            pass
        unitDict = {'b': 1, 'kb': 1024, 'mb': 1048576, 'gb': 1073741824, 'tb': 1099511627776}
        return float(sizeli[0])*int(unitDict[sizeli[1]])
    def getMagnetLink(self):
        rawhtml = client.get(self.link).text
        return re.search('href="magnet.*?"', rawhtml).group()[6:-1]
configFile = open("config.json", "rt").read()
config = json.loads(configFile)['requester']
resultsPage = config['results_on_page']
def getLink(searchterm: str, category: str, page = 1) -> str:
    if searchterm == "":
        raise TypeError('No search term.') # ValueError would be better but gui.py needs to catch the two exceptions separately
    if category in {"Movies", "TV", "Games", "Music", "Apps", "Documentaries", "Anime", "Other", "XXX"}:
        return f"https://1337x.to/category-search/{searchterm}/{category}/{page}/"
    else:
        raise ValueError('Wrong category.')
def getTorrents(link: str) -> list[Torrent]:
    req = client.get(link).content.decode('utf-8') # gets rid of weird gibberish that would appear instead of Polish text
    rawTorrentNameList = re.findall('name">.*?</td>', req)
    rawTorrentSeedList = re.findall('seeds">[0-9]+</td>', req)
    rawTorrentLeechList = re.findall('leeches">[0-9]+</td>', req)
    rawTorrentSizeList = re.findall('[0-9,]+[\s.,]?[0-9]*\s[kmgtiKMGTI]{1,2}[bB]{1}[^p]', req)
    rawTorrentSizeList = [i[:-1] for i in rawTorrentSizeList]
    torrentListPrivate = []
    for i in range(len(rawTorrentNameList)):
        linkAttr = "https://1337x.to" + re.search('<a href="/torrent/.*?/">', rawTorrentNameList[i]).group()[9:-2].strip()
        nameAttr = re.search('/">.*</a>', rawTorrentNameList[i]).group()[3:-4]
        seedAttr = int(re.search('[0-9]+', rawTorrentSeedList[i]).group())
        leechAttr = int(re.search('[0-9]+', rawTorrentLeechList[i]).group())
        sizeAttr = rawTorrentSizeList[i]
        torrentListPrivate.append(Torrent(i+1, nameAttr, seedAttr, leechAttr, linkAttr, sizeAttr))
    return torrentListPrivate
def main():
    while True:
        inp = input("Search term: ").strip().lower()
        torrentList = getTorrents(getLink(inp, config['category']))
        if torrentList and all([i.seed for i in torrentList]): # checks if there are torrents and the torrents found have any seeders
            break # if no torrents or all have 0 seeders, break and ask for working search term again
        print("No downloadable torrents found. Try again.")
    iterations = 0
    while True:
        startval = iterations*resultsPage
        endval = startval + resultsPage
        hmm = 'Y'
        if iterations >= 1 and endval <= 40:
            hmm = input("Do you want to see the next page? (Y/N) ") # next "page" (resultsPage of new results)
        elif endval > 40:
            hmm = 'N'
        if hmm == 'Y':
            for i in torrentList[iterations*resultsPage:(iterations+1)*resultsPage]:
                print(i.getDName())
            iterations += 1
        else:
            break
    while True:
        hmm = input("Do you want to download a torrent? If yes, input torrent index. To exit, input anything else. ")
        if hmm.isnumeric(): # checks if it's a number, if it's not a number it leaves the loop and program ends
            hmm = int(hmm)
            if hmm > 0 and hmm <= len(torrentList): # runs if number is a valid index
                print(torrentList[hmm-1].getMagnetLink())
                magnet = torrentList[hmm-1].getMagnetLink()
                qbit.torrentAdd(magnet)
        else:
            qbit.main()
            break
if __name__ == "__main__":
    main()