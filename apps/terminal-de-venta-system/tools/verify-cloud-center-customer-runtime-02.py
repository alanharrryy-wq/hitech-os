#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


def require(condition, code):
    if not condition:
        raise AssertionError(code)


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_http(url, timeout=20):
    end=time.time()+timeout
    last=None
    while time.time()<end:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status==200:
                    return
        except Exception as exc:
            last=exc
        time.sleep(.25)
    raise RuntimeError(f'RUNTIME_HTTP_TIMEOUT:{last}')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out-dir',required=True); args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    app=Path(__file__).resolve().parents[1]
    cloud=app/'Prisma Cloud Ctr'
    server=cloud/'internal'/'py'/'prisma_unified_lab_v3.py'
    checks=[]; console_errors=[]; request_failures=[]; api_requests=[]; draft_responses=[]
    with tempfile.TemporaryDirectory(prefix='prisma-cloud-runtime-') as td:
        td=Path(td); port=free_port(); base=f'http://127.0.0.1:{port}'
        env=os.environ.copy(); env['PRISMA_COMMAND_CENTER_DB_PATH']=str(td/'runtime.db'); env['PRISMA_CLOUD_CENTER_RUNTIME_DIR']=str(td/'runtime-contracts')
        proc=subprocess.Popen([sys.executable,str(server),'--serve','--lab-root',str(cloud),'--protected-current',str(td/'protected'),'--out-dir',str(td/'out'),'--host','127.0.0.1','--port',str(port),'--no-open'],cwd=str(cloud),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            wait_http(base+'/api/command-center/bootstrap')
            with urllib.request.urlopen(base+'/api/command-center/bootstrap',timeout=3) as r:
                bootstrap=json.load(r)
            require(bootstrap.get('customerCatalogSchemaVersion')=='1.0.0','RUNTIME_BOOTSTRAP_CATALOG_VERSION'); checks.append('runtime_bootstrap')
            require(len(bootstrap['catalogs']['state_mx']['options'])==32,'RUNTIME_STATE_OPTIONS'); checks.append('runtime_catalog_snapshot')
            try:
                from playwright.sync_api import sync_playwright
            except Exception as exc:
                raise RuntimeError('PLAYWRIGHT_NOT_INSTALLED') from exc
            with sync_playwright() as pw:
                browser=pw.chromium.launch(channel='chrome',headless=True)
                page=browser.new_page(viewport={'width':1440,'height':1000})
                page.on('console',lambda msg: console_errors.append(msg.text) if msg.type=='error' else None)
                page.on('requestfailed',lambda req: request_failures.append(req.url) if req.url.startswith(base) else None)
                page.on('request',lambda req: api_requests.append({'method':req.method,'url':req.url}) if '/api/' in req.url else None)
                page.on('response',lambda res: draft_responses.append(res) if '/api/command-center/draft-client' in res.url else None)
                page.goto(base+'/',wait_until='domcontentloaded',timeout=30000)
                # Initial boot performs asynchronous API fan-out after DOMContentLoaded. Wait for
                # that bootstrap to settle before starting operator interaction, avoiding a test-only
                # race with the first loadAll() render.
                page.wait_for_load_state('networkidle',timeout=20000)
                page.wait_for_selector('[data-surface="provisioning"]',timeout=15000)
                require(page.locator('html').get_attribute('lang')=='es-MX','HTML_LANGUAGE_NOT_HOMOLOGATED')
                require(page.locator('[data-surface="billing"]').count()==1,'BILLING_NAV_MISSING')
                nav_surfaces=page.locator('[data-surface]').evaluate_all('(els)=>els.map(e=>e.dataset.surface)')
                require(len(nav_surfaces)==len(set(nav_surfaces)),'DUPLICATE_NAV_SURFACE')
                checks.append('navigation_homologated')
                page.click('[data-surface="provisioning"]')
                page.wait_for_selector('[data-action="prepare-client"]')
                require(page.locator('[data-flow-field="vertical"]').count()==1,'VERTICAL_FIELD_DUPLICATED')
                require(page.locator('[data-flow-field="cityZone"]').count()==0,'LEGACY_CITY_ZONE_FIELD_VISIBLE')
                require(page.locator('[data-flow-field="plan"]').count()==0,'PLAN_DUPLICATED_IN_CUSTOMER_REGISTRATION')
                require(page.locator('[data-action="save-other-values"]').count()==0,'MANUAL_OTHER_SAVE_STILL_REQUIRED')
                for field in ('vertical','businessSize','operationMode','acquisitionChannel'):
                    require(page.locator(f'select[data-flow-field="{field}"][required]').count()==1,f'REQUIRED_FIELD_MISSING:{field}')
                checks.append('customer_form_homologated')

                vertical_button=page.locator('[data-picker-toggle="vertical"]')
                vertical_button.wait_for(state='visible',timeout=10000)
                before=page.evaluate("""()=>{const b=document.querySelector('[data-picker-toggle="vertical"]'); const p=document.querySelector('[data-picker-panel="vertical"]'); return {activeTag:document.activeElement?.tagName||null,activePicker:document.activeElement?.dataset?.pickerToggle||null,buttonConnected:!!b?.isConnected,aria:b?.getAttribute('aria-expanded')||null,panelConnected:!!p?.isConnected,panelClass:p?.className||null};}""")
                print('PICKER_DIAG_BEFORE='+json.dumps(before,ensure_ascii=False))
                vertical_button.press('Enter')
                page.wait_for_timeout(250)
                after=page.evaluate("""()=>{const b=document.querySelector('[data-picker-toggle="vertical"]'); const p=document.querySelector('[data-picker-panel="vertical"]'); const cs=p?getComputedStyle(p):null; const r=p?p.getBoundingClientRect():null; return {activeTag:document.activeElement?.tagName||null,activePicker:document.activeElement?.dataset?.pickerToggle||null,buttonConnected:!!b?.isConnected,aria:b?.getAttribute('aria-expanded')||null,panelConnected:!!p?.isConnected,panelClass:p?.className||null,display:cs?.display||null,visibility:cs?.visibility||null,opacity:cs?.opacity||null,rect:r?{x:r.x,y:r.y,w:r.width,h:r.height}:null};}""")
                print('PICKER_DIAG_AFTER='+json.dumps(after,ensure_ascii=False))
                (out/'PICKER_DIAGNOSTIC.json').write_text(json.dumps({'before':before,'after':after},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                page.wait_for_selector('[data-picker-panel="vertical"].show',state='visible',timeout=10000)
                vertical_codes=page.locator('[data-pick-flow="vertical"]').evaluate_all('(els)=>els.map(e=>e.dataset.value)')
                require('multi_branch' not in vertical_codes and 'abarrotes' in vertical_codes,'VERTICAL_DROPDOWN_DRIFT')
                require(len(vertical_codes)==len(set(vertical_codes)),'VERTICAL_DUPLICATE_OPTIONS')
                page.click('[data-pick-flow="vertical"][data-value="restaurant"]')
                page.click('[data-picker-toggle="subvertical"]')
                sub_codes=page.locator('[data-pick-flow="subvertical"]').evaluate_all('(els)=>els.map(e=>e.dataset.value)')
                require('restaurant_tables' in sub_codes and 'minisuper' not in sub_codes,'SUBVERTICAL_DEPENDENCY_DRIFT')
                checks.append('dropdown_dependency_and_keyboard')

                page.fill('[data-flow-field="displayName"]','Cliente Runtime UI')
                page.fill('[data-flow-field="email"]','runtime-ui@example.test')
                page.select_option('select[data-flow-field="vertical"]','abarrotes')
                page.select_option('select[data-flow-field="subvertical"]','minisuper')
                page.select_option('select[data-flow-field="businessSize"]','small')
                page.select_option('select[data-flow-field="operationMode"]','counter')
                page.select_option('select[data-flow-field="acquisitionChannel"]','referral')
                page.select_option('select[data-flow-field="country"]','MX')
                page.select_option('select[data-flow-field="state"]','jalisco')
                page.fill('[data-flow-field="city"]','Guadalajara')

                create_before=page.evaluate("""()=>{const button=document.querySelector('[data-action="prepare-client"]'); const fields={}; document.querySelectorAll('[data-flow-field]').forEach(el=>fields[el.dataset.flowField]=el.value); return {button:{exists:!!button,disabled:!!button?.disabled,outerHTML:button?.outerHTML||null},fields,activeTag:document.activeElement?.tagName||null,activeField:document.activeElement?.dataset?.flowField||null};}""")
                print('CREATE_DIAG_BEFORE='+json.dumps(create_before,ensure_ascii=False))
                start_request_count=len(api_requests)
                page.click('[data-action="prepare-client"]')
                page.wait_for_timeout(2000)
                create_after=page.evaluate("""()=>({bodyTail:(document.body?.innerText||'').slice(-5000),buttonDisabled:!!document.querySelector('[data-action="prepare-client"]')?.disabled,activeTag:document.activeElement?.tagName||null,activeField:document.activeElement?.dataset?.flowField||null})""")
                create_diag={'before':create_before,'after':create_after,'newApiRequests':api_requests[start_request_count:],'consoleErrors':list(console_errors),'requestFailures':list(request_failures)}
                print('CREATE_DIAG_AFTER='+json.dumps(create_diag,ensure_ascii=False))
                (out/'CREATE_CLIENT_DIAGNOSTIC.json').write_text(json.dumps(create_diag,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                require(draft_responses, f'UI_CLIENT_CREATE_NO_DRAFT_RESPONSE:{create_diag}')
                draft_response=draft_responses[-1]
                try:
                    draft_payload=draft_response.json()
                except Exception:
                    draft_payload={'raw':draft_response.text()}
                print('DRAFT_CLIENT_RESPONSE='+json.dumps({'status':draft_response.status,'payload':draft_payload},ensure_ascii=False))
                (out/'DRAFT_CLIENT_RESPONSE.json').write_text(json.dumps({'status':draft_response.status,'payload':draft_payload},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                require(draft_response.ok and draft_payload.get('ok') is not False, f'UI_CLIENT_CREATE_API_FAILED:{draft_response.status}:{draft_payload}')
                checks.append('ui_customer_create_api')
                # The provisioning surface confirms the action/result. The created customer row is
                # intentionally projected on the Customers desk, so verify it there rather than
                # requiring the customer name to be duplicated into the provisioning screen.
                page.screenshot(path=str(out/'cloud-center-customer-provisioning.png'),full_page=True)
                page.click('[data-surface="customers"]')
                page.wait_for_function("()=>document.body.innerText.includes('Medición homologada') && document.body.innerText.includes('Cliente Runtime UI')",timeout=15000)
                require(page.get_by_text('Cliente Runtime UI').count()>=1,'CUSTOMER_NOT_VISIBLE_IN_CUSTOMER_DESK')
                checks.append('ui_customer_create_projection')
                page.screenshot(path=str(out/'cloud-center-customers.png'),full_page=True)
                checks.append('customer_metrics_ui')

                page.click('[data-surface="fleet"]'); page.wait_for_selector('[data-picker-toggle="deviceRole"]')
                require(page.get_by_text('Sucursal / zona').count()==0,'DEVICE_CITY_ZONE_SEMANTIC_DUPLICATION')
                require(page.get_by_text('Se deriva del contrato/licencia.').count()>=1,'DEVICE_BRANCH_DERIVATION_COPY_MISSING')
                checks.append('device_dropdown_homologation')

                page.click('[data-surface="security"]'); page.wait_for_selector('[data-picker-toggle="targetKind"]')
                require(page.locator('[data-flow-field="targetCode"][type="text"]').count()==0,'DEACTIVATION_FREE_TEXT_TARGET_VISIBLE')
                require(page.locator('[data-picker-toggle="targetCode"]').count()==1,'DEACTIVATION_EXACT_TARGET_PICKER_MISSING')
                checks.append('deactivation_dropdown_homologation')

                browser.close()
            require(not console_errors, f'BROWSER_CONSOLE_ERRORS:{console_errors}')
            require(not request_failures, f'LOCAL_REQUEST_FAILURES:{request_failures}')
            checks.append('browser_console_network_clean')
        finally:
            proc.terminate()
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
            output=(proc.stdout.read() if proc.stdout else '')
            (out/'cloud-center-runtime-server.log').write_text(output,encoding='utf-8')

    report={'status':'PASS','result':'PASS_CLOUD_CENTER_CUSTOMER_RUNTIME_VISUAL_VERIFIED','checkCount':len(checks),'checks':checks,'consoleErrors':console_errors,'localRequestFailures':request_failures,'realDatabaseTouched':False,'liveProcessesTouched':False,'screenshots':['cloud-center-customer-provisioning.png','cloud-center-customers.png'],'diagnostics':['PICKER_DIAGNOSTIC.json','CREATE_CLIENT_DIAGNOSTIC.json','DRAFT_CLIENT_RESPONSE.json'],'doesNotProve':['live cloud customer creation','real customer data correctness','Tablet/PC/Mobile visual state']}
    (out/'CLOUD_CENTER_CUSTOMER_RUNTIME_VERIFY.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(report['result']); print(f"checks={len(checks)}")

if __name__=='__main__': main()
