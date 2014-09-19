##############################################################################
## Intent: To be single point of contact for pushing the version to gae sever
## Date: 2014-Mar-31 Mon 03:10 PM
## Author: Ashish Anand
##############################################################################

from Util.Misc import PrintInBox, cd, YYYY_MM_DD
from Util.Persistent import Persistent
from util_gae import FixSysPath, gae_sdk_path

import argparse
import json
import os
import subprocess

HASH_SECTION = "DEFAULT"

UBEROBSERVERDIR = os.environ["UBEROBSERVERDIR"]
RELATIVE_JS_PATH = os.path.join("static", "js")
RELATIVE_CSS_PATH = os.path.join("static", "css")
PMT_PREFIX = "PMT"
ORDER_PREFIX = "ORDER"
KMO_PREFIX = "KMO"
FORMC_PREFIX = "FORMC"
RAW_MAT_PREFIX = "RAWMAT"

DB_LOOKUP_PATH  = os.path.abspath(os.path.join(UBEROBSERVERDIR, "static", "dbs"))

APPS=[
    os.path.join(os.path.dirname(UBEROBSERVERDIR), "GZBDocs"),
    #Well somebody has to know all the paths. The apps are independent but this app by very nature needs to know what all apps need to be merged.
    ]

def ParseArguments():
  p = argparse.ArgumentParser(description='Process some integers.')
  p.add_argument("--localTesting", "-l", dest="localTesting", action="store_true", default=False, help="If present things will not be pushed to the local server")
  p.add_argument("-V", "--version", dest="version", default="live", help="version to update - dev/live")
  p.add_argument("--email", dest="email", default="moc.slootdnaseiddradnats@repoleved"[::-1], help="email of the uploader")
  p.add_argument("--oauth2", dest="oauth2", action="store_true", default=False, help="Use oauth2 if specified")
  p.add_argument("-f", "--force-upload", dest="forceUpload", action="store_true", default=False, help="If present, app will be uploaded whether data is new or not")

  args = p.parse_args()
  return args

def DuePmtWithInterest(customer):
  INTEREST_PER_ANNUM = 5.0
  if not customer["trust"]:
    raise Exception("{} has no trust. Please fix the db")
  ONE_DAY_EFFECTIVE_INTEREST = INTEREST_PER_ANNUM/(12.0*365.0*float(customer["trust"]))
  return sum([float(b["ba"]) * ONE_DAY_EFFECTIVE_INTEREST for b in customer["bills"]])

def MergeAllJsons():
  MergeRawMaterialJsons()
  MergePendingFormCJsons()
  MergeKMOrdersJsons()
  MergePaymentJsons()
  MergeOrdersJsons()

def MergeOrdersJsons():
  finalJsonPath = os.path.join(DB_LOOKUP_PATH, "order.json")
  if os.path.exists(finalJsonPath):
    os.remove(finalJsonPath)
  def AddSingleOrder(argData, singleOrder):
    oDate = singleOrder["oDate"]
    data = argData[:]
    for obj in data:
      #Add it in data
      if obj["date"] == oDate:
        obj["orders"].append(singleOrder)
        break
    else:
      obj = dict()
      obj["date"]= oDate
      obj["orders"] = list()
      obj["orders"].append(singleOrder)
      data.append(obj)
    return data

  for fp in os.listdir(DB_LOOKUP_PATH):
    if fp.startswith(ORDER_PREFIX) and os.path.splitext(fp)[1] == ".json":
      jsonFilePath = os.path.join(DB_LOOKUP_PATH, fp)
      with open(jsonFilePath, "r") as f:
        jsonData = json.load(f)
        #Every Object in read jsonData is a complete order.
        data = list()
        for singleOrder in jsonData:
          data = AddSingleOrder(data, singleOrder)

  data = sorted(data, key=lambda obj: YYYY_MM_DD(obj["date"]))
  with open(finalJsonPath, "w") as f:
    json.dump(data, f, separators=(',',':'), indent=0)
  return


def MergeKMOrdersJsons():
  finalJsonPath = os.path.join(DB_LOOKUP_PATH, "kmOrder.json")
  if os.path.exists(finalJsonPath):
    os.remove(finalJsonPath)

  from collections import OrderedDict
  finalKMOrders = OrderedDict()
  finalShowVerbatimOnTopData = list()
  finalShowVerbatimOnTopDateISO = dict()

  for fp in os.listdir(DB_LOOKUP_PATH):
    if fp.startswith(KMO_PREFIX) and os.path.splitext(fp)[1] == ".json":
      jsonFilePath = os.path.join(DB_LOOKUP_PATH, fp)
      with open(jsonFilePath, "r") as f:
        jsonData = json.load(f)
        finalKMOrders.update(jsonData["allKMOrders"])#Since the kmorders are uniquely idetified by combination of pelletsize and compname we dont risk a data overwriting here.
        finalShowVerbatimOnTopData.append(jsonData["showVerbatimOnTop"])
        if "showVerbatimOnTopDateISO" in jsonData: #TODO: Delete once it is finalized
          finalShowVerbatimOnTopDateISO.update(jsonData["showVerbatimOnTopDateISO"])

  finalKMOrders = sorted(finalKMOrders.items(), key=lambda o: o[0])

  finalJsonData = {
      "kmOrders": finalKMOrders,
      "showVerbatimOnTop": finalShowVerbatimOnTopData,
      "showVerbatimOnTopDateISO" : finalShowVerbatimOnTopDateISO,
      }

  with open(finalJsonPath, "w") as f:
    json.dump(finalJsonData, f, separators=(',',':'), indent=0)
  return

def MergePendingFormCJsons():
  finalJsonPath = os.path.join(DB_LOOKUP_PATH, "formC.json") #TODO: Json file names are hardcoded in two places. Read them from one place.
  if os.path.exists(finalJsonPath):
    os.remove(finalJsonPath)

  finalShowVerbatimOnTopData = list()
  finalFormC = list()

  for fp in os.listdir(DB_LOOKUP_PATH):
    if fp.startswith(FORMC_PREFIX) and os.path.splitext(fp)[1] == ".json":
      jsonFilePath = os.path.join(DB_LOOKUP_PATH, fp)
      with open(jsonFilePath, "r") as f:
        jsonData = json.load(f)
        finalFormC.extend(jsonData["allCompsFormC"])
        finalShowVerbatimOnTopData.append(jsonData["showVerbatimOnTop"])

  finalFormC = sorted(finalFormC, key=lambda f: min(f["yd"]))

  finalJsonData = {
      "allCompsFormC": finalFormC,
      "showVerbatimOnTop": finalShowVerbatimOnTopData,
      }

  with open(finalJsonPath, "w") as f:
    json.dump(finalJsonData, f, separators=(',', ':'), indent=0)
  return

def MergeRawMaterialJsons():
  from names import HOSTED_RAW_MATERIAL_JSON_NAME
  finalJsonPath = os.path.join(DB_LOOKUP_PATH, HOSTED_RAW_MATERIAL_JSON_NAME)
  if os.path.exists(finalJsonPath):
    os.remove(finalJsonPath)

  finalRawMaterial = list()
  finalShowVerbatimOnTopData = list()

  for fp in os.listdir(DB_LOOKUP_PATH):
    if fp.startswith(RAW_MAT_PREFIX) and os.path.splitext(fp)[1] == ".json":
      jsonFilePath = os.path.join(DB_LOOKUP_PATH, fp)
      with open(jsonFilePath, "r") as f:
        jsonData = json.load(f)
        finalRawMaterial += jsonData["parts"]
        finalShowVerbatimOnTopData.extend(jsonData["showVerbatimOnTop"])
  finalRawMaterial = sorted(finalRawMaterial, key=lambda x: x["diff"], reverse=False)

  finalJsonData = {
      "parts": finalRawMaterial,
      "showVerbatimOnTop": finalShowVerbatimOnTopData,
      }

  with open(finalJsonPath, "w") as f:
    json.dump(finalJsonData, f, separators=(',',':'), indent=0)
  return

def MergePaymentJsons():
  finalJsonPath = os.path.join(DB_LOOKUP_PATH, "pmt.json")
  if os.path.exists(finalJsonPath): os.remove(finalJsonPath)

  finalCutomers = list()
  finalShowVerbatimOnTopData = list()

  for fp in os.listdir(DB_LOOKUP_PATH):
    if fp.startswith(PMT_PREFIX) and os.path.splitext(fp)[1] == ".json":
      jsonFilePath = os.path.join(DB_LOOKUP_PATH, fp)
      with open(jsonFilePath, "r") as f:
        jsonData = json.load(f)
        finalCutomers += jsonData["customers"]
        finalShowVerbatimOnTopData.append(jsonData["showVerbatimOnTop"])
  #finalCutomers = sorted(finalCutomers, key=lambda c: c["name"])
  finalCutomers = sorted(finalCutomers, key=DuePmtWithInterest, reverse=True)

  finalJsonData = {
      "customers": finalCutomers,
      "showVerbatimOnTop": finalShowVerbatimOnTopData,
      }

  with open(finalJsonPath, "w") as f:
    json.dump(finalJsonData, f, separators=(',',':'), indent=0)
  return

class PersistentLastModifiedTimeOfBillsForJsonDataCheck(Persistent):
  def __init__(self):
    super(PersistentLastModifiedTimeOfBillsForJsonDataCheck, self).__init__(self.__class__.__name__)


def _InvokeJsonGenerationApp(app):
  #Assumption: All apps have similar structure. If structure changes, the following logic will change too.
  pythonApp = os.path.join(app, "code", "whopaid", "json_data_generator.py")
  dbGenerateCmd = "python \"{a}\" --generate-json".format(a=pythonApp)
  with cd(os.path.dirname(pythonApp)):
    PrintInBox("Running: {}".format(dbGenerateCmd))
    subprocess.check_call(dbGenerateCmd, shell=True)

  return

def GenerateMergedJsonsForApps():
  anythingChanged = False
  for app in APPS:
    billsDir = os.path.abspath(os.path.join(app, "entries")) #Hack: We are storing parent directory path because name of bills file is different in different apps but "Bills" name of dir is constant.
    p = PersistentLastModifiedTimeOfBillsForJsonDataCheck()
    if billsDir in p:
      if p[billsDir] == os.stat(billsDir).st_mtime:
        #If same as last time, then dont invoke the app
        continue
    _InvokeJsonGenerationApp(app)
    anythingChanged = True
    p[billsDir] = os.stat(billsDir).st_mtime

  if anythingChanged:
    MergeAllJsons()
    ExecuteUnitTests()

  return anythingChanged


def ExecuteUnitTests():
  unitTestsPath = os.path.normpath(os.path.join(UBEROBSERVERDIR, "utils", "unittests.py"))
  if not os.path.exists(unitTestsPath):
    raise Exception("Path does not exist: {}".format(unitTestsPath))

  subprocess.check_call("python {}".format(unitTestsPath), shell=True) #Run unit tests
  return

def main():
  print("Inside observer.push.py main() ...")
  args = ParseArguments()

  anythingChanged = GenerateMergedJsonsForApps()

  if args.localTesting:
    return

  if args.forceUpload or anythingChanged:
    #If we have to have to upload then...
    UploadAppOnGoogleAppEngine(args)
    return

  if not anythingChanged:
    PrintInBox("App Engine seems upto date. Not uploading ...")
  return

def UploadAppOnGoogleAppEngine(args):
  PrintInBox("Uploading the app on Google App Engine")

  #MinifyAllCSS(os.path.join(UBEROBSERVERDIR, RELATIVE_CSS_PATH))
  #MinifyAllJavascripts(os.path.join(UBEROBSERVERDIR, RELATIVE_JS_PATH))

  appcfgPath = os.path.normpath(os.path.join(gae_sdk_path, "appcfg.py"))
  if not os.path.exists(appcfgPath):
    raise Exception("Path does not exist: {}".format(appcfgPath))
  oauth2 = "--oauth2 --noauth_local_webserver" if args.oauth2 else ""
  updateCmd = "python \"{a}\" --version={v} --email={e} {oauth} update {w}".format(a=appcfgPath, v=args.version, e=args.email,w=UBEROBSERVERDIR, oauth=oauth2)
  subprocess.check_call(updateCmd, shell=True)
  #SaveNewHash() #TODO: Better naming for these methods
  return


if __name__ == '__main__':
  FixSysPath()
  main()
