#!/usr/bin/env python
import os
import logging
import requests
import json
import urllib3
import time
import sys
import threading
# Import functions from pa_functions
from pa_functions import pa_login, pa_apicall

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] (%(threadName)-10s) %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sem = threading.Semaphore()

# Parse JSON function
def parse_json(json_path):
    with open(json_path, 'r') as json_file:
        json_data = json.load(json_file)
    return json_data

# Get Firewall backups function
def getBackup(fwname, fwip, username, password):
    # Get the API key
    key = pa_login(fwip, fwname, username, password)

    # Check that the login was properly done and API key is retrieved
    if "error" in key:
        logging.warning('Error backing up configuration on %s', fwname)
    else:
        # Get the configuration output via API call
        logging.debug('Backing up configuration on %s', fwname)
        output = pa_apicall(fwip, fwname, "export", "configuration", key)

        # Write the data to the backups/ directory with name suffix '-conf'
        sem.acquire()
        with open("backups/" + fwname + "-conf", 'wb') as outfile:
            outfile.write(output.content)
        sem.release()

def main():
    logging.info('Starting Palo Alto configuration backup script...')

    # File to read the firewalls from and parse the JSON
    firewallSource = "firewalls.json"
    fws = parse_json(firewallSource)

    # File to read the config from and parse the JSON
    configSource = "config.json"
    config = parse_json(configSource)

    # Initiate jobs list
    jobs = []

    for fw in fws["firewalls"]:
        # Append backup function calls to threading jobs list
        thread_apicall = threading.Thread(target=getBackup, args=(fw["name"], fw["ip"], config["username"], config["password"]))
        jobs.append(thread_apicall)

    # Start the jobs in list
    for j in jobs:
        j.start()

    # Join the jobs in list
    for j in jobs:
        j.join()

if __name__ == "__main__":
    main()
