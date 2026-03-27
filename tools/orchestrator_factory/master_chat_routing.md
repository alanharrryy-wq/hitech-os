
# Master Chat Routing

Default operating model:

- **Chat 0** -> `00-governance-core` and mission-control duties
- **Chat 1** -> `01-identity-access-and-trust`
- **Chat 2** -> `02-domain-data-and-persistence`
- **Chat 3** -> `03-service-contracts-and-orchestration`
- **Chat 4** -> `04-experience-clients-and-interactions`
- **Chat 5** -> `05-platform-infrastructure-and-delivery`
- **Chat 6** -> `06-quality-release-and-operations`

## Why the governance chat also acts as mission control by default
The target operating model is one governing chat plus six work chats. Mission control therefore sits inside the governance chat unless the operator explicitly delegates it to a separate integration judge chat for unusually large runs.

## Routing rules
- Governance chat may update constitutional docs, run manifests, acceptance reports, active work packets, and freeze notices.
- Package chats may update only their package folders and the runtime paths assigned to them by the active work packet.
- Package chats never send direct edits or direct governing instructions to each other.
- Cross-package coordination flows through frozen docs, decision records, work packets, acceptance reports, and retry prompts.

## When to split mission control into a separate chat
Only split if:
- the governance chat has become a bottleneck,
- integration logic is heavy enough to distract from constitutional upkeep, or
- an independent adjudicator is needed for audit or compliance reasons.

Even in split mode, the governance constitution still outranks the mission-control chat.
