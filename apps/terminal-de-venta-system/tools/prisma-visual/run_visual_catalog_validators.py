# -*- coding: utf-8 -*-
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from visual_catalog_validators import main
if __name__ == '__main__':
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    raise SystemExit(main([str(repo), 'all']))
