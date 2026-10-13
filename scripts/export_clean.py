"""Nettoie un export `n8n export:workflow` : sans identifiants, sans credentials, inactif. Usage: export_clean.py <dossier_source> <nom>..."""
import json, sys
src = sys.argv[1]
for n in sys.argv[2:]:
    d = json.load(open(f"{src}/{n}.json", encoding="utf-8"))
    w = d[0] if isinstance(d, list) else d
    for k in ["shared", "tags", "activeVersionId", "versionId", "versionCounter", "createdAt", "updatedAt", "versionMetadata", "triggerCount", "isArchived", "description", "pinData", "staticData", "id", "meta"]:
        w.pop(k, None)
    w["active"] = False
    for nd in w["nodes"]:
        c = nd.pop("credentials", None)
        if c:
            nd["notes"] = (nd.get("notes", "") + " [Credential à créer : " + ", ".join(v["name"] for v in c.values()) + "]").strip()
    json.dump(w, open(f"workflows/{n}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(n, len(w["nodes"]), w.get("settings"))
