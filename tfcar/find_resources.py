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