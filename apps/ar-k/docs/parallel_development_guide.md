# Parallel Development Guide

Teams can build engines in parallel only if they respect the constitution:
- do not change canonical contracts from inside engine folders
- do not invent extra states or registry families
- keep imports thin and side-effect free
- declare every new artifact and event in the manifest
- update docs and tests together with any contract or ownership change
