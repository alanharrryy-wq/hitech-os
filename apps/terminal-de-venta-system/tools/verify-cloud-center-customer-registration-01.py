#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path


def require(condition, code):
    if not condition:
        raise AssertionError(code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', default='')
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[3]
    app = Path(__file__).resolve().parents[1]
    cloud = app / 'Prisma Cloud Ctr'
    pyroot = cloud / 'internal' / 'py'
    sys.path.insert(0, str(pyroot))

    checks = []
    with tempfile.TemporaryDirectory(prefix='prisma-customer-reg-') as td:
        db_path = Path(td) / 'customer-runtime.db'
        os.environ['PRISMA_COMMAND_CENTER_DB_PATH'] = str(db_path)
        import command_center_store as store

        store.ensure_initialized()
        require(store.DB_PATH == db_path, 'TEMP_DB_OVERRIDE_NOT_HONORED'); checks.append('temp_db_override')
        with store.db() as con:
            cats = store.catalogs(con)
            require('city_zone' not in cats, 'LEGACY_CITY_ZONE_STILL_ACTIVE'); checks.append('legacy_city_zone_retired')
            require(len(cats['state_mx']['options']) == 32, 'MEXICO_STATE_CATALOG_NOT_32'); checks.append('mexico_states_32')
            require('multi_branch' not in {x['code'] for x in cats['vertical']['options']}, 'MULTI_BRANCH_STILL_VERTICAL'); checks.append('no_multi_branch_vertical')
            plan_codes = {x['code'] for x in cats['license_plan']['options']}
            require(plan_codes == {'TABLET_SOLO','TABLET_PRO','TABLET_PC_MANAGED'}, f'CANONICAL_PLAN_DRIFT:{sorted(plan_codes)}'); checks.append('canonical_license_plans')
            for code, cat in cats.items():
                codes=[x['code'] for x in cat.get('options',[])]
                labels=[str(x['label']).strip().casefold() for x in cat.get('options',[])]
                require(len(codes)==len(set(codes)), f'DUPLICATE_OPTION_CODE:{code}'); require(len(labels)==len(set(labels)), f'DUPLICATE_OPTION_LABEL:{code}')
            checks.append('catalog_no_duplicates')

            seed = con.execute("SELECT legalName,verticalCode,subverticalCode,sizeCode,operationCode,cityZoneCode FROM CommandClient WHERE id='client_prisma_original_customer'").fetchone()
            require(seed is not None, 'FIRST_CUSTOMER_SEED_MISSING')
            require(all(seed[k] is None for k in ('legalName','verticalCode','subverticalCode','sizeCode','operationCode','cityZoneCode')), f'FIRST_CUSTOMER_UNVERIFIED_FACTS_INFERRED:{dict(seed)}'); checks.append('seed_no_unverified_customer_facts')

            # stale catalog option must be retired without deleting history
            con.execute("INSERT OR IGNORE INTO Catalog(id,code,label,allowOther,sortOrder) VALUES('cat_city_zone','city_zone','Legacy City Zone',1,999)")
            con.execute("INSERT OR IGNORE INTO CatalogOption(id,catalogId,code,label,active) VALUES('old_city_zone','cat_city_zone','legacy','Legacy',1)")
            con.commit()
        store.ensure_initialized()
        with store.db() as con:
            retired = con.execute("SELECT mode FROM Catalog WHERE code='city_zone'").fetchone()
            opt = con.execute("SELECT active FROM CatalogOption WHERE id='old_city_zone'").fetchone()
            require(retired and retired['mode']=='retired' and opt and int(opt['active'])==0, 'STALE_CATALOG_RECONCILIATION_FAILED'); checks.append('stale_catalog_reconciled')

            id_before = con.execute('SELECT COUNT(*) FROM GeneratedIdentity').fetchone()[0]
            bad = store.draft_client(con, {'displayName':'Sin contacto','vertical':'abarrotes','businessSize':'small','operationMode':'counter','acquisitionChannel':'referral'})
            require(not bad.get('ok') and bad.get('resultCode')=='CUSTOMER_CONTACT_METHOD_REQUIRED', f'CUSTOMER_VALIDATION_FAILED:{bad}')
            require(con.execute('SELECT COUNT(*) FROM GeneratedIdentity').fetchone()[0] == id_before, 'IDS_GENERATED_BEFORE_VALIDATION'); checks.append('validation_before_ids')

            payload = {
                'clientRequestId':'runtime-test-customer-001',
                'displayName':'Abarrotes Runtime Test',
                'contactName':'Operador Prueba',
                'contactRole':'owner',
                'email':'runtime@example.test',
                'vertical':'abarrotes',
                'subvertical':'minisuper',
                'businessSize':'small',
                'operationMode':'counter',
                'acquisitionChannel':'referral',
                'country':'MX',
                'state':'jalisco',
                'city':'Guadalajara',
                'zone':'Centro',
            }
            created = store.draft_client(con, payload)
            require(created.get('ok') and not created.get('idempotent'), f'CUSTOMER_CREATE_FAILED:{created}'); checks.append('customer_create')
            require(created['recommendation']['suggestedPlan']=='TABLET_PRO', f'PLAN_RECOMMENDATION_DRIFT:{created["recommendation"]}'); checks.append('recommendation_is_canonical')
            dedup_key=created['profile']['dedupKey']
            try:
                con.execute("INSERT INTO ClientProfile(id,clientId,relationshipStageCode,dedupKey,profileSource) VALUES('dup_profile','dup_client','onboarding',?,'test')",(dedup_key,))
                raise AssertionError('DEDUP_KEY_NOT_UNIQUE')
            except sqlite3.IntegrityError:
                pass
            checks.append('dedup_key_unique_constraint')
            client_code=created['client']['humanCode']
            count_after=con.execute('SELECT COUNT(*) FROM CommandClient').fetchone()[0]
            ids_after=con.execute('SELECT COUNT(*) FROM GeneratedIdentity').fetchone()[0]

            retry=store.draft_client(con,payload)
            require(retry.get('ok') and retry.get('idempotent') and retry['client']['humanCode']==client_code,'REQUEST_ID_IDEMPOTENCY_FAILED')
            require(con.execute('SELECT COUNT(*) FROM CommandClient').fetchone()[0]==count_after and con.execute('SELECT COUNT(*) FROM GeneratedIdentity').fetchone()[0]==ids_after,'IDEMPOTENT_RETRY_MUTATED'); checks.append('client_request_idempotency')

            same=dict(payload); same['clientRequestId']='runtime-test-customer-002'
            retry2=store.draft_client(con,same)
            require(retry2.get('idempotent') and retry2['client']['humanCode']==client_code,'CUSTOMER_FINGERPRINT_DEDUP_FAILED'); checks.append('customer_fingerprint_dedup')

            mismatch=dict(payload); mismatch.update({'clientRequestId':'bad-subvertical','displayName':'Bad Subvertical','email':'bad@example.test','vertical':'restaurant','subvertical':'minisuper'})
            res=store.draft_client(con,mismatch)
            require(not res.get('ok') and res.get('resultCode')=='CUSTOMER_SUBVERTICAL_MISMATCH', f'SUBVERTICAL_DEPENDENCY_NOT_ENFORCED:{res}'); checks.append('subvertical_parent_guard')

            other_payload=dict(payload); other_payload.update({'clientRequestId':'other-001','displayName':'Vertical Especial','email':'other@example.test','vertical':'other','subvertical':'','other':{'vertical':'Mercado ambulante'}})
            other_res=store.draft_client(con,other_payload)
            require(other_res.get('ok'),'OTHER_AUTOSUBMIT_CLIENT_FAILED')
            pending=con.execute("SELECT COUNT(*) FROM CatalogOtherSubmission WHERE normalized='mercado ambulante' AND status='pending_catalog_review'").fetchone()[0]
            require(pending==1,'OTHER_AUTOSUBMIT_NOT_DEDUPED');
            other_retry=store.draft_client(con,other_payload)
            pending2=con.execute("SELECT COUNT(*) FROM CatalogOtherSubmission WHERE normalized='mercado ambulante' AND status='pending_catalog_review'").fetchone()[0]
            require(other_retry.get('idempotent') and pending2==1,'OTHER_RETRY_DUPLICATED'); checks.append('other_auto_submit_idempotent')

            bad_device=store.draft_device(con,{'clientCode':'CLI-NO-EXISTE','deviceType':'tablet_pos'})
            require(not bad_device.get('ok') and bad_device.get('resultCode')=='CUSTOMER_SELECTION_REQUIRED','INVALID_CLIENT_FELL_BACK_FOR_DEVICE'); checks.append('device_no_latest_customer_fallback')

            device=store.draft_device(con,{'clientCode':client_code,'deviceType':'tablet_pos','deviceRole':'tablet_pos','deviceAlias':'Caja Runtime'})
            require(device.get('ok') and device['device'].get('displayAlias')=='Caja Runtime','DEVICE_ALIAS_OR_ROLE_NOT_PERSISTED')
            stored=con.execute('SELECT displayAlias,roleCode FROM ManagedDevice WHERE humanCode=?',(device['device']['humanCode'],)).fetchone()
            require(stored and stored['displayAlias']=='Caja Runtime' and stored['roleCode']=='tablet_pos','DEVICE_STORAGE_DRIFT'); checks.append('device_alias_role_persisted')

            bad_license=store.draft_license(con,{'clientCode':'CLI-NO-EXISTE','plan':'TABLET_PRO'})
            require(not bad_license.get('ok') and bad_license.get('resultCode')=='CUSTOMER_SELECTION_REQUIRED','INVALID_CLIENT_FELL_BACK_FOR_LICENSE'); checks.append('license_no_latest_customer_fallback')
            invalid_plan=store.draft_license(con,{'clientCode':client_code,'plan':'starter'})
            require(not invalid_plan.get('ok') and invalid_plan.get('resultCode')=='LICENSE_PLAN_INVALID','LEGACY_PLAN_CODE_STILL_ACCEPTED'); checks.append('legacy_plan_rejected')

            cats=store.catalogs(con)
            require(any(x['code']==client_code for x in cats['client']['options']),'DYNAMIC_CLIENT_CATALOG_MISSING')
            require(any(x['code']==device['device']['humanCode'] for x in cats['managed_device']['options']),'DYNAMIC_DEVICE_CATALOG_MISSING'); checks.append('dynamic_entity_dropdowns')

            deact=store.draft_deactivation(con,{'targetKind':'device','targetCode':device['device']['humanCode'],'reason':'device_replacement'})
            require(deact.get('ok'),'DYNAMIC_DEACTIVATION_TARGET_FAILED')
            bad_deact=store.draft_deactivation(con,{'targetKind':'device','targetCode':'DEV-NO-EXISTE','reason':'device_replacement'})
            require(not bad_deact.get('ok') and bad_deact.get('resultCode')=='DEACTIVATION_TARGET_REQUIRED','DEACTIVATION_FREE_TEXT_TARGET_STILL_ACCEPTED'); checks.append('deactivation_exact_target')

            metrics=store._customer_metrics(con)
            ref = next((x for x in metrics['byAcquisition'] if x['code']=='referral'),None)
            require(ref and ref['count']>=1,'CUSTOMER_ACQUISITION_METRIC_MISSING')
            require(metrics['dataQuality']['seedLegacyClassificationNeedsReview']==0,'CLEAN_SEED_FALSE_POSITIVE_REVIEW')
            con.execute("UPDATE CommandClient SET verticalCode='abarrotes',subverticalCode='minisuper',sizeCode='small',operationCode='counter',cityZoneCode='mexico_city' WHERE id='client_prisma_original_customer'")
            legacy_metrics=store._customer_metrics(con)
            require(legacy_metrics['dataQuality']['seedLegacyClassificationNeedsReview']==1 and legacy_metrics['dataQuality']['legacyCityZoneValues']>=1,'LEGACY_SEED_REVIEW_SIGNAL_MISSING')
            con.execute("UPDATE CommandClient SET verticalCode=NULL,subverticalCode=NULL,sizeCode=NULL,operationCode=NULL,cityZoneCode=NULL WHERE id='client_prisma_original_customer'")
            checks.append('structured_customer_metrics')

            bp=store.bootstrap(con)
            require(bp.get('customerCatalogSchemaVersion')=='1.0.0' and 'customerMetrics' in bp,'BOOTSTRAP_CUSTOMER_AUTHORITY_MISSING'); checks.append('bootstrap_customer_authority')

    report={'status':'PASS','result':'PASS_CLOUD_CENTER_CUSTOMER_REGISTRATION_LOCAL_VERIFIED','checks':checks,'checkCount':len(checks),'realDatabaseTouched':False,'surfacesTouched':['Prisma Cloud Center test DB only'],'doesNotProve':['runtime visual layout','live cloud customer creation','real client data correctness']}
    if args.out_dir:
        out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
        (out/'CLOUD_CENTER_CUSTOMER_REGISTRATION_VERIFY.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(report['result']); print(f"checks={len(checks)}")

if __name__=='__main__':
    main()
