#!/usr/local/bin/python3

## Import the bridge
from sleep_python_bridge.striker import CSConnector
from argparse import ArgumentParser
from pprint import pp, pprint

###################
## Argparse
def parseArguments():
    parser = ArgumentParser()
    parser.add_argument('host', help='The teamserver host.')
    parser.add_argument('port', help='The teamserver port.')
    parser.add_argument('username', help='The desired username.')
    parser.add_argument('password', help='The teamserver password.')
    parser.add_argument('path', help="Directory to CobaltStrike")
    
    args = parser.parse_args()
    return args

## Let's go
def main(args):

    cs_host = args.host
    cs_port = args.port
    cs_user = args.username
    cs_pass = args.password
    cs_directory = args.path

    ## Connect to server
    print(f"[*] Connecting to teamserver: {cs_host}")
    with CSConnector(
        cs_host=cs_host, 
        cs_port=cs_port, 
        cs_user=cs_user, 
        cs_pass=cs_pass,
        cs_directory=cs_directory) as cs:

        # Perform some actions
        # 
        # Get beacon metadata - i.e., x beacons() from the script console
        beacons = cs.get_beacons()
        print("BEACONS")
        pprint(beacons)

        # Get list of listners - i.e., x listeners_stageless() from the script console
        listeners = cs.get_listeners_stageless()
        print("LISTENERS")
        pprint(listeners)

if __name__ == "__main__":
    args = parseArguments()
    main(args)