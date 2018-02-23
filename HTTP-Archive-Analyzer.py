
# coding: utf-8

# In[6]:


import pandas as pd
import json

from haralyzer import HarParser
from urllib.request import urlopen , unquote

from bs4 import BeautifulSoup
import re

#1Sec = 1000Milisec
inputFile = 'user.har'
inPath = './data/'
outPathFile = './output/'+inputFile

with open(inPath + inputFile , 'r',encoding="utf8") as f:
    har_parser = HarParser(json.loads(f.read()))


userRequestPages = [] ### User Requested Pages ###
entries = [] ### CREATE A TIMELINE OF ALL THE ENTRIES ###
for page in har_parser.pages:
    userRequestPages.append((page.url, page.image_load_time,page.page_size, page.image_size))
    #userRequestPages.append((page.url,0,0,0))
    for entry in page.entries:
        entries.append(entry)

#User Requested pages
userRequestPagesDF = pd.DataFrame(userRequestPages,columns=['url','loadtime','page_size','image_size'])
userRequestPagesDF.to_csv(outPathFile+'_userRequestPages.tsv',sep='\t',header=True,index=False)

timeline = har_parser.create_asset_timeline(entries)
webRequestURL = []
for key, value in timeline.items():
    for data in value:
        webRequestURL.append((data['request']['url'],data['time'])) # ,data['request']['queryString']

domain = set()
domainURL = []
domainDqpKeyValue = []
df = pd.DataFrame(webRequestURL,columns=['url','time'])
df = df.groupby('url')['time'].sum().reset_index()


def cleanDqp(dqp):
    return re.sub('=+','=',re.sub('&+','&',dqp)).strip()

def keyValueProcessing(domainDqpKeyValue,dqp,fkey=''):
    if fkey != '': fkey = fkey + "_"
    dqp = cleanDqp(dqp)
    dqpsplit = dqp.split('&')
    for keyValue in dqpsplit:

        keyValue = keyValue.strip()
        keyValueList = keyValue.split('=')

        try:
            if len(keyValueList) == 2:
                key, value = keyValueList[0], unquote(unquote(keyValueList[1]))
                domainDqpKeyValue.append((domainPart,baseurl,fkey+key,value))
                if re.search('&',value): keyValueProcessing(domainDqpKeyValue,value,key)
        except:
            pass

        
for index,row in df[['url','time']].drop_duplicates().iterrows():
    url = row['url']
    domainPart = url.split('/')[2]
    if re.search('\?',url):
        urlSplit = url.split('?')
        baseurl,dqp = urlSplit[0],urlSplit[1]
        if re.search('&',dqp):
            keyValueProcessing(domainDqpKeyValue,dqp)
            url = baseurl
        elif(re.search('=',dqp)):
                keyValueList = dqp.split('=')
                try:
                    key, value = keyValueList[0], unquote(unquote(keyValueList[1])) #.decode('utf8')
                    domainDqpKeyValue.append((domainPart,baseurl,key,value))
                    if re.search('&',value): keyValueProcessing(domainDqpKeyValue,value)
                    url = baseurl
                except:
                    pass
            
    domain.add( domainPart)
    domainURL.append((domainPart,row['url'],row['time']))
    
#Turning DomainURL data to a dataframe
domainURLDF = pd.DataFrame.from_records(domainURL, index=None, exclude=None, columns = ['domain','url','time'])
#grouping by domain
#domainURLDF.groupby(['domain'])['time'].sum()


# In[2]:


# Getting the Title of the website
endDomains = ['com','net','org','co']

def cleanTitle(title):
    if re.match('error',title): title = ''
    return re.sub('\s+',' ',re.sub('\n','',title)).strip()

websiteTitle = []
for website in domain:
    title = website
    mainDomain = subDomain = ''
    domainPartList = website.split('.')
    if domainPartList[-1] in endDomains:
        mainDomain = domainPartList[-2]+'.'+ domainPartList[-1]
        subDomain = '.'.join(domainPartList[:-2])
    #Get Title of the main website
    try:
        html = urlopen('http://'+mainDomain, timeout = 3)
        soup = BeautifulSoup(html,'html.parser')
        title = cleanTitle(soup.title.string)
    except:
        #If main website errors out then try with subdomain
        try:
            html = urlopen('http://'+website, timeout = 3)
            soup = BeautifulSoup(html,'html.parser')
            title = cleanTitle(soup.title.string)
        except:
            pass
    if title == None or title == '': title = website
    websiteTitle.append((title,website,mainDomain,subDomain))
    
websiteTitleDF = pd.DataFrame.from_records(websiteTitle, index=None, exclude=None, columns = ['title','domain','maindomain','subdomain'])
# websiteTitleDF.to_csv(outPathFile+'_domainTitles.tsv',sep='\t',header=True,index=False)

def get_stats(group):
    return {'min': group.min(), 'max': group.max(), 'Calls': group.count(), 'mean': group.mean(), 'Time': group.sum()}

domainCallsorig = domainURLDF['time'].groupby(domainURLDF['domain']).apply(get_stats).unstack().sort_values('Time',ascending=False).reset_index()
domainCallsorig = domainCallsorig.merge(websiteTitleDF,how='inner' ,left_on =['domain'],right_on=['domain'])[['domain', 'Calls', 'Time', 'max', 'mean', 'min', 'title', 'maindomain', 'subdomain']]
domainCallsorig[['title','domain','maindomain', 'subdomain','Calls', 'Time', 'max', 'mean', 'min']].to_csv(outPathFile+'_summary.tsv',sep='\t',header=True,index=False)
#Saving the domain ,baseURL, Key , Value data
pd.DataFrame(domainDqpKeyValue,columns=['domain','url','key','value']).to_csv(outPathFile+'_domainKeyValue.tsv',sep='\t',header=True,index=False)


# In[4]:


#D3js charting data
def label_domains(row):
    label = row['domain']
    if row['Calls'] == 1: label = 'OneCallDomain'
    if row['Calls'] == 2: label = 'TwoCallDomain'
    return label

domainCallsorig['repDomain'] = domainCallsorig.apply(label_domains, axis=1)
domainCallsDataforViz = domainCallsorig.groupby(domainCallsorig['repDomain']).sum().reset_index().rename(index=str,columns={"repDomain":"id","Calls":"value"})[['id','value']]
domainCallsDataforViz['id'] = domainCallsDataforViz['id'].str.replace('.','*')
domainCallsDataforViz.to_csv(outPathFile+'_bubble.csv',sep=',',header=True,index=False)
domainCallsDataforViz.columns = ['letter','frequency']
domainCallsDataforViz.to_csv(outPathFile+'_bar.tsv',sep='\t',header=True,index=False)

