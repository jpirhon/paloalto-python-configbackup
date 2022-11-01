#!/usr/bin/env python
import json
import logging
import requests
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAApiLoginUrl = "https://{}/api/?type=keygen&user={}&password={}"
PAApiCallUrl = "https://{}/api/?type={}&action=get&xpath={}&key={}"
PAOpApiCallUrl = "https://{}/api/?type={}&cmd={}&key={}"
PAExportApiCallUrl = "https://{}/api/?type={}&category={}&key={}"

# Palo Alto API login function to get the API-key
def pa_login(fwip, fwname, username, password):
    logging.debug('Logging into %s as %s', fwname, username)

    # Login to Palo Alto API and get session cookie
    try:
        r = requests.get(PAApiLoginUrl.format(fwip, username, password), verify=False, timeout=3)
    except:
        logging.warning("Connect to firewall failed: %s", fwname)
        return("error")

    # Check that login results in proper response code
    if r.status_code != 200:
        logging.warning("Login failed to %s - status code: %i", fwname, r.status_code)
        return("error")
    else:
        # If login successful, parse the XML tree and return the apikey
        tree = ET.fromstring(r.content)
        finder = tree.find('.//result')
        apikey = finder[0].text
        return apikey

# Palo Alto API call function
def pa_apicall(fwip, fwname, calltype, cmd, key):
    logging.debug('Querying API on %s', fwname)

    # Call API on proper URL based on calltype
    if calltype == 'config':
        r = requests.get(PAApiCallUrl.format(fwip, calltype, cmd, key), verify=False, timeout=10)
    elif calltype == 'export':
        r = requests.get(PAExportApiCallUrl.format(fwip, calltype, cmd, key), verify=False, timeout=10)
    else:
        r = requests.get(PAOpApiCallUrl.format(fwip, calltype, cmd, key), verify=False, timeout=10)

    if r.status_code != 200:
        logging.info("API call failed at %s - status code: %i", fwname, r.status_code)
        return("error")
    else:
        return r
