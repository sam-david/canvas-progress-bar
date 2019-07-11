import requests
import json
import pdb
import math
import time
import datetime
from pytz import timezone
import pytz

NANOLEAF_API_ENDPOINT = "http://10.0.1.30:16021/api/v1/"
NANOLEAF_AUTH_TOKEN = "9T3xpTPNxsBxlWEnHmmIxOuElgfFNdQl"
NANOLEAF_BASE_URL = NANOLEAF_API_ENDPOINT + NANOLEAF_AUTH_TOKEN
MAKERGEAR_API_KEY = "25C8431CFE07466D81CF9FA8831D0D40"
LULZBOT_API_KEY = "25BF160035354521978E60B57E7F18C6"
ENDER_API_KEY = "BE943CE2F30D43F6A87C16EFE3340A7C"
TOTAL_PRINTER_COUNT = 3
DATE_FORMAT='%m/%d/%Y %H:%M:%S %Z'

def get_job(printer):
    if printer == 'makergear':
        api_endpoint = 'http://10.0.1.12'
        headers = { 'X-Api-Key': MAKERGEAR_API_KEY }
    elif printer == 'lulzbot':
        api_endpoint = 'http://10.0.1.4'
        headers = { 'X-Api-Key': LULZBOT_API_KEY }
    elif printer == 'ender':
        api_endpoint = 'http://10.0.1.36'
        headers = { 'X-Api-Key': ENDER_API_KEY }
    else:
        raise Exception("Invalid Printer")

    request_url = api_endpoint + "/api/job"
    response = requests.get(url = request_url, headers=headers).json()

    return response

def nano_progress_bar(printer, job_info):
    panel_count = lit_panel_count(job_info)
    print(str(printer), "POST Nano panel count: ", panel_count)
    data = { 'select': printer.capitalize() + ' ' + str(panel_count) }
    request_url = NANOLEAF_BASE_URL + "/effects"

    requests.put(url = request_url, data = json.dumps(data))


def lit_panel_count(job_info):
    percent_complete = job_info['progress']['completion']
    panel_count = 10
    lit_panel_count = math.ceil((percent_complete / 100) * panel_count)

    return lit_panel_count


# POWER FUNCTIONS
def get_power_state():
    request_state_url = NANOLEAF_BASE_URL + "/state/on"
    response = requests.get(url = request_state_url)
    return response.json()['value']

def turn_off_canvas():
    is_on = get_power_state()
    # print('Power is_on = ' + str(is_on))
    if is_on:
        request_url = NANOLEAF_BASE_URL + "/state"
        data = {'on':{'value':False}}
        headers = { 'Content-Type': 'application/json' }

        response = requests.put(url = request_url, data = json.dumps(data), headers= headers)
        if response.status_code == 204:
            print('Success: Nanoleaf turned off')

def get_current_hour():
    date = datetime.datetime.now(tz=pytz.utc)
    pst_date = date.astimezone(timezone('US/Pacific'))
    print('Current PST date & time is:', pst_date.strftime(DATE_FORMAT))
    current_hour = pst_date.hour
    return current_hour

current_hour = get_current_hour()
print("CURRENT HOUR: ", current_hour)

#if current_hour < 23 and current_hour > 8:
if current_hour:
    job_status = {
        "makergear": get_job('makergear'),
        "lulzbot": get_job('lulzbot'),
        "ender": get_job('ender')
    }

    offline_printer_count = 0
    # Is printer offline or done job?
    for printer in job_status:
        print(printer, " JOB STATE: ", job_status[printer]['state'])
        if job_status[printer]['state'] != 'Printing':
            offline_printer_count += 1

    online_printer_count = TOTAL_PRINTER_COUNT - offline_printer_count
    print("Online Printer Count:", online_printer_count)


    if online_printer_count == 0:
        # No printers online
        turn_off_canvas()
    elif online_printer_count > 0:
        # Loop through online printers and POST panels
        timeout_length = 60 / online_printer_count

        for printer in job_status:
            if job_status[printer]['state'] == 'Printing':
                job_info = job_status[printer]
                nano_progress_bar(printer, job_info)
                time.sleep(timeout_length)
    else:
        turn_off_canvas()
else:
    turn_off_canvas()


