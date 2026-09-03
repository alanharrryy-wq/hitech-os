from __future__ import annotations
import json, tempfile
from pathlib import Path
from visual_application.hashing import sha256_file


def make_repo():
    td=tempfile.TemporaryDirectory(); root=Path(td.name)
    source=root/'prisma-html/authority/rifat/tablet/runtime-sources/test.css'
    output=root/'apps/terminal-de-venta-system/products/tablet/test.css'
    source.parent.mkdir(parents=True); output.parent.mkdir(parents=True)
    source.write_text('.button {\n  color: red;\n  border-radius: 4px;\n}\n',encoding='utf-8')
    output.write_bytes(source.read_bytes())
    manifest=root/'prisma-html/authority/rifat/visual-source-manifest.json'; manifest.parent.mkdir(parents=True,exist_ok=True)
    entry={"surface":"tablet","kind":"test","source":"prisma-html/authority/rifat/tablet/runtime-sources/test.css","output":"apps/terminal-de-venta-system/products/tablet/test.css","sourceSha256":sha256_file(source),"outputSha256":sha256_file(output),"projectionMode":"exact-byte-copy","generated":True,"manualEditsForbidden":True}
    manifest.write_text(json.dumps({"schema":"prisma.rifat.visual-source-manifest.v2","surfaceCount":1,"entryCount":1,"projectionCount":1,"entries":[entry]},indent=2)+'\n',encoding='utf-8')
    tx=root/'transactions'
    def provider():
        current=sha256_file(source)
        return {"records":[{"targetId":"TGT.TEST","surface":"tablet","selector":".button","bindingId":"BND.TEST","layerId":"LYR.TEST","semanticMeaningId":"ACT.primary","recipeId":"REC.button.primary","adapterId":"ADP.TEST","canonicalSourcePath":entry['source'],"generatedOutputPath":entry['output'],"sourceSha256":current,"outputSha256":sha256_file(output),"projectionMode":"exact-byte-copy","manualEditsForbidden":True,"status":"APPLY_READY","blockers":[]}]}
    def request(mode='APPLY',color='blue'):
        return {"schema":"prisma.visual.application.request.v1","mode":mode,"targetId":"TGT.TEST","expectedSourceSha256":sha256_file(source),"surface":"tablet","includeSurfaces":["tablet"],"excludeSurfaces":["pc","mobile","web","chart-lab","control-center","shared-ui"],"semanticMeaningId":"ACT.primary","bindingId":"BND.TEST","layerId":"LYR.TEST","adapterId":"ADP.TEST","recipeId":"REC.button.primary","operations":[{"type":"cssDeclarations","path":".button","values":{"color":color}}]}
    return td,root,source,output,manifest,tx,provider,request
