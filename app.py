import json

from flask import Flask, jsonify
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from googleapiclient.errors import HttpError
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def main():

    new_list = fetch()
    sub_list = {k: new_list[k] for k in list(new_list)[:2]}
    print(sub_list)

    sub_list_keys = sub_list.keys()
    print(sub_list_keys)
    orders = []
    for s in sub_list_keys:
        orderNumber = getOrderNumber(s, new_list)
        if orderNumber == "FAILED":
            print("EXITING LIST EARLY")
            print(orders)
            return dict(zip(sub_list_keys, orders))
        orders.append(orderNumber)

    print(orders)
    return dict(zip(sub_list_keys, orders))


@app.route('/list')
def fetch():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('static/stratus-integration-329517-25e194966e64.json',
                                                             scope)
    sheet_ID = "1vQzh51e1W-KJtMQRJxwyFELyn4-r8vu68aOkbi1SUN8"

    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1vQzh51e1W-KJtMQRJxwyFELyn4-r8vu68aOkbi1SUN8/edit?usp=sharing")

    try:
        sheet_instance = sheet.get_worksheet(2)
        serials = sheet_instance.col_values(5)
        processors = sheet_instance.col_values(8)

        serials_data = serials[1:]
        processors_data = processors[1:]

        serial_list = []
        proc_list = []
        for serial in serials_data:
            serial_list.append(serial)
        for proc in processors_data:
            proc_list.append(proc)

        comp_info = dict(zip(serial_list, proc_list))

        return comp_info

    except HttpError as err:
        print(err)


@app.route('/lookup')
def lookup(q):

    try:
        every_mac_url = "https://everymac.com/api/search"
        every_mac_token = "92bc20adb19b61a586bb409188e7b55b6e20fcb7"
        Q = q
        headers = {'User-Agent': 'Mozilla/5.0'}
        parameters = {'token': every_mac_token, 'q': Q, 'format': "json"}

        # Request Mac Details
        response = requests.get(url=every_mac_url, headers=headers, params=parameters)

        # View Results
        jsonResponse = response.json()

        if response.status_code == 429:
            delay = jsonResponse['token']['retryAfter']
            print("Throttled . . . retry after ", delay, " seconds")
            if jsonResponse['token']['requestsMade'] > 150:
                print("Limit has been reached. TERMINATING")
                return []

    except BaseException as e:
        if (response.status_code == 429) and (jsonResponse['token']['requestsMade'] < 150):
            delay = jsonResponse['token']['retryAfter']
            print("Throttled . . . retry after ", delay, " seconds")
            time.sleep(60)
            jsonResponse = lookup(q)

        print("Response Code = ", response.status_code)
        print("Response Headers = ", response.headers)
        print(e)

    print(jsonResponse['token']['requestsMade'])

    return jsonResponse


@app.route('/order')
def getOrderNumber(target, computer_list):

    print("Searching for ", target)

    comp_info = lookup(target)
    if not comp_info:
        return "FAILED"

    # Find out how many matching order numbers there are
    totalResults = comp_info['total']
    print("Total Results = ", totalResults)

    comp_details = comp_info['results']

    orderNumber = "NOT FOUND"
    if totalResults == 1:
        orderNumber = comp_details[0]['orderNumber']
        print("Order Number is: ", orderNumber)

    elif totalResults > 1:
        # need to match the processor speed
        proc_speed = computer_list[target]
        print(proc_speed)
        orderFound = False
        comp_index = 0
        for item in comp_details:
            if comp_index >= len(comp_details):

                break
            if item['processorSpeed'] == proc_speed:
                print("FOUND MATCH AT INDEX ", comp_index)
                orderFound = True
                break
            else:
                comp_index += 1
        if orderFound:
            orderNumber = comp_details[comp_index]['orderNumber']

    finalOrderNumber = orderNumber.replace('*', '')
    print("Final: ", finalOrderNumber)

    return finalOrderNumber

if __name__ == '__main__':
    app.run()
