from __future__ import annotations

from collections import Counter

from ..engine.context import FileFacts


SIGNAL_PATTERNS = {
    'browser_api': ('window.', 'document.', 'navigator.', 'location.', 'history.'),
    'storage_api': ('localStorage', 'sessionStorage', 'indexedDB'),
    'nondeterministic': ('Date.now(', 'new Date(', 'Math.random(', 'randomUUID('),
    'dom_mutation': ('document.createElement(', '.appendChild(', '.prepend(', '.insertBefore('),
    'dynamic_ssr_false': ('ssr: false',),
    'suppress_hydration_warning': ('suppressHydrationWarning',),
    'hydration_keyword': ('hydrate', 'hydration', 'server render', 'client render'),
}


class GraphSignalExtractor:
    def signals_for_file(self, file_facts: FileFacts) -> tuple[str, ...]:
        text = file_facts.text
        signals: list[str] = []
        if file_facts.has_use_client:
            signals.append('use_client')
        if file_facts.has_use_server:
            signals.append('use_server')
        if self._looks_like_component(file_facts):
            signals.append('react_component')
        if self._looks_like_hook_container(file_facts):
            signals.append('react_hook_surface')
        for signal, patterns in SIGNAL_PATTERNS.items():
            if any(pattern in text for pattern in patterns):
                signals.append(signal)
        if file_facts.probable_tooling_path:
            signals.append('tooling_surface')
        if file_facts.probable_serverish_path:
            signals.append('serverish_surface')
        counter = Counter(signals)
        ordered = sorted(counter.keys(), key=lambda item: (item != 'react_component', item))
        return tuple(ordered)

    @staticmethod
    def _looks_like_component(file_facts: FileFacts) -> bool:
        if file_facts.extension not in {'.tsx', '.jsx'}:
            return False
        return '<' in file_facts.text or 'return (' in file_facts.text or 'return <' in file_facts.text

    @staticmethod
    def _looks_like_hook_container(file_facts: FileFacts) -> bool:
        return any(token in file_facts.text for token in ('useEffect(', 'useLayoutEffect(', 'useMemo(', 'useState('))
