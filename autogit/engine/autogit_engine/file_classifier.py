from __future__ import annotations
from dataclasses import dataclass
from .file_metadata import FileMeta
SKIP_DIR_PARTS={".git","node_modules",".next","out","dist","build","coverage",".turbo",".cache",".vite",".parcel-cache","storybook-static","__pycache__",".pytest_cache",".prisma_installer_backups"}
EVIDENCE_HINTS=["/evidence/","/receipts/","/receipt/","/reports/","/report/","/logs/","/log/","/diagnostic/","/diagnostics/","/rollback/","/rollbacks/","/backup/","/backups/"]
HARD_SKIP_EXTS={".zip",".7z",".rar",".tar",".gz",".tgz",".bz2",".xz",".iso",".dmg",".exe",".dll",".pdb",".msi",".apk",".ipa",".sqlite",".sqlite3",".db",".db-shm",".db-wal",".pem",".key",".p12",".pfx",".crt",".cer"}
@dataclass
class Decision:
    action:str; group:str; reason:str
def classify(meta:FileMeta)->Decision:
    low="/"+meta.rel.lower().replace("\\","/"); parts=[p for p in low.split("/") if p]
    if meta.status=="D" or not meta.exists: return Decision("include","cleanup","tracked deletion")
    if any(h in low for h in EVIDENCE_HINTS): return Decision("trash" if meta.status=="??" else "reject","evidence","generated evidence/log/report")
    if any(p in SKIP_DIR_PARTS for p in parts[:-1]): return Decision("reject","generated","generated/cache directory")
    if meta.ext in HARD_SKIP_EXTS: return Decision("reject","hard-ext",f"hard blocked extension {meta.ext}")
    name=parts[-1] if parts else meta.rel.lower()
    if name in {"package.json","pnpm-lock.yaml","package-lock.json","yarn.lock"}: return Decision("include","deps","dependency metadata")
    if "/docs/" in low or meta.ext in {".md",".mdx"}: return Decision("include","docs","documentation")
    if "prisma-control-center/" in low: return Decision("include","control-center","control center")
    if meta.ext in {".png",".jpg",".jpeg",".webp",".gif",".ico",".bmp",".mp3",".wav",".mp4",".mov",".pdf"}: return Decision("include","assets","allowed asset") if meta.size<25*1024*1024 else Decision("reject","asset-large","asset too large")
    if meta.ext in {".py",".ps1",".psm1",".sh",".bat",".cmd"} or "/tools/" in low or "/scripts/" in low: return Decision("include","tooling","tooling")
    if meta.ext in {".ts",".tsx",".js",".jsx",".css",".scss",".html"}: return Decision("include","app-surfaces","app surface")
    if meta.is_text: return Decision("include","misc","text misc")
    return Decision("reject","unknown-binary","unknown binary")
