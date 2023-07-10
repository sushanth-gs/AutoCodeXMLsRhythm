import pandas as pd 
#import numpy as np numpy and matplotlib needed if you want to make figures or manipulate values otherwise comment
#import matplotlib.pyplot as plt 
from glob import glob
from bs4 import BeautifulSoup
from sys import argv
#beautiful soup (bs4) and pandas to be installed via pip
#call from commandline as python extractXMLParams.py <path to xml files> <path to save CSVs>
def GetAllEventTags(xmlFname):
    """ 
    Populates all event tags in workflow log xml 
    """
    with open(xmlFname, 'r') as f:
        data = f.read()
    bs_data=BeautifulSoup(data,'xml')
    AllEventTags=list(bs_data.find_all('Event'))
    return(AllEventTags)

def GetEventDictList(AllEventTags):
    """ 
    Organizes event tags as dictionary of following fields: 
    1.Index -- str (event index)
    2.TimeStamp(s)  (set to 00:00:00 as starting, 5:00 is 5*3600.0 seconds+Timefraction(if any)*1e-6) float
    3.Description -- str(description of the event) (E.g. TSP activated)
    4.InfoCategory -- str Category of information (E.g. TSPUsage)
    5.NumEventsInTag -- (int) Number of actual events in this event tag.
    6.Events -- Event and type of each event (E.g. <absolute>Event_Set_Caliper</absolute>)
    7.ImpactsResource -- (bool)does it impact a resource (T/F)  
    8.Instance -- str (instance impacted(?) not sure)
    9.Component impacted -- str e.g. IAD, WorkflowArbitration
    10.What layer --str e.g. Application
    11.Member -- str Member in the layer e.g. TwoDDistance, AnchorCaliper
    12.Resource -- Resource impacted
    """
    EventDictList=[]
    for i in range(len(AllEventTags)):
        print(i)
        EventDict={}
        EventDict['Index']=AllEventTags[i]['Index']
        EventDict['TimeStamp(s)']=float(AllEventTags[i]['TimeStamp'].split(':')[1])*3600.0+float(AllEventTags[i]['TimeStamp'].split(':')[2])*60.0+1e-6*float(AllEventTags[i]['TimeFraction'])
        EventDict['Description']=AllEventTags[i].EventInfo['Description']
        EventDict['EventCategory']=AllEventTags[i].EventInfo['EventCategory']
        EventDict['InfoCategory']=AllEventTags[i].EventInfo['InfoCategory']
        childTagList=list(AllEventTags[i].findChildren())
        childTagNames=[t.name for t in childTagList]
        intVal=AllEventTags[i].PreEventHandlingMemberValue

        if('events' in childTagNames):
            EventDict['NumEventsInTag']=(len(AllEventTags[i].events)-1)//2
            EventDict['Events']=[t for t  in AllEventTags[i].events.findChildren()]
            eventChildTagNames=[t.name for t  in AllEventTags[i].events.findChildren()]
            for j in range(len(eventChildTagNames)):
                if(eventChildTagNames[j]!='basic' and eventChildTagNames[j]!='absolute' ):
                    EventDict['Minimum']=intVal.minimum.decode().split('>')[1].split('<')[0]
                    EventDict['Maximum']=intVal.maximum.decode().split('>')[1].split('<')[0]
                else:
                    EventDict['Minimum']='NA'
                    EventDict['Maximum']='NA'
        else:
            EventDict['NumEventsInTag']=0
            EventDict['Events']='NA'

        if('ResourceMember' in childTagNames):
            EventDict['ImpactsResource']=True 
            EventDict['Component']=AllEventTags[i].ResourceMember.MemberId['Component']
            EventDict['Layer']=AllEventTags[i].ResourceMember.MemberId['Layer']
            EventDict['Member']=AllEventTags[i].ResourceMember.MemberId['Member']
            EventDict['Resource']=AllEventTags[i].ResourceMember.MemberId['Resource']
            intValChildTags=list(intVal.findChildren())
            intValChildTagNames=[t.name for t in intValChildTags]
            if('Instance' in intValChildTagNames):
                EventDict['Instance']=AllEventTags[i].ResourceMember.MemberId['Instance']
            else:
                EventDict['Instance']='NA'
            EventDict['Available']=bool(intVal.available.decode().split('>')[1].split('<')[0])
            EventDict['Enabled']=bool(intVal.enabled.decode().split('>')[1].split('<')[0])
            
           
        else:
            EventDict['ImpactsResource']=False 
            EventDict['Component']='NA'
            EventDict['Layer']='NA'
            EventDict['Member']='NA'
            EventDict['Resource']='NA'
            EventDict['Instance']='NA'
            EventDict['Available']='NA'
            EventDict['Enabled']='NA'
            EventDict['Minimum']='NA'
            EventDict['Maximum']='NA'
        EventDictList.append(EventDict)
    return(EventDictList)

#dataPath=r'C:\Users\320159870\Downloads\RAPressure\20230616_141026_RhySmA1-STPBTAL'
dataPath=argv[1]
xmlFiles=glob(dataPath+'\*.xml')

savePath=argv[2]
#save_path=r'C:\Users\320159870\Downloads\\'
for i in range(1,len(xmlFiles)):
    print(f'Analysing {xmlFiles[i]}')
    AllEventTags=GetAllEventTags(xmlFiles[i])
    EventDictList=GetEventDictList(AllEventTags)
    df=pd.DataFrame(EventDictList)
    print('Saving as CSV')
    DefaultFname=xmlFiles[i].split('\\')[-1].split('.')[0]+'.csv'
    df.to_csv(savePath+DefaultFname)