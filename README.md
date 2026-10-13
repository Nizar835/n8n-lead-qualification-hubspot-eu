# Lead qualification: form → local AI → HubSpot EU, with failure alerts

**A contact form that scores, summarises and files every lead in HubSpot (EU) within seconds, runs its AI on your own machine, and tells you when something breaks, instead of silently losing leads.**

> Fictional data only. No client data in this repository. Video: link to be added.

## Problem
Leads arrive by form and get copied into the CRM by hand: late, unprioritised, sometimes lost when a tool is down. Good ones go cold.

## Diagram
```
Form ─▶ clean ─▶ valid? ──no──▶ reason shown to the visitor (nothing sent to the CRM)
                   │yes
                   ▼
            score (budget + timeline) ─▶ local AI (topic + summary)
                   ▼                          │ AI down / invalid JSON → "a_qualifier"
            number guard ◀───────────────────┘ (summary may not invent or alter a figure or a period)
                   ▼
            HubSpot upsert by email (3 tries) ──error──▶ "Lead not saved" ─▶ alert carrying the full lead
                   ▼
            "Request received" screen

Watchdog (every 5 min) ─▶ pings the form ─▶ no answer ─▶ alert
Any failure ─▶ "Alert" workflow ─▶ Telegram ─▶ (if it fails) email
```
Files: `workflows/demo1-v5.json` (main), `demo1-alerte.json` (error workflow), `demo1-watchdog.json`.

## Steps
1. Validate: email format, first name, need, consent.
2. Score: budget (>5 k€ = 2, 1–5 k€ = 1) + timeline (this month = 2, this quarter = 1). ≥3 hot, 2 warm, else cold.
3. Local AI (Ollama, qwen2.5:3b): topic + one-sentence summary, JSON enforced. Guard: any number or period in the summary must appear in the request, otherwise a fixed summary is used.
4. HubSpot (EU, `api-eu1`, Service Key): upsert on the custom properties `score_ia`, `categorie_ia`, `resume_ia` (filterable).

## Tests (full report: TESTS.md)
All run in a real n8n against a real HubSpot test account, fictional leads, execution ids in TESTS.md.

| Test | Case | Result |
| --- | --- | --- |
| A / B / C | hot / warm / cold lead | OK (score and category as expected) |
| D | AI unreachable | OK, lead saved as `a_qualifier` |
| E | AI returns truncated JSON | OK, lead saved as `a_qualifier` |
| F | workflow deactivated | OK, form answers 404, watchdog alerts, reactivated |
| G1 | "50 devis par semaine" | OK with a caveat, see below |
| G2 | AI invents "500 devis" | OK, replaced by a fixed summary |
| H | HubSpot down | OK, alert carries the whole lead |
| I | invalid email | OK, reason shown, nothing sent to HubSpot |
| Duplicate | same email twice | OK, same contact |

**Honest caveat (G1).** The 3B local model does not always keep "50 devis par semaine" word for word (once it wrote "semestriels"). What is guaranteed: no wrong figure or period reaches HubSpot (a fixed summary replaces it), and the full request always stays in the contact's `message` field.

## Duplicates
The upsert key is the email. Submitting the same email twice updates the same contact and never creates a second one (same HubSpot id on both runs).

## Failures
| Failure | What happens | Lead lost? |
| --- | --- | --- |
| Invalid form | Visitor sees the reason; nothing sent to HubSpot | No, the visitor corrects it |
| AI down or invalid JSON | Contact saved with `categorie_ia = a_qualifier` and a neutral summary | No |
| AI invents a figure | Summary replaced by a fixed one | No |
| HubSpot down | 3 tries, then alert with the whole lead | No, it is in the alert |
| Workflow deactivated | Watchdog gets a 404 within 5 min and alerts | Visitors see an error until reactivated |

**Alerts.** The alert workflow and the watchdog are provided and were proven to fire (journal node) and to try Telegram, then email. Delivery of real messages depends on credentials that **you** fill in: the repository ships none. Privacy note: the HubSpot-failure alert carries the lead (so nothing is lost); Telegram is not an EU-only service, so if that matters to you, shorten the message in the "Lead non enregistré" node and keep the lead in the n8n execution log only.

## Install in 10 minutes
1. Run n8n (EU host) and Ollama; `ollama pull qwen2.5:3b`. The AI node calls `http://ollama:11434` (adapt to your setup).
2. In HubSpot (EU), create three contact properties: `score_ia` (number), `categorie_ia` (text), `resume_ia` (multi-line text). Create a Service Key with contacts read/write.
3. In n8n, create the credentials: *Header Auth* named `HubSpot – n8n-demo1` (`Authorization: Bearer <your key>`), *Telegram API* (your bot token), *SMTP*. Put your chat id in the Telegram node and your addresses in the email node.
4. Import `demo1-alerte.json`, `demo1-watchdog.json`, `demo1-v5.json`. Re-select the credentials on the nodes (the exports contain none).
5. In *Settings → Error workflow* of the v5 and the watchdog, choose "Démo 1 – Alerte d'échec". Activate the alert workflow first, then v5, then the watchdog. In the watchdog, replace the form URL by your own production form URL.
6. Submit a fictional lead (the `/form/<id>` URL of the form trigger, or `python scripts/send_lead.py <form_id> a@example.com "need" "Plus de 5 000 €" "Ce mois-ci"`) and check the contact in HubSpot. Break the HubSpot URL once to see the alert.

## Compliance
EU hosting, the AI step runs locally (HubSpot and, if you use it, Telegram are third parties), consent collected in the form, GDPR processor clause (art. 28) in client quotes, no secret in this repository, fictional data only.

---

# FR (court)

**Problème** : les demandes arrivent par formulaire, sont recopiées à la main dans le CRM, trop tard, et parfois perdues quand un outil tombe.
**Solution** : formulaire → validation → score (budget + délai) → IA locale (thème + résumé) → HubSpot UE, sans doublon (clé = email).
**Pannes** : IA seule en échec → lead enregistré en « a_qualifier » ; HubSpot en échec → alerte avec le lead complet ; démo désactivée → le watchdog alerte sous 5 min.
**Installer** : voir « Install in 10 minutes » (importer les 3 JSON, créer vos credentials, choisir le workflow d'erreur). Les alertes réelles fonctionnent avec vos propres jetons Telegram et SMTP.
**Preuves** : TESTS.md. **Réserve** : le petit modèle local ne garde pas toujours « 50 devis par semaine » mot pour mot ; aucune valeur fausse n'atteint le CRM.
**Données fictives uniquement.**

Asynk Studio, workflows testés, supervisés, hébergés en UE. studioasynk@gmail.com
