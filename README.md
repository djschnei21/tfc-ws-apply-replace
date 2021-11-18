# tfc-ws-cred-replace
## Usage
1. Set an environment variable "TFC_TOKEN" equal to a valid TFC token with adequate permissions
2. run `python3 rotate.py <org name> <workspace ID> <resource name filter>` where `org name` is the name of the org that contains your workspace, `workspace ID` is the ws-xxxxxxxxxxxx formatted ID of your target workspace, and `resource name filter` is a string that prepends the name of the resources you're trying to rotate

Example: `python3 rotate.py djs-admin ws-Zh2kBGmXrh5hgBxA workspace_creds`