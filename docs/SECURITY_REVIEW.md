# Security review: demo 1 publication (13/10/2026)

**Scope.** Everything in this repository: `README.md`, `TESTS.md`, `LICENSE`, `.gitignore`, `workflows/` (v5, alert, watchdog), `scripts/` (send_lead.py, mock_ia.py, export_clean.py). History: brand-new repository, one initial commit, nothing carried over from the private working repository.

**Method.** Manual review of code and workflow JSON, plus pattern searches over every file: API keys, bearer tokens, passwords, bot tokens (`NNN:xxxx`), GitHub tokens, e-mail addresses, Windows paths, internal URLs, n8n credential and workflow ids, HubSpot ids. The search covers the public tree only.

**Results.**
| Check | Result |
| --- | --- |
| Keys, tokens, passwords | None. The only matches are prose ("your bot token") and the placeholder `A_RENSEIGNER`. |
| E-mail addresses | Only `@example.com` test addresses, `camille@entreprise-fictive.fr` (placeholder text) and `studioasynk@gmail.com` (contact). |
| Local paths | None (`C:\Users`, `OneDrive`: no match). |
| n8n credential ids / `credentials` blocks | None. Exports are stripped; nodes only carry a note naming the credential to create. |
| Instance ids | The `errorWorkflow` setting (instance-specific id) was removed from the exports; the install steps ask the user to choose it. |
| Form webhook ids | The form and watchdog carry the demo form's webhook UUID (needed so the watchdog URL matches after import). It is not a secret; on a public instance anyone who knows it can submit the form, so keep the demo local. Webhook ids on the alert nodes were removed. |
| HubSpot ids / portal id | Removed from TESTS.md. |
| Internal URLs | Only `localhost:5678`, `ollama:11434`, `host.docker.internal:8099` (documented defaults, not secrets). |

**Code findings.**
- `scripts/mock_ia.py` listened on all interfaces. Fixed: it now binds to `127.0.0.1` (verified still reachable from the n8n container).
- `scripts/send_lead.py` only talks to `http://localhost:5678` and sends fictional values given on the command line. No finding.
- Workflow expressions build the HubSpot body with `JSON.stringify` (no string concatenation into JSON). The Telegram node sends plain text without parse mode. No injection found.
- Design note (not a vulnerability): the HubSpot-failure alert contains the lead so that nothing is lost. If alerts go to Telegram, that personal data transits a non-EU-only service. Documented in the README; the user can shorten the message.

**Second, independent read (separate reviewer, all files + history):** no secret or personal data; low/info points were the webhook ids (above), the lead inside the failure alert (documented), no CAPTCHA/rate limit on the demo form (demo only), and the wording about local data, softened in the README.

**Verdict.** Clean: no secret, token or personal data found. Fit to publish.
