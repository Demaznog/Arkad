#!/usr/bin/env python3
"""
Assemble un fichier HTML unique contenant le hub et tous les jeux.

Chaque jeu est encodé en base64 et décodé à la volée dans une iframe isolée :
- aucun conflit de variables globales, de CSS ni d'identifiants entre les jeux ;
- aucune modification à apporter aux jeux eux-mêmes ;
- un seul fichier à déposer sur tiiny.host.

Pour ajouter un jeu : déposer son .html à côté de ce script et l'ajouter à
CATALOGUE ci-dessous. Puis relancer : python3 assembler.py
"""
import base64, datetime, json, os, sys

CATALOGUE = [
    dict(id="lucarne", fichier="lucarne.html",
         nom="Upper90", cats=["sport", "reflex"], joueurs="1 à 6",
         phrase="Tes buts deviennent le gardien. La cage se referme sur toi.",
         recordCle="lucarne.record", recordSuffixe="buts", vignette="lucarne",
         enligne=True,
         teinte=dict(haut="#12332c", bas="#061713", accent="#d9a441", nom="#f2f6ee")),
    dict(id="ailes", fichier="ailes.html",
         nom="Pylon", cats=["reflex"], joueurs="1 à 6",
         phrase="Championnat en cinq courses. Plus tu vas vite, plus ton virage s'élargit.",
         recordCle="ailes.meilleur", recordSuffixe="s", vignette="ailes", enligne=True,
         teinte=dict(haut="#2c6b45", bas="#08170e", accent="#ffcf5a", nom="#ffffff")),
    dict(id="steeple", fichier="steeple.html",
         nom="Steeple", cats=["sport","reflexe"], joueurs="1 à 10",
         phrase="Hippodrome ou cross. Reste dans un dos, garde ton cheval, déborde à la fin.",
         recordCle=None, recordSuffixe="", vignette="steeple", enligne=True,
         teinte=dict(haut="#2b5c33", bas="#0a1a0e", accent="#ffcf5a", nom="#ffffff")),
    dict(id="boules", fichier="boules.html",
         nom="Pitch", cats=["sport", "mind"], joueurs="1 à 6",
         phrase="La pétanque, aux règles officielles. Pointer, tirer, plomber.",
         recordCle=None, recordSuffixe="", vignette="boules", enligne=True,
         teinte=dict(haut="#7a6034", bas="#241a0c", accent="#e8b84b", nom="#f6f3ec")),
    dict(id="bank", fichier="bank.html",
         nom="Bank", cats=["reflex", "mind"], joueurs="1",
         phrase="Vise avec les rebonds. Chaque trou a son par, comme au golf.",
         recordCle="bank.record", recordSuffixe="trous", vignette="bank",
         teinte=dict(haut="#1d3a6b", bas="#070b18", accent="#35e7ff", nom="#f7fbff")),
    dict(id="orbit", fichier="orbit.html",
         nom="Orbit", cats=["reflex", "mind"], joueurs="1",
         phrase="Tir gravitationnel. Les astres courbent ta sonde.",
         recordCle="orbit.record", recordSuffixe="orbites", vignette="orbit",
         teinte=dict(haut="#2a2160", bas="#05060f", accent="#7ee8ff", nom="#f4f7ff")),
    dict(id="baby", fichier="baby.html",
         nom="Kickr", cats=["sport", "reflex"], joueurs="2",
         phrase="Le baby-foot à un doigt. Couvrir un côté ouvre l'autre.",
         recordCle=None, recordSuffixe="", vignette="baby",
         teinte=dict(haut="#40301c", bas="#1b130b", accent="#e8c37a", nom="#f7f0e2")),
    dict(id="blitz", fichier="blitz.html",
         nom="Blitz", cats=["strat", "mind"], joueurs="1 ou 2",
         phrase="Bataille napoléonienne. Cinq batailles, trois victoires pour l'emporter.",
         recordCle=None, recordSuffixe="", vignette="blitz", enligne=True,
         teinte=dict(haut="#4a3a22", bas="#171208", accent="#e0b657", nom="#f6efe0")),
    dict(id="toka", fichier="toka.html",
         nom="Toka", cats=["mind"], joueurs="2 à 6",
         phrase="Le mercato aux enchères. Composer l'effectif le plus fort.",
         recordCle=None, recordSuffixe="", vignette="toka", enligne=True,
         teinte=dict(haut="#2f8049", bas="#0e2a1b", accent="#eaf6e4", nom="#ffffff")),
]

CATEGORIES = [
    ("tout",   "Tout"),
    ("sport",  "Sport"),
    ("reflex", "Réflexe"),
    ("mind",   "Réflexion"),
    ("strat",  "Stratégie"),
]

TITRE_HUB = "ARKAD"
# Numéro de version affiché dans l'application : c'est lui qui permet de vérifier
# d'un coup d'œil quelle version est réellement en ligne, quel que soit le nom
# du fichier déposé chez l'hébergeur.
VERSION = "10.5"
SOUS_TITRE = "Jeux d'arcade, seul ou à six"


MARQUE_PEERJS = "<!--ARKAD:PEERJS-->"


def mutualiser_peerjs(texte, biblio):
    """PeerJS pèse 90 Ko et il est présent dans plusieurs jeux. On le remplace
    par un marqueur, et le hub le réinjecte à l'ouverture : une seule copie
    dans le fichier final au lieu de deux."""
    if not biblio or biblio not in texte:
        return texte, False
    return texte.replace(biblio, MARQUE_PEERJS), True


def extraire_biblio(chemins):
    """Repère le bloc PeerJS commun aux jeux, s'il existe."""
    import re
    for c in chemins:
        if not os.path.exists(c):
            continue
        t = open(c, encoding="utf-8").read()
        m = re.search(r"<script>\s*/\* PeerJS 1\.5\.4 embarqué.*?</script>", t, re.S)
        if m:
            return m.group(0)
    return None


def charger(jeux, biblio):
    """Encode chaque jeu présent sur le disque, signale les absents."""
    sortie, absents = [], []
    for j in jeux:
        entree = dict(j)
        chemin = j["fichier"]
        if os.path.exists(chemin):
            texte = open(chemin, encoding="utf-8").read()
            texte, mutualise = mutualiser_peerjs(texte, biblio)
            brut = texte.encode("utf-8")
            entree["b64"] = base64.b64encode(brut).decode("ascii")
            entree["poids"] = len(brut)
            entree["peerjs"] = mutualise
        else:
            entree["b64"] = None
            entree["poids"] = 0
            absents.append(chemin)
        sortie.append(entree)
    return sortie, absents


def construire():
    biblio = extraire_biblio([j["fichier"] for j in CATALOGUE])
    jeux, absents = charger(CATALOGUE, biblio)
    if biblio:
        print("PeerJS mutualisé : %.0f Ko stockés une seule fois" % (len(biblio) / 1024))
    catalogue_js = json.dumps(jeux, ensure_ascii=False)
    cats_js = json.dumps(CATEGORIES, ensure_ascii=False)

    with open("icone-arkad.png", "rb") as f:
        icone = base64.b64encode(f.read()).decode("ascii")
    with open("icone-arkad-192.png", "rb") as f:
        icone192 = base64.b64encode(f.read()).decode("ascii")
    # les trois avions de la vignette, rendus par le jeu lui-même
    avions = {}
    for teinte in ("rouge", "bleu", "or"):
        with open("avion-%s.png" % teinte, "rb") as f:
            avions[teinte] = base64.b64encode(f.read()).decode("ascii")

    gabarit = open("gabarit.html", encoding="utf-8").read()
    page = (gabarit
            .replace("/*__CATALOGUE__*/", "const CATALOGUE = " + catalogue_js + ";")
            .replace("/*__CATEGORIES__*/", "const CATEGORIES = " + cats_js + ";")
            .replace("__ICONE192__", icone192)
            .replace("__AVION_ROUGE__", avions["rouge"])
            .replace("__AVION_BLEU__", avions["bleu"])
            .replace("__AVION_OR__", avions["or"])
            .replace("__ICONE__", icone)
            # la chaîne contient « </script> », qui fermerait la balise du hub :
            # on l'échappe en « <\\/script> », que JavaScript relit à l'identique
            .replace("__PEERJS__",
json.dumps(biblio or "", ensure_ascii=False).replace("</", "<" + chr(92) + "/"))
            .replace("__VERSION__", VERSION)
            .replace("__DATE__", datetime.date.today().strftime("%d/%m/%Y"))
            .replace("__TITRE__", TITRE_HUB)
            .replace("__SOUS_TITRE__", SOUS_TITRE))

    with open("arkad.html", "w", encoding="utf-8") as f:
        f.write(page)

    print("arkad.html écrit — %.0f Ko" % (len(page.encode()) / 1024))
    for j in jeux:
        etat = "%6.0f Ko" % (j["poids"] / 1024) if j["b64"] else "  ABSENT"
        print("   %-10s %s" % (j["nom"], etat))
    if absents:
        print("\nfichiers manquants (cartes affichées en « bientôt ») : "
              + ", ".join(absents))
    return 0


if __name__ == "__main__":
    sys.exit(construire())
