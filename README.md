# tfc-ws-resource-replace
## What does it do?
This script targets a TFC workspace and runs the equivalent of a `terraform apply -replace=[]` on a dynamic set of resources determined by a provided keyword

## Why?
In certain TFC implementations, people will use a tightly controlled organization and workspace to create child organizations and workspaces. This is commonly referred to as the `workspace vending machine` approach.  In this model, the parent workspace is also responsible for managing the child's workspace credentials in the form of sensitive workspace variables.  Using this script, you can schedule the rotation of those credentials.  

## Usage
1. Set an environment variable `TFC_TOKEN` equal to a valid TFC token with adequate permissions
2. run `python3 rotate.py <org name> <workspace ID> <resource name filter>` where:
- `org name`: is the name of the org that contains your workspace
- `workspace ID`: is the ws-xxxxxxxxxxxxxxxx formatted ID of your target workspace
- `resource name filter`: is the beginning of the resource name string

## Example 
My parent workspace creates a child workspace and an IAM user specific to the child workspace.  It then generates `aws_iam_access_key` credentials and assigns them to the child workspace as a sensitive variable:
```terraform
resource "aws_iam_user" "iam_user" {
  name = "tfc_workspace_${tfe_workspace.workspace.name}"
}

resource "aws_iam_user_policy_attachment" "iam_user_policy_attach" {
  user       = aws_iam_user.iam_user.name
  policy_arn = var.workspace_iam_policy
}

resource "aws_iam_access_key" "workspace_creds" {
  user = aws_iam_user.iam_user.name
}
```
If I wanted to replace/rotate the resource `aws_iam_access_key`, I would use the resources given name `workspace_creds`

`python3 rotate.py some-org ws-xxxxxxxxxxxxxxxx workspace_creds`

This script can be scheduled to rotate the credentials limiting the risk of bad terraform code leaking the sensitive variables.