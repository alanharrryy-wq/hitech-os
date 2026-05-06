#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
PLUGIN_ID='verifier.project-capability-pack'
PLUGIN_VERSION='1.0.0'
PLUGIN_DESCRIPTION='Verifica capability packs universales'
PLUGIN_MIN_RUNTIME='6.0.0'
PLUGIN_KIND='verifier'
PLUGIN_PHASE='verifier'
from pathlib import Path
def verify(context=None, **kwargs):
    root = context.get('root_dir') if isinstance(context, dict) else None
    if not root: return {'ok':False,'reason':'missing-root-dir'}
    from capatch_packs.dependency_map.verifier import verify_project
    return verify_project(Path(str(root)))
def register(api):
    if hasattr(api, 'register_verifier'): api.register_verifier(verify)

