# tfc-ws-resource-replace
## What does it do?

## Usage
1. Set an environment variable "TFC_TOKEN" equal to a valid TFC token with adequate permissions
2. run `python3 rotate.py <org name> <workspace ID> <resource name filter>` where:
`org name`: is the name of the org that contains your workspace
`workspace ID`: is the ws-xxxxxxxxxxxxxxxx formatted ID of your target workspace
`resource name filter`: is the beginning of the resource name string

## Example 

For the below terraform code:
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

`python3 rotate.py djs-admin ws-Zh2kBGmXrh5hgBxA workspace_creds`