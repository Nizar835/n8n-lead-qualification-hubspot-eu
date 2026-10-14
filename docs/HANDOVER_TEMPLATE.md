# Handover document: <workflow name> (template)

Client: <name> · Delivered: <date> · Version: <vX> · Contact: studioasynk@gmail.com (written support only)

## 1. What the workflow does
<2 to 4 sentences: input, processing, output. Example: a form lead is validated, scored by fixed rules, summarised by a local AI, filed in the CRM.>
Scoring is rule-based and fixed (<rules>). The AI only categorises and summarises; fallback value: `a_qualifier`. Any AI agent announces itself as an AI.

## 2. Triggers
| Workflow | Trigger | Frequency / URL |
| --- | --- | --- |
| <main> | <form / webhook / schedule> | <...> |
| <watchdog> | schedule | every <5> min |

## 3. Credentials to create (none are shipped)
| Name in n8n | Type | Needed scopes | Where used |
| --- | --- | --- | --- |
| <HubSpot key> | Header Auth | contacts read/write | <node> |
| <Telegram / SMTP> | <type> | <...> | alerts |
Also: CRM properties to create <list>; hosting <EU region>; error workflow to select in Settings.

## 4. Failures and alerts
| Failure | What happens | Alert | Lead lost? |
| --- | --- | --- | --- |
| Invalid input | Reason shown, nothing sent | none | No |
| AI down | Saved as `a_qualifier` | none | No |
| CRM down | 3 tries, then alert with full data | <channel> | No |
| Workflow off | Watchdog alerts within <5> min | <channel> | Visitors see an error |
Test report: <TESTS.md, execution numbers>.

## 5. Pause and resume
Pause: switch the workflow off in n8n (toggle "Active"). Keep the alert workflow active. Resume: switch on, send one fictional test lead, check the CRM contact.

## 6. Who to contact
Day-to-day owner (client): <name, email>. Technical support (Asynk Studio): studioasynk@gmail.com, by email only; reply within <X> working days. Maintenance plan: <none / 79 / 149 EUR per month>.
