import os
from terrasnek.api import TFC

TFC_TOKEN = os.getenv("TFC_TOKEN", None)
TFC_ORG = os.getenv("TFC_ORG", None)
TFC_URL = "https://app.terraform.io"


api = TFC(TFC_TOKEN, url=TFC_URL)
api.set_org(TFC_ORG)