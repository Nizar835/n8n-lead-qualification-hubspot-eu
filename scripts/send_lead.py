"""Envoie un lead FICTIF au formulaire n8n local. Usage: send_lead.py <form_uuid> <email> <besoin> <budget> <delai>"""
import sys, urllib.request, uuid
form, email, besoin, budget, delai = sys.argv[1:6]
f = {"field-0": "Camille", "field-1": "Martin", "field-2": email, "field-3": "Entreprise Fictive",
     "field-4": "https://entreprise-fictive.fr", "field-5": besoin, "field-6": budget, "field-7": delai,
     "field-8": "J'accepte que mes données soient utilisées pour traiter ma demande"}
b = uuid.uuid4().hex
body = b"".join(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in f.items()) + f"--{b}--\r\n".encode()
r = urllib.request.Request(f"http://localhost:5678/form/{form}", body, {"Content-Type": f"multipart/form-data; boundary={b}"})
print(urllib.request.urlopen(r, timeout=200).read().decode())
