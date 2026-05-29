from __future__ import annotations
import os,platform,sys
def info(): return {"python":sys.version,"platform":platform.platform(),"cwd":os.getcwd(),"env":{k:v for k,v in os.environ.items() if k.startswith("AUTOGIT_")}}
