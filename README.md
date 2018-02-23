# third-party-website-accessed-from-browser

[HTTP Archive](https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/HAR/Overview.html) file can be saved from [Chrome browser](https://support.zendesk.com/hc/en-us/articles/204410413-Generating-a-HAR-file-for-troubleshooting). Save this file as **user.har** to **./data/** subfolder and execute the script. *This is Work In Progress* 

###### Python libs used
```
import pandas as pd
import json
import re

from haralyzer import HarParser
from urllib.request import urlopen
from bs4 import BeautifulSoup
```
### Processed files in ./output folder

###### Data output files
```
user.har_domainCalls.csv  
    # Times a domain was accessed
user.har_domainKeyValue.txt 
    # The key value passed as data with the calls
user.har_domainTime.csv 
    # @ this moment this is work in progress
user.har_domainTitles.txt 
    # Subdomains processed into 'Title/Name of Website', 'Domain' ,'Primary/Main domain' , 'subdomain part'
user.har_userRequestPages.txt 
    # User requested pages as appeared in the browser address bar
```
###### Data files for D3js Viz
```
user.har_bar.tsv 
    # input for bar viz
user.har_bubble.csv 
    # input for bubble & pie viz
```
![alt text](https://github.com/gsnaveen/third-party-website-accessed-from-browser/blob/master/bar.png)

![alt text](https://github.com/gsnaveen/third-party-website-accessed-from-browser/blob/master/bubble.png)
