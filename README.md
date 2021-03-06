# tfc-ws-apply-replace
## What does it do?
This script targets a TFC workspace and runs the equivalent of a `terraform apply -replace=[]` on a dynamic set of resources determined by a provided keyword

## Why?
In certain TFC implementations, people will use a tightly controlled organization and workspace to create child organizations and workspaces. This is commonly referred to as the `workspace vending machine` approach.  In this model, the parent workspace is also responsible for managing the child workspace's credentials in the form of sensitive workspace variables.  However, setting those variables once and never rotating them introduces some risk.  Using this script, you can schedule the rotation of those credentials (or any other type of resource).  

## Usage
1. Set an environment variable `TFC_TOKEN` equal to a valid TFC token with adequate permissions
```
usage: tfc-apply-replace [-h] --org ORG --ws WS --keyword KEYWORD [--message MESSAGE] [-a]

Tool to perform dynamic terraform applies w/replacement on TFC using resource name keywords.

optional arguments:
  -h, --help         show this help message and exit
  --org ORG          Name of the org you're targeting (default: None)
  --ws WS            ID of the workspace you're targeting (default: None)
  --keyword KEYWORD  Keyword matching the beginning of the resource name(s) you are trying to find (default: None)
  --message MESSAGE  Message to be displayed in TFC GUI as the reason for the run (default: API Triggered Key Rotation)
  -a, --auto         Whether or not to auto apply the plan (default: False)
```

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

resource "tfe_variable" "aws_access_key_id" {
  key          = "AWS_ACCESS_KEY_ID"
  category     = "env"
  value        = aws_iam_access_key.workspace_creds.id
  workspace_id = tfe_workspace.workspace.id
}

resource "tfe_variable" "aws_secret_access_key" {
  key          = "AWS_SECRET_ACCESS_KEY"
  category     = "env"
  sensitive    = true
  value        = aws_iam_access_key.workspace_creds.secret
  workspace_id = tfe_workspace.workspace.id
}
```
If I wanted to replace/rotate the resource `aws_iam_access_key` (and by relation any resource that depends on it, i.e. the `tfe_variable.aws_secret_access_key` resource), I would use the resources given name `workspace_creds`

```
tfc-apply-replace --org djs-admin --ws ws-Zh2kBGmXrh5hgBxA --keyword workspace_creds
-------------------------------------
TFC Organization Name: some-org
TFC Workspace ID: ws-xxxxxxxxxxxxxxxx
Resource Name FIlter: workspace_creds
Auto Apply: False
-------------------------------------

Found 1 resources whose name(s) start with the keyword:

    module.ws_vending_machine["djs-ec2"].aws_iam_access_key.workspace_creds

Triggering a 'terraform apply -replace=' to rotate the found resources...

Link to run: https://app.terraform.io/app/some-org/workspaces/ws-xxxxxxxxxxxxxxxx/runs/run-xxxxxxxxxxxxxxxx

Status: planning...
Status: cost_estimating...
Status: cost_estimated...

!! Plan is waiting for approval in the GUI, please click the URL provided above !!

Status: confirmed...
Status: applying...
Status: applied...
```
While this workspace manages 23 resources in total, you can see below the script targeted only the resources needed to rotate the downstream workspace's access keys:
![screen shot](https://github.com/djschnei21/tfc-ws-resource-replace/raw/main/screenshot.png)
This script can be scheduled to rotate the credentials limiting the risk of bad terraform code leaking the sensitive variables.