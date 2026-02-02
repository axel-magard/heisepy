# heisepy
Command Line Tool to create a flat html file of all comments for a given article on heise.de

## Synopsis
```
Usage: 
python3 heise.py URL_TO_HEISE_DISCUSSION_THREAD


URL_TO_HEISE_DISCUSSION_THREAD needs to be a URL to a discussion thread on heise.de, e.g.:
https://www.heise.de/forum/heise-online/Kommentare/Windows-XP-Nachbau-ReactOS-ist-30/forum-576575/comment/
```
## Description

The script will create a html file heise.html with all the comments made in the discussion thread of an article, see screenshot below.

![Screenshot of html file](https://i.imgur.com/sUDbIsE.png)


## Installation

Clone this git repo on your computer, then
install missing Python modules:

```
pip3 install bs4
pip3 install pandas
pip3 install IPython
```

