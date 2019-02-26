import getopt
import sys
import requests
from requests.auth import HTTPBasicAuth


def request(pw):
    uri = "https://api.splunk.com/2.0/rest/login/splunk"
    response = requests.get(uri, auth=HTTPBasicAuth("rabeyta", pw))
    user_token = response.json().get("data").get("token")
    print(user_token)
    sys.exit(0)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:o:")
    except getopt.GetoptError:
        print 'helloworld.py -p <password>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-p':
            request(arg)


if __name__ == "__main__":
    main(sys.argv[1:])
