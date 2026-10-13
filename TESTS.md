# TESTS — Démo 1 v5 (13/10/2026)

Instance n8n locale uniquement, données fictives (emails @example.com). Exécutés par l'agent dev via le formulaire public local (`scripts/send_lead.py`) ; lecture des résultats avec n8n-mcp. Preuve = numéro d'exécution n8n + sortie du nœud.
Règle de score : budget (Plus de 5 000 € = 2, 1 000 à 5 000 € = 1, sinon 0) + délai (Ce mois-ci = 2, Ce trimestre = 1, sinon 0). ≥ 3 chaud, 2 tiède, sinon froid.
Pannes simulées par `scripts/mock_ia.py` (faux Ollama, port 8099) ou en pointant temporairement une URL vers un port fermé / un chemin inexistant, puis restaurée.

## Suite finale (tous verts)
| Test | Entrée | Attendu | Observé | Exécution | Verdict |
| --- | --- | --- | --- | --- | --- |
| A chaud | Plus de 5 000 € / Ce mois-ci | score_ia 4, categorie_ia chaud | HubSpot : score_ia 4, categorie_ia chaud, resume_ia « [autre] … » | 56 (1re passe : 40) | OK |
| B tiède | 1 000 à 5 000 € / Ce trimestre | score_ia 2, tiede | score_ia 2, tiede, « [reporting] … » | 58 (41) | OK |
| C froid | Moins de 1 000 € / Plus tard | score_ia 0, froid | score_ia 0, froid | 59 (42) | OK |
| D IA en panne | URL IA vers un port fermé | lead enregistré, a_qualifier | ECONNREFUSED sur le nœud IA, flux continué, a_qualifier, « Analyse IA indisponible » | 66 (46, HubSpot : contact enregistré) | OK |
| E JSON IA invalide | faux Ollama renvoie `{"categorie": "autre", "resume": ` (tronqué) | a_qualifier, lead enregistré | ia_ok false, a_qualifier ; HubSpot a créé le contact | 65 (47, contact créé) | OK |
| F workflow désactivé | v5 désactivé, watchdog actif | formulaire 404, alerte déclenchée | formulaire HTTP 404 ; watchdog en erreur → alerte, message « La démo 1 ne répond pas (HTTP 404)… » ; réactivation OK | watchdog 72 → alerte 73 (avant désactivation : watchdog 70 vert) | OK |
| G1 chiffres gardés | « 50 devis par semaine », vrai Ollama | aucun chiffre ni fréquence altérés | exéc. 44 : résumé « …50 devis par semaine… » gardé ; exéc. 61 : l'IA écrit « 50 devis semestriels », le garde-fou le remplace par le résumé fixe | 44, 61 | OK avec réserve (voir ci-dessous) |
| G2 chiffre inventé | faux Ollama : « Reçoit 500 devis par semaine » | résumé fixe | garde_fou true, « [autre] Demande de Entreprise Fictive, budget Plus de 5 000 €, délai Ce trimestre » | 63 (45) | OK |
| H HubSpot en erreur | URL HubSpot pointée vers un chemin inexistant (404, 3 essais) | pas de perte, alerte avec le lead | sortie erreur → « Lead non enregistré » ; workflow d'alerte déclenché avec tout le lead dans le message ; Telegram tenté, repli email tenté | 68 → alerte 69 | OK |
| I formulaire invalide | email « pas-un-email » | rien envoyé à HubSpot, motif affiché | motif « adresse email invalide », HubSpot non exécuté | 71 (50) | OK |
| Doublon | même email envoyé deux fois (A, B, C, G) | un seul contact | même identifiant HubSpot à chaque passage (ex. A, « new »: false) | 40 et 56 | OK |

## Correctif en cours de route (v4)
- 1re passe G1 (exéc. 43) : l'IA a écrit « 50 devis semestriels » ; le garde-fou v4 ne vérifiait que les nombres, donc le résumé passait avec une fréquence fausse. Correctif minimal : le garde-fou compare aussi les périodes (semaine, jour, mois, trimestre, semestre, an, heure) du résumé à celles de la demande. Commit 0d02afe. Re-test : 44 (gardé), 45 (G2), 61 (attrapé).

## Réserve G1
qwen2.5:3b est non déterministe : « 50 devis par semaine » n'est pas toujours conservé à l'identique. Ce qui est garanti : aucun chiffre ni période faux n'atteint HubSpot (résumé fixe sinon) ; la demande complète reste toujours dans le champ `message` du contact.

## Alerte : ce qui est prouvé et ce qui reste à faire par l utilisateur
- Prouvé : le workflow d'alerte se déclenche (exéc. 49, 53, 55, 69, 73), compose le message (workflow, nœud, erreur, lien d'exécution, lead), le consigne dans « Journal alerte », tente Telegram puis l'email de repli.
- Non prouvé : la **réception réelle** d'un message Telegram / email. Les credentials contiennent la valeur A_RENSEIGNER : Telegram répond « Not Found », le SMTP « ENOTFOUND ». l utilisateur les renseigne (voir README, « Installer »), puis relance le test H.
- Un message Telegram avec jeton factice a été tenté vers api.telegram.org (rejeté, rien livré).

## Contacts de test (HubSpot, non supprimés)
test-a-chaud, test-b-tiede, test-c-froid, test-d-iapanne, test-g-50devis, test-e-jsoninvalide @example.com.

## Procédure E et F pour l utilisateur (10 min, à refaire après l'ajout des credentials)
**E — JSON IA invalide** : lancer `python scripts/mock_ia.py` ; dans n8n, nœud « IA locale – Catégorie et résumé », URL = `http://host.docker.internal:8099/e` ; ouvrir le formulaire ; envoyer un lead fictif ; dans HubSpot, le contact doit avoir categorie_ia = a_qualifier. Remettre l'URL `http://ollama:11434/api/chat` et fermer le mock.
**F — workflow désactivé** : activer « Démo 1 – Watchdog » ; désactiver « v5 » ; attendre 5 min ; un message d'alerte arrive (Telegram, sinon email). Réactiver « v5 ».

## Tests d'attaque (13/10, exécutions 83 à 96) et failles trouvées
| Cas | Résultat | Verdict |
| --- | --- | --- |
| T1 injection de prompt dans le besoin | IA indisponible (délai), repli a_qualifier ; aucun contenu injecté dans le CRM | OK (repli) |
| T2 guillemets, `<script>`, `{{ 7*7 }}`, `${7*7}` | stockés tels quels, jamais évalués (pas d'injection d'expression) | OK |
| T3 email ` ATK-T3-Case@Example.COM ` | normalisé `atk-t3-case@example.com` | OK |
| T4 budget « Plus de pirate » / délai libre | **FAILLE** : score 4, « chaud » (n8n n'impose pas la liste côté serveur, le score utilisait `includes`) | **Corrigé** : la validation exige les 3 valeurs de budget et de délai ; test R1 (exéc. 92) : rejeté, motif « budget invalide, délai invalide », HubSpot non appelé |
| T5 consentement vide | rejeté, motif « consentement manquant » (exéc. 87) | OK |
| T6 email `a@b.c` | **défaut** : accepté par notre regex, refusé par HubSpot (400), le visiteur voit une erreur, alerte avec le lead (exéc. 88) | **Corrigé** : domaine ≥ 2 lettres ; test R2 (exéc. 93) : rejeté avec motif |
| T7 besoin de 6000 caractères | traité sans erreur | OK |
| T8 prénom vide | rejeté, motif « prénom manquant » (exéc. 90) | OK |

**Limite non corrigée (exploitation)** : le nœud IA a un délai de 120 s. Quand Ollama est froid ou saturé (rafale de plusieurs envois, PC chargé), l'appel dépasse 120 s et tous ces leads partent en `a_qualifier` (aucun lead perdu). Constaté pendant ces tests : sur cette machine, même un lead seul a dépassé le délai (exéc. 94, 95, 96, Ollama très lent après remise en route du PC), alors que les exécutions de la matinée prenaient ~20 s. Conseils : envoyer un lead de chauffe après un redémarrage, limiter les rafales, ou relever le délai du nœud.
**Non vérifié** : affichage du texte saisi dans l'écran final du formulaire (échappement HTML).
Contacts de test ajoutés (HubSpot, @example.com) : atk-*, conservés.
