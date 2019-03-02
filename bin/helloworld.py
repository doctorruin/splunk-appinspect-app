import getopt
import json
import sys
import os
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from requests.auth import HTTPBasicAuth


def check_status(request_id, user_token):
    uri = "https://appinspect.splunk.com/v1/app/validate/status/" + request_id

    report_status_done = 0

    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": "application/json",
               "max-messages": "all"}

    while report_status_done == 0:
        response = requests.get(uri, headers=headers)
        response_status = response.json().get("status")
        if response_status != "SUCCESS":
            print("Report completion is still pending")
            time.sleep(2)
        else:
            print("Report is complete!")
            report_status_done += 1

    return


def get_report(request_id, user_token):
    uri = "https://appinspect.splunk.com/v1/app/report/" + request_id

    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": "application/json",
               "max-messages": "all"}

    response = requests.get(uri, headers=headers)

    parsed = json.loads(response)

    print (json.dumps(parsed, indent=4, sort_keys=True))


def validate_app(user_token):
    uri = "https://appinspect.splunk.com/v1/app/validate"
    file_path = "./myapp.tgz"
    app_name = os.path.basename(file_path)

    fields = {('app_package', (app_name, open(file_path, "rb")))}
    payload = MultipartEncoder(fields=fields)
    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": payload.content_type,
               "max-messages": "all"}

    response = requests.request("POST", uri, data=payload, headers=headers)

    print(response.status_code)
    print(response.json())

    request_id = response.json().get("request_id")

    check_status(request_id, user_token)

    get_report(request_id, user_token)


def request_login_token(pw):
    uri = "https://api.splunk.com/2.0/rest/login/splunk"
    basic_auth = HTTPBasicAuth("rabeyta", pw)
    response = requests.get(uri, auth=basic_auth)
    user_token = response.json().get("data").get("token")
    print(user_token)
    validate_app(user_token)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:o:")
    except getopt.GetoptError:
        print 'helloworld.py -p <password>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-p':
            request_login_token(arg)


if __name__ == "__main__":
    main(sys.argv[1:])
