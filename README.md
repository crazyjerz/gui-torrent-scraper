# gui-torrent-scraper
Python GUI script made using tkinter that searches through the torrent tracker 1337x, returns results that fulfill criteria set by the user and lets the user download the torrent using QBittorrent.
## Setup
To run the script, Python must be installed. The script was tested on Python 3.9.5, but it should work with any newer Python3 version.
Some dependencies are required to run the script:
* httpx - a faster HTTP requests module
* tksheet - small module that adds a table widget to tkinter
* qbittorrent-api - QBittorent API wrapper
The dependencies can be installed on Windows by running the `install.bat` file.

Remember to **enable WebUI** in your QBittorrent settings, and if you are not using the default login credentials, change them in the `config.json` file.
## How to run
Run the `py gui.pyw` command or just click on the gui.pyw file.
## Other information
The script only supports QBittorrent at the moment, more torrenting apps can be added in the future.
The files `requester.py` and `qbit.py` contain code used by the main file, but can also be ran separately - `requester` letting you search through torrents in the terminal, `qbit` showing you the current state of your torrents downloaded using the app.
## Disclaimer
The creator of this script does not endorse using it to obtain pirated material.
