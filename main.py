import os
import sys
import json
import requests
import time
# import wxpython
import filecmp
import logging

initcurtime = time.localtime()
curtime = (f'{initcurtime.tm_hour}{initcurtime.tm_min}{initcurtime.tm_sec}')
curdate = (f'{initcurtime.tm_year}{initcurtime.tm_mon}{initcurtime.tm_mday}')

logging.basicConfig(filename=f"RHS_ADisplay_EventParse_{curdate}.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a')
log = logging.getLogger()
log.setLevel(logging.DEBUG) # use this for debugging. # TODO: define this in a config JSON file seperate from event API JSON files
# log.setLevel(logging.INFO) # use this for production
logging.getLogger("urllib3").setLevel(logging.WARNING) # requests uses urllib3 for doing majority of its functions, which produces unnecessarily a lot if logged

global isfileNewest

# Load in main settings json
with open("./settings.json", "r") as configjsonFile:
    scriptconfig = json.load(configjsonFile)
    LOGTYPE = scriptconfig['logtype']
    # APILINK = scriptconfig["apilink"]


apilink = ("https://thrillshare-cmsv2.services.thrillshare.com/api/v4/o/11340/cms/events?slug=events-rudder")
## should be the API link RHS uses for events according to BISD's new apptegy site. not sure if this was used in edlio or not (confirm with TSC if they manage this)
fileout = f'EventsAPI_{curdate}_{curtime}.json' # defining filename
rq = requests.get(apilink)

def initFolder(): # check if data folder exists
    if not os.path.exists("data/"):
        print("data folder wasn't found, creating it")
        os.makedirs("data/")
    if not os.path.exists("displaydata/"):
        print("data folder wasn't found, creating it")
        os.makedirs("data/")
    else:
        print("data folders exists, we jud")

def getNewestFile(): # get newest JSON file in data directory
    ## manages duplicates of files automatically in localDownload function!
    for filename in os.listdir("./data"):
        if filename.endswith(".json"):
            newest = max(filename , key = os.path.getctime) ## https://stackoverflow.com/questions/34551190/python-newest-file-in-a-directory
            return newest
        else:
            # log.warning("No JSON files were found in the ./data directory")
            # not needed -- print("No JSON files were found in the ./data directory, either because this is a first-run, all files were deleted, or a different error occurred.")
            log.debug(f"{filename} in ./data directory is not a JSON.")

def localDownload():
    #make a local copy of the returned events for daily/scheduled comparsions
    compare = filecmp.cmp(getNewestFile(), rq.content, shallow=False) # maybe?? non-shallow comparison compares contents, that's what we want.
    if compare == False:
    # if the latest file and contents of current API GET request are not the same, download the new version.
        if rq.headers['content-type'] == "application/json":
            open(f'data/{fileout}', 'wb').write(rq.content)
        else:
            print("API could not be parsed due to the API not returning in JSON format") # this function is called first before any API parsing
    else:
        isfileNewest == True

def eventParse(): # parse API to get events from
    with open(f"./data/{fileout}", "r") as eventjsonfile:
        eventjson = json.load(eventjsonfile)
        for event in eventjson['events']:
            etitle = event['title']
            eid = event['id'] # not sure if used publicly - also not to be confused with Eid, the holiday
            emonth = event['month']
            eday = event['day']
            eyear = event['year']
            elocation = event['venue']
            etime = event['time']
            eprettydate = event['formatted_date']
            if event['all_day'] == 'true':
                eallday = True
            if event['recurrent'] == 'true':
                # this is a recurring event. there are none of these at the time of writing this. if this gets set to true, that's weird.
                log.info(f"Recurring event found! {event['title']}")
                recurring = True
        

# run program when started
initFolder() # initialize data folder
localDownload() # download event JSON from endpoint
eventParse() # parse events and write to display event JSON
