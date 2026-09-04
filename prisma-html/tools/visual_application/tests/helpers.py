from __future__ import annotations
import hashlib, io, json, tempfile, zipfile
from pathlib import Path
from visual_application.hashing import sha256_file

def _canonical_digest(value):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def make_repo():
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    source=root/'prisma-html/authority/rifat/tablet/runtime-sources/test.css'
    output=root/'apps/terminal-de-venta-system/products/tablet/test.css'
    source.parent.mkdir(parents=True); output.parent.mkdir(parents=True)
    source.write_text('.button {\n  color: red;\n  border-radius: 4px;\n}\n',encoding='utf-8')
    output.write_bytes(source.read_bytes())
    manifest=root/'prisma-html/authority/rifat/visual-source-manifest.json'; manifest.parent.mkdir(parents=True,exist_ok=True)
    entry={"surface":"tablet","kind":"test","source":"prisma-html/authority/rifat/tablet/runtime-sources/test.css",
           "output":"apps/terminal-de-venta-system/products/tablet/test.css","sourceSha256":sha256_file(source),
           "outputSha256":sha256_file(output),"projectionMode":"exact-byte-copy","generated":True,"manualEditsForbidden":True}
    manifest.write_text(json.dumps({"schema":"prisma.rifat.visual-source-manifest.v2","surfaceCount":1,"entryCount":1,"projectionCount":1,"entries":[entry]},indent=2)+'\n',encoding='utf-8')
    tx=root/'prisma-html/.gvae-transactions'
    def provider():
        current=sha256_file(source)
        return {"records":[{"targetId":"TGT.TEST","surface":"tablet","selector":".button","jsonRoot":None,
            "bindingId":"BND.TEST","layerId":"LYR.TEST","implementationLayerId":"impl.test",
            "semanticMeaningId":"ACT.primary","recipeId":"REC.button.primary","adapterId":"ADP.TEST",
            "canonicalSourcePath":entry['source'],"generatedOutputPath":entry['output'],"sourceSha256":current,
            "outputSha256":sha256_file(output) if output.exists() else None,"projectionMode":"exact-byte-copy",
            "manualEditsForbidden":True,"status":"APPLY_READY","blockers":[]}],"globalBlockers":[]}
    def request(mode='APPLY',color='blue'):
        req={"schema":"prisma.visual.application.request.v1","mode":mode,"targetId":"TGT.TEST",
             "expectedSourceSha256":sha256_file(source),"surface":"tablet","includeSurfaces":["tablet"],
             "excludeSurfaces":["pc","mobile","web","chart-lab","control-center","shared-ui"],
             "semanticMeaningId":"ACT.primary","bindingId":"BND.TEST","layerId":"LYR.TEST",
             "adapterId":"ADP.TEST","recipeId":"REC.button.primary",
             "operations":[{"type":"cssDeclarations","path":".button","values":{"color":color}}]}
        if mode=="APPLY":
            req["authorityCommit"]="a"*40
            req["authorization"]={
                "task":"Synthetic governed visual application test.","authorityTaskId":"gvae-test",
                "authorityMeshArtifact":"evidence/mesh.zip","authorityMeshArtifactSha256":"b"*64,
                "authorityMeshRequestDigest":"c"*64,"uiBridgePlanPath":"evidence/plan.json",
                "uiBridgePlanSha256":"d"*64,"uiBridgeSemanticDiffPath":"evidence/diff.json",
                "uiBridgeSemanticDiffSha256":"e"*64}
        return req
    def auth(*args,**kwargs): return {"status":"PASS_TEST_AUTHORITY","mesh":{"status":"PASS_COMPOSED_AUTHORITY_MESH"}}
    return td,root,source,output,manifest,tx,provider,request,auth

def make_json_repo():
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    source=root/'prisma-html/authority/rifat/data/test.json'
    output=root/'apps/terminal-de-venta-system/products/tablet/test.json'
    source.parent.mkdir(parents=True); output.parent.mkdir(parents=True)
    source.write_text('{"visual":{"a":1,"arr":[1,2]},"outside":5}\n',encoding='utf-8'); output.write_bytes(source.read_bytes())
    manifest=root/'prisma-html/authority/rifat/visual-source-manifest.json'; manifest.parent.mkdir(parents=True,exist_ok=True)
    entry={"surface":"tablet","source":"prisma-html/authority/rifat/data/test.json","output":"apps/terminal-de-venta-system/products/tablet/test.json",
           "sourceSha256":sha256_file(source),"outputSha256":sha256_file(output),"projectionMode":"exact-byte-copy","manualEditsForbidden":True}
    manifest.write_text(json.dumps({"entries":[entry]},indent=2)+'\n',encoding='utf-8')
    def provider():
        return {"records":[{"targetId":"TGT.JSON","surface":"tablet","selector":None,"jsonRoot":"/visual",
            "bindingId":"BND.JSON","layerId":"LYR.JSON","implementationLayerId":"impl.json","semanticMeaningId":"TOK.visual",
            "recipeId":"REC.JSON","adapterId":"ADP.TEST","canonicalSourcePath":entry["source"],"generatedOutputPath":entry["output"],
            "sourceSha256":sha256_file(source),"outputSha256":sha256_file(output),"projectionMode":"exact-byte-copy",
            "manualEditsForbidden":True,"status":"APPLY_READY","blockers":[]}],"globalBlockers":[]}
    def request(mode="PREVIEW",values=None,path="/visual"):
        values=values or {"/visual/a":2}
        return {"schema":"prisma.visual.application.request.v1","mode":mode,"targetId":"TGT.JSON","expectedSourceSha256":sha256_file(source),
            "surface":"tablet","includeSurfaces":["tablet"],"excludeSurfaces":[],"semanticMeaningId":"TOK.visual","bindingId":"BND.JSON",
            "layerId":"LYR.JSON","adapterId":"ADP.TEST","recipeId":"REC.JSON","operations":[{"type":"jsonValues","path":path,"values":values}]}
    return td,root,source,output,manifest,provider,request

def make_mesh_artifact(root:Path, task_id="gvae-test", head="a"*40, request_digest="c"*64):
    ev=root/"evidence"; ev.mkdir(parents=True,exist_ok=True)
    legacy_buf=io.BytesIO()
    cert={"status":"PASS","read_only_repo":True,"provenance_verified":True,
          "repo_drift":{"stable":True,"changed_count":0},
          "children":[{"task_id":task_id,"returncode":0,"manifest_status":"PASS","provenance":{"verified":True}}]}
    with zipfile.ZipFile(legacy_buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("PARALLEL_CERTIFICATION.json",json.dumps(cert))
        z.writestr(f"tasks/{task_id}/authority_mesh/reports/LAYERS_MAP.json",json.dumps({"status":"PASS","layers":[{"id":"x"}]}))
    composed_buf=io.BytesIO()
    report={"status":"PASS_COMPOSED_AUTHORITY_MESH","repoHead":head,"requestDigest":request_digest}
    preflight={"status":"PASS_PREFLIGHT","repoHead":head,"blockers":[],"lanes":[{"id":task_id,"coverage":{"resolvedPercent":100.0},"missing":[]}]}
    with zipfile.ZipFile(composed_buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("PRISMA_MESH_GATEWAY_REPORT.json",json.dumps(report))
        z.writestr("authority/PREFLIGHT_MANIFEST.json",json.dumps(preflight))
        z.writestr("legacy_surface_mesh.zip",legacy_buf.getvalue())
    artifact=ev/"mesh.zip"
    with zipfile.ZipFile(artifact,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("prisma-automesh-composed-result.zip",composed_buf.getvalue())
    return artifact.relative_to(root).as_posix(), sha256_file(artifact), request_digest

def make_plan(root:Path,target:dict,properties=("color",),selector=".button"):
    ev=root/"evidence"; ev.mkdir(parents=True,exist_ok=True)
    ops=[{"unitId":"base","selector":selector,"targetResolutionStatus":"SOURCE_RESOLVED",
          "propertyChanges":[{"property":p,"instruction":{"mode":"LITERAL","value":"x"}} for p in properties]}]
    plan={"schema":"prisma.ui.bridge.plan.v1","planId":"BRPLAN."+"1"*24,"mode":"READ_ONLY_SOURCE_PLAN",
          "applicationEnabled":False,"status":"PLAN_READY_FOR_REVIEW","blockingReasons":[],
          "bindingId":target["bindingId"],"layerId":target["layerId"],"adapterId":target["adapterId"],"recipeId":target["recipeId"],
          "operations":ops}
    diff={"schema":"prisma.ui.bridge.semantic-diff.v1","planId":plan["planId"],"status":"DIFF_READY",
          "sourceMutationPerformed":False,"operations":ops,"checksum":_canonical_digest(ops)}
    pp=ev/"plan.json"; dp=ev/"diff.json"
    pp.write_text(json.dumps(plan),encoding="utf-8"); dp.write_text(json.dumps(diff),encoding="utf-8")
    return pp.relative_to(root).as_posix(),sha256_file(pp),dp.relative_to(root).as_posix(),sha256_file(dp)
