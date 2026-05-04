#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
PLUGIN_ID='fixer.project-capability-pack'
PLUGIN_VERSION='1.0.0'
PLUGIN_DESCRIPTION='Declara fixer advisory para capability packs'
PLUGIN_MIN_RUNTIME='6.0.0'
PLUGIN_KIND='fixer'
PLUGIN_PHASE='fixer'
def fix(context=None, **kwargs):
    return {'status':'advisory-only','message':'Use --capability dependency-map --capability-action install'}
def register(api):
    if hasattr(api, 'register_fixer'): api.register_fixer(fix)

