import getopt
import sys
import os
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from requests.auth import HTTPBasicAuth


def check_status(request_id):
    uri = "https://appinspect.splunk.com/v1/app/validate/status/" + request_id

    report_status_done = 0

    while report_status_done == 0:
        response = requests.get(uri)
        print(response.json())
        response_status = response.json().get("status")
        if response_status != "SUCCESS":
            print("Report completion is still pending")
            time.sleep(2)
        else:
            print("Report is complete!")
            report_status_done += 1

    return


def get_report(request_id):
    uri = "https://appinspect.splunk.com/v1/app/report/" + request_id
    response = requests.get(uri)

    print (response.json)


def validate_app(auth_token):
    url = "https://appinspect.splunk.com/v1/app/validate"
    file_path = "./myapp.tgz"
    user_token = auth_token
    app_name = os.path.basename(file_path)

    fields = {('app_package', (app_name, open(file_path, "rb")))}
    payload = MultipartEncoder(fields=fields)
    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": payload.content_type,
               "max-messages": "all"}

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.status_code)
    print(response.json())

    check_status(response.json().get("request_id"))


def request_login_token(pw):
    uri = "https://api.splunk.com/2.0/rest/login/splunk"
    response = requests.get(uri, auth=HTTPBasicAuth("rabeyta", pw))
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
