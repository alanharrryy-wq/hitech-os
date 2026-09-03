from __future__ import annotations
from typing import Any

def evidence(mode:str,status:str,*,target_id:str,transaction_id:str|None=None,details:dict[str,Any]|None=None)->dict[str,Any]:
    return {"schema":"prisma.visual.application.result.v1","mode":mode,"status":status,"targetId":target_id,"transactionId":transaction_id,"evidenceClassification":"SOURCE_STATIC_ONLY","runtimeVisualGreen":False,"ready":False,"doesNotProve":["browser rendering","runtime visual certification","production readiness","all-surface correctness","authorization beyond the exact governed target"],"details":details or {}}
