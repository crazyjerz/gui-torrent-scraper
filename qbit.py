import qbittorrentapi
import json
from time import sleep
def loadJSON(part: str, filename = "config.json") -> dict:
    return json.loads(open(filename, "rt").read())[part]
config = loadJSON("qbit_login")
ip = config['ip']+":"+str(config['port']) # sets the IP (fstrings can't be used with string keys in them)
try:
    qbt_client = qbittorrentapi.Client(ip, username=config['username'], password=config['password']) # logs into qbittorrent
except ConnectionRefusedError:
    raise Exception('Login error. Your login data are incorrect. Use config.json to correct them.')
def torrentAdd(magnet: str): # adds the scraped torrent to qbittorrent
    ret = qbt_client.torrents_add(urls=magnet, tags="scraped")
    if ret == "Ok.": # checks if the API responds with "Ok." (successful operation)
        return True # used to detect errors in gui.App.download()
    else:
        return False
class Info: 
    def __init__(self, name: str, size: str, al: int):
        self.name = name
        self.size = size
        self.amountLeft = al
        self.dlspeeds = []
    def addDlspeed(self, speed:int): # adds the torrent download speed (in bytes) to the list of speeds
        self.dlspeeds.append(speed)
    def avgDlspeed(self) -> int: # calculates the average of 5 measurements
        return int(sum(self.dlspeeds)/len(self.dlspeeds))
    def timeLeft(self) -> int: # calculates the time in seconds left to download the torrent
        return int(self.amountLeft/self.avgDlspeed())
    def percentDownloaded(self) -> float: # calculate percent of torrent that has been downloaded
        return (1-(self.amountLeft/self.size))*100
    @staticmethod
    def parseTime(time: int) -> str: # returns readable time (in days, hours, minutes, seconds) from seconds calculated by Info.timeLeft()
        output = ""
        if time > 86400:
            d = time // 86400
            output += f"{d}d "
        if time > 3600:
            h = time % 86400 // 3600
            output += f"{h}h "
        if time > 60:
            m = time % 3600 // 60
            output += f"{m}m "
        s = time % 60
        output += f"{s}s"
        return output 
    @staticmethod
    def parseSpeed(speed: int) -> str: # same as above, except with download speed
        if speed > 1048576:
            return f"{round(speed/1048576, 2)} MB/s"
        elif speed > 1024:
            return f"{round(speed/1024, 2)} kB/s"
        else:
            return f"{speed} bytes/s"
    def printInfo(self):
        if self.avgDlspeed() == 0 and self.amountLeft > 0: # checks if torrent is stalled (not downloading and not finished)
            print(f"{getShortname(self.name)} {self.percentDownloaded()}%: Torrent stalled.")   
        elif self.amountLeft > 0 and self.size > 0: # if speed > 0, the torrent is loaded (size > 0) and it's not finished, prints all info
            print(f"{getShortname(self.name)} {self.percentDownloaded()}%: download speed: {Info.parseSpeed(self.avgDlspeed())}, time left: {Info.parseTime(self.timeLeft())}")
        elif self.size == 0: # if size == 0, the magnetlink is being processed
            print(f"{getShortname(self.name)}: qbittorrent has not yet retrieved magnetlink data.")
        else: # if none of those special cases are true and the torrent does not download, it's ready
            print(f"{getShortname(self.name)}: Torrent downloaded.")
def getShortname(text: str, length = 40) -> str: # generates the short name used for printing results - no detailed info (all tech info is found by findResolution() and findEncoding() and shortened actual title in case of overly long titles, see next line)
    v = text.split('[')[0].strip()
    if len(v) < length:
        return v
    else:
        return v[:length]+"..."
def checkScraped(): 
    scraperList = [] # list of all torrents to be printed
    for i in qbt_client.torrents_info(): # searches for all torrents with the tag "scraper" to add them to the list of objects
        if config['display_only_scraped_torrents']: # checks if the json config display_only_scraped_torrents is True
            if i['tags'] == "scraped": # then it checks only torrents with tag "scraped" assigned by torrentAdd()
                scraperList.append(Info(i['name'], i['size'], i['amount_left']))
        else: # if not, it checks all torrents
            scraperList.append(Info(i['name'], i['size'], i['amount_left']))
    for k in range(5): # checks the speed for all scraper torrents 5 times to get an average
        for i in qbt_client.torrents_info(): # gets the list of all torrents to get new dlspeeds each time
            for l in scraperList: # looks through torrents in scraperList
                if i['name'] == l.name: # if it finds a torrent with a matching name, scrapes the dlspeed and adds it to the list of dlspeeds
                    dlspeed = int(i['dlspeed'])
                    l.addDlspeed(dlspeed)
        if k != 4:
            sleep(1.15) # optimal time to check torrents
    return scraperList
def main():
    for i in checkScraped():
        i.printInfo()
if __name__ == "__main__": # if the file is ran directly (by running "py qbit.py" in cmd), it runs checkScraped()
    main() # if not, it omits this part