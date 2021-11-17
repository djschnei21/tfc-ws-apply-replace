import os
from terrasnek.api import TFC

TFC_TOKEN = os.getenv("TFC_TOKEN", None)
TFC_ORG = os.getenv("TFC_ORG", None)
TFC_WS_FILTER = os.getenv("TFC_WS_FILTER", None)
TFC_URL = "https://app.terraform.io"

print("----------------")
print(TFC_TOKEN)
print(TFC_ORG)
print(TFC_URL)
print("----------------")


api = TFC(TFC_TOKEN, url=TFC_URL)
api.set_org(TFC_ORG)

found_ws = []

for i in api.workspaces.list()['data']:
    if i['attributes']['name'].startswith(TFC_WS_FILTER):
        found_ws.append(i['attributes']['name'])

print(found_ws)