import getopt
import sys
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from requests.auth import HTTPBasicAuth

def validate_app(auth_token):
    url = "https://appinspect.splunk.com/v1/app/validate"
    file_path = "./myapp.tgz"
    user_token = auth_token
    app_name = os.path.basename(file_path)

    fields = {('app_package', (app_name, open(file_path, "rb")))}
    payload = MultipartEncoder(fields=fields)
    headers = {"Authorization": "bearer {}".format(user_token), "Content-Type": payload.content_type, "max-messages": "all"}
    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.status_code)
    print(response.json())


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
