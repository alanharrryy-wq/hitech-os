from pathlib import Path
from tempfile import TemporaryDirectory
from capatch_contracts.operations import build_operation_spec,is_valid_operation_type
from capatch_ops.registry import execute_operation
from capatch_policy.verification_requirements import compute_verification_policy
from capatch_verify.registry import run_required_verifiers
def test_visual_ready_pack():
    assert is_valid_operation_type('ReplaceCssRuleBlock')
    op=build_operation_spec({'type':'ReplaceCssRuleBlock','file':'x.css','selector':'.btn','new_block':'  color: red;'})
    assert 'color: red' in execute_operation(Path('x.css'),'.btn { color: blue; }\n',op).final_text
    pol=compute_verification_policy({'risk_level':'medium'},['products/tablet/app/components/pos/pos.module.css','products/tablet/app/components/pos/pos.tsx'])
    assert {'css-sanity','css-module-sanity','visual-static-gates','typescript-parse','react-css-link'} <= set(pol['required_verifiers'])
    with TemporaryDirectory() as td:
        root=Path(td); (root/'pos.module.css').write_text('.payButton { color: red; }\n',encoding='utf-8')
        (root/'pos.tsx').write_text("import styles from './pos.module.css';\nexport function X(){ return <button className={styles.payButton}/> }\n",encoding='utf-8')
        rows=run_required_verifiers(['pos.module.css','pos.tsx'],['css-module-sanity','react-css-link','visual-static-gates'],{'root_dir':td})
        assert rows and all(r['ok'] for r in rows), rows
