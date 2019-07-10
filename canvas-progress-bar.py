import requests
import json
import pdb
import math
import time
import datetime
from pytz import timezone
import pytz

NANOLEAF_API_ENDPOINT = "http://10.0.1.19:16021/api/v1/"
NANOLEAF_AUTH_TOKEN = "wmyApYFd5t7LA0GXomcQ4Od5aSQ5AcWd"
NANOLEAF_BASE_URL = NANOLEAF_API_ENDPOINT + NANOLEAF_AUTH_TOKEN
MAKERGEAR_API_KEY = "25C8431CFE07466D81CF9FA8831D0D40"
LULZBOT_API_KEY = "25BF160035354521978E60B57E7F18C6"
DATE_FORMAT='%m/%d/%Y %H:%M:%S %Z'

def nano_progress_bar(printer, level):
    data = { 'select': printer.capitalize() + ' ' + str(level) }
    request_url = NANOLEAF_BASE_URL + "/effects"

    requests.put(url = request_url, data = json.dumps(data))

def get_job(printer):
    if printer == 'makergear':
        api_endpoint = 'http://10.0.1.12'
        headers = { 'X-Api-Key': MAKERGEAR_API_KEY }
    elif printer == 'lulzbot':
        api_endpoint = 'http://10.0.1.4'
        headers = { 'X-Api-Key': LULZBOT_API_KEY }
    else:
        raise Exception("Invalid Printer")

    request_url = api_endpoint + "/api/job"
    response = requests.get(url = request_url, headers=headers).json()
    if response['progress']['completion'] == None:
        return 'Offline'
    else:
        percent_complete = response['progress']['completion']
	panel_count = 10
        lit_panel_count = math.ceil((percent_complete / 100) * panel_count)

        return {
                'percent_complete': percent_complete,
                'panel_count': lit_panel_count 
        }

def get_power_state():
    request_state_url = NANOLEAF_BASE_URL + "/state/on"
    response = requests.get(url = request_state_url)
    return response.json()['value']


def turn_off():
    request_url = NANOLEAF_BASE_URL + "/state"
    data = {'on':{'value':False}}
    headers = { 'Content-Type': 'application/json' }

    response = requests.put(url = request_url, data = json.dumps(data), headers= headers)
    if response.status_code == 204:
        print('Success: Nanoleaf turned off')



date = datetime.datetime.now(tz=pytz.utc)
pst_date = date.astimezone(timezone('US/Pacific'))
print('Current PST date & time is:', pst_date.strftime(DATE_FORMAT))
current_hour = pst_date.hour

#if current_hour < 23 and current_hour > 8:
if current_hour:
    makergear_job_status = get_job('makergear')
    lulzbot_job_status = get_job('lulzbot')

    if lulzbot_job_status == 'Offline' and makergear_job_status == 'Offline':
        # Both Offline
        is_on = get_power_state()
        print('Power is_on = ' + str(is_on))
        if is_on:
            turn_off()
    elif lulzbot_job_status == 'Offline' and makergear_job_status['percent_complete'] != 100.0:
        # Makergear on
        print('PUT makergear panels count: ' + str(makergear_job_status['panel_count']))
        nano_progress_bar('makergear', makergear_job_status['panel_count'])
    elif makergear_job_status == 'Offline' and lulzbot_job_status['percent_complete'] != 100.0:
        # Lulzbot on
        print('PUT lulzbot panels count: ' + str(lulzbot_job_status['panel_count']))
        nano_progress_bar('lulzbot', lulzbot_job_status['panel_count'])
    elif makergear_job_status['percent_complete'] != 100.0 and lulzbot_job_status['percent_complete'] != 100.0:
        # Both on
        print('PUT makergear panels count: ' + str(makergear_job_status['panel_count']))
        nano_progress_bar('makergear', makergear_job_status['panel_count'])

        time.sleep(30)

        print('PUT lulzbot panels count: ' + str(lulzbot_job_status['panel_count']))
        nano_progress_bar('lulzbot', lulzbot_job_status['panel_count'])
    else:
        # Fallback
        is_on = get_power_state()
        print('Power is_on = ' + str(is_on))
        if is_on:
            turn_off()
else:
    is_on = get_power_state()
    print('Power is_on = ' + str(is_on))
    if is_on:
        turn_off()


