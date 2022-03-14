import requests

baseurl = "https://www.thebluealliance.com/api/v3"
requrl = "events/2022"

headers = {
    "X-TBA-Auth-Key": "cd5hhdZZjmiGBQlA4uP2M5Y52MnhgUSUidzQpi9qHmlqTSdSHxXJL0iUhSeHzLVD"
}

response = requests.get(baseurl + "/" + requrl, headers=headers)