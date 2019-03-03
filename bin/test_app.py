import argparse
import sys
import os
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
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
    parsed = response.json()
    print_report(parsed)


def print_report(report):
    for summary, val in report["summary"].items():
        print(summary, val)
    for k, v in report["reports"][0].items():
        if k == "groups":
            for items in v:
                for other, val in items.items():
                    if other == "checks":
                        for checks in val:
                            result = checks["result"]
                            if result == "failure":
                                for mess, stuff in checks.items():
                                    if mess == "description":
                                        print(stuff)
                                    if mess == "messages":
                                        for n in stuff:
                                            print("\n Error: \n", n["message"])
                                    if mess == "tags":
                                        print(stuff)


def validate_app(user_token):
    print("token: " + user_token)
    uri = "https://appinspect.splunk.com/v1/app/validate"
    file_path = "./rabeyta_myapp.tgz"
    app_name = os.path.basename(file_path)

    fields = {('app_package', (app_name, open(file_path, "rb")))}
    payload = MultipartEncoder(fields=fields)
    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": payload.content_type,
               "max-messages": "all"}

    response = requests.request("POST", uri, data=payload, headers=headers)

    request_id = response.json().get("request_id")

    print(request_id)
    check_status(request_id, user_token)

    get_report(request_id, user_token)


def request_login_token(pw):
    uri = "https://api.splunk.com/2.0/rest/login/splunk"
    basic_auth = HTTPBasicAuth("rabeyta", pw)
    response = requests.get(uri, auth=basic_auth)
    user_token = response.json().get("data").get("token")
    return user_token


def main(argv):
    parser = argparse.ArgumentParser(description='Splunk App Validator')

    parser.add_argument("-p", "--password", dest="user_token",
                        help="Splunk user password")

    parser.add_argument("-t", "--tag", dest="tags", action="append",
                        help="Appinspect Tag. Multiple Tags supported (i.e. -t Cloud -t splunk_appinspect")

    args = parser.parse_args(argv)

    print(args)

    validate_app(args.user_token)


if __name__ == "__main__":
    main(sys.argv[1:])
