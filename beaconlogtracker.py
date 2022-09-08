#!/usr/local/bin/python3
from sleep_python_bridge.striker import CSConnector

from argparse import ArgumentParser

from pprint import pp, pprint
import time
import signal

from pathlib import Path
import json

# Initialize lists
beaconlogresult = [] # raw data from CS
beaconLogs = [] # Cleaned list to feed final JSON

# JSON file
datafile = "output/html/data/beaconlogs.json"

####################
## FUNCTIONS
def handler(signum, frame):
    exit(1)

def parseArguments():
    parser = ArgumentParser()
    parser.add_argument('host', help='The teamserver host.')
    parser.add_argument('port', help='The teamserver port.')
    parser.add_argument('username', help='The desired username.')
    parser.add_argument('password', help='The teamserver password.')
    parser.add_argument('path', help="Directory to CobaltStrike")
    
    args = parser.parse_args()
    return args

def main(args):

    signal.signal(signal.SIGINT, handler)

    cs_host = args.host
    cs_port = args.port
    cs_user = args.username
    cs_pass = args.password
    cs_directory = args.path
    sleeptime = 30

    ####################
    ## Connect to server
    cs = CSConnector(
        cs_host=cs_host, 
        cs_user=cs_user, 
        cs_pass=cs_pass,
        cs_directory=cs_directory)
    
    while(1):
        print(f"[*] Connecting to teamserver: {cs_host}")
        try:
           cs.connectTeamserver()
           break
        except:
            print(f"[!] Unable to connect to the teamserver, is it running? Waiting {sleeptime} seconds to try again.")
            time.sleep(sleeptime)
            continue

    while(1):
        print("[Beacon Log Tracker] Getting beacon logs from teamserver...")
        cs.logToEventLog("[Beacon Log Tracker] Getting beacon logs from teamserver",event_type="external")

        beaconlogresult = cs.get_beaconlog()

        ####################
        ## Process Logs

        cs.logToEventLog("[Beacon Log Tracker] Processing logs",event_type="external")

        # JSON field reference: type, beacon_id, user, command, result, timestamp

        if beaconlogresult is None:
            print(f"[!] No logs yet. Waiting {sleeptime} seconds for a beacon to check in.")
            time.sleep(sleeptime)
            continue

        for log in beaconlogresult:

            # job types
            beacon_checkin_types = ["beacon_checkin"]
            beacon_input_types   = ["beacon_input"]
            beacon_output_types  = ["beacon_tasked",
                                    "beacon_output",
                                    "beacon_output_alt",
                                    "beacon_output_ls",
                                    "beacon_output_ps",
                                    "beacon_output_jobs"
                                    ]
            beacon_error_types   = ["beacon_error"]

            # initialize a dict record
            logDict = {}

            logType = log[0]

            # Checkins
            if logType in beacon_checkin_types:
                logDict["type"]      = str(log[0])
                logDict["beacon_id"] = str(log[1])
                logDict["user"]      = ""
                logDict["command"]   = ""
                logDict["result"]    = str(log[2])
                logDict["timestamp"] = str(log[3])

            # Inputs
            elif logType in beacon_input_types:
                logDict["type"]      = str(log[0])
                logDict["beacon_id"] = str(log[1])
                logDict["user"]      = str(log[2])
                logDict["command"]   = str(log[3])
                logDict["result"]    = ""
                logDict["timestamp"] = str(log[4])

            # Outputs
            elif logType in beacon_output_types:
                logDict["type"]      = str(log[0])
                logDict["beacon_id"] = str(log[1])
                logDict["user"]      = ""
                logDict["command"]   = ""
                logDict["result"]    = str(log[2])
                logDict["timestamp"] = str(log[3])
            
            # Beacon Errors
            elif logType in beacon_error_types:
                logDict["type"]      = str(log[0])
                logDict["beacon_id"] = str(log[1])
                logDict["user"]      = ""
                logDict["command"]   = ""
                logDict["result"]    = str(log[2])
                logDict["timestamp"] = str(log[3])

            else:
                print(f"Unknown log type: {logType}")
                print(log)

            beaconLogs.append(logDict)

        ####################
        ## Read log file

        print(f"[Beacon Log Tracker] Log count: {len(beaconLogs)}")

        path = Path(datafile)

        # Load existing data file
        if path.is_file():
            print("[*] Found log file")
            f = open(datafile)
            fileLogs = json.loads(f.read())
            f.close()

            currentLogCount = len(beaconlogresult)
            fileLogCount = len(fileLogs["data"])

            print(f"[Beacon Log Tracker] Current Log Count     :  {currentLogCount}")
            print(f"[Beacon Log Tracker] Current Log File Count: {fileLogCount}")

            cs.logToEventLog(f"[Beacon Log Tracker] Log count since teamserver started: {currentLogCount}",event_type="external")
            cs.logToEventLog(f"[Beacon Log Tracker] Log count saved to JSON           : {fileLogCount}",event_type="external")

            # Check for missing entrys in the beaconlogs.json file from the current log data
            updatedBeaconLog = fileLogs["data"]

            for log in beaconLogs:
                if log in fileLogs["data"]:
                    pass
                else:
                    updatedBeaconLog.append(log)

            # Update beaconlogs.json with new data
            f = open(datafile,"w+")
            f.write(json.dumps({"data":updatedBeaconLog}))
            f.close()

        else: 
            # Create data file it does not exist and load current data
            print("[!] Missing log file. Creating...")
            f = open(datafile,"w+")
            logs = {"data":beaconLogs}
            f.write(json.dumps(logs))
            f.close()
    
        print(f"[*] Wait {sleeptime} ...")
        time.sleep(sleeptime)

if __name__ == "__main__":
    print("------------------")
    print("Beacon Log Tracker")
    print("------------------")

    args = parseArguments()
    main(args)

