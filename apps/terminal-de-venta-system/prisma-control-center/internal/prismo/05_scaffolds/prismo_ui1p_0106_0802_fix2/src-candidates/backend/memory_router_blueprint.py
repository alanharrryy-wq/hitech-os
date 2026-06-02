"""Memory router blueprint for PRISMO UI1P."""
MEMORY_TYPES = ['semantic_memory','episodic_memory','procedural_memory','working_memory','operational_memory','governance_memory','visual_memory']

def select_memory_types(objective: str, domain: str, lens: str):
    selected = {'working_memory','semantic_memory'}
    if objective in {'diagnose','audit','investigate'}: selected |= {'episodic_memory','operational_memory','governance_memory'}
    if objective in {'prepare_action','recommend'}: selected |= {'procedural_memory','governance_memory'}
    if domain in {'pc_ui','chart_lab','visual_os'} or lens == 'visual_memory': selected |= {'visual_memory'}
    if lens in MEMORY_TYPES: selected.add(lens)
    return [m for m in MEMORY_TYPES if m in selected]

def build_memory_context(intent: dict, stores: dict | None = None):
    mem_types = select_memory_types(intent.get('objective','diagnose'), intent.get('domain','learning'), intent.get('lens','evidence_recent'))
    return {'memory_types': mem_types, 'top_items': [{'label': f'{m} listo', 'type': m} for m in mem_types], 'safety': {'db_touched': False, 'env_touched': False}}
