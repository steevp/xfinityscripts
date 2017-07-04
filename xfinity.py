#!/usr/bin/env python3
import requests
import re
import random
from time import sleep
from string import ascii_letters

def start_wifi():
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0"
    r = s.get("http://google.com/")
    r.raise_for_status()

    m = re.search(r'data-redirect=\'(.+?)\'', r.text)
    if not m:
        raise Exception("Unable to extract redirect URL!")

    redirect_url = m.group(1).replace("\t", "")
    r = s.get(redirect_url)
    r.raise_for_status()

    # Get offer id
    r = s.get("https://wifiondemand.xfinity.com/wod/ecommerce/offers/list")
    r.raise_for_status()
    js = r.json()
    offer_id = js["offers"][0]["id"]

    r = s.get("https://wifiondemand.xfinity.com/wod/client/configuration", headers={"Content-Type": "application/json"})
    r.raise_for_status()
    auth = "UXF_CSRFToken:" + r.headers["UXF_CSRFToken"]

    # Select offer
    payload = {"chosenOfferId": offer_id, "salesChannel": "CC", "locale": "en"}
    r = s.post("https://wifiondemand.xfinity.com/wod/ecommerce/select-offer", json=payload, headers={"uxfauthorization": auth})
    r.raise_for_status()
    auth = "UXF_CSRFToken:" + r.headers["UXF_CSRFToken"]

    # Register
    email = rand_string() + "@gmail.com"
    password = rand_string() + "6"
    payload = {
        "firstName": "jack",
        "lastName": "smith",
        "zipCode": "94916",
        "email": email,
        "marketingConsent": "true"
    }
    r = s.post("https://wifiondemand.xfinity.com/wod/ecommerce/user/register", json=payload, headers={"uxfauthorization": auth})
    r.raise_for_status()
    js = r.json()

    # Finish registration
    next_page = js["nextPage"]
    r = s.get(next_page)
    r.raise_for_status()
    m = re.search(r'execution=(e[0-9]+?s)', r.text)

    if not m:
        raise Exception("Unable to find execution id")

    execution = m.group(1)
    print(execution)

    #payload = {
    #    "_eventId": "validatePasswordGuessability",
    #    "ajaxSource": "true",
    #    "password": password,
    #    "fragments": "passwordGuessabilityValidationStatus"
    #}
    #r = s.post("https://idm.xfinity.com/myaccount/create-uid?execution={}1".format(execution), data=payload)
    #r.raise_for_status()

    payload = {
        "firstName": "jack",
        "lastName": "smith",
        "emailValidationInfo.contactEmail": email,
        "primaryEmail": email,
        "userName": "",
        "password": password,
        "passwordRetype": password,
        "alternateEmail": "",
        "secretQuestion": "What+is+your+favorite+beverage?",
        "secretAnswer": "beer",
        "cimTcAccepted": "true",
        "_cimTcAccepted": "on",
        "_eventId": "submit"
    }
    r = s.post("https://idm.xfinity.com/myaccount/create-uid?execution={}1".format(execution), data=payload)
    r.raise_for_status()

    r = s.get("https://idm.xfinity.com/myaccount/create-uid?execution={}2&_eventId=initiateLoader&ajaxSource=true&fragments=statusLoader".format(execution))
    r.raise_for_status()
    print(r.text)

    payload = {"_eventId": "done"}
    r = s.post("https://idm.xfinity.com/myaccount/create-uid?execution={}2".format(execution), data=payload)
    r.raise_for_status()
    auth = "UXF_CSRFToken:" + r.headers["UXF_CSRFToken"]

    # Activate pass
    r = s.post("https://wifiondemand.xfinity.com/wod/ecommerce/activate-pass", json={}, headers={"uxfauthorization": auth})
    r.raise_for_status()
    print(r.text)

def rand_string():
    return "".join(random.choice(ascii_letters) for i in range(10))

if __name__ == "__main__":
    for i in range(5):
        try:
            start_wifi()
            break
        except Exception as e:
            print("An error occurred: %s" % e)
        sleep(3)
