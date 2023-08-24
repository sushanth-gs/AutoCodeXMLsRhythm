from os import listdir,mkdir 
from shutil import copy
from os.path import exists
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from sys import argv
#copies selected logs from all file links on stp dashboard 
#needs install lxml parser and beautifulsoup4 (pip)
#call from python venv command line with python getSelectedLogsStpDashboard.py <DashboardURL> <savepath>
#DashboardURL and savepath must be in quotes 
#switch allows to selectively copy service logs (s), application logs (a), debug logs (d) or service, application, debug and workflow (A) (note case sensitve)
#default behaviour (no switch) gives combined.log summary.txt and workflow logs

def getfilelinks(req):
    """ 
    Accepts webpage request and grabs all fileLinks
    inputs:HTMLrequest
    returns:list of 'file' links
    """
    htmlPage = urlopen(req)
    soup = BeautifulSoup(htmlPage, "lxml")
    allLinks=list(soup.findAll('a')) #finds all links from html page, filtered to only file links below
    allLinks=[allLinks[i].get('href') for i in range(len(allLinks))]
    fileLinks=[]
    for i in range(len(allLinks)):
        if(allLinks[i]):
            if('file' in allLinks[i]):
                fileLinks.append(allLinks[i][8:]) #removes file://// from start of link (8:)
    return(fileLinks)

stpwebURL=argv[1]
#req = Request("http://stpweb.btl.ms.philips.com/cgi-bin/TriageDashboard.plx?Comment=%_ADS100764%&Since=20230519")
req = Request(stpwebURL)
fileLinks=getfilelinks(req) #links to directory of logs for each hit

linkList=['_'.join(fileLinks[i].split('\\')[-1].split('_')[-3:]) for i in range(len(fileLinks))]

#save_path=r'C:\Users\320159870\Downloads\RAPressure\\'
savePath=argv[2]
if(len(argv)==4):
    switch=argv[3]
    



def copyLogList(fileLink,logPath,logList,savePath,link):
    """ 
    Copies all log files in log path 
    fileLink is directory of the hit
    logPath is path to corresponding logs
    logList is list of log files (xml)
    savePath+link is directory to save 
    """
    logName=logPath.split('\\')[1]
    print(f'Copying {len(logList)} {logName} logs')
    for j in range(len(logList)):
        copy(fileLink+fr'{logPath}\{logList[j]}',savePath+link)


def defaultCopy(fileLink,savePath,link):
    """ 
    default copy copies combined log, summary.txt and workflow logs
    fileLink is directory of the hit
    savePath+link is directory to save 
    """
    copy(fileLink+r'\\Combined.log',savePath+link) #grab combined log
    copy(fileLink+r'\\Summary.txt',savePath+link) #grab Summary.txt
    workflowLogList=listdir(fileLink+r'\\Product\\Workflow') #copy workflow log files
    copyLogList(fileLink,r'\\Product\\Workflow',workflowLogList,savePath,link)


def copydata(fileLink,savePath,link,copyArg):
    """ 
    default copy copies combined log, summary.txt and workflow logs
    fileLink is directory of the hit
    copyArg is the corresponding switch
    savePath+link is the directory in which logs are saved
    """
    if(copyArg=='d'):
        logPath=r'\\Product\\Debug'
        if(not exists(savePath+link[i]+'\\Debug')):
            mkdir(savePath+link[i]+'\\Debug')
        print('Copying debug log')
    elif(copyArg=='a'):
        logPath=r'\\Product\\Application'
        if(not exists(savePath+link[i]+'\\Application')):
            mkdir(savePath+link[i]+'\\Application')
        print('Copying application log')
    elif(copyArg=='s'):
        logPath=r'\\Product\\Service'
        if(not exists(savePath+link[i]+'\\Service')):
            mkdir(savePath+link[i]+'\\Service')
        print('Copying service log')
    logList=listdir(fileLink+logPath) #copy workflow log files
    logListxml=[logList[i] for i in range(len(logList)) if logList[i].split('.')[1]=='xml']
    if(len(logListxml)==0):
        print('No xml logs available')
    else:
        copyLogList(fileLink,logPath,logListxml,savePath,link)


for i in range(len(linkList)):
    print(f'Copying from:{linkList[i]}')
    if(not exists(savePath+linkList[i])):
        mkdir(savePath+linkList[i])
    print('Copying combined log, workflow log and summary.txt')
    defaultCopy(fileLinks[i],savePath,linkList[i])
    if(switch=='A'):
       print('Copying debug, application, and service logs in addition to default')
       if(not exists(savePath+linkList[i]+'\\Debug')):
           mkdir(savePath+linkList[i]+'\\Debug')
       if(not exists(savePath+linkList[i]+'\\Application')):
           mkdir(savePath+linkList[i]+'\\Application')
       if(not exists(savePath+linkList[i]+'\\Service')):
           mkdir(savePath+linkList[i]+'\\Service')    
       copydata(fileLinks[i],savePath,linkList[i],'d')
       copydata(fileLinks[i],savePath,linkList[i],'a')
       copydata(fileLinks[i],savePath,linkList[i],'s')
    elif(switch not in 'dasA'):
        print('Invalid argument')
        break
    else:
       val=copydata(fileLinks[i],savePath,linkList[i],switch) 

print('Complete')    