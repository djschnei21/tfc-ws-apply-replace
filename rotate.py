import os
import sys
import json
import time
from terrasnek.api import TFC

tfc_url = "https://app.terraform.io"
api_token = os.getenv("TFC_TOKEN")

if api_token == None:
    print("\nPlease set TFC_TOKEN as an environment variable equal to a valid TFC token")
    sys.exit(1)

org_name = sys.argv[1]
ws_id = sys.argv[2]
resource_name_keyword = sys.argv[3]

with open("payload.json", "r") as read_file:
    payload_tpl = json.load(read_file)

api = TFC(api_token, url=tfc_url)

api.set_org(org_name)

def workspace_name (ws_id):
    name = api.workspaces.list(ws_id)['data'][0]['attributes']['name']
    return name

def find_resources (ws_id, resource_name_keyword):
    resource_to_replace = list()
    state = api.state_versions.get_current(ws_id)
    for r in state['data']['attributes']['resources']:
        if r['name'].startswith(resource_name_keyword):
            if r['module'] == 'root':
                addr = r['type'] + '.' + r['name']
            else:
                addr = r['module'].replace('root', 'module') + '.' + r['type'] + '.' + r['name']
            resource_to_replace.append(addr)
    return resource_to_replace

def replace (ws_id, resources, payload):
    payload['data']['attributes']['replace-addrs'] = resources
    payload['data']['relationships']['workspace']['data']['id'] = ws_id
    resp = api.runs.create(payload)['data']['id']
    return resp

def run_status (run_id):
    status = api.runs.show(run_id)['data']['attributes']['status']
    return status

print("-------------------------------------", flush=False)
print("TFC Organization Name: " + org_name, flush=False)
print("TFC Workspace ID: " + ws_id, flush=False)
print("Resource Name FIlter: " + resource_name_keyword, flush=False)
print("-------------------------------------\n", flush=False)

ws_name = workspace_name(ws_id)
resources = find_resources(ws_id, resource_name_keyword)
if len(resources) > 0:
    print("Found " + str(len(resources)) + " resources whose name(s) contain the keyword!:\n", flush=False)
    for r in resources:
        print("    " + r, flush=False)
    run_id = replace(ws_id, resources, payload_tpl)
    status1 = run_status(run_id)
    status2 = status1
    print("\nTriggering a \'terraform apply -replace=" + str(resources) + "\' to rotate the found resources...", flush=False)
    print("\nLink to run: " + tfc_url + "/app/" + org_name + "/workspaces/" + ws_name + "/runs/" + run_id, flush=False)
    print("\nTFC Run Status: " + status1 + "...", flush=False)
    while status1 != "applied" and status1 != "errored":
        time.sleep(1)
        status2 = run_status(run_id)
        if status1 != status2:
            print("TFC Run Status: " + status2 + "...", flush=False)
            status1 = status2
    if status1 == "errored":
        print("Looks like something went wrong... Please see logs above.", flush=False)
        sys.exit(1)