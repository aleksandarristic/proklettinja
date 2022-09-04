## Description:

A tool to download embedded media files from iframes on a page. The media files are (rather naively) identified by ```source``` tag within an iframe. This is a very dumb yet very effective tool for the usecase.

## Usage:

* Edit ```config/config.json``` to your needs according to ```config/example.json```
* Run ```python3 downloader.py``` to download the files

### requirements:
* python3
  * BeautifulSoup4 package
  * requests package
* aria2c
