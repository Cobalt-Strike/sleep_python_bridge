# Cobalt Strike Sleep Python Bridge

This project is 'bridge' between the sleep and python language. It allows the control of a Cobalt Strike teamserver through python without the need for for the standard GUI client. 

NOTE: This project is very much in BETA. The goal is to provide a playground for testing and is in no way an officially support feature. Perhaps this could be something added in the future to the core product.

The project was inspired by the work done by @BinaryFaultline and @Mcgigglez16 in the project https://github.com/emcghee/PayloadAutomation. I want to offer a special thanks you both !!

The heart of this bridge is a python implementation of a headless Cobalt Strike client. This is achieved by using the Aggressor Script Console provided by **agscript** as the engine. Agscript allows for headless interaction with Cobalt Stike (https://www.cobaltstrike.com/aggressor-script/index.html). The 'bridge' works by using python helper functions in sleepy.py to generate the needed sleep commands expected by the agscript console. Instead of writing the sleep functions, striker.py provides helper functions that abstracts sleep and allows the use of python. 

## Changes of note from the original project

Because the PayloadAutomation project inspired this, it started with much of the same code, but I wanted to strip this down to use the components needed to act as an agscript wrapper.

- Renamed from Payload_Automation to sleep_python_bridge. This project is more than payload generation.
- Changed from a PyPI library to local modules. This was down for testing and may be a good candidate for a python library after extensive testing
- Updated and added helpers to match aggressor versions
- Add ability to load external script.

## Included Libraries

- Striker: A set of functions to interact with Cobalt Strike and execute functionality typically only accessible via Sleep/GUI.
- Sleepy: A set of functions to help facilitate a bridge between Sleep objects and Python objects.
- Compyler: A set of functions to compile various payloads from platform or cross-platform.
- Artifactor: A set of functions to inspect and review artifacts and collect and track IoCs.

## Files and Directories

Item                | Description
--------------------|------------
sleep_python_bridge | The libray that allows python to interface with Cobalt Strike
output/html         | path for html data viewers
output/html/data    | path for json data used by data viewer
output/payloads     | path for saved payloads (used by payload generator)
payload_scripts     | path for external scripts to be loaded by payloadgenerator.py
payload_scripts.cna | init script for loading external scripts loaded by payloadgenerator.py
beaconlogtracker.py | Implementation of a beacon log tracker the uses an HTML datagrid to display beacon logs
payloadgenerator.py | Implementation of a beacon payload genertor that create payloads for each listener
beacongrapher.py    | Implementation of a beacon graph tracker the uses an HTML javascript directed graph to beacons

## TODO

- Document the exposed functions
- move compile based functions from striker.py to compyler.py
- Add additional error checking, specifically for application dependencies
- Expand compyler to include remote builds and mingw
- Add IOC tracking to payloads generated via artifactor.py
- handle error: "User is already connected."
- Consider converting this to a formal python library

---

## How to use

The examples in this project may be the easist way to understand but is the script example.py

```Python
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
```

Call the script

```bash
python3 example.py 127.0.0.1 50050 example password ~/cobaltstrike
```

## Practical Examples

### Log Tracker

Beacon logs are available at runtime in a teamserver or through the beacon log files saved on the teamserver. The data is always there, but may not be presented in a way you would like. This is an example of log tracker that use an HTML data grid to quickly view beacon logs.

`beaconlogtracker.py` is a script that connects to a teamserver, extracts the running beacon logs every 30 seconds, saves to `<code>`beaconlogs.json` and, displays in a searchable and sortable HTML data grid.

Beacons logs are always saved to the logs directory, but this is an alternate way to track the in memory logs with an alternate viewer. If the teamserver is restarted the in memory logs are lost and you must refer to the logs stored in the logs directory on the teamserver. This script keep in memory logs sync'd to the file `beaconlogs.json`. This way you have a quick and easy way to visualize all data without digging through the logs directory even if Cobalt Strike is restarted.

Start the script by having it connect to your teamserver to sync logs every 30 seconds

Usage: 

`python3 beaconlogtracker.py 127.0.0.1 50050 logtracker password ~/cobaltstrike`

This will keep beaconlogs.json sync'd with saved and running beacon logs. It syncs every 30 seconds

Start a webserver from output/html directory

`python3 http.server`

Connect to http://localhost:8000/beaconlogs.html

### Payload Generator

A feature often requested by red team operators is the ability to create payloads programmatically with the need for the Cobalt Strike GUI. The reference project did this with a payload generator. This was great, but there is a unique challenge. Aggressor provides several hooks to influence how a payload is built. These hooks are used by the various kits (i.e., artifact kit, sleep mask kit, or UDRL kit). They are normally used by loading an aggressor script through the GUI. This project was extended to allow the loading of external scripts. Without this, using this payload hooks would be difficult. This code could easily be extended to pass the payloads to external functions to add custom obfuscation, embed in a customer loader, or any other modification.

The payload generator script connecta to the teamserver, loads the additional scripts, and creates payloads.

Usage:

- Update payload_scripts.cna with external scripts (if needed. and see the note below on external scripts)
- Add external scripts to the payload_scripts directory
- run `python3 payloadgenerator.py 127.0.0.1 50050 payloads password ~/cobaltstrike`

**NOTE: Loading of external scripts**

Loading external scripts is not always needed but it used for payload modification scripts that include payload hooks (i.e., artifiact, sleepmask, and udrl kits). If you load scripts from the Cobalt Strike GUI, payloads will honor these scripts from the GUI but not from the agscript client (These are different clients). You must load the scripts in your python code. 

- scripts must be added to a 'scripts' directory
- the data should be flat for best file path resolution
- Currently there is no feedback provided that allows you to know if a script was successfully loaded. You can use the `elog` function to monitor the event log for dirty debugging.

The default `script_resource` function adds "/scripts/" to the path during resolution. This must be changed or paths built with the expected usage. Without updating, this function flow to loaded scripts and can cause weird path issues. The playloadgenerator script has an inline patch to help with this.

Code references for loading external scripts

**striker.py**

```
	def ag_load_script(self, script_path):
		command = f"include(getFileProper('{script_path}'))"
		self.ag_sendline(command)
```

**init.cna**

Overloads `script_resource` to point to the root of the scripts directory

**Timing**

The script needs time to load. Currently there is no feedback provide that allows you to know if a script was successfully loaded. You can use the `elog` function to monitor the event log for dirty debugging.

```python
cs.ag_load_script(script_path.name)
time.sleep(3) # Allow time for the script to load
```

### Beacon Grapher

This is beta code that will display beacon in a directed graph.

The script updates the file output/data/beacons.json

Start a webserver and open http://localhost:8000/beacons.html

Usage:

`python3 beacongrapher.py 127.0.0.1 50050 grapher password ~/cobaltstrike`

This will create the beacons.json file used by the javascript grapher.

Start a webserver from output/html directory

`python3 http.server`

Connect to http://localhost:8000/beacons.html