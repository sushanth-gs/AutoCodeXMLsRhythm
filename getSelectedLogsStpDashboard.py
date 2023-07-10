from os import listdir,mkdir 
from shutil import copy
from os.path import exists
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from sys import argv
#copies selected logs from all file links on stp dashboard 
#needs install lxml parser and beautifulsoup4 (pip)
#call from python venv command line with python getSelectedLogsStpDashboard.py <DashboardURL> <savepath>
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
fileLinks=getfilelinks(req)
linkList=['_'.join(fileLinks[i].split('\\')[-1].split('_')[-3:]) for i in range(len(fileLinks))]

#save_path=r'C:\Users\320159870\Downloads\RAPressure\\'
save_path=argv[2]
for i in range(len(linkList)):
    print(f'Copying from:{linkList[i]}')
    if(not exists(save_path+linkList[i])):
        mkdir(save_path+linkList[i])
    copy(fileLinks[i]+r'\\Combined.log',save_path+linkList[i]) #grab combined log
    copy(fileLinks[i]+r'\\Summary.txt',save_path+linkList[i]) #grab Summary.txt
    workflowLogList=listdir(fileLinks[i]+r'\\Product\\Workflow') #copy workflow log files
    print(f'Copying {len(workflowLogList)} workflow logs')
    for j in range(len(workflowLogList)):
        copy(fileLinks[i]+fr'\\Product\\Workflow\\\{workflowLogList[j]}',save_path+linkList[i])
print('Complete')    