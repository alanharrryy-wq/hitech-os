const ORDER = { S0: 0, S1: 1, S2: 2, S3: 3, S4: 4 };
export function worstSeverity(findings = []) { if (!findings.length) return null; return findings.map(f => f.severity || 'S4').sort((a, b) => (ORDER[a] ?? 9) - (ORDER[b] ?? 9))[0]; }
export function blocksProfile(severity, profile) { if (severity === 'S0' || severity === 'S1') return true; if (severity === 'S2') return profile === 'release'; return false; }
export function summarizeFindings(findings = [], profile = 'commit') { const blockers = findings.filter(f => blocksProfile(f.severity, profile)); const warnings = findings.filter(f => !blocksProfile(f.severity, profile) && ['S2', 'S3'].includes(f.severity)); const info = findings.filter(f => f.severity === 'S4'); return { blockers, warnings, info, worst: worstSeverity(findings) }; }
