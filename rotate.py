import os
import json
from terrasnek.api import TFC

TFC_TOKEN = os.getenv("TFC_TOKEN", None)
TFC_ORG = os.getenv("TFC_ORG", None)
TFC_URL = "https://app.terraform.io"
TFC_WS = os.getenv("TFC_WS_FILTER", None)

with open("payload.json", "r") as read_file:
    payload_tpl = json.load(read_file)

api = TFC(TFC_TOKEN, url=TFC_URL)
api.set_org(TFC_ORG)

# TODO: implement downstream workspace locking to avoid breakage mid rotation (very unlikely, but possible)
def workspace_lock (org, ws):
    api.set_org(org)
    ws_locked = api.workspaces.lock(
        ws, {"reason": "Key Rotation."})["data"]
    print(ws_locked)
    return

for ws in api.workspaces.list()['data']:
    creds_to_rotate = []
    
    ws_name = ws['attributes']['name']
    ws_id = ws['id']
    
    if ws_name == TFC_WS:
        state = api.state_versions.get_current(ws['id'])
        payload = payload_tpl
        for r in state['data']['attributes']['resources']:
            if r['name'] == 'workspace_creds':
                addr = r['module'].replace('root', 'module') + '.' + r['type'] + '.' + r['name']
                creds_to_rotate.append(addr)
        if len(creds_to_rotate) > 0:
            #workspace_lock(org_name, child_ws_id)
            payload['data']['attributes']['replace-addrs'] = creds_to_rotate
            payload['data']['relationships']['workspace']['data']['id'] = ws_id
            print(json.dumps(payload, indent=4, sort_keys=True))
            api.runs.create(payload)

