#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
PLUGIN_ID='recommender.project-capability-pack'
PLUGIN_VERSION='1.0.0'
PLUGIN_DESCRIPTION='Recomienda capability packs universales'
PLUGIN_MIN_RUNTIME='6.0.0'
PLUGIN_KIND='recommender'
PLUGIN_PHASE='recommender'
def recommend(context=None, **kwargs):
    return [{'proposal_id':'capability.dependency-map.install','title':'Instalar dependency-map','family':'project-capability','risk_level':'low','reversible':True}]
def register(api):
    if hasattr(api, 'register_recommender'): api.register_recommender(recommend)

