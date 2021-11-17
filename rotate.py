import os
import json
from terrasnek.api import TFC

TFC_TOKEN = os.getenv("TFC_TOKEN", None)
TFC_ORG = os.getenv("TFC_ORG", None)
TFC_URL = "https://app.terraform.io"
TFC_WS_FILTER = os.getenv("TFC_WS_FILTER", None)

api = TFC(TFC_TOKEN, url=TFC_URL)
api.set_org(TFC_ORG)

for i in api.workspaces.list()['data']:
    ws_name = i['attributes']['name']
    ws_id = i['id']
    creds_to_rotate = []
    if ws_name == TFC_WS_FILTER:
        state = api.state_versions.get_current(i['id'])
        for r in state['data']['attributes']['resources']:
                if r['name'] == 'workspace_creds':
                        addr = r['module'].replace('root','module') + '.' + r['type'] + '.' + r['name']
                        creds_to_rotate.append(addr)
        payload = json.loads('{\"data\":{\"attributes\":{\"message\":\"API Triggered Key Rotation\",\"replace-addrs\":' + str(creds_to_rotate).replace('"','\\"').replace("'",'"') + ',\"auto-apply\":true},\"type\":\"runs\",\"relationships\":{\"workspace\":{\"data\":{\"type\":\"workspaces\",\"id\":\"' + ws_id +'\"}}}}}')
        print(payload)
        api.runs.create(payload)