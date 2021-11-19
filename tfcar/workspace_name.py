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