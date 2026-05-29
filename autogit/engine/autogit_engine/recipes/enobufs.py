from __future__ import annotations
from pathlib import Path
from .base import Recipe,RecipeResult
MAX_BUFFER="128 * 1024 * 1024"
def find_function_span(text:str,function_name:str)->tuple[int,int]:
    marker=f"function {function_name}"; start=text.find(marker)
    if start<0: raise RuntimeError(f"{marker} not found")
    brace=text.find("{",start); depth=0; i=brace; n=len(text); state="code"; quote=""
    while i<n:
        ch=text[i]; nxt=text[i+1] if i+1<n else ""
        if state=="code":
            if ch=="/" and nxt=="/": state="line"; i+=2; continue
            if ch=="/" and nxt=="*": state="block"; i+=2; continue
            if ch in ("'", '"'): state="string"; quote=ch; i+=1; continue
            if ch=="`": state="template"; i+=1; continue
            if ch=="{": depth+=1
            elif ch=="}":
                depth-=1
                if depth==0:
                    end=i+1
                    while end<n and text[end] in " \t\r\n": end+=1
                    return start,end
            i+=1; continue
        if state=="line":
            if ch in "\r\n": state="code"
            i+=1; continue
        if state=="block":
            if ch=="*" and nxt=="/": state="code"; i+=2
            else: i+=1
            continue
        if state=="string":
            if ch=="\\": i+=2; continue
            if ch==quote: state="code"
            i+=1; continue
        if state=="template":
            if ch=="\\": i+=2; continue
            if ch=="`": state="code"
            i+=1; continue
    raise RuntimeError("function close not found")
class GitLsFilesBufferRecipe(Recipe):
    name="git-ls-files-enobufs"; patterns=("spawnSync git ENOBUFS","git ls-files","ENOBUFS")
    def patch_file(self,path:Path,sorted_result:bool)->bool:
        text=path.read_text(encoding="utf-8",errors="replace")
        ret='files.sort((left, right) => left.localeCompare(right))' if sorted_result else 'files'
        replacement=f'''function listTrackedFiles() {{
  const output = execFileSync("git", ["ls-files"], {{
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: {MAX_BUFFER},
    stdio: ["ignore", "pipe", "pipe"]
  }});

  const files = output
    .split(/\\r?\\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => toPosix(line));

  return {ret};
}}
'''
        start,end=find_function_span(text,"listTrackedFiles"); patched=text[:start]+replacement+"\n"+text[end:]
        if patched!=text: path.write_text(patched,encoding="utf-8",errors="replace",newline=""); return True
        return False
    def apply(self,ctx,text:str|None=None)->RecipeResult:
        rows=[]
        for rel,sort in [("tools/scripts/report_repo_hygiene.mjs",False),("tools/scripts/report_codeowners_coverage.mjs",True)]:
            p=ctx.repo/rel
            if p.exists(): rows.append({"path":rel,"changed":self.patch_file(p,sort)})
        return RecipeResult(self.name,bool(rows),{"files":rows})
