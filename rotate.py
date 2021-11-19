import os
import sys
import json
import time
from terrasnek.api import TFC

tfc_url = "https://app.terraform.io"
api_token = os.getenv("TFC_TOKEN")

if api_token == None:
    sys.exit("\nPlease set TFC_TOKEN as an environment variable equal to a valid TFC token")

org_name = sys.argv[1]
ws_id = sys.argv[2]
resource_name_keyword = sys.argv[3]

with open("payload.json", "r") as read_file:
    payload_tpl = json.load(read_file)

api = TFC(api_token, url=tfc_url)

api.set_org(org_name)

def workspace_name (ws_id):
    """Returns the workspace name.

    Related Doc:
        https://www.terraform.io/docs/cloud/api/workspaces.html#list-workspaces

    Args:
        ws_id (string): workspace ID can be found in the workspace settings

    Returns:
        string: name of the workspace
    """
    name = api.workspaces.list(ws_id)['data'][0]['attributes']['name']
    return name

def find_resources (ws_id, resource_name_keyword):
    """Finds resources created in the root module and any child modules in the workspace.

    Related Doc:
        https://www.terraform.io/docs/cloud/api/state-versions.html#fetch-the-current-state-version-for-a-workspace

    Args:
        ws_id (string): workspace ID can be found in the workspace settings
        resource_name_keyword (string): a keyword matching the beginning of the resource name(s) you are trying to find

    Returns:
        list: resource addresses whose names start with the resource_name_keyword
    """
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
    """Generates the appropriate payload to trigger a run on the specified workspace replacing the listed resources addresses.

    Related Doc:
        https://www.terraform.io/docs/cloud/api/run.html#create-a-run

    Args:
        ws_id (string): workspace ID can be found in the workspace settings
        resources (list): resource addresses you want to target with a replace
        payload (json): a valid json object which will be used as the API payload template

    Returns:
        string: the triggered run ID
    """
    payload['data']['attributes']['replace-addrs'] = resources
    payload['data']['relationships']['workspace']['data']['id'] = ws_id
    resp = api.runs.create(payload)['data']['id']
    return resp

def run_status (run_id):
    """[summary]

    Related Doc:
        https://www.terraform.io/docs/cloud/api/run.html#get-run-details

    Args:
        run_id (string): run ID who's status you want to retrieve

    Returns:
        string: status of the run
    """
    status = api.runs.show(run_id)['data']['attributes']['status']
    return status

print("-------------------------------------")
print("TFC Organization Name: " + org_name)
print("TFC Workspace ID: " + ws_id)
print("Resource Name FIlter: " + resource_name_keyword)
print("-------------------------------------\n")

ws_name = workspace_name(ws_id)
resources = find_resources(ws_id, resource_name_keyword)
if len(resources) > 0:
    print("Found " + str(len(resources)) + " resources whose name(s) start with the keyword:\n")
    for r in resources:
        print("    " + r)
    run_id = replace(ws_id, resources, payload_tpl)
    status1 = run_status(run_id)
    status2 = status1
    print("\nTriggering a \'terraform apply -replace=\' to rotate the found resources...")
    print("\nLink to run: " + tfc_url + "/app/" + org_name + "/workspaces/" + ws_name + "/runs/" + run_id)
    print("\nStatus: " + status1 + "...")
    while status1 != "applied" and status1 != "errored":
        time.sleep(1)
        status2 = run_status(run_id)
        if status1 != status2:
            print("Status: " + status2 + "...")
            status1 = status2
    if status1 == "errored":
        sys.exit("Looks like something went wrong... Please see logs above.")