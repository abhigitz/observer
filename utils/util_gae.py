import sys
import os

IS_NT = os.name.lower()=="nt"
if IS_NT:
  gae_sdk_path = os.path.join(os.environ["ProgramFiles"], "Google", "google_appengine")
else:
  gae_sdk_path=os.path.abspath(os.environ["MY_GAE_SDK_PATH"])
  
def FixSysPath():
    if not os.path.exists(gae_sdk_path):
        raise Exception("Path: {} does not exists".format(gae_sdk_path))

    if gae_sdk_path not in sys.path:
        sys.path.insert(0, gae_sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
