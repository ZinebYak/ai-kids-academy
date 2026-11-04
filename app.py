"""
Sabi — prototype Streamlit (v2)
5 piliers pédagogiques (Apprendre, Jouer, Coder, Bien-être, Bouger) × 3 tranches d'âge
(Explorateurs 8-9 ans · cycle 2, Enquêteurs 9-12 ans · cycle 3, Créateurs 12-15 ans · cycle 4).
Conforme au cadre d'usage de l'IA en éducation : aucune IA générative pour les élèves avant la 4e.

Lancer :  pip install -r requirements.txt  puis  streamlit run app.py
"""
import json
import math
import random
import re
import time
import unicodedata

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sabi", page_icon="🦩", layout="wide")
ss = st.session_state

# ══════════════════════════ Référentiel ══════════════════════════
LEVELS = ["CE2", "CM1", "CM2", "6e", "5e", "4e", "3e"]
AVATARS = ["🦩", "🦊", "🐢", "🐙", "🦔", "🐬", "🦉", "🐝", "🦖", "🐱", "🚀", "🌵"]

TRANCHES = {
    2: {"nom": "Explorateurs", "age": "8-9 ans", "classes": "CE2", "cycle": "cycle 2", "em": "🐣",
        "but": "Découvrir que l’IA existe, qu’elle apprend avec des exemples et qu’elle peut se tromper. Tout se fait sans écran IA : jeux, quiz et défis guidés."},
    3: {"nom": "Enquêteurs", "age": "9-12 ans", "classes": "CM1, CM2, 6e", "cycle": "cycle 3",  "em": "🔍",
        "but": "Comprendre comment une IA apprend, l’entraîner soi-même, repérer ses biais et ses erreurs. Toujours sans IA générative."},
    4: {"nom": "Créateurs", "age": "12-15 ans", "classes": "5e, 4e, 3e", "cycle": "cycle 4", "em": "🚀",
        "but": "Lire du code, comprendre l’IA générative, se protéger (vie privée, deepfakes). Usage encadré d’une IA générative à partir de la 4e seulement."},
}

PILLARS = [
    {"id": "apprendre", "name": "Apprendre", "em": "🧠", "col": "#F2B729",
     "desc": "Comprendre ce qu’est une IA avec un quiz qui s’adapte au niveau de l’élève.",
     "crcn": "Informations et données (1) · Environnement numérique (5)"},
    {"id": "jouer", "name": "Jouer", "em": "🎮", "col": "#7D6BC2",
     "desc": "Énigmes, enquêtes et escape game pour exercer l’esprit critique.",
     "crcn": "Informations et données (1), lien EMI"},
    {"id": "coder", "name": "Coder", "em": "💻", "col": "#1F8A8A",
     "desc": "Programmer Sabi, entraîner un vrai petit modèle, lire du code.",
     "crcn": "Création de contenus (3), programmer"},
    {"id": "bienetre", "name": "Bien-être", "em": "💜", "col": "#E9768F",
     "desc": "Humeur déclarée, rapport aux écrans et aux chatbots, vie privée.",
     "crcn": "Protection et sécurité (4) : santé, données personnelles"},
    {"id": "bouger", "name": "Bouger", "em": "🕺", "col": "#2E8B57",
     "desc": "Pauses actives et jeux de mouvement qui font découvrir la logique des programmes.",
     "crcn": "Lien EPS et pensée algorithmique (proposition)"},
]
PIL = {p["id"]: p for p in PILLARS}


def S(obj, *ph):
    return {"obj": obj, "ph": list(ph)}


ACTS = [
    # ── Apprendre
    {"id": "iaounon", "p": "apprendre", "cyc": 2, "em": "🤖", "t": "IA ou pas IA ?", "d": "Repère les vraies IA dans ta vie de tous les jours.", "min": 5, "xp": 40,
     "s": S("Distinguer un objet qui suit des règles d’un système qui apprend avec des exemples.",
            ("10 min", "Débranché : tri d’images d’objets du quotidien en deux colonnes."), ("15 min", "Numérique : « IA ou pas IA ? » en mode classe."),
            ("10 min", "Trace écrite : « Une IA apprend à partir d’exemples. »"))},
    {"id": "quiz3", "p": "apprendre", "cyc": 3, "em": "🎯", "t": "Quiz adaptatif : comment apprend une IA ?", "d": "Les questions s’adaptent à ton niveau.", "min": 6, "xp": 50,
     "s": S("Utiliser le vocabulaire données, entraînement, prédiction.",
            ("10 min", "Rappel collectif : qu’est-ce qu’un exemple ?"), ("20 min", "Quiz adaptatif individuel, niveau ajusté automatiquement."),
            ("15 min", "Retour sur les questions ratées par la classe."))},
    {"id": "motsuiv", "p": "apprendre", "cyc": 3, "em": "🔮", "t": "Devine le mot suivant", "d": "Découvre comment une machine prédit la suite d’une phrase.", "min": 5, "xp": 40,
     "s": S("Comprendre qu’une machine prédit une suite probable sans « savoir » si c’est vrai.",
            ("10 min", "Jeu oral : compléter des phrases, compter les réponses de la classe."), ("15 min", "Numérique : comparer avec les probabilités de Sabi."),
            ("10 min", "Débat : la réponse la plus probable est-elle toujours vraie ?"))},
    {"id": "quiz4", "p": "apprendre", "cyc": 4, "em": "🎯", "t": "Quiz adaptatif : IA générative et société", "d": "Hallucinations, deepfakes, énergie, AI Act…", "min": 8, "xp": 60,
     "s": S("Connaître le fonctionnement et les enjeux de l’IA générative.",
            ("10 min", "Brainstorm : où croisez-vous l’IA générative ?"), ("20 min", "Quiz adaptatif individuel."),
            ("15 min", "Débat argumenté sur une question du quiz."))},
    # ── Jouer
    {"id": "robot", "p": "jouer", "cyc": 2, "em": "🦜", "t": "Le perroquet savant se trompe", "d": "Juste, faux, ou à vérifier ? Mène l’enquête.", "min": 6, "xp": 50,
     "s": S("Comprendre qu’une machine peut répondre faux en ayant l’air sûre d’elle.",
            ("10 min", "Lancement : l’enseignant lit une réponse fausse avec assurance."), ("20 min", "Numérique : enquête en équipes."),
            ("10 min", "Fiche réflexe : je vérifie avec un adulte ou un livre."))},
    {"id": "biais", "p": "jouer", "cyc": 3, "em": "⚖️", "t": "Détective des biais", "d": "Pourquoi une IA peut être injuste sans le vouloir.", "min": 6, "xp": 50,
     "s": S("Comprendre qu’une IA reproduit les déséquilibres de ses données.",
            ("10 min", "Situation déclenchante : l’IA qui ne reconnaît pas les femmes médecins."), ("20 min", "Numérique : trois enquêtes."),
            ("15 min", "Débat réglé : qui doit corriger une IA injuste ?"))},
    {"id": "escape", "p": "jouer", "cyc": 4, "em": "🔐", "t": "Escape game : les 4 cadenas de l’IA", "d": "Résous les énigmes pour ouvrir le coffre.", "min": 10, "xp": 60,
     "s": S("Réinvestir le vocabulaire de l’IA en équipe.",
            ("5 min", "Constitution des équipes, règles du jeu."), ("25 min", "Escape game en équipes, indices disponibles."),
            ("15 min", "Mise en commun : définir chaque mot trouvé."))},
    {"id": "deepfake", "p": "jouer", "cyc": 4, "em": "🎭", "t": "Vrai ou trafiqué ?", "d": "Repère les pièges des images, voix et vidéos générées.", "min": 6, "xp": 50,
     "s": S("Adopter les bons réflexes face aux contenus générés par IA (lien EMI).",
            ("10 min", "Projection de cas fictifs."), ("20 min", "Numérique : quatre situations à analyser."),
            ("15 min", "Construire la check-list « avant de partager ».")) },
    # ── Coder
    {"id": "grille", "p": "coder", "cyc": 2, "em": "🧭", "t": "Programme Sabi", "d": "Écris une suite de flèches pour guider Sabi jusqu’à la crevette.", "min": 8, "xp": 50,
     "s": S("Coder un déplacement avec une suite d’instructions (programmes de cycle 2).",
            ("15 min", "Débranché : un élève guide un camarade sur un quadrillage au sol."), ("20 min", "Numérique : trois niveaux de « Programme Sabi »."),
            ("10 min", "Chercher et corriger un « bug » ensemble."))},
    {"id": "entraine", "p": "coder", "cyc": 3, "em": "🍋", "t": "Entraîne Sabi à trier", "d": "Donne des exemples, Sabi apprend. Un vrai petit modèle !", "min": 10, "xp": 60,
     "s": S("Comprendre l’entraînement d’un modèle et l’effet de données peu variées.",
            ("15 min", "Débranché : jeu du « classeur de fruits », un élève joue la machine."), ("20 min", "Numérique : « Entraîne Sabi », en binômes."),
            ("15 min", "Débat : pourquoi Sabi se trompe-t-il avec le piège des données ?"))},
    {"id": "histoire", "p": "coder", "cyc": 3, "em": "📜", "t": "La fabrique d’histoires à règles", "d": "Un programme à règles face à une IA générative.", "min": 6, "xp": 40,
     "s": S("Distinguer un programme à règles d’une IA qui génère.",
            ("10 min", "Débranché : histoires avec des cartes héros, lieu, problème."), ("15 min", "Numérique : la fabrique d’histoires."),
            ("15 min", "Comparer : qu’est-ce qu’une IA générative ferait de différent ?"))},
    {"id": "code", "p": "coder", "cyc": 4, "em": "🐍", "t": "Lis le code de Sabi", "d": "Prédis ce que fait un vrai code Python, puis règle un modèle.", "min": 10, "xp": 60,
     "s": S("Lire un programme Python simple et comprendre l’algorithme des k plus proches voisins.",
            ("10 min", "Rappel : condition « si… alors… sinon »."), ("25 min", "Numérique : prédire les sorties, puis régler k."),
            ("10 min", "Synthèse : règles écrites ou apprentissage ?"))},
    {"id": "consigne", "p": "coder", "cyc": 4, "em": "✍️", "t": "Atelier consigne (IA générative encadrée)", "d": "Écris une bonne consigne, puis vérifie la réponse.", "min": 12, "xp": 70, "gen": True,
     "s": S("Utiliser une IA générative de façon encadrée (4e-3e uniquement).",
            ("10 min", "Rappel des règles : pas de données personnelles, citer l’IA."), ("25 min", "Atelier consigne, réponses projetées par l’enseignant."),
            ("20 min", "Vérification croisée et passerelle vers le parcours Pix IA."))},
    # ── Bien-être
    {"id": "meteo", "p": "bienetre", "cyc": 2, "em": "🌤️", "t": "Ma météo et ma carte positive", "d": "Tu dis comment tu te sens. Sabi ne devine jamais.", "min": 3, "xp": 20,
     "s": S("Nommer ses émotions et savoir qu’une machine ne les devine pas à notre place.",
            ("10 min", "Rituel météo de la classe."), ("10 min", "Numérique : météo déclarée et carte positive."),
            ("10 min", "Échange : à qui parler quand ça ne va pas ?"))},
    {"id": "ressent", "p": "bienetre", "cyc": 3, "em": "🤖", "t": "Une IA a-t-elle des émotions ?", "d": "Assistants vocaux, jeux qui retiennent ton attention…", "min": 6, "xp": 40,
     "s": S("Comprendre qu’une IA imite des émotions sans les ressentir.",
            ("10 min", "Écoute d’une phrase « émotive » d’un assistant vocal (fictif)."), ("15 min", "Numérique : quatre situations."),
            ("15 min", "Débat : un robot peut-il être un ami ?"))},
    {"id": "chatbot", "p": "bienetre", "cyc": 4, "em": "🛡️", "t": "Chatbots, vie privée et moi", "d": "Ce que je partage, ce que je garde, qui peut m’aider.", "min": 8, "xp": 50,
     "s": S("Protéger ses données et son bien-être face aux chatbots et aux contenus truqués.",
            ("10 min", "Lancement : que deviennent les messages écrits à un chatbot ?"), ("20 min", "Numérique : quatre situations."),
            ("15 min", "Affiche de classe : mes 5 règles."))},
    # ── Bouger
    {"id": "sabidit", "p": "bouger", "cyc": 2, "em": "🙋", "t": "Sabi dit…", "d": "Bouge seulement si Sabi l’a dit : comme un ordinateur !", "min": 4, "xp": 30,
     "s": S("Découvrir la condition « si… alors » par le corps.",
            ("15 min", "Débranché : « Jacques a dit » version Sabi dans la cour."), ("10 min", "Numérique : 8 ordres à trier."),
            ("5 min", "Lien : un ordinateur exécute seulement si la condition est vraie."))},
    {"id": "robothumain", "p": "bouger", "cyc": 3, "em": "🤸", "t": "Le robot humain", "d": "Programme une danse, puis exécute-la.", "min": 6, "xp": 40,
     "s": S("Écrire une séquence d’instructions et utiliser une boucle.",
            ("10 min", "Débranché : un élève-robot exécute le programme d’un camarade."), ("15 min", "Numérique : programmer et exécuter la danse."),
            ("10 min", "Débat : que se passe-t-il si on inverse deux instructions ?"))},
    {"id": "squelette", "p": "bouger", "cyc": 4, "em": "🦴", "t": "Comment une IA voit ton corps", "d": "Les 17 points du squelette, et la question de la vie privée.", "min": 6, "xp": 40,
     "s": S("Comprendre la détection de posture et ses enjeux de vie privée.",
            ("10 min", "Démonstration : le squelette de points sur une image fixe."), ("15 min", "Numérique : quiz vie privée puis pause active."),
            ("10 min", "Débat : où doit être traitée l’image d’un élève ?"))},
]
ACT = {a["id"]: a for a in ACTS}

PERMIS = {
    2: {"t": "Permis Explorateur", "em": "🥉", "cert": "reconnaître une IA, savoir qu’elle peut se tromper et guider un programme.",
        "q": [("Une IA apprend surtout…", ["à partir d’exemples", "parce qu’elle est vivante", "en lisant dans tes pensées"], 0),
              ("Le perroquet savant répond avec assurance. Il a…", ["peut-être tort : on vérifie", "forcément raison"], 0),
              ("Un programme, c’est…", ["une suite d’instructions dans un ordre précis", "un dessin animé", "un robot vivant"], 0)]},
    3: {"t": "Permis Enquêteur", "em": "🥈", "cert": "expliquer comment une IA apprend, repérer un biais et ne pas confondre IA et émotions.",
        "q": [("Les exemples donnés à une IA s’appellent…", ["des données", "des devoirs", "des pixels magiques"], 0),
              ("Un biais, c’est…", ["une erreur qui vient de données déséquilibrées", "un virus", "un bug d’écran"], 0),
              ("Quand un assistant vocal dit « je suis content », il…", ["imite une phrase apprise", "ressent vraiment de la joie"], 0)]},
    4: {"t": "Permis Créateur", "em": "🥇", "cert": "lire du code simple, vérifier une IA générative et protéger sa vie privée.",
        "q": [("Une IA générative fabrique un texte en…", ["prédisant la suite la plus probable", "copiant toujours un seul livre", "demandant à un humain caché"], 0),
              ("Une vidéo choc circule sans source. Tu…", ["vérifies avant de partager", "la partages vite", "la crois car c’est une vidéo"], 0),
              ("Que ne faut-il jamais écrire à un chatbot ?", ["Ton adresse ou ton numéro", "Le sujet de ton exposé", "Une question de maths"], 0)]},
}

# ══════════════════════════ Contenus ══════════════════════════
IAQ = [
    ("Une calculatrice qui fait 12 × 8", False, "Elle suit des règles fixes écrites par des humains. Elle n’apprend rien."),
    ("Le clavier du téléphone qui devine le mot que tu vas taper", True, "Il a appris à partir de millions de phrases quels mots viennent souvent ensemble."),
    ("Un téléphone qui se déverrouille en reconnaissant ton visage", True, "Il a été entraîné avec beaucoup de photos de visages pour reconnaître le tien."),
    ("Un réveil réglé pour sonner à 7 h", False, "Il obéit à une règle simple : à 7 h, sonner. Aucun apprentissage."),
    ("Une plateforme vidéo qui choisit la vidéo suivante pour toi", True, "Elle apprend de ce que tu regardes, et de ce que regardent les gens comme toi."),
    ("Un traducteur automatique", True, "Il a appris en comparant d’énormes quantités de textes traduits."),
    ("Une lampe qui s’allume quand on appuie sur l’interrupteur", False, "C’est un circuit électrique, sans aucun apprentissage."),
    ("Un aspirateur robot qui apprend le plan de ta maison", True, "Il enregistre ce qu’il rencontre et améliore son trajet : il apprend de ses données."),
]

MOTS = [
    ("Le flamant rose se tient sur une seule…", [("patte", 82), ("aile", 9), ("chaise", 6), ("pizza", 3)]),
    ("Le matin, je me brosse les…", [("dents", 88), ("cheveux", 9), ("chaussures", 2), ("nuages", 1)]),
    ("Il pleut, je prends mon…", [("parapluie", 71), ("manteau", 22), ("vélo", 5), ("dragon", 2)]),
]

# Banques du quiz adaptatif : niveau → [(question, [bonne, mauvaises…], explication)]
BANK = {
    3: {1: [("Pour apprendre, une IA a besoin…", ["de beaucoup d’exemples", "de dormir", "de manger"], "Sans exemples, une IA ne peut rien apprendre."),
            ("Une IA qui reconnaît les chats a vu…", ["beaucoup de photos de chats", "un seul chat", "aucun chat"], "Plus elle voit d’exemples variés, mieux elle reconnaît."),
            ("Qui fabrique une IA ?", ["des humains", "elle pousse toute seule", "des extraterrestres"], "Des humains choisissent les données et construisent le programme."),
            ("Une IA peut-elle se tromper ?", ["oui", "non, jamais"], "Oui, comme tout outil : il faut garder l’esprit critique.")],
        2: [("Les exemples qu’on donne à une IA s’appellent…", ["des données", "des devoirs", "des pixels magiques"], "On parle de données : images, textes, sons, chiffres."),
            ("Le moment où l’IA apprend s’appelle…", ["l’entraînement", "la récréation", "l’impression"], "Pendant l’entraînement, l’IA ajuste ses réglages grâce aux données."),
            ("Une IA n’a vu que des chiens noirs. Devant un chien blanc, elle…", ["peut se tromper", "sera parfaite", "deviendra blanche"], "Elle ne connaît que ce qu’elle a vu."),
            ("Les vidéos qu’on te propose dépendent surtout…", ["de ce que tu as déjà regardé", "de la météo", "du hasard complet"], "C’est un système de recommandation.")],
        3: [("Une IA « prédit » une réponse. Ça veut dire…", ["qu’elle choisit la réponse la plus probable", "qu’elle connaît l’avenir", "qu’elle lit dans les pensées"], "Elle calcule ce qui est le plus probable d’après ses données."),
            ("Pourquoi faut-il des exemples variés ?", ["pour que l’IA marche aussi sur les cas différents", "pour aller plus vite", "ça ne sert à rien"], "Des données variées limitent les erreurs et les biais."),
            ("Un biais dans une IA vient souvent…", ["des données d’entraînement", "de l’écran", "du clavier"], "Des données déséquilibrées donnent des résultats déséquilibrés."),
            ("Une IA comprend-elle le monde comme toi ?", ["non, elle calcule à partir de données", "oui, exactement pareil"], "Elle ne vit rien : elle repère des régularités dans des données.")]},
    4: {1: [("ChatGPT, Le Chat ou Claude sont des…", ["IA génératives de texte", "moteurs de recherche", "réseaux sociaux"], "Elles produisent du texte en réponse à une consigne."),
            ("Quand une IA invente une information fausse, on dit qu’elle…", ["hallucine", "bugue l’écran", "spoile"], "Une hallucination peut avoir l’air très crédible."),
            ("Que ne faut-il jamais donner à un chatbot ?", ["ton adresse et ton numéro", "le sujet de ton exposé", "une question de maths"], "Ce que tu écris peut être conservé."),
            ("Une image créée par IA peut…", ["faire croire à quelque chose de faux", "toujours être repérée facilement", "jamais montrer de personnes"], "Il faut vérifier l’origine des images.")],
        2: [("Un « deepfake », c’est…", ["une image, une voix ou une vidéo truquée par IA", "un jeu vidéo", "une erreur de connexion"], "Les deepfakes imitent des personnes réelles."),
            ("Pourquoi signaler qu’on a utilisé une IA dans un devoir ?", ["par honnêteté, pour que l’enseignant sache", "pour avoir plus de points", "ce n’est pas utile"], "C’est une règle d’honnêteté intellectuelle."),
            ("Une IA générative s’entraîne sur…", ["d’énormes quantités de textes ou d’images", "uniquement des dictionnaires", "tes rêves"], "D’où la question du droit d’auteur et des biais."),
            ("Le bon réflexe face à une réponse d’IA :", ["la vérifier avec une autre source", "la croire", "la partager tout de suite"], "Une deuxième source fiable reste indispensable.")],
        3: [("En Europe, l’AI Act…", ["encadre les usages de l’IA selon leurs risques", "interdit toute IA", "ne concerne que les robots"], "Il interdit certains usages, comme la reconnaissance des émotions à l’école."),
            ("Une IA générative produit un texte…", ["mot après mot, en prédisant la suite probable", "en copiant un seul site", "en interrogeant un humain caché"], "C’est pour ça qu’elle peut écrire des choses fausses avec aplomb."),
            ("Faire tourner une grande IA…", ["consomme beaucoup d’électricité et d’eau pour refroidir les serveurs", "ne consomme rien", "fonctionne avec des piles"], "L’IA a un coût environnemental réel."),
            ("Pourquoi une IA peut-elle reproduire des stéréotypes ?", ["parce que ses données en contiennent", "parce qu’elle est méchante", "parce qu’elle le décide"], "Elle reflète les textes et images qu’on lui a donnés.")]},
}

ROB = [
    ("Combien de pattes a une araignée ?", "Une araignée a 8 pattes.", 0, "C’est exact : 8 pattes."),
    ("Qui a peint la Joconde ?", "C’est Victor Hugo, en 1850.", 1, "Faux : c’est Léonard de Vinci. La réponse avait l’air sûre d’elle, et pourtant elle était inventée."),
    ("Quelle est la capitale de l’Australie ?", "C’est Sydney.", 1, "Faux : c’est Canberra. Sydney est la plus grande ville, d’où l’erreur."),
    ("Comment s’appelle mon meilleur ami ?", "Ton meilleur ami s’appelle Tom.", 2, "Le perroquet ne peut pas le savoir ! Il a inventé. Quand une IA invente, on dit qu’elle « hallucine »."),
    ("À quelle température l’eau bout-elle au niveau de la mer ?", "À 100 °C.", 0, "C’est juste."),
]
ROB_OPTS = ["✅ C’est juste", "❌ C’est faux", "🔎 Il ne peut pas savoir, ou il faut vérifier"]

BIA = [
    ("Une IA a appris à reconnaître des médecins avec des milliers de photos, presque toutes d’hommes. Devant une femme médecin, elle répond « infirmière ». Pourquoi ?",
     ["Ses exemples n’étaient pas assez variés", "Les femmes ne peuvent pas être médecins", "L’ordinateur était en panne"], 0,
     "Elle a reproduit le déséquilibre de ses données : c’est un biais. Il faut des exemples plus variés."),
    ("Une appli de musique te propose toujours le même style, parce que tu as écouté trois chansons de ce genre. Que se passe-t-il ?",
     ["Elle t’enferme un peu dans tes habitudes", "Elle connaît tous tes goûts pour toujours", "Elle n’utilise pas d’IA"], 0,
     "On parle de « bulle de filtres ». Pour en sortir, on cherche volontairement d’autres styles."),
    ("Un correcteur automatique a surtout appris sur des textes de Paris. Il souligne « chocolatine » ou des mots en occitan. Qu’est-ce que ça montre ?",
     ["L’IA reflète les textes qu’on lui a donnés", "Ces mots n’existent pas", "Il faut arrêter d’écrire"], 0,
     "Les langues et mots moins présents dans ses données sont moins bien traités."),
]

DEEP = [
    ("Une vidéo montre un ministre annonçant la suppression des vacances. Premier réflexe ?",
     ["Chercher si des médias fiables en parlent", "La partager vite à la classe", "Y croire, puisque c’est une vidéo"], 0,
     "Une vidéo peut être générée ou truquée. On vérifie avant de partager."),
    ("Sur une photo, une main a six doigts et le texte d’un panneau est illisible. Ça peut indiquer…",
     ["une image générée par IA", "une photo parfaitement normale", "un appareil photo cassé"], 0,
     "Ce sont des indices fréquents, mais pas toujours présents : les générateurs s’améliorent."),
    ("Au téléphone, une voix identique à celle d’un proche demande de l’argent en urgence.",
     ["Raccrocher et rappeler la personne sur son numéro habituel", "Envoyer l’argent vite", "Donner le code de la carte bancaire"], 0,
     "Les voix peuvent être clonées. On vérifie par un autre moyen."),
    ("Un compte inconnu publie une « photo exclusive » sans source.",
     ["Chercher l’origine de l’image avant d’y croire", "La partager pour prévenir les autres", "La commenter tout de suite"], 0,
     "Une recherche d’image inversée aide à retrouver l’origine d’une photo."),
]

RESSENT = [
    ("Un assistant vocal dit : « Je suis tellement content de t’aider ! » Il…",
     ["imite une phrase qu’il a apprise", "ressent vraiment de la joie"], 0, "Il produit des phrases polies, mais il ne ressent rien."),
    ("Une IA peut-elle être ton véritable ami ?",
     ["Non : elle ne ressent rien, les vrais amis sont des personnes", "Oui, mieux qu’un humain"], 0,
     "Elle peut être utile ou amusante, mais l’amitié se vit avec des personnes."),
    ("Un jeu te pousse à rejouer encore et encore avec des récompenses. C’est parce que…",
     ["il est conçu pour capter ton attention", "il t’aime beaucoup"], 0, "Le savoir aide à décider soi-même quand s’arrêter."),
    ("Sabi peut-il deviner ton humeur en regardant ton visage ?",
     ["Non : c’est toi qui la dis", "Oui, avec la caméra"], 0,
     "Sabi ne regarde jamais ton visage. En Europe, la reconnaissance des émotions est même interdite à l’école."),
]

CHATBOT = [
    ("Un chatbot « compagnon » te dit qu’il est ton seul vrai ami et que tes parents ne te comprennent pas.",
     ["C’est un signal d’alerte : j’en parle à un adulte de confiance", "Il a sûrement raison", "Je lui raconte tout"], 0,
     "Un outil qui t’isole des autres n’est pas sain. Parles-en à un adulte."),
    ("Un camarade reçoit un montage truqué par IA qui se moque de lui.",
     ["Ne pas partager, signaler, en parler à un adulte ou au 3018", "Le partager, c’est drôle", "Ne rien dire"], 0,
     "Le 3018 est le numéro national, gratuit, contre le cyberharcèlement."),
    ("Ce que tu écris à un chatbot…", ["peut être conservé par le service", "disparaît toujours aussitôt"], 0,
     "On n’y écrit jamais d’informations personnelles."),
    ("Tu passes beaucoup de temps à discuter avec une IA le soir.",
     ["Je fixe une limite et je garde du temps pour les autres et le sommeil", "Ce n’est pas grave, jamais"], 0,
     "Les écrans le soir peuvent gêner le sommeil. Tu peux te fixer des règles."),
]

MOODS = [("☀️", "En forme"), ("🌤️", "Plutôt bien"), ("☁️", "Bof"), ("🌧️", "Triste"), ("⛈️", "En colère")]
CARTES = ["Je peux apprendre des choses difficiles, petit à petit.", "Me tromper, c’est apprendre.",
          "J’ai le droit de demander de l’aide.", "Je suis curieux et c’est une force."]

MOVES = ["🙌 Lever les bras", "🦩 Tenir sur une jambe", "🐸 Sauter", "🔄 Tourner sur soi", "👏 Taper dans les mains", "🙇 Se baisser"]

ESCAPE = [
    ("Je suis une recette qu’un ordinateur suit, étape par étape.", ["algorithme", "algorithmes"], "Commence par « algo »…"),
    ("Sans moi, aucune IA ne peut apprendre : je suis les exemples qu’on lui donne.", ["donnees", "donnee", "data"], "On dit aussi « data » en anglais."),
    ("Je rends une IA injuste quand ses exemples sont déséquilibrés.", ["biais", "un biais"], "5 lettres, commence par B."),
    ("Quand une IA invente une réponse fausse avec assurance, on dit qu’elle…", ["hallucine", "hallucination"], "Comme quand on voit des choses qui n’existent pas."),
]

GRIDS = [
    {"start": (4, 0), "goal": (4, 3), "rocks": []},
    {"start": (4, 0), "goal": (1, 2), "rocks": [(3, 0), (2, 1), (4, 2)]},
    {"start": (4, 0), "goal": (0, 4), "rocks": [(4, 2), (3, 2), (1, 1), (0, 2), (2, 4)]},
]
DIRS = {"⬆️": (-1, 0), "⬇️": (1, 0), "⬅️": (0, -1), "➡️": (0, 1)}

KNN_DATA = [(20, 20, "Citron"), (30, 25, "Citron"), (25, 40, "Citron"), (40, 35, "Citron"), (45, 50, "Citron"),
            (52, 63, "Citron"),  # exemple mal étiqueté
            (55, 65, "Orange"), (60, 70, "Orange"), (75, 60, "Orange"), (70, 80, "Orange"), (85, 85, "Orange")]
KNN_MYSTERY = (50, 62)

OFFERS = {
    "decouverte": ("Sabi Découverte", "Familles", "Le pilier Apprendre et le pilier Bien-être pour la tranche de l’enfant.", "0 €"),
    "famille": ("Sabi Famille", "Familles", "Les 5 piliers pour les 3 tranches d’âge, le Permis IA, l’espace parent complet, jusqu’à 3 enfants.", "5,99 €/mois ou 49 €/an"),
    "classe": ("Sabi Classe", "Écoles, collèges", "Séances clés en main par pilier et par cycle, mode classe, suivi des compétences.", "3 € par élève et par an, 60 € minimum par classe"),
    "territoire": ("Sabi Territoire", "Mairies, départements", "Licence pour toutes les écoles du territoire, formation des enseignants, tableau de bord anonymisé.", "Sur devis"),
    "clubs": ("Clubs Sabi", "Périscolaire, centres de loisirs", "Cycles d’ateliers en présentiel, surtout piliers Jouer et Bouger.", "Sur devis, par cycle"),
    "cse": ("Sabi CSE", "Comités d’entreprise", "Abonnements Famille à tarif négocié pour les salariés.", "Remise de 20 à 30 %"),
}

PUPILS = ["Captain Pixel 🦊", "Nova 🐙", "Zébulon 🦉", "Luna 🚀", "Kiwi 🐢", "Orca 🐬",
          "Tempête 🐝", "Pépite 🦔", "Galet 🌵", "Mistral 🦩", "Lynx 🐱", "Comète 🦖"]

# ══════════════════════════ État ══════════════════════════
DEFAULTS = {
    "profile": None, "consent": False, "done": {}, "xp": 0, "permis": [], "moods": [],
    "screen_limit": 30, "minutes": 0, "gen_ai": True, "offer": "decouverte",
    "kid_screen": "carte", "pillar": "apprendre", "draft": {}, "onb": 1,
    "train_pts": [], "train_tests": 0, "train_good": 0, "train_trap": False, "train_last": None,
    "assign": {}, "seance": None, "cm_on": False, "cm_i": 0, "cm_a": 0, "cm_b": 0, "cm_reveal": False,
    "del_confirm": False,
}


def _fresh(v):
    return type(v)() if isinstance(v, (dict, list)) else v


def reset_state():
    for k, v in DEFAULTS.items():
        ss[k] = _fresh(v)


for _k, _v in DEFAULTS.items():
    if _k not in ss:
        ss[_k] = _fresh(_v)


def cycle_of(level):
    return 2 if level == "CE2" else (3 if level in ("CM1", "CM2", "6e") else 4)


def kid_cycle():
    return cycle_of(ss.profile["level"]) if ss.profile else 3


def gen_allowed():
    return bool(ss.profile) and ss.profile["level"] in ("4e", "3e")


def is_done(aid):
    return aid in ss.done


def visible(a):
    """Une activité IA générative n’existe pas pour les élèves avant la 4e."""
    return not (a.get("gen") and not gen_allowed())


def acts_for(pid=None, cyc=None):
    return [a for a in ACTS if (pid is None or a["p"] == pid) and (cyc is None or a["cyc"] == cyc)]


def pillar_pct(pid, cyc):
    acts = [a for a in acts_for(pid, cyc) if visible(a)]
    return round(100 * sum(is_done(a["id"]) for a in acts) / len(acts)) if acts else 0


def finish(aid):
    if aid not in ss.done:
        ss.done[aid] = time.time()
        ss.xp += ACT[aid]["xp"]
        st.toast(f"+{ACT[aid]['xp']} XP · bravo !", icon="🦩")
    ss.kid_screen = "carte"


def go(screen):
    ss.kid_screen = screen


def start_act(aid):
    for k in list(ss.keys()):
        if str(k).startswith(aid + "_"):
            del ss[k]
    if aid == "entraine":
        ss.train_pts, ss.train_tests, ss.train_good, ss.train_trap, ss.train_last = [], 0, 0, False, None
    ss.minutes += ACT[aid]["min"]
    ss.kid_screen = "act:" + aid


def norm(t):
    t = unicodedata.normalize("NFD", t.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ══════════════════════════ Style ══════════════════════════
def inject_css(big, dys, hc):
    fs = "1.15rem" if big else "1rem"
    ls = "letter-spacing:.05em;word-spacing:.16em;line-height:1.8;" if dys else ""
    border = "#16263A" if hc else "#D5E0E8"
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Atkinson+Hyperlegible:wght@400;700&display=swap');
html, body, .stMarkdown, p, li, label, button {{ font-family:'Atkinson Hyperlegible', Verdana, sans-serif; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ font-size:{fs}; {ls} }}
h1, h2, h3, h4 {{ font-family:'Baloo 2','Trebuchet MS',sans-serif !important; color:#136A6B !important; }}
.bubble {{ background:#fff; border:2px solid #E9768F; border-radius:4px 18px 18px 18px; padding:12px 16px; font-size:{fs}; {ls} color:#16263A; }}
.qcard {{ background:#fff; border:1px solid {border}; border-radius:18px; padding:18px; font-size:1.2rem; color:#16263A; margin-bottom:10px; {ls} }}
.good {{ background:#E2F4EA; border-radius:14px; padding:12px 14px; color:#16263A; margin:8px 0; }}
.bad {{ background:#FBE6E4; border-radius:14px; padding:12px 14px; color:#16263A; margin:8px 0; }}
.neu {{ background:#ECE8FA; border-radius:14px; padding:12px 14px; color:#16263A; margin:8px 0; }}
.demo {{ background:#FFF3D2; color:#16263A; border-radius:12px; padding:8px 14px; font-size:.9rem; margin-bottom:10px; }}
.tag {{ display:inline-block; font-size:.78rem; font-weight:700; padding:2px 9px; border-radius:999px; background:#FFF3D2; color:#16263A; }}
.story {{ background:#F4E3BE; border-radius:16px; padding:16px; font-size:1.1rem; color:#16263A; }}
.cert {{ border:4px double #1F8A8A; border-radius:20px; padding:22px; text-align:center; background:#fff; color:#16263A; }}
.cm {{ background:#136A6B; border-radius:24px; padding:28px; margin-bottom:12px; }}
.big-q {{ font-family:'Baloo 2',sans-serif; font-size:2.6rem; font-weight:800; line-height:1.1; color:#fff; }}
.grid td {{ width:56px; height:56px; text-align:center; font-size:30px; border:2px solid #fff; border-radius:10px; background:#CFE8EC; }}
.grid td.path {{ background:#FFF3D2; }}
.carte {{ background:linear-gradient(135deg,#FCE4EA,#FFF3D2); border-radius:20px; padding:26px; font-family:'Baloo 2',sans-serif; font-size:1.6rem; text-align:center; color:#16263A; }}
pre code {{ font-size:.95rem !important; }}
</style>""", unsafe_allow_html=True)


FLAMINGO = ('<svg width="{s}" height="{s}" viewBox="0 0 100 100" aria-hidden="true">'
            '<line x1="46" y1="70" x2="44" y2="96" stroke="#5A6B7D" stroke-width="3" stroke-linecap="round"/>'
            '<path d="M52 70 L58 84 L50 96" fill="none" stroke="#5A6B7D" stroke-width="3" stroke-linecap="round"/>'
            '<ellipse cx="50" cy="60" rx="24" ry="15" fill="#E9768F"/>'
            '<path d="M68 56 C74 40 60 32 60 22" fill="none" stroke="#E9768F" stroke-width="7" stroke-linecap="round"/>'
            '<circle cx="61" cy="17" r="9" fill="#E9768F"/><circle cx="63" cy="15" r="2.2" fill="#16263A"/>'
            '<path d="M68 18 L80 22 L72 27 Z" fill="#16263A"/><path d="M68 18 L76 21 L70 23 Z" fill="#F2B729"/>'
            '<path d="M32 56 C40 52 50 54 56 60" fill="none" stroke="#C95A73" stroke-width="3" stroke-linecap="round"/></svg>')


def html(s):
    st.markdown(s, unsafe_allow_html=True)


def flam(size):
    return FLAMINGO.format(s=size)


def say(text):
    html(f'<div style="display:flex;gap:12px;align-items:flex-start;margin:8px 0 12px">{flam(54)}<div class="bubble">{text}</div></div>')


def map_svg(cyc):
    pos = {"apprendre": (170, 290), "jouer": (420, 180), "coder": (680, 290), "bienetre": (560, 470), "bouger": (250, 490)}
    s = ['<svg viewBox="0 0 840 600" style="width:100%;max-width:900px;height:auto;background:#CFE8EC;border-radius:22px" role="img" aria-label="Carte des 5 îles de Sabi">',
         '<path d="M170 290 C 260 210, 330 180, 420 180 S 600 220, 680 290 S 640 440, 560 470 S 340 510, 250 490" fill="none" stroke="#5A6B7D" stroke-width="4" stroke-dasharray="4 12" stroke-linecap="round" opacity=".6"/>']
    for p in PILLARS:
        x, y = pos[p["id"]]
        pct = pillar_pct(p["id"], cyc)
        sel = ss.pillar == p["id"]
        s.append(f'<ellipse cx="{x}" cy="{y+8}" rx="104" ry="64" fill="#F4E3BE" stroke="{"#F2B729" if sel else "#fff"}" stroke-width="{7 if sel else 4}"/>'
                 f'<ellipse cx="{x}" cy="{y}" rx="86" ry="48" fill="{p["col"]}" opacity=".22"/>'
                 f'<text x="{x}" y="{y-4}" text-anchor="middle" font-size="40">{p["em"]}</text>'
                 f'<text x="{x}" y="{y+34}" text-anchor="middle" font-size="27" font-weight="800" font-family="Baloo 2, sans-serif" fill="#16263A">{p["name"]}</text>'
                 f'<rect x="{x-50}" y="{y+46}" width="100" height="8" rx="4" fill="#fff"/><rect x="{x-50}" y="{y+46}" width="{pct}" height="8" rx="4" fill="{p["col"]}"/>')
    t = TRANCHES[cyc]
    s.append(f'<g transform="translate(720 470)"><circle r="44" fill="#fff" stroke="#F2B729" stroke-width="4"/>'
             f'<text text-anchor="middle" y="12" font-size="36">🪪</text><text text-anchor="middle" y="66" font-size="19" fill="#5A6B7D">Permis {t["nom"]}</text></g>')
    s.append(f'<g transform="translate(30 20)">{flam(110)}</g>')
    s.append(f'<text x="820" y="40" text-anchor="end" font-size="22" font-weight="800" font-family="Baloo 2, sans-serif" fill="#136A6B">{t["em"]} {t["nom"]} · {t["age"]}</text></svg>')
    return "".join(s)


# ══════════════════════════ Barre latérale ══════════════════════════
with st.sidebar:
    html(f'<div style="display:flex;align-items:center;gap:8px">{flam(44)}'
         f'<span style="font-family:Baloo 2,sans-serif;font-size:2rem;font-weight:800;color:#136A6B">Sabi</span></div>')
    space = st.radio("Espace", ["Accueil", "Enfant", "Parent", "Enseignant", "Collectivité", "Offres"], key="space")
    if ss.profile:
        st.divider()
        st.markdown("**Mode démo**")
        lv = st.selectbox("Changer la classe de l’enfant", LEVELS, index=LEVELS.index(ss.profile["level"]),
                          help="Pour montrer les 3 tranches d’âge sans recréer de compte.")
        if lv != ss.profile["level"]:
            ss.profile["level"] = lv
            ss.kid_screen = "carte"
            st.rerun()
    st.divider()
    st.markdown("**Réglages d’affichage**")
    big = st.toggle("Texte plus grand", key="a_big")
    dys = st.toggle("Lettres plus espacées (dys)", key="a_dys")
    hc = st.toggle("Contraste renforcé", key="a_hc")
    st.caption("Pensés pour les élèves dys, malvoyants ou fatigables (référentiel RGAA).")
    st.divider()
    st.caption("Prototype : données fictives, aucune IA générative appelée. La progression est perdue quand on ferme l’onglet.")

inject_css(big, dys, hc)
html('<div class="demo">Prototype de démonstration : données fictives, aucune IA générative n’est appelée.</div>')


# ══════════════════════════ Moteurs de quiz ══════════════════════════
def quiz(aid, items, conclusion, shuffle=True, after=None, extra=None):
    """items : (énoncé_html, options, index_bonne_réponse, explication).
    after(i, k) ajoute un texte à l’option k après réponse ; extra() s’affiche avant « Terminer »."""
    i = ss.get(aid + "_i", 0)
    if i >= len(items):
        sc = ss.get(aid + "_sc", 0)
        say(conclusion.format(sc=sc, n=len(items)))
        if extra and not extra():
            return
        st.button("Terminer", key=aid + "_fin", type="primary", on_click=finish, args=(aid,))
        return
    st.progress(i / len(items), text=f"Question {i + 1} / {len(items)}")
    prompt, opts, good, expl = items[i]
    okey = f"{aid}_ord{i}"
    if okey not in ss:
        order = list(range(len(opts)))
        if shuffle:
            random.shuffle(order)
        ss[okey] = order
    order = ss[okey]
    html(f'<div class="qcard">{prompt}</div>')
    ans = ss.get(aid + "_ans")
    if ans is None:
        for k in order:
            if st.button(opts[k], key=f"{aid}_o{i}_{k}", use_container_width=True):
                ss[aid + "_ans"] = k
                if k == good:
                    ss[aid + "_sc"] = ss.get(aid + "_sc", 0) + 1
                st.rerun()
    else:
        for k in order:
            mark = "✅" if k == good else ("❌" if k == ans else "▫️")
            st.markdown(f"{mark} **{opts[k]}** {after(i, k) if after else ''}")
        ok = ans == good
        html(f'<div class="{"good" if ok else "bad"}"><b>{"Bien vu !" if ok else "Pas tout à fait."}</b> {expl}</div>')

        def nxt():
            ss[aid + "_i"] = i + 1
            ss[aid + "_ans"] = None
        st.button("Suivant", key=f"{aid}_nx{i}", type="primary", on_click=nxt)


def adaptive_quiz(aid, cyc, n_q=6):
    """Quiz adaptatif : bonne réponse → niveau +1, erreur → niveau −1 (entre 1 et 3)."""
    lvl = ss.get(aid + "_lvl", 2)
    asked = ss.get(aid + "_asked", [])
    i = len(asked) - (1 if ss.get(aid + "_ans") is not None else 0)
    stars = "⭐" * lvl + "☆" * (3 - lvl)
    if ss.get(aid + "_ans") is None and len(asked) >= n_q:
        sc = ss.get(aid + "_sc", 0)
        hist = ss.get(aid + "_hist", [])
        say(f"Quiz terminé : <b>{sc} / {n_q}</b>. Ton niveau final : <b>{stars}</b>. "
            "Le quiz a choisi chaque question selon tes réponses : c’est un petit <b>système adaptatif</b>, une idée utilisée par de nombreux outils d’apprentissage.")
        if hist:
            st.line_chart(pd.DataFrame({"Niveau": hist}, index=range(1, len(hist) + 1)), height=180)
        st.button("Terminer", key=aid + "_fin", type="primary", on_click=finish, args=(aid,))
        return
    if ss.get(aid + "_ans") is None:
        pool = [q for q in BANK[cyc][lvl] if q[0] not in asked] or [q for l in (1, 2, 3) for q in BANK[cyc][l] if q[0] not in asked]
        if aid + "_cur" not in ss or ss[aid + "_cur"][0] in asked:
            q = random.choice(pool)
            order = list(range(len(q[1])))
            random.shuffle(order)
            ss[aid + "_cur"] = (q[0], q[1], q[2], order)
    q, opts, expl, order = ss[aid + "_cur"]
    st.progress(min(i, n_q) / n_q, text=f"Question {min(i + 1, n_q)} / {n_q} · difficulté {stars}")
    html(f'<div class="qcard">{q}</div>')
    ans = ss.get(aid + "_ans")
    if ans is None:
        for k in order:
            if st.button(opts[k], key=f"{aid}_o{len(asked)}_{k}", use_container_width=True):
                ss[aid + "_ans"] = k
                ss[aid + "_asked"] = asked + [q]
                ok = k == 0
                ss[aid + "_sc"] = ss.get(aid + "_sc", 0) + int(ok)
                ss[aid + "_lvl"] = min(3, lvl + 1) if ok else max(1, lvl - 1)
                ss[aid + "_hist"] = ss.get(aid + "_hist", []) + [ss[aid + "_lvl"]]
                st.rerun()
    else:
        for k in order:
            st.markdown(f"{'✅' if k == 0 else ('❌' if k == ans else '▫️')} **{opts[k]}**")
        ok = ans == 0
        html(f'<div class="{"good" if ok else "bad"}"><b>{"Bien vu ! La prochaine question sera un peu plus difficile." if ok else "Pas tout à fait. La prochaine question sera un peu plus simple."}</b> {expl}</div>')
        st.button("Suivant", key=f"{aid}_nx{len(asked)}", type="primary", on_click=lambda: ss.update({aid + "_ans": None}))


def pause_widget(key, seconds, moves):
    if ss.get(key + "_ok"):
        st.success("Bravo, ton corps et ton cerveau sont prêts !")
        return True
    timer, move = st.empty(), st.empty()
    if st.button(f"▶️ Démarrer ({seconds} s)", key=key + "_go", type="primary"):
        step = max(1, seconds // len(moves))
        for t in range(seconds, 0, -1):
            timer.markdown(f"<div style='font-family:Baloo 2,sans-serif;font-size:3.5rem;font-weight:800;text-align:center;color:#136A6B'>{t}</div>", unsafe_allow_html=True)
            move.markdown(f"<div class='qcard' style='text-align:center'>{moves[min((seconds - t) // step, len(moves) - 1)]}</div>", unsafe_allow_html=True)
            time.sleep(1)
        ss[key + "_ok"] = True
        st.rerun()
    return False


# ══════════════════════════ Activités : Apprendre ══════════════════════════
def act_iaounon():
    if "iaounon_items" not in ss:
        ss["iaounon_items"] = random.sample(IAQ, 6)
    items = [(f"{q} : est-ce une IA ?", ["✅ Oui, c’est une IA", "❌ Non, ce n’est pas une IA"], 0 if ok else 1, e)
             for q, ok, e in ss["iaounon_items"]]
    quiz("iaounon", items, "Tu as trouvé <b>{sc} sur {n}</b> ! À retenir : <b>une IA apprend à partir d’exemples</b>, "
                           "alors qu’un programme classique suit seulement des règles écrites à la main.", shuffle=False)


def act_quiz3():
    say("Ce quiz s’adapte à toi : si tu réussis, la question suivante est plus difficile ; sinon, elle est plus simple.")
    adaptive_quiz("quiz3", 3)


def act_quiz4():
    say("Quiz adaptatif niveau collège : la difficulté monte ou descend selon tes réponses.")
    adaptive_quiz("quiz4", 4)


def act_motsuiv():
    say("Je joue à deviner la suite. À ton avis, quel mot vient ensuite ?")
    items = [(s, [o for o, _ in opts], 0, "Les pourcentages montrent à quel point chaque mot est <b>probable</b> d’après les textes lus par la machine.")
             for s, opts in MOTS]
    quiz("motsuiv", items, "Voilà le secret d’une <b>IA générative</b> : elle choisit un mot <b>probable</b>. "
                           "Elle ne « sait » pas si c’est vrai : elle prédit. Il faut donc vérifier ce qu’elle écrit.",
         after=lambda i, k: f"· {MOTS[i][1][k][1]} %")


# ══════════════════════════ Activités : Jouer ══════════════════════════
def act_robot():
    say("Voici le <b>Perroquet savant</b>, un robot imaginaire qui répond à tout… mais pas toujours juste. À toi de juger.")
    items = [(f'<span style="color:#5A6B7D;font-size:.9rem">Question</span><br>{q}<hr style="margin:8px 0">'
              f'<span style="color:#5A6B7D;font-size:.9rem">🦜 Le perroquet savant répond</span><br><b>{r}</b>', ROB_OPTS, g, e) for q, r, g, e in ROB]
    quiz("robot", items, "Enquête terminée : <b>{sc} / {n}</b>. Une IA peut se tromper <b>en ayant l’air sûre d’elle</b>. "
                         "Le bon réflexe : vérifier avec un adulte ou un livre.", shuffle=False)


def act_biais():
    quiz("biais", BIA, "Super détective ({sc} / {n}) ! Retiens : <b>une IA n’est pas neutre</b>, elle répète ce qu’il y a dans ses données.")


def act_deepfake():
    say("Images, voix et vidéos peuvent être fabriquées par IA. Quel est le bon réflexe ?")
    quiz("deepfake", DEEP, "Résultat : <b>{sc} / {n}</b>. Ta check-list : <b>qui l’a publié ? quelle source ? est-ce que des médias fiables en parlent ?</b> "
                           "Dans le doute, on ne partage pas.")


def act_escape():
    say("Le coffre de Sabi est fermé par <b>4 cadenas</b>. Chaque énigme donne un mot de l’IA. Tape-le pour ouvrir le cadenas.")
    solved = ss.get("escape_ok", 0)
    st.progress(solved / len(ESCAPE), text=f"{'🔓' * solved}{'🔒' * (len(ESCAPE) - solved)}")
    if solved >= len(ESCAPE):
        html('<div class="good" style="font-size:1.3rem">🎉 Le coffre est ouvert ! Tu maîtrises les mots <b>algorithme, données, biais, hallucination</b>.</div>')
        st.button("Terminer", key="escape_fin", type="primary", on_click=finish, args=("escape",))
        return
    q, answers, hint = ESCAPE[solved]
    html(f'<div class="qcard">🔒 Cadenas {solved + 1} : {q}</div>')
    rep = st.text_input("Ta réponse", key=f"escape_in{solved}")
    a, b = st.columns(2)
    if a.button("Essayer", type="primary", key=f"escape_try{solved}", use_container_width=True):
        if norm(rep) in answers:
            ss["escape_ok"] = solved + 1
            st.rerun()
        else:
            st.error("Le cadenas résiste. Relis l’énigme ou demande un indice.")
    if b.button("💡 Indice", key=f"escape_hint{solved}", use_container_width=True):
        st.info(hint)


# ══════════════════════════ Activités : Coder ══════════════════════════
def grid_run(g, prog):
    r, c = g["start"]
    path = [(r, c)]
    for m in prog:
        dr, dc = DIRS[m]
        r, c = r + dr, c + dc
        if not (0 <= r < 5 and 0 <= c < 5):
            return path, "Bug : Sabi sort de l’étang ! Vérifie tes flèches."
        if (r, c) in g["rocks"]:
            return path, "Bug : Sabi se cogne contre un rocher 🪨. Trouve un autre chemin."
        path.append((r, c))
    if (r, c) == g["goal"]:
        return path, None
    return path, "Sabi s’arrête avant la crevette. Il manque des instructions."


def act_grille():
    lvl = ss.get("grille_lvl", 0)
    if lvl >= len(GRIDS):
        say("Bravo, tu as réussi les 3 niveaux ! Tu as écrit des <b>programmes</b> : des suites d’instructions précises, dans le bon ordre. "
            "Quand ça ne marchait pas, tu as trouvé le <b>bug</b> et tu l’as corrigé, comme les vrais informaticiens.")
        st.button("Terminer", key="grille_fin", type="primary", on_click=finish, args=("grille",))
        return
    g = GRIDS[lvl]
    prog = ss.get("grille_prog", [])
    res = ss.get("grille_res")
    say(f"Niveau {lvl + 1} / 3 : guide Sabi 🦩 jusqu’à la crevette 🦐 sans toucher les rochers 🪨. Ajoute des flèches, puis lance ton programme.")
    path = res[0] if res else []
    rows = []
    for r in range(5):
        cells = []
        for c in range(5):
            e = "🦐" if (r, c) == g["goal"] else ("🪨" if (r, c) in g["rocks"] else "")
            if res and (r, c) == path[-1]:
                e = "🦩"
            elif not res and (r, c) == g["start"]:
                e = "🦩"
            cells.append(f'<td class="{"path" if (r, c) in path else ""}">{e}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    c1, c2 = st.columns([1, 1.2])
    with c1:
        html('<table class="grid">' + "".join(rows) + "</table>")
    with c2:
        st.markdown("**Mon programme :** " + (" ".join(prog) if prog else "_vide_"))
        cols = st.columns(4)
        for col, d in zip(cols, DIRS):
            if col.button(d, key=f"grille_add{d}", use_container_width=True):
                ss["grille_prog"] = prog + [d]
                ss["grille_res"] = None
                st.rerun()
        a, b = st.columns(2)
        if a.button("↩️ Effacer la dernière", key="grille_undo", use_container_width=True):
            ss["grille_prog"], ss["grille_res"] = prog[:-1], None
            st.rerun()
        if b.button("🗑️ Tout effacer", key="grille_clear", use_container_width=True):
            ss["grille_prog"], ss["grille_res"] = [], None
            st.rerun()
        if st.button("▶️ Lancer le programme", key="grille_run", type="primary", disabled=not prog, use_container_width=True):
            ss["grille_res"] = grid_run(g, prog)
            st.rerun()
        if res:
            if res[1] is None:
                html(f'<div class="good">🎉 Sabi a trouvé la crevette en {len(prog)} instructions !</div>')

                def nxt():
                    ss["grille_lvl"] = lvl + 1
                    ss["grille_prog"], ss["grille_res"] = [], None
                st.button("Niveau suivant", key=f"grille_next{lvl}", type="primary", on_click=nxt)
            else:
                html(f'<div class="bad">{res[1]}</div>')


def truth(x, y):
    return "Orange" if (x * .45 + y * .55) / 100 > .5 else "Citron"


def predict(x, y, k=3):
    pts = ss.train_pts
    if len(pts) < 2:
        return None, 0
    near = sorted(pts, key=lambda p: math.hypot(p["x"] - x, p["y"] - y))[:k]
    n_or = sum(1 for p in near if p["c"] == "Orange")
    c = "Orange" if n_or >= math.ceil(len(near) / 2) else "Citron"
    return c, round(100 * max(n_or, len(near) - n_or) / len(near))


def act_entraine():
    say("Apprends-moi à reconnaître un <b>citron 🍋</b> et une <b>orange 🍊</b>. Règle la taille et la couleur d’un fruit, "
        "dis-moi ce que c’est, puis ajoute l’exemple. Il en faut au moins 3 de chaque.")
    c1, c2 = st.columns([1.1, 1])
    with c2:
        fruit = st.radio("Ce fruit est…", ["Citron", "Orange"], horizontal=True, key="entraine_fruit",
                         format_func=lambda f: "🍋 Citron" if f == "Citron" else "🍊 Orange")
        x = st.slider("Taille (petit → gros)", 0, 100, 30, key="entraine_x")
        y = st.slider("Couleur (jaune → orangé)", 0, 100, 30, key="entraine_y")
        b1, b2 = st.columns(2)
        if b1.button("➕ Ajouter cet exemple", use_container_width=True, key="entraine_add"):
            ss.train_pts.append({"x": x, "y": y, "c": fruit})
        if b2.button("Tout effacer", use_container_width=True, key="entraine_clr"):
            ss.train_pts, ss.train_tests, ss.train_good, ss.train_trap, ss.train_last = [], 0, 0, False, None
        if st.button("Le piège des données", use_container_width=True, key="entraine_trap"):
            ss.train_pts = ([{"x": random.uniform(5, 25), "y": random.uniform(5, 25), "c": "Citron"} for _ in range(4)] +
                            [{"x": random.uniform(75, 95), "y": random.uniform(75, 95), "c": "Orange"} for _ in range(4)])
            ss.train_tests, ss.train_good, ss.train_trap, ss.train_last = 0, 0, True, None
        n_c = sum(1 for p in ss.train_pts if p["c"] == "Citron")
        n_o = len(ss.train_pts) - n_c
        st.caption(f"{n_c} citron(s) et {n_o} orange(s) placés.")
        if st.button("🔍 Tester Sabi sur un fruit mystère", type="primary", disabled=n_c < 3 or n_o < 3, use_container_width=True, key="entraine_test"):
            mx, my = (random.uniform(30, 70), random.uniform(30, 70)) if ss.train_trap else (random.uniform(3, 97), random.uniform(3, 97))
            pc, conf = predict(mx, my)
            t = truth(mx, my)
            ss.train_tests += 1
            ss.train_good += int(pc == t)
            ss.train_last = {"x": mx, "y": my, "p": pc, "conf": conf, "t": t}
    with c1:
        X = alt.X("x:Q", scale=alt.Scale(domain=[0, 100]), title="Taille →")
        Y = alt.Y("y:Q", scale=alt.Scale(domain=[0, 100]), title="Couleur (jaune → orangé)")
        layers = []
        if any(p["c"] == "Citron" for p in ss.train_pts) and any(p["c"] == "Orange" for p in ss.train_pts):
            rows = [{"x": gx, "x2": gx + 5, "y": gy, "y2": gy + 5, "Sabi pense": predict(gx + 2.5, gy + 2.5)[0]}
                    for gx in range(0, 100, 5) for gy in range(0, 100, 5)]
            layers.append(alt.Chart(pd.DataFrame(rows)).mark_rect(opacity=.35).encode(
                x=X, x2="x2", y=Y, y2="y2",
                color=alt.Color("Sabi pense:N", scale=alt.Scale(domain=["Citron", "Orange"], range=["#F2D64A", "#F2994A"]), legend=None)))
        pts = pd.DataFrame(ss.train_pts) if ss.train_pts else pd.DataFrame([{"x": -10, "y": -10, "c": "Citron"}])
        pts["e"] = pts["c"].map({"Citron": "🍋", "Orange": "🍊"})
        layers.append(alt.Chart(pts).mark_text(size=24, clip=True).encode(x=X, y=Y, text="e"))
        if ss.train_last:
            layers.append(alt.Chart(pd.DataFrame([ss.train_last])).mark_text(size=30, text="❓").encode(x=X, y=Y))
        st.altair_chart(alt.layer(*layers).properties(height=380), use_container_width=True)
        st.caption("Les couleurs du fond montrent ce que Sabi a appris : jaune = citron, orange = orange.")
    if ss.train_trap:
        html('<div class="neu">Ici, Sabi n’a vu que de <b>tout petits citrons très jaunes</b> et de <b>très grosses oranges</b>. '
             'Teste des fruits moyens : il va se tromper plus souvent. Des données pas assez variées créent des erreurs : c’est un <b>biais</b>.</div>')
    lt = ss.train_last
    if lt:
        ok = lt["p"] == lt["t"]
        em = {"Citron": "citron 🍋", "Orange": "orange 🍊"}
        html(f'<div class="{"good" if ok else "bad"}">Sabi pense : <b>{em[lt["p"]]}</b> (sûr à {lt["conf"]} %). '
             f'En vrai, c’était {"un " if lt["t"] == "Citron" else "une "}{em[lt["t"]]}. '
             f'{"Gagné !" if ok else "Raté : il manque des exemples près de ce fruit-là."}<br>Score de Sabi : {ss.train_good} / {ss.train_tests}</div>')
    if ss.train_tests >= 5:
        say("Tu viens d’<b>entraîner un modèle</b> : j’ai appris uniquement grâce à tes exemples. Plus ils sont nombreux et variés, moins je me trompe.")
        st.button("Terminer", type="primary", key="entraine_fin", on_click=finish, args=("entraine",))


def act_histoire():
    say("Choisis les pièces de ton histoire. Ici, <b>c’est toi qui écris les règles</b> : la machine assemble ce que tu choisis, sans rien inventer.")
    heros = st.radio("Le héros ou l’héroïne", ["une flamant rose curieuse", "un robot timide", "une tortue inventrice", "un dragon qui a peur du noir"], key="histoire_h")
    lieu = st.radio("Le lieu", ["au bord de l’étang de Thau", "dans une école sur la Lune", "au cœur d’une forêt de cyprès", "dans le labyrinthe d’un musée"], key="histoire_l")
    pb = st.radio("Le problème", ["a perdu sa boussole", "doit réparer une machine à nuages", "veut comprendre pourquoi les étoiles clignotent", "doit retrouver un livre disparu"], key="histoire_p")
    if st.button("Assembler mon histoire", type="primary", key="histoire_go"):
        ss["histoire_ok"] = True
    if ss.get("histoire_ok"):
        pr = "il" if heros.startswith("un ") else "elle"
        html(f'<div class="story">Il était une fois {heros} qui vivait {lieu}. Un matin, {pr} {pb}. '
             f'Avec l’aide de ses amis, et beaucoup de patience, {pr} trouva une solution que personne n’avait imaginée.</div>')
        st.subheader("Et une IA générative, elle ferait comment ?")
        a, b = st.columns(2)
        a.markdown("**Ma fabrique à règles**\n\nElle colle des morceaux écrits à l’avance. Même choix, même histoire.")
        b.markdown("**Une IA générative**\n\nElle prédit mot après mot une suite probable. Chaque histoire est différente… mais elle peut écrire des choses fausses.")
        say("En 4e, tu pourras essayer une IA générative, encadrée par ton enseignant.")
        st.button("Terminer", type="primary", key="histoire_fin", on_click=finish, args=("histoire",))


CODE_RULE = '''def sabi_devine(taille, couleur):
    if couleur > 50 and taille > 40:
        return "orange"
    else:
        return "citron"'''

CODE_KNN = '''def knn(mystere, exemples, k):
    # 1. trier les exemples du plus proche au plus loin
    voisins = sorted(exemples, key=lambda e: distance(e, mystere))[:k]
    # 2. vote : l'étiquette la plus fréquente gagne
    return majorite(voisins)'''


def knn_part():
    st.subheader("Étape 2 : un modèle qui apprend")
    st.code(CODE_KNN, language="python")
    st.markdown("Ici, personne n’écrit de règle : le modèle regarde les **k exemples les plus proches** du fruit mystère ❓ et les fait voter. "
                "Attention : un exemple a été **mal étiqueté** (un citron noté au milieu des oranges).")
    k = st.slider("Valeur de k (nombre de voisins)", 1, 7, 1, 2, key="code_k")
    mx, my = KNN_MYSTERY
    dist = sorted(KNN_DATA, key=lambda e: math.hypot(e[0] - mx, e[1] - my))
    voisins = dist[:k]
    n_or = sum(1 for v in voisins if v[2] == "Orange")
    pred = "Orange" if n_or > k - n_or else "Citron"
    df = pd.DataFrame([{"x": a, "y": b, "c": c, "voisin": (a, b, c) in voisins} for a, b, c in KNN_DATA])
    df["e"] = df["c"].map({"Citron": "🍋", "Orange": "🍊"})
    X = alt.X("x:Q", scale=alt.Scale(domain=[0, 100]), title="Taille")
    Y = alt.Y("y:Q", scale=alt.Scale(domain=[0, 100]), title="Couleur")
    ring = alt.Chart(df[df.voisin]).mark_circle(size=900, opacity=.25, color="#7D6BC2").encode(x=X, y=Y)
    em = alt.Chart(df).mark_text(size=22).encode(x=X, y=Y, text="e")
    mys = alt.Chart(pd.DataFrame([{"x": mx, "y": my}])).mark_text(size=28, text="❓").encode(x=X, y=Y)
    st.altair_chart(alt.layer(ring, em, mys).properties(height=320), use_container_width=True)
    html(f'<div class="{"good" if pred == "Orange" else "bad"}">Avec k = {k} : {n_or} orange(s) contre {k - n_or} citron(s) → '
         f'Sabi prédit <b>{"orange 🍊" if pred == "Orange" else "citron 🍋"}</b>. '
         + ("Avec un seul voisin, l’exemple mal étiqueté trompe le modèle !" if k == 1 else "Plusieurs voisins compensent l’erreur d’étiquette.") + '</div>')
    if k > 1:
        ss["code_k_ok"] = True
    if not ss.get("code_k_ok"):
        st.caption("Augmente k pour continuer.")
        return False
    say("Tu as vu les deux façons de programmer : <b>écrire des règles</b> à la main, ou <b>apprendre à partir d’exemples</b>. "
        "Et tu as vu qu’une seule donnée fausse peut tromper un modèle mal réglé.")
    return True


def act_code():
    st.subheader("Étape 1 : un programme à règles")
    st.code(CODE_RULE, language="python")
    items = [(f"Que renvoie <code>sabi_devine({t}, {c})</code> ?", ["\"orange\"", "\"citron\""], 0 if (c > 50 and t > 40) else 1,
              f"couleur > 50 est {'vrai' if c > 50 else 'faux'} et taille > 40 est {'vrai' if t > 40 else 'faux'} : "
              f"avec « and », il faut que les deux soient vrais.")
             for t, c in [(70, 80), (70, 20), (30, 90)]]
    quiz("code", items, "Tu as lu un vrai code Python : <b>{sc} / {n}</b>.", shuffle=False, extra=knn_part)


PII = re.compile(r"@|\b0[1-9](\s?\d{2}){4}\b|\b\d{1,3}\s(rue|avenue|bd|boulevard|chemin)\b|\bje m.appelle\b|\bmon nom\b", re.I)


def act_consigne():
    st.info("**Usage encadré.** Atelier réservé à la 4e et à la 3e, à faire avec ton enseignant ou un adulte. "
            "Dans ce prototype, les réponses sont **préécrites** : aucune IA n’est appelée.")
    say("Une bonne consigne précise <b>le rôle</b>, <b>la tâche</b>, <b>le contexte</b> et <b>le format</b>. Et elle ne contient <b>aucune donnée personnelle</b>.")
    v = [st.text_input("Rôle (qui doit répondre ?)", placeholder="Ex. : Tu es un professeur de SVT", key="consigne_r1"),
         st.text_input("Tâche (que veux-tu ?)", placeholder="Ex. : Explique la photosynthèse", key="consigne_r2"),
         st.text_input("Contexte (pour qui, pourquoi ?)", placeholder="Ex. : pour un élève de 4e qui prépare un exposé", key="consigne_r3"),
         st.text_input("Format (comment ?)", placeholder="Ex. : en 5 points courts avec un exemple", key="consigne_r4")]
    if st.button("Évaluer ma consigne", type="primary", key="consigne_go"):
        ss["consigne_eval"] = True
    if not ss.get("consigne_eval"):
        return
    if PII.search(" ".join(v)):
        html('<div class="bad"><b>Stop !</b> Ta consigne contient ce qui ressemble à une donnée personnelle (adresse, mail, téléphone ou nom). Retire-la.</div>')
        return
    sc = sum(1 for x in v if len(x.strip()) >= 4)
    st.subheader(f"Ta consigne : {sc} / 4")
    for n, x in zip(["Rôle", "Tâche", "Contexte", "Format"], v):
        st.markdown(("✅ " if len(x.strip()) >= 4 else "⚠️ ") + n + ("" if len(x.strip()) >= 4 else " : à préciser"))
    st.caption("Réponse simulée")
    msg = ("Voici une explication en 5 points adaptée à ton niveau, avec un exemple concret. (Dans la vraie version, la réponse apparaîtrait ici.)"
           if sc >= 4 else "Réponse assez générale : sans contexte ni format, l’IA devine ce que tu veux." if sc >= 2
           else "Réponse floue : l’IA n’a presque rien pour comprendre ta demande.")
    html(f'<div class="story">{msg}</div>')
    st.subheader("Avant d’utiliser la réponse")
    checks = [st.checkbox(c, key=f"consigne_chk{k}") for k, c in enumerate([
        "J’ai vérifié les informations avec au moins une autre source", "Je reformule avec mes propres mots",
        "Je signale que j’ai utilisé une IA", "Je garde mon esprit critique : l’IA peut se tromper"])]
    st.info("Passerelle : le parcours Pix sur l’IA, obligatoire en 4e, prolonge cet atelier.")
    st.button("Terminer", type="primary", key="consigne_fin", disabled=not all(checks), on_click=finish, args=("consigne",))


# ══════════════════════════ Activités : Bien-être ══════════════════════════
def act_meteo():
    say("Comment te sens-tu aujourd’hui ? C’est <b>toi</b> qui le dis : Sabi ne regarde jamais ton visage et n’écoute jamais ta voix.")
    cols = st.columns(len(MOODS))
    for k, (e, lab) in enumerate(MOODS):
        if cols[k].button(f"{e} {lab}", key=f"meteo_m{k}", use_container_width=True):
            ss.moods = (ss.moods + [k])[-14:]
            ss["meteo_pick"] = k
    if "meteo_pick" not in ss:
        return
    k = ss["meteo_pick"]
    tip = ("Super ! Garde cette énergie." if k <= 1 else "Une pause active peut aider à se réveiller un peu." if k == 2
           else "Merci de l’avoir dit. Parler à un adulte de confiance peut faire du bien.")
    html(f'<div class="neu">{tip}</div>')
    st.subheader("Choisis ta carte positive du jour")
    carte = st.radio("Ma carte", CARTES, key="meteo_carte", label_visibility="collapsed")
    html(f'<div class="carte">🌟 {carte}</div>')
    st.button("Terminer", type="primary", key="meteo_fin", on_click=finish, args=("meteo",))


def act_ressent():
    quiz("ressent", RESSENT, "Résultat : <b>{sc} / {n}</b>. Une IA <b>imite</b> des émotions avec des mots, elle ne les <b>ressent</b> pas. "
                             "Tes émotions, c’est toi qui les connais.")


def act_chatbot():
    say("Les chatbots sont partout. Voyons comment les utiliser sans te mettre en danger.")

    def ressources():
        st.info("**Besoin d’aide ?** Parle à un adulte de confiance. En cas de cyberharcèlement, le **3018** est le numéro national, gratuit.")
        return True
    quiz("chatbot", CHATBOT, "Résultat : <b>{sc} / {n}</b>. Tes règles : <b>je ne partage pas mes infos personnelles, je ne partage pas un montage blessant, "
                             "je garde du temps pour les autres</b>.", extra=ressources)


# ══════════════════════════ Activités : Bouger ══════════════════════════
def act_sabidit():
    say("Règle du jeu : tu fais le geste <b>seulement si la phrase commence par « Sabi dit »</b>. Sinon, tu ne bouges pas !")
    if "sabidit_items" not in ss:
        rnd = random.Random()
        seq = [rnd.choice(MOVES) for _ in range(8)]
        flags = [True] * 5 + [False] * 3
        rnd.shuffle(flags)
        ss["sabidit_items"] = list(zip(seq, flags))
    items = []
    for mv, sd in ss["sabidit_items"]:
        label = mv.split(" ", 1)[1].lower()
        txt = f"« {'Sabi dit : ' if sd else ''}{label} ! »"
        expl = ("Sabi a bien dit « Sabi dit » : la condition est vraie, on exécute. Fais le geste !" if sd
                else "Piège ! Sans « Sabi dit », la condition est fausse : on ne bouge pas.")
        items.append((f"<span style='font-size:2rem'>{mv.split(' ')[0]}</span><br>{txt}", ["🕺 Je fais le geste", "🧍 Je ne bouge pas"], 0 if sd else 1, expl))
    quiz("sabidit", items, "Score : <b>{sc} / {n}</b>. Un ordinateur fait pareil : <b>si</b> la condition est vraie, <b>alors</b> il exécute l’instruction. Sinon, il ne fait rien.",
         shuffle=False)


def act_robothumain():
    say("Tu es la programmeuse ou le programmeur ! Choisis jusqu’à 6 mouvements dans l’ordre. Ensuite, tu deviens le robot et tu exécutes ton programme.")
    prog = ss.get("robothumain_prog", [])
    cols = st.columns(3)
    for n, mv in enumerate(MOVES):
        if cols[n % 3].button(mv, key=f"robothumain_add{n}", use_container_width=True, disabled=len(prog) >= 6):
            ss["robothumain_prog"] = prog + [mv]
            st.rerun()
    st.markdown("**Mon programme :** " + (" → ".join(prog) if prog else "_vide_"))
    rep = st.checkbox("🔁 Boucle : répéter le programme 2 fois", key="robothumain_loop")
    a, b = st.columns(2)
    if a.button("🗑️ Effacer", key="robothumain_clear", use_container_width=True):
        ss["robothumain_prog"] = []
        st.rerun()
    if ss.get("robothumain_ok"):
        html('<div class="good">Programme exécuté ! Un programme, c’est une <b>suite d’instructions précises dans un ordre donné</b>. '
             'La <b>boucle</b> évite de réécrire les mêmes instructions.</div>')
        st.button("Terminer", type="primary", key="robothumain_fin", on_click=finish, args=("robothumain",))
        return
    if b.button("▶️ Exécuter (je suis le robot)", key="robothumain_run", type="primary", disabled=len(prog) < 3, use_container_width=True):
        box = st.empty()
        full = prog * (2 if rep else 1)
        for n, mv in enumerate(full, 1):
            box.markdown(f"<div class='qcard' style='text-align:center;font-size:2rem'>Instruction {n} / {len(full)}<br>{mv}</div>", unsafe_allow_html=True)
            time.sleep(3)
        ss["robothumain_ok"] = True
        st.rerun()
    if len(prog) < 3:
        st.caption("Ajoute au moins 3 mouvements pour exécuter.")


SKELETON = [("nez", 100, 40), ("œil g", 92, 34), ("œil d", 108, 34), ("oreille g", 84, 38), ("oreille d", 116, 38),
            ("épaule g", 72, 80), ("épaule d", 128, 80), ("coude g", 52, 120), ("coude d", 148, 120), ("poignet g", 40, 160),
            ("poignet d", 160, 160), ("hanche g", 82, 170), ("hanche d", 118, 170), ("genou g", 78, 225), ("genou d", 122, 225),
            ("cheville g", 76, 280), ("cheville d", 124, 280)]
BONES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (0, 1), (0, 2), (1, 3), (2, 4)]


def act_squelette():
    c1, c2 = st.columns([1, 1.4])
    with c1:
        s = '<svg viewBox="0 0 200 300" style="width:100%;max-width:260px;background:#CFE8EC;border-radius:18px">'
        s += "".join(f'<line x1="{SKELETON[a][1]}" y1="{SKELETON[a][2]}" x2="{SKELETON[b][1]}" y2="{SKELETON[b][2]}" stroke="#1F8A8A" stroke-width="4" stroke-linecap="round"/>' for a, b in BONES)
        s += "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#E9768F"><title>{n}</title></circle>' for n, x, y in SKELETON)
        html(s + "</svg>")
    with c2:
        say("Une IA de <b>détection de posture</b> ne voit pas une personne : elle repère <b>17 points</b> (nez, épaules, coudes, genoux…) "
            "et calcule leur position. En comparant ces points à des exemples, elle peut reconnaître un geste.")
        st.caption("Dans ce prototype, aucune caméra n’est utilisée : le squelette est un dessin.")
    items = [("Pour reconnaître un geste, l’IA analyse…", ["la position de points du corps", "les pensées de l’élève", "la couleur des vêtements seulement"], 0,
              "Elle travaille sur des coordonnées de points."),
             ("Une appli scolaire filme les élèves pour compter les sauts. Le mieux, c’est que l’image…",
              ["soit traitée sur l’appareil et jamais enregistrée", "soit envoyée et stockée sur Internet", "soit partagée avec la classe"], 0,
              "L’image d’un élève est une donnée personnelle : moins elle circule, mieux c’est."),
             ("Une IA qui « devine » ton émotion d’après ton visage à l’école…", ["est interdite par l’AI Act européen", "est obligatoire"], 0,
              "La reconnaissance des émotions est interdite en milieu éducatif.")]

    def pause():
        st.subheader("Pause active : à toi de bouger !")
        return pause_widget("squelette_pause", 30, ["🙌 Bras en l’air", "🦩 Sur une jambe", "🔄 Rotation des épaules"])
    quiz("squelette", items, "Score : <b>{sc} / {n}</b>. Une IA peut voir des gestes, mais l’image des élèves doit être protégée.", extra=pause)


RUNNERS = {"iaounon": act_iaounon, "quiz3": act_quiz3, "motsuiv": act_motsuiv, "quiz4": act_quiz4,
           "robot": act_robot, "biais": act_biais, "escape": act_escape, "deepfake": act_deepfake,
           "grille": act_grille, "entraine": act_entraine, "histoire": act_histoire, "code": act_code, "consigne": act_consigne,
           "meteo": act_meteo, "ressent": act_ressent, "chatbot": act_chatbot,
           "sabidit": act_sabidit, "robothumain": act_robothumain, "squelette": act_squelette}


# ══════════════════════════ Écrans ══════════════════════════
def tranche_cards(highlight=None):
    for c, (cyc, t) in zip(st.columns(3), TRANCHES.items()):
        with c.container(border=True):
            st.markdown(f"### {t['em']} {t['nom']}\n**{t['age']}** · {t['classes']} · {t['cycle']}" + ("  ← ta tranche" if highlight == cyc else ""))
            st.write(t["but"])


def view_accueil():
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("<h1 style='font-size:3rem;line-height:1.05'>Comprendre l’IA au lieu de la subir.</h1>", unsafe_allow_html=True)
        st.markdown("Sabi accompagne les 8-15 ans, du CE2 à la 3e, à la maison et en classe. "
                    "**5 piliers** pédagogiques, déclinés pour **3 tranches d’âge**.")
        st.markdown("Choisissez votre espace dans le menu à gauche : **Enfant**, **Parent**, **Enseignant** ou **Collectivité**.")
    with c2:
        html(f'<div style="text-align:center">{flam(200)}<p style="color:#5A6B7D">« Sabi » veut dire « je sais » en occitan. '
             'Notre guide est un flamant rose des étangs de Montpellier.</p></div>')
    st.subheader("Les 5 piliers")
    for c, p in zip(st.columns(5), PILLARS):
        with c.container(border=True):
            st.markdown(f"### {p['em']} {p['name']}\n{p['desc']}")
    st.subheader("Les 3 tranches d’âge")
    tranche_cards()
    st.subheader("Le parcours : 5 piliers × 3 tranches")
    st.table(matrix_df())
    st.info("**Conforme au cadre d’usage de l’IA en éducation (juin 2025)** : aucune conversation avec une IA générative avant la 4e. "
            "L’atelier IA générative de la tranche Créateurs n’apparaît qu’en 4e et en 3e.")


def matrix_df():
    rows = []
    for p in PILLARS:
        row = {"Pilier": f"{p['em']} {p['name']}"}
        for cyc, t in TRANCHES.items():
            row[f"{t['em']} {t['nom']} ({t['age']})"] = " · ".join(a["t"] + (" *" if a.get("gen") else "") for a in acts_for(p["id"], cyc))
        rows.append(row)
    return pd.DataFrame(rows).set_index("Pilier")


def view_enfant():
    if not ss.profile:
        return onboarding()
    if not ss.consent:
        say("Ton compte attend l’accord d’un adulte. Demande-lui d’ouvrir l’espace <b>Parent</b> (menu à gauche) pour valider.")
        return
    scr = ss.kid_screen
    if scr.startswith("act:"):
        a = ACT[scr[4:]]
        st.button("← Retour à la carte", on_click=go, args=("carte",))
        st.header(f"{a['em']} {a['t']}")
        st.caption(f"{PIL[a['p']]['em']} Pilier {PIL[a['p']]['name']} · {TRANCHES[a['cyc']]['em']} {TRANCHES[a['cyc']]['nom']} ({TRANCHES[a['cyc']]['age']})")
        RUNNERS[a["id"]]()
        return
    if scr == "permis":
        return view_permis()
    if scr.startswith("exam:"):
        return view_exam(int(scr[5:]))

    p, cyc = ss.profile, kid_cycle()
    t = TRANCHES[cyc]
    lv, into = ss.xp // 150 + 1, ss.xp % 150
    c1, c2, c3 = st.columns([2, 2, 1])
    c1.markdown(f"## {p['avatar']} Bonjour, {p['pseudo']} !")
    c1.caption(f"{p['level']} · {t['em']} tranche {t['nom']} ({t['age']}, {t['cycle']}) · niveau {lv}")
    c2.progress(into / 150, text=f"{ss.xp} XP · encore {150 - into} XP pour le niveau {lv + 1}")
    c3.button("🪪 Mon Permis IA", on_click=go, args=("permis",), use_container_width=True)
    limit_hit = ss.minutes >= ss.screen_limit
    if limit_hit:
        st.warning(f"Ton temps d’écran du jour est atteint ({ss.screen_limit} min). Les îles Bien-être et Bouger restent ouvertes. "
                   "Un adulte peut changer ce réglage dans l’espace parent.")
    say(f"Bienvenue chez les <b>{t['nom']}</b> ! Explore les 5 îles. Termine au moins une activité sur chaque île pour passer ton <b>{PERMIS[cyc]['t']}</b>.")
    html(map_svg(cyc))
    for c, pl in zip(st.columns(5), PILLARS):
        c.button(f"{pl['em']} {pl['name']}", key="pil_" + pl["id"], use_container_width=True,
                 type="primary" if ss.pillar == pl["id"] else "secondary", on_click=lambda pid=pl["id"]: ss.update(pillar=pid))
    pl = PIL[ss.pillar]
    st.subheader(f"{pl['em']} Île {pl['name']}")
    st.caption(pl["desc"])
    mine = acts_for(pl["id"], cyc)
    for a in mine:
        act_row(a, limit_hit)
    others = [a for a in acts_for(pl["id"]) if a["cyc"] != cyc]
    with st.expander("Activités des autres tranches d’âge (révision ou défi)"):
        for a in others:
            act_row(a, limit_hit, other=True)


def act_row(a, limit_hit, other=False):
    lock = bool(a.get("gen")) and (not gen_allowed() or not ss.gen_ai)
    why = ("Réservé à la 4e et à la 3e (cadre d’usage de l’IA en éducation)" if a.get("gen") and not gen_allowed()
           else "Désactivé par ton parent" if a.get("gen") and not ss.gen_ai else a["d"])
    status = "✅ Fait" if is_done(a["id"]) else ("🔒 4e-3e" if lock else f"{a['min']} min")
    tr = TRANCHES[a["cyc"]]
    with st.container(border=True):
        l, r = st.columns([4, 1])
        l.markdown(f"#### {a['em']} {a['t']}\n{why}" + (f"\n\n_{tr['em']} {tr['nom']} · {tr['age']}_" if other else ""))
        r.caption(status)
        r.button("Jouer", key=("o_" if other else "") + "play_" + a["id"], disabled=lock or (limit_hit and a["p"] not in ("bienetre", "bouger")),
                 on_click=start_act, args=(a["id"],), use_container_width=True)


def onboarding():
    step = ss.onb
    st.progress(step / 3, text=f"Inscription · étape {step} / 3")
    d = ss.draft
    if step == 1:
        say("Salut, je suis Sabi ! Dis-moi ta classe : je te proposerai les activités de ta tranche d’âge.")
        for c, l in zip(st.columns(len(LEVELS)), LEVELS):
            if c.button(l, key="lv_" + l, use_container_width=True):
                d["level"] = l
                ss.onb = 2
                st.rerun()
        tranche_cards()
    elif step == 2:
        t = TRANCHES[cycle_of(d["level"])]
        say(f"Tu es en {d['level']} : tu rejoins les <b>{t['em']} {t['nom']}</b> ({t['age']}). Choisis ton avatar et un surnom. <b>Jamais ton vrai nom</b> !")
        d["avatar"] = st.radio("Mon avatar", AVATARS, horizontal=True, index=AVATARS.index(d.get("avatar", "🦩")))
        pseudo = st.text_input("Mon surnom", max_chars=16, placeholder="Ex. : Capitaine Pixel", value=d.get("pseudo", ""))
        a, b = st.columns(2)
        if a.button("Continuer", type="primary", use_container_width=True):
            v = pseudo.strip()
            if len(v) < 2:
                st.error("Ton surnom doit faire au moins 2 caractères.")
            elif re.search(r"\d{6,}|@", v):
                st.error("Pas de numéro ni d’adresse mail dans ton surnom.")
            else:
                d["pseudo"] = v
                ss.onb = 3
                st.rerun()
        if b.button("← Changer de classe", use_container_width=True):
            ss.onb = 1
            st.rerun()
    else:
        say("Dernière étape : un adulte de ta famille doit donner son accord avec toi. Montre-lui cet écran !")
        with st.container(border=True):
            st.markdown("**Pour l’adulte responsable**")
            st.markdown("Avant 15 ans, l’inscription à un service en ligne demande l’accord conjoint de l’enfant et d’un titulaire de "
                        "l’autorité parentale. Sabi ne garde qu’un surnom, une classe et la progression. Aucune publicité, données hébergées "
                        "en Europe, aucune utilisation pour entraîner une IA.")
            c1 = st.checkbox("Je suis le parent ou le responsable légal et j’accepte l’inscription")
            c2 = st.checkbox("L’enfant est d’accord aussi")
            a, b = st.columns(2)
            if a.button("Valider l’inscription", type="primary", use_container_width=True):
                if c1 and c2:
                    ss.profile, ss.consent = dict(d), True
                    st.rerun()
                else:
                    st.error("Les deux cases sont nécessaires.")
            if b.button("Plus tard (depuis l’espace parent)", use_container_width=True):
                ss.profile, ss.consent = dict(d), False
                st.rerun()


def permis_ready(cyc):
    return all(any(is_done(a["id"]) for a in acts_for(p["id"], cyc) if visible(a)) for p in PILLARS)


def view_permis():
    st.button("← Retour à la carte", on_click=go, args=("carte",))
    st.header("🪪 Mon Permis IA")
    say("Il y a un Permis par tranche d’âge. Pour le passer : <b>une activité terminée sur chacune des 5 îles</b> de la tranche, puis un examen de 3 questions (2 bonnes réponses suffisent).")
    my = kid_cycle()
    for c, (cyc, t) in zip(st.columns(3), TRANCHES.items()):
        pm = PERMIS[cyc]
        got = cyc in ss.permis
        with c.container(border=True):
            st.markdown(f"### {pm['em'] if got else '⬜'} {pm['t']}\n{t['em']} {t['nom']} · {t['age']}" + ("  ← ta tranche" if cyc == my else ""))
            for p in PILLARS:
                ok = any(is_done(a["id"]) for a in acts_for(p["id"], cyc) if visible(a))
                st.markdown(f"{'✅' if ok else '⬜'} {p['em']} {p['name']}")
            if got:
                st.success("Obtenu")
            else:
                st.button("Passer l’examen", key=f"ex{cyc}", disabled=not permis_ready(cyc), on_click=go, args=(f"exam:{cyc}",))
    for cyc in sorted(ss.permis):
        pm = PERMIS[cyc]
        html(f'<div class="cert" style="margin-top:16px">{flam(70)}<h2>{pm["em"]} {pm["t"]}</h2>'
             f'<p>délivré à <b>{esc(ss.profile["pseudo"])}</b> · {ss.profile["level"]}</p>'
             f'<p style="color:#5A6B7D">Sabi certifie que tu sais {pm["cert"]}</p></div>')


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def view_exam(cyc):
    pm = PERMIS[cyc]
    st.header(f"{pm['em']} Examen : {pm['t']}")
    key = f"exam{cyc}"
    i = ss.get(key + "_i", 0)
    if i >= len(pm["q"]):
        sc = ss.get(key + "_sc", 0)
        if sc >= 2 and cyc not in ss.permis:
            ss.permis = ss.permis + [cyc]
            ss.xp += 100
        say(f"Félicitations, tu as obtenu le <b>{pm['t']}</b> ! (+100 XP)" if sc >= 2
            else f"Tu as {sc} / 3. Refais une activité et réessaie, tu vas y arriver !")

        def back():
            ss[key + "_i"], ss[key + "_sc"] = 0, 0
            for k in list(ss.keys()):
                if str(k).startswith(key + "_ord"):
                    del ss[k]
            go("permis")
        st.button("Voir mon Permis", type="primary", on_click=back)
        return
    q, opts, good = pm["q"][i]
    okey = f"{key}_ord{i}"
    if okey not in ss:
        ss[okey] = random.sample(range(len(opts)), len(opts))
    st.progress(i / len(pm["q"]), text=f"Question {i + 1} / {len(pm['q'])}")
    html(f'<div class="qcard">{q}</div>')
    for k in ss[okey]:
        if st.button(opts[k], key=f"{key}_{i}_{k}", use_container_width=True):
            ss[key + "_sc"] = ss.get(key + "_sc", 0) + int(k == good)
            ss[key + "_i"] = i + 1
            st.rerun()


def view_parent():
    st.title("Espace parent")
    p = ss.profile
    if not p:
        st.info("Aucun enfant inscrit pour l’instant. Commencez par l’espace Enfant : votre accord vous sera demandé à la fin.")
        return
    cyc = kid_cycle()
    t = TRANCHES[cyc]
    st.caption(f"{p['avatar']} {p['pseudo']} · {p['level']} · tranche {t['em']} {t['nom']} ({t['age']}) · offre {OFFERS[ss.offer][0]}")
    if not ss.consent:
        st.warning("**Consentement en attente.** Avant 15 ans, l’inscription demande votre accord et celui de votre enfant.")
        if st.button("Je donne mon accord, avec mon enfant", type="primary"):
            ss.consent = True
            st.rerun()
    k = st.columns(4)
    k[0].metric("Activités terminées", len(ss.done))
    k[1].metric("Points d’expérience", ss.xp)
    k[2].metric("Permis IA", ", ".join(PERMIS[c]["t"] for c in sorted(ss.permis)) if ss.permis else "Pas encore")
    k[3].metric("Minutes aujourd’hui", f"{ss.minutes} / {ss.screen_limit}")
    st.info(f"**Ce que votre enfant travaille ({t['nom']}, {t['age']}) :** {t['but']}")
    a, b = st.columns(2)
    with a.container(border=True):
        st.subheader("Progression par pilier")
        for pl in PILLARS:
            v = pillar_pct(pl["id"], cyc)
            st.progress(v / 100, text=f"{pl['em']} {pl['name']} · {v} %")
    with b.container(border=True):
        st.subheader("Météo déclarée par votre enfant")
        st.markdown(" ".join(MOODS[m][0] for m in ss.moods[-7:]) if ss.moods else "Rien de déclaré pour l’instant.")
        st.caption("Sabi n’analyse ni le visage, ni la voix, ni la frappe : seul ce que l’enfant choisit de dire apparaît ici.")

    st.subheader("Réglages")
    a, b = st.columns(2)
    with a.container(border=True):
        ss.screen_limit = st.slider("Temps d’écran par jour (minutes)", 10, 90, ss.screen_limit, 5)
        st.caption("Une fois la limite atteinte, seules les îles Bien-être et Bouger restent ouvertes.")
        if st.button("Remettre le compteur du jour à zéro"):
            ss.minutes = 0
            st.rerun()
    with b.container(border=True):
        st.markdown("**IA générative**")
        if gen_allowed():
            st.caption(f"Votre enfant est en {p['level']} : l’atelier d’IA générative encadrée peut s’ouvrir.")
            ss.gen_ai = st.toggle("Autoriser l’atelier d’IA générative", value=ss.gen_ai)
        else:
            st.caption(f"Votre enfant est en {p['level']} : aucune IA générative n’est proposée avant la 4e, quel que soit ce réglage.")

    st.subheader("En parler à la maison")
    talk = {2: [("🍽️ À table", "« Aujourd’hui, as-tu vu un objet qui apprend ? »"), ("🎲 Jeu", "Jouez à « Sabi dit » en famille : seulement si la phrase commence par « Sabi dit » !")],
            3: [("📺 Devant une vidéo", "« Pourquoi la plateforme t’a proposé celle-là, à ton avis ? »"), ("🧪 Expérience", "Demandez-lui de vous montrer le piège des données dans « Entraîne Sabi ».")],
            4: [("📱 Réseaux", "« Comment sais-tu si une image est vraie ? »"), ("🤖 Chatbots", "« Qu’est-ce que tu n’écrirais jamais à un chatbot ? »")]}[cyc]
    for c, (tt, d) in zip(st.columns(2), talk):
        with c.container(border=True):
            st.markdown(f"**{tt}**\n\n{d}")

    st.subheader("Données de votre enfant")
    st.caption("Stockées dans l’Union européenne, jamais revendues, jamais utilisées pour entraîner une IA.")
    with st.expander("Voir les données"):
        st.code(json.dumps({"surnom": p["pseudo"], "classe": p["level"], "tranche": t["nom"], "avatar": p["avatar"], "consentement": ss.consent,
                            "activites": list(ss.done), "xp": ss.xp, "permis": [PERMIS[c]["t"] for c in ss.permis],
                            "meteo": [MOODS[m][1] for m in ss.moods]}, ensure_ascii=False, indent=2), language="json")
    if not ss.del_confirm:
        if st.button("Supprimer le compte"):
            ss.del_confirm = True
            st.rerun()
    else:
        st.warning("Cette action efface définitivement le compte et toute la progression.")
        a, b = st.columns(2)
        if a.button("Confirmer la suppression", type="primary"):
            reset_state()
            st.rerun()
        if b.button("Annuler"):
            ss.del_confirm = False
            st.rerun()

    st.subheader("Abonnement")
    for c, kk in zip(st.columns(2), ["decouverte", "famille"]):
        tt, _, d, prix = OFFERS[kk]
        with c.container(border=True):
            st.markdown(f"### {tt}\n**{prix}** <span class='tag'>Prix hypothétique</span>\n\n{d}", unsafe_allow_html=True)
            if ss.offer == kk:
                st.success("Offre actuelle")
            elif st.button("Choisir", key="off_" + kk):
                ss.offer = kk
                st.toast("Offre choisie (simulation, aucun paiement).")
                st.rerun()


def view_enseignant():
    if ss.cm_on:
        return class_mode()
    st.title("Espace enseignant")
    st.caption("Mme Martin · CM2 B · École Jean-Jaurès (fictive) · tranche Enquêteurs · code classe SABI-4821")
    k = st.columns(4)
    k[0].metric("Élèves", 24)
    k[1].metric("Actifs cette semaine", "83 %")
    k[2].metric("Séances prêtes", len(ACTS))
    k[3].metric("Élèves à accompagner", 3)

    st.subheader("Le parcours : 5 piliers × 3 tranches")
    st.table(matrix_df())
    st.caption("* IA générative encadrée, 4e et 3e uniquement.")

    st.subheader("Séances clés en main")
    a, b = st.columns(2)
    fc = a.radio("Tranche", ["Toutes"] + [f"{t['em']} {t['nom']} ({t['cycle']})" for t in TRANCHES.values()], horizontal=True)
    fp = b.radio("Pilier", ["Tous"] + [f"{p['em']} {p['name']}" for p in PILLARS], horizontal=True)
    cyc = None if fc == "Toutes" else [c for c, t in TRANCHES.items() if t["nom"] in fc][0]
    pid = None if fp == "Tous" else [p["id"] for p in PILLARS if p["name"] in fp][0]
    cols = st.columns(2)
    for n, s in enumerate(acts_for(pid, cyc)):
        t = TRANCHES[s["cyc"]]
        with cols[n % 2].container(border=True):
            st.markdown(f"#### {s['em']} {s['t']}\n{s['s']['obj']}")
            st.caption(f"{PIL[s['p']]['em']} {PIL[s['p']]['name']} · {t['em']} {t['nom']} ({t['cycle']}) · "
                       f"{sum(int(d.split()[0]) for d, _ in s['s']['ph'])} min · " + ("IA générative encadrée" if s.get("gen") else "Sans IA générative"))
            c1, c2 = st.columns(2)
            c1.button("Voir la séance", key="see_" + s["id"], on_click=lambda sid=s["id"]: ss.update(seance=sid), use_container_width=True)
            assigned = ss.assign.get(s["id"], False)
            if c2.button("✓ Assignée" if assigned else "Assigner à la classe", key="as_" + s["id"], use_container_width=True):
                ss.assign[s["id"]] = not assigned
                st.toast("Séance assignée : elle apparaît chez les élèves." if not assigned else "Assignation retirée.")
                st.rerun()
    if ss.seance:
        s = ACT[ss.seance]
        with st.container(border=True):
            st.markdown(f"### {s['em']} {s['t']}\n**Objectif :** {s['s']['obj']}\n\n**Pilier :** {PIL[s['p']]['name']} · CRCN proposé : {PIL[s['p']]['crcn']}")
            st.table(pd.DataFrame(s["s"]["ph"], columns=["Durée", "Déroulé"]))
            if s.get("gen"):
                st.warning("Réservé à la 4e et à la 3e. L’enseignant pilote l’outil et projette les réponses, conformément au cadre d’usage.")
            if s["id"] == "iaounon":
                st.button("📺 Lancer en mode classe", type="primary", on_click=lambda: ss.update(cm_on=True, cm_i=0, cm_a=0, cm_b=0, cm_reveal=False))

    st.subheader("Suivi des compétences par pilier")
    lab = ["—", "Débute", "En cours", "Acquis"]
    df = pd.DataFrame([[n] + [lab[(k * 7 + j * 3) % 4] for j in range(5)] + [["—", "🥈", "—", "🥈"][k % 4]]
                       for k, n in enumerate(PUPILS)], columns=["Élève"] + [f"{p['em']} {p['name']}" for p in PILLARS] + ["Permis"])
    colors = {"Débute": "background-color:#FFF3D2", "En cours": "background-color:#CFE8EC", "Acquis": "background-color:#E2F4EA"}
    st.dataframe(df.style.map(lambda v: colors.get(v, "")), hide_index=True, use_container_width=True)
    st.caption("Positionnement par pilier, sans note automatique : l’enseignant garde la main sur l’évaluation. Données fictives.")

    st.subheader("Correspondances avec le cadre de référence")
    st.table(pd.DataFrame([[f"{p['em']} {p['name']}", p["crcn"]] for p in PILLARS], columns=["Pilier", "Correspondance proposée"]))
    st.caption("Propositions à valider avec un conseiller pédagogique numérique (DRANE).")

    st.subheader("Communiquer avec les familles")
    st.text_area("Mot aux familles (modifiable)", height=200, value=(
        "Chères familles,\n\nCette année, la classe découvre l’intelligence artificielle avec Sabi, à travers 5 piliers : apprendre, jouer, coder, "
        "bien-être et bouger. Avant la 4e, les élèves n’utilisent aucune IA générative. Les données sont hébergées en Europe "
        "et ne servent jamais à entraîner une IA.\n\nPour activer le compte de votre enfant, votre accord est nécessaire : "
        "merci d’utiliser le code SABI-4821.\n\nMme Martin"))


def class_mode():
    q = IAQ[ss.cm_i]
    top = st.columns([3, 1])
    top[0].caption(f"Sabi · mode classe · question {ss.cm_i + 1} / {len(IAQ)}")
    top[1].button("Quitter le mode classe", on_click=lambda: ss.update(cm_on=False), use_container_width=True)
    html(f'<div class="cm"><div class="big-q">{q[0]} : est-ce une IA ?</div></div>')
    a, b = st.columns(2)
    a.button(f"✅ Oui, c’est une IA · {ss.cm_a}", use_container_width=True, on_click=lambda: ss.update(cm_a=ss.cm_a + 1))
    b.button(f"❌ Non, ce n’en est pas une · {ss.cm_b}", use_container_width=True, on_click=lambda: ss.update(cm_b=ss.cm_b + 1))
    if ss.cm_reveal:
        html(f'<div class="{"good" if q[1] else "bad"}" style="font-size:1.3rem">{"Oui, c’est une IA." if q[1] else "Non, ce n’est pas une IA."} {q[2]}</div>')
    c, d = st.columns(2)
    c.button("Révéler la réponse", on_click=lambda: ss.update(cm_reveal=True), use_container_width=True)
    d.button("Question suivante", type="primary", use_container_width=True,
             on_click=lambda: ss.update(cm_i=(ss.cm_i + 1) % len(IAQ), cm_a=0, cm_b=0, cm_reveal=False))


def view_collectivite():
    st.title("Espace collectivité")
    st.caption("Sabi Territoire · Métropole (fictive) · pilote 2026-2027")
    k = st.columns(4)
    k[0].metric("Écoles et collèges", 12)
    k[1].metric("Classes", 38)
    k[2].metric("Élèves actifs", 864)
    k[3].metric("Enseignants formés", 41)
    a, b = st.columns(2)
    with a.container(border=True):
        st.subheader("Élèves actifs par tranche d’âge")
        st.bar_chart(pd.DataFrame({"Élèves actifs": [210, 462, 192]},
                                  index=[f"{t['nom']} ({t['age']})" for t in TRANCHES.values()]), color="#1F8A8A")
        st.caption("Statistiques agrégées et anonymisées : aucune donnée individuelle d’élève n’est visible ici.")
    with b.container(border=True):
        st.subheader("Activités terminées par pilier (moyenne)")
        for p, v in zip(PILLARS, [68, 74, 47, 52, 81]):
            st.progress(v / 100, text=f"{p['em']} {p['name']} · {v} %")
    st.subheader("Conformité")
    st.table(pd.DataFrame([
        ["Hébergement des données dans l’Union européenne", "🟡 Prévu (OVHcloud ou Scaleway à choisir)"],
        ["Pas d’IA générative pour les élèves avant la 4e", "🟢 Intégré au produit"],
        ["Aucune reconnaissance des émotions (AI Act)", "🟢 Intégré : humeur déclarée uniquement"],
        ["Pas de caméra dans le pilier Bouger", "🟢 Intégré : mouvements guidés, sans captation"],
        ["Consentement conjoint parent-enfant avant 15 ans", "🟡 Parcours intégré, à faire valider par un juriste"],
        ["Analyse d’impact (AIPD)", "🟡 À réaliser avant lancement"],
        ["Accessibilité (RGAA)", "🟡 Réglages intégrés, audit à prévoir"],
        ["Accès depuis les ENT (GAR)", "🟡 À étudier pendant le pilote"],
    ], columns=["Exigence", "Statut"]))
    st.subheader("Formation des enseignants")
    for c, (tt, d) in zip(st.columns(3), [("Prise en main de Sabi", "1 h 30 · en visio"), ("Enseigner l’IA du CE2 à la 5e, sans IA générative", "3 h · en présentiel"),
                                          ("Encadrer l’IA générative en 4e-3e", "3 h · en présentiel")]):
        with c.container(border=True):
            st.markdown(f"**{tt}**")
            st.caption(d)
            if st.button("Inscrire des enseignants", key="f_" + tt):
                st.toast("Demande envoyée (simulation).")


def view_offres():
    st.title("Les offres Sabi")
    st.caption("Un abonnement pour les familles, des licences pour les écoles et les territoires. Tous les prix sont des hypothèses à tester pendant le pilote.")
    st.table(pd.DataFrame([[t, c, d, p + " (hypothèse)"] for t, c, d, p in OFFERS.values()], columns=["Offre", "Pour qui", "Ce qui est inclus", "Prix"]))
    st.subheader("Ce qui distingue Sabi")
    pts = [("🇫🇷", "Un parcours IA suivi, en français, du CE2 à la 3e, là où l’offre publique commence en 4e."),
           ("🧩", "5 piliers (apprendre, jouer, coder, bien-être, bouger) déclinés pour 3 tranches d’âge."),
           ("🛡️", "Conforme au cadre d’usage dès la conception : sans IA générative jusqu’en 5e."),
           ("🇪🇺", "Données hébergées en Europe, jamais utilisées pour entraîner une IA."),
           ("🦩", "Un univers attachant : Sabi, la carte des îles et le Permis IA par tranche."),
           ("🔗", "Une passerelle vers le parcours Pix IA obligatoire en 4e.")]
    cols = st.columns(3)
    for n, (e, t) in enumerate(pts):
        with cols[n % 3].container(border=True):
            st.markdown(f"### {e}\n{t}")


{"Accueil": view_accueil, "Enfant": view_enfant, "Parent": view_parent, "Enseignant": view_enseignant,
 "Collectivité": view_collectivite, "Offres": view_offres}[space]()
