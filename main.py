import os
import sys
import json
import requests
import time
# import wxpython
import filecmp
import logging
import csv
import glob

# Load in main settings json
with open("./settings.json", "r") as configjsonFile:
    scriptconfig = json.load(configjsonFile)
    logtype = scriptconfig['logtype']
    apilink = scriptconfig["apilink"]

initcurtime = time.localtime()
curtime = (f'{initcurtime.tm_hour}{initcurtime.tm_min}{initcurtime.tm_sec}')
curdate = (f'{initcurtime.tm_year}{initcurtime.tm_mon}{initcurtime.tm_mday}')

logging.basicConfig(filename=f"RHS_ADisplay_EventParse_{curdate}.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a')
log = logging.getLogger()
if "debug" in logtype:
    log.setLevel(logging.DEBUG) # use this for debugging.
elif "info" in logtype:
    log.setLevel(logging.INFO) # use this for production
else:
    log.setLevel(logging.INFO)
    log.error("A logger type was not specified in the configuration file.")
    print("Error: A logger type was not specified in the configuration file.")
    exit()
logging.getLogger("urllib3").setLevel(logging.WARNING) # requests uses urllib3 for doing majority of its functions, which produces unnecessarily a lot if logged

isfileNewest = False # default this before anything runs for comparing file contents.

csvfile = (f"EventData_{curdate}_{curtime}.csv") # output data file parsed with API
csvfields = ['name','venue', 'time', 'month', 'day', 'year', 'pretty_date', 'allday', 'recurring', 'id'] # ^

# apilink = ("https://thrillshare-cmsv2.services.thrillshare.com/api/v4/o/11340/cms/events?slug=events-rudder")
## should be the API link RHS uses for events according to BISD's new apptegy site. not sure if this was used in edlio or not (confirm with TSC if they manage this)
fileout = (f'EventsAPI_{curdate}_{curtime}.json') # defining filename
rq = requests.get(apilink)

def initFolder(): # check if data folder exists
    if not os.path.exists("./data"):
        # this should only happen during first-time-run
        print("data folder wasn't found, creating it")
        log.debug("making data folder")
        os.makedirs("./data/")
    elif not os.path.exists("./displaydata"):
        # this should only happen during first-time-run
        print("displaydata folder wasn't found, creating it")
        log.debug("making displaydata folder")
        os.makedirs("./displaydata/")
    elif not os.path.exists("./temp"):
        # this should only happen during first-time-run
        print("temp folder wasn't found, creating it")
        log.debug("making temp folder")
        os.makedirs("./temp/")
    elif not os.path.exists(f"./displaydata/{csvfile}"):
        log.warning("csv file doesn't exist. creating it")
        with open(f'./displaydata/{csvfile}', 'a') as listfile:
            csvwrite = csv.writer(listfile)
            csvwrite.writerow(csvfields)
    else:
        print("data folders exists, we jud")

def getNewestFile(path,returnAsFile): # get newest JSON file in data directory
    log.debug(f"Retrieving newest file in passed directory argument {path}")
    list_of_files = glob.glob(f'{path}/*') # * means all files in directory
    latest_file = max(list_of_files, key=os.path.getctime)
    if returnAsFile == True: # if returnasfile is true, return the latest file's contents as a file object
        log.debug(f"Returning newest file in {path} as a file object")
        return open(latest_file)
    else: # if returnasfile is not true, return the path to the latest file
        log.debug(f"Returning newest file in {path} as a file name")
        return latest_file


def getTempFile(filename):
    if rq.headers['content-type'] == "application/json; charset=utf-8":
        open(f'./temp/{filename}', 'wb').write(rq.content)
    else:
        print("getTempFile: API could not be downloaded due to the API not returning in JSON format") # this function is called first before any API parsing
    return filename

def clearTempFiles():
    tempdir = os.listdir("./temp/")
    for files in tempdir:
        os.remove(files) # yikes. not running this yet to make sure it doesn't remove anything crucial.
        

def localDownload():
    #make a local copy of the returned events for daily/scheduled comparsions
    log.info("Downloading latest API GET response to data/ directory")
    if rq.headers['content-type'] == "application/json; charset=utf-8":
        open(f'./data/{fileout}', 'wb').write(rq.content)
    else:
        log.error("localDownload: API could not be downloaded due to the API not returning in JSON format") # this function is called first before any API parsing is done to show on the display
        print("localDownload: API could not be downloaded due to the API not returning in JSON format") # this function is called first before any API parsing is done to show on the display
    
def compareAPI():
    # this is the same thing as localDownload, however only compares the newest file in the ./data directory to the latest data returned by the API.
    log.info("Beginning to compare latest file to response")
    global isfileNewest
    getTempFile("temp_"+fileout) # retrieve local temp file from latest API GET request.
    compare = filecmp.cmp(getNewestFile("./data/",False), getNewestFile("./temp/",False), shallow=False) # maybe?? non-shallow comparison compares contents, that's what we want.
    if compare == False:
    # if the latest file and contents of current API GET request are not the same, download the new version.
        log.warning("Latest file in data/ and current API GET response are not identical, downloading new version")
        print("Latest file in data/ and current API GET response are not identical")
        isfileNewest = False
        localDownload()
    else:
        log.info("Latest file in data/ and current API GET response are identical, skipping")
        print("Latest file in data/ and current API GET response are identical")
        isfileNewest = True

    # clearTempFiles()
    

def appendCSV(list):
    with open(f'./displaydata/{csvfile}', 'a') as listfile:
            csvwrite = csv.writer(listfile)
            csvwrite.writerow(list)

def parseAPI():
    log.info("Starting to iterate through events")
    print("Starting to iterate through events")
    eallday = False
    recurring = False
    eventapijson = json.load(getNewestFile("./data/",True))
    for event in eventapijson['events']:
        log.info(f"Found event {event['id']} ({event['title']})")
        etitle = event['title'] # Title of the event
        eid = event['id'] # not sure if used publicly - also not to be confused with Eid, the holiday
        emonth = event['month'] # date - month
        eday = event['day'] # date - day
        eyear = event['year'] # date - year
        elocation = event['venue'] # event location
        etime = event['time'] # "fake" event time in local timezone
        eprettydate = event['formatted_date'] # the above date format, in a cleaner format without the year. likely won't be used.
        if event['all_day'] == 'true':
            # if the event is flagged to be all-day, set a variable to true.
            log.info(f"Event {event['id']} is an all-day event")
            print(f"Event {event['id']} is an all-day event")
            eallday = True
        if event['recurrent'] == 'true':
            # this is a recurring event. there are none of these at the time of writing this. if this gets set to true, that's weird.
            log.info(f"Recurring event found! {event['title']}")
            print(f"Event {event['id']} is a recurring event")
            recurring = True

        # v format to be used in CSV. this is just a tad bit important for parsing through to be displayed.
        # ['name','venue', 'time', 'month', 'day', 'year', 'pretty_date', 'allday', 'recurring', 'id'] # ^
        csvevent = [etitle, elocation, etime, emonth, eday, eyear, eprettydate, eallday, recurring, eid]
        appendCSV(csvevent)
        print(f"Event {event['id']} was saved")

# run program when started
initFolder() # initialize data folder
compareAPI() # compare newest downloaded event JSON to endpoint response, download latest version if they are not identical.
parseAPI() # parse events and write to display event JSON
print("APIParse has finished")
log.info("APIParse has finished")