"""AI Sabi Academy - prototype de démonstration (version 1).

Cible : accueils de loisirs et périscolaires, enfants de 8 à 12 ans.
Parcours « Découverte IA » : 6 séances de 45 minutes, la moitié sans écran.
Toutes les données du tableau de bord sont FICTIVES (démonstration).
"""

import datetime
import html as html_lib
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# =====================================================================
# CONTENU ET LOGIQUE (fonctions sans dépendance à l'interface)
# =====================================================================

SEANCES = [
    {
        "num": 1,
        "titre": "Trier et classer",
        "notion": "Classification, k plus proches voisins",
        "format": "Cartes (sans écran) + jeu sur la plateforme",
        "objectif": "Comprendre qu'une IA décide en comparant avec des exemples qu'elle connaît.",
        "deroule": [
            (5, "Accueil : « C'est quoi une IA ? » Tour de table, sans corriger les idées des enfants."),
            (20, "Jeu de cartes : par groupes de 4, 20 cartes d'animaux (taille, poids). Chaque enfant tire une carte mystère et choisit son groupe en regardant les 3 cartes les plus proches."),
            (10, "Plateforme : jeu « À qui ressemble-t-il ? » (page Jeux)."),
            (10, "Retour : « Quand l'IA hésite-t-elle ? Qu'est-ce qui la rend plus sûre ? »"),
        ],
        "materiel": "20 cartes d'animaux, feuilles, crayons",
        "retenir": "Une IA compare ce qu'elle voit à des exemples qu'elle connaît.",
    },
    {
        "num": 2,
        "titre": "Apprendre par exemples",
        "notion": "Apprentissage supervisé, exemples d'entraînement et de test",
        "format": "Jeu en équipes (sans écran)",
        "objectif": "Distinguer les exemples avec lesquels l'IA apprend de ceux avec lesquels on la teste.",
        "deroule": [
            (5, "Règle du jeu : un enfant joue « la machine ». On lui montre 8 cartes avec leur groupe."),
            (15, "Entraînement : les équipes cherchent une règle pour classer les cartes."),
            (15, "Test : 4 cartes jamais vues. On vérifie la règle de chaque équipe."),
            (10, "Retour : « Pourquoi garde-t-on des cartes cachées ? »"),
        ],
        "materiel": "2 jeux de cartes (entraînement et test), tableau",
        "retenir": "On teste une IA sur des exemples qu'elle n'a jamais vus.",
    },
    {
        "num": 3,
        "titre": "Apprendre par cœur n'est pas comprendre",
        "notion": "Surapprentissage",
        "format": "Plateforme (jeu) + discussion",
        "objectif": "Voir qu'une IA qui mémorise trop se trompe sur les exemples nouveaux.",
        "deroule": [
            (5, "Histoire : un élève apprend les réponses par cœur et rate le contrôle avec de nouvelles questions."),
            (20, "Plateforme : jeu « Apprendre par cœur » (curseur de mémoire)."),
            (10, "Discussion : « Quand est-il utile de retenir ? Quand faut-il comprendre ? »"),
            (10, "Synthèse : une phrase par groupe."),
        ],
        "materiel": "Tablettes ou ordinateurs (1 pour 2 enfants)",
        "retenir": "Une bonne IA généralise : elle réussit aussi sur du nouveau.",
    },
    {
        "num": 4,
        "titre": "Se tromper",
        "notion": "Évaluation, faux positifs et faux négatifs, biais",
        "format": "Quiz + débat guidé (presque sans écran)",
        "objectif": "Comprendre pourquoi une IA se trompe et que ses erreurs ont des conséquences.",
        "deroule": [
            (10, "Situations racontées par l'animateur : un détecteur de chats, un filtre de messages."),
            (10, "Plateforme : quiz « Se tromper »."),
            (15, "Débat guidé : des exemples trop peu variés donnent-ils une IA juste ? Qui est responsable d'une erreur ?"),
            (10, "Retour : trois questions à se poser devant une réponse d'IA."),
        ],
        "materiel": "Cartes « situations », tableau",
        "retenir": "Une IA peut se tromper : il faut vérifier, et regarder les exemples qui l'ont formée.",
    },
    {
        "num": 5,
        "titre": "Les groupes cachés",
        "notion": "Apprentissage non supervisé, regroupement (k-means)",
        "format": "Cartes + plateforme",
        "objectif": "Découvrir qu'une IA peut regrouper des choses sans qu'on lui dise les groupes.",
        "deroule": [
            (15, "Cartes sans étiquette : chaque équipe fait ses groupes, puis compare."),
            (15, "Plateforme : jeu « Groupes cachés » (choix du nombre de groupes)."),
            (10, "Comparaison : qui a trouvé les mêmes groupes ? Y a-t-il une seule bonne réponse ?"),
            (5, "Retour."),
        ],
        "materiel": "30 cartes sans étiquette, tablettes",
        "retenir": "Sans étiquettes, l'IA cherche des ressemblances. Le nombre de groupes est un choix.",
    },
    {
        "num": 6,
        "titre": "Bouge avec l'IA",
        "notion": "Vision et pose du corps (version sans caméra)",
        "format": "Défis de mouvement en binômes (sans écran)",
        "objectif": "Comprendre qu'une IA peut « voir » un corps comme des points, et conclure le cycle.",
        "deroule": [
            (5, "Échauffement."),
            (25, "Défis en binômes : un enfant décrit les positions des « points » du corps (épaules, coudes, mains), l'autre reproduit la pose."),
            (10, "Parallèle : une IA qui regarde une vidéo voit des points, pas une personne."),
            (5, "Bilan du cycle et diplôme symbolique."),
        ],
        "materiel": "Cartes de poses, espace libre",
        "retenir": "Une IA peut décrire un mouvement avec des points. Dans ce parcours, aucun corps d'enfant n'est filmé.",
    },
]

DEFIS_MOUVEMENT = [
    ("L'étoile de mer", "Debout, jambes et bras écartés : tiens la pose 5 secondes.", "Une IA repère la tête, les mains et les pieds comme des points."),
    ("L'arbre", "Équilibre sur une jambe, bras en l'air : tiens 10 secondes.", "Les points du corps bougent peu : la pose est stable."),
    ("Le robot", "Marche comme un robot en ne bougeant qu'une articulation à la fois.", "Une IA décrit un mouvement point par point."),
    ("La statue", "Un enfant prend une pose, l'autre la décrit avec 5 points : tête, épaules, coudes, mains, genoux.", "C'est ce que fait une IA qui estime la pose."),
    ("Le miroir", "Un binôme bouge lentement, l'autre copie en miroir.", "Copier un mouvement, c'est comparer des positions de points."),
    ("La pause respiration", "Inspire 4 secondes, expire 6 secondes, trois fois.", "Pause active : on revient au calme avant la suite."),
]

QUIZ_ERREURS = [
    {
        "q": "Un détecteur de chats regarde la photo d'un lapin et répond « chat ». Comment s'appelle cette erreur ?",
        "options": ["Un faux positif (il dit oui à tort)", "Un faux négatif (il dit non à tort)", "Ce n'est pas une erreur"],
        "reponse": 0,
        "explication": "L'IA a dit « chat » alors que ce n'est pas un chat : c'est un faux positif.",
    },
    {
        "q": "Un filtre de messages laisse passer un message dangereux en pensant qu'il est normal. Quelle erreur ?",
        "options": ["Un faux positif", "Un faux négatif (il dit non à tort)", "Ce n'est pas une erreur"],
        "reponse": 1,
        "explication": "Le filtre n'a pas vu le danger : c'est un faux négatif. Ces erreurs peuvent avoir des conséquences.",
    },
    {
        "q": "Une IA a appris avec des photos de grands chiens seulement. Elle se trompe sur les petits chiens. D'où vient le problème ?",
        "options": [
            "L'ordinateur est fatigué",
            "Les exemples d'apprentissage n'étaient pas assez variés",
            "Les petits chiens sont bizarres",
        ],
        "reponse": 1,
        "explication": "Quand les exemples manquent de variété, l'IA est biaisée : elle connaît mal ce qu'elle n'a presque jamais vu.",
    },
    {
        "q": "Pourquoi teste-t-on une IA avec des exemples qu'elle n'a jamais vus ?",
        "options": [
            "Pour la fatiguer",
            "Pour vérifier qu'elle ne fait pas qu'apprendre par cœur",
            "Parce que c'est plus joli",
        ],
        "reponse": 1,
        "explication": "Si elle réussit sur du nouveau, c'est qu'elle a vraiment compris et pas seulement mémorisé.",
    },
]

# Données fictives pour le tableau de bord (démonstration)
SITES_DEMO = {
    "Accueil de loisirs A": {
        "Groupe 1 (8-9 ans)": {"inscrits": 22, "participation": [95, 91, 86, 88, 82, 90]},
        "Groupe 2 (10-12 ans)": {"inscrits": 18, "participation": [89, 94, 89, 83, 78, 89]},
    },
    "Accueil de loisirs B": {
        "Groupe 1 (8-9 ans)": {"inscrits": 16, "participation": [94, 88, 81, 75, 81, 88]},
        "Groupe 2 (10-12 ans)": {"inscrits": 20, "participation": [90, 85, 90, 80, 85, 85]},
    },
}


def donnees_voisins():
    """Petit jeu de données animaux (valeurs imaginaires pour la démonstration)."""
    chats = pd.DataFrame(
        {
            "taille": [23, 25, 26, 28, 30, 32, 34],
            "poids": [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.5],
            "classe": "Chat",
        }
    )
    chiens = pd.DataFrame(
        {
            "taille": [31, 35, 40, 45, 55, 60, 70],
            "poids": [6.0, 8.0, 12.0, 18.0, 25.0, 30.0, 38.0],
            "classe": "Chien",
        }
    )
    return pd.concat([chats, chiens], ignore_index=True)


def knn_predire(df, taille, poids, k):
    """Prédit la classe par vote des k plus proches voisins (valeurs mises à l'échelle)."""
    ecart_t = df["taille"].max() - df["taille"].min()
    ecart_p = df["poids"].max() - df["poids"].min()
    distance = np.sqrt(((df["taille"] - taille) / ecart_t) ** 2 + ((df["poids"] - poids) / ecart_p) ** 2)
    voisins = df.assign(distance=distance).nsmallest(k, "distance")
    votes = voisins["classe"].value_counts()
    gagnants = votes[votes == votes.max()].index.tolist()
    # En cas d'égalité, on suit le voisin le plus proche.
    prediction = gagnants[0] if len(gagnants) == 1 else voisins.iloc[0]["classe"]
    return prediction, votes, voisins


def donnees_surapprentissage(graine=0):
    """12 points d'entraînement et 30 points de test autour d'une courbe sinusoïdale."""
    rng = np.random.default_rng(graine)
    x_app = np.sort(rng.uniform(0, 1, 12))
    y_app = np.sin(2 * np.pi * x_app) + rng.normal(0, 0.25, 12)
    x_test = np.sort(rng.uniform(0, 1, 30))
    y_test = np.sin(2 * np.pi * x_test) + rng.normal(0, 0.25, 30)
    return x_app, y_app, x_test, y_test


def ajuster(x_app, y_app, x_test, y_test, degre):
    """Ajuste un polynôme et renvoie le modèle et les erreurs moyennes (appris / nouveaux)."""
    modele = np.polynomial.Polynomial.fit(x_app, y_app, degre)
    err_app = float(np.mean((modele(x_app) - y_app) ** 2))
    err_test = float(np.mean((modele(x_test) - y_test) ** 2))
    return modele, err_app, err_test


def meilleure_erreur_test(x_app, y_app, x_test, y_test, degre_max=9):
    """Plus petite erreur sur les nouveaux exemples parmi les degrés 1 à degre_max."""
    return min(ajuster(x_app, y_app, x_test, y_test, d)[2] for d in range(1, degre_max + 1))


def kmeans(X, k, graine=0, iterations=30):
    """k-means minimal (numpy) : renvoie les étiquettes et les centres."""
    rng = np.random.default_rng(graine)
    centres = X[rng.choice(len(X), k, replace=False)]
    etiquettes = np.zeros(len(X), dtype=int)
    for _ in range(iterations):
        d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
        etiquettes = d.argmin(axis=1)
        nouveaux = np.array(
            [X[etiquettes == j].mean(axis=0) if (etiquettes == j).any() else centres[j] for j in range(k)]
        )
        if np.allclose(nouveaux, centres):
            break
        centres = nouveaux
    return etiquettes, centres


def donnees_groupes(graine=3):
    """Trois nuages de points cachés."""
    rng = np.random.default_rng(graine)
    centres = np.array([[2.0, 2.0], [7.0, 3.0], [4.5, 8.0]])
    points = np.vstack([c + rng.normal(0, 0.8, (12, 2)) for c in centres])
    return points


def texte_bilan(site, groupes):
    """Texte du bilan de fin de cycle (données fictives de démonstration)."""
    lignes = [f"Bilan du cycle « Découverte IA » : {site}", ""]
    total = 0
    for nom, d in groupes.items():
        moyenne = sum(d["participation"]) / len(d["participation"])
        lignes.append(f"{nom} : {d['inscrits']} enfants inscrits, participation moyenne {moyenne:.0f} %.")
        total += d["inscrits"]
    lignes += [
        "",
        f"Total : {total} enfants.",
        "Séances réalisées : 6 sur 6.",
        "Notions abordées : classification, apprentissage par exemples, surapprentissage, erreurs et biais, regroupement, pose du corps.",
        "",
        "Observations de l'animateur : [à compléter]",
        "Points forts : [à compléter]",
        "Points à améliorer : [à compléter]",
        "",
        "ATTENTION : données fictives, générées pour la démonstration d'AI Sabi Academy.",
    ]
    return "\n".join(lignes)



# Démo interactive de l'accueil : « Entraîne ta première IA » (HTML + JavaScript, 100 % dans le navigateur)
HTML_WOW = r"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--green:#0F6E56;--greend:#0A4A38;--gold:#F9C74F}
*{box-sizing:border-box}
body{margin:0;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#1A2A1A;background:transparent}
.hero{position:relative;overflow:hidden;border-radius:18px;padding:20px 22px 16px;color:#fff;
  background:linear-gradient(120deg,#0A4A38,#0F6E56,#1A7A60,#0A4A38);background-size:300% 300%;animation:bg 9s ease infinite}
@keyframes bg{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.net{position:absolute;right:-6px;top:-6px;width:300px;height:220px;opacity:.38;pointer-events:none}
.net line{stroke:#fff;stroke-width:1.2;stroke-dasharray:6 8;animation:flow 2.2s linear infinite}
.net circle{fill:#F9C74F;animation:pulse 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes flow{to{stroke-dashoffset:-28}}
@keyframes pulse{0%,100%{transform:scale(.75);opacity:.55}50%{transform:scale(1.3);opacity:1}}
.badge{display:inline-block;background:rgba(249,199,79,.18);border:1px solid rgba(249,199,79,.45);color:var(--gold);
  padding:4px 12px;border-radius:99px;font-size:12px;font-weight:700;margin-bottom:10px}
h1{position:relative;margin:0 0 6px;font-size:clamp(21px,4vw,34px);line-height:1.15;font-weight:800;max-width:640px}
h1 em{font-style:normal;color:var(--gold)}
.sub{position:relative;margin:0;opacity:.9;font-size:clamp(13px,2vw,16px);max-width:560px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:12px 0 10px}
.btn{border:0;border-radius:99px;padding:9px 14px;font-weight:700;font-size:14px;cursor:pointer;background:#fff;color:#0A4A38;
  box-shadow:0 1px 4px rgba(0,0,0,.18);transition:transform .12s,box-shadow .12s;font-family:inherit}
.btn:hover{transform:translateY(-1px);box-shadow:0 3px 8px rgba(0,0,0,.2)}
.btn.on{background:#0F6E56;color:#fff}
.btn.gold{background:var(--gold);color:#4a3600;animation:glow 1.8s ease-in-out infinite}
@keyframes glow{0%,100%{box-shadow:0 0 0 0 rgba(249,199,79,.7)}50%{box-shadow:0 0 0 9px rgba(249,199,79,0)}}
.btn.ghost{background:transparent;box-shadow:none;border:1.5px solid #9DB8AD;color:#3C5A4E}
.k{font-size:13px;color:#3C5A4E;display:flex;align-items:center;gap:6px;margin-left:auto}
.k input{width:90px;accent-color:#0F6E56}
#wrap{width:100%;display:flex;justify-content:center}
canvas{border-radius:16px;box-shadow:0 6px 22px rgba(10,74,56,.18);border:1px solid #CFE3D8;touch-action:manipulation;cursor:crosshair;background:#F7FBF8}
.msg{margin:10px 2px 0;min-height:44px;font-size:15px;font-weight:600;color:#0A4A38}
.foot{margin:6px 2px 0;font-size:11.5px;color:#6B7F75}
</style></head><body>
<div class="hero"><svg class="net" viewBox="0 0 300 220" aria-hidden="true"><line x1="40" y1="40" x2="150" y2="25" style="animation-delay:0.00s"/><line x1="40" y1="40" x2="150" y2="80" style="animation-delay:0.25s"/><line x1="40" y1="40" x2="150" y2="135" style="animation-delay:0.50s"/><line x1="40" y1="40" x2="150" y2="190" style="animation-delay:0.75s"/><line x1="40" y1="100" x2="150" y2="25" style="animation-delay:1.00s"/><line x1="40" y1="100" x2="150" y2="80" style="animation-delay:1.25s"/><line x1="40" y1="100" x2="150" y2="135" style="animation-delay:1.50s"/><line x1="40" y1="100" x2="150" y2="190" style="animation-delay:0.00s"/><line x1="40" y1="160" x2="150" y2="25" style="animation-delay:0.25s"/><line x1="40" y1="160" x2="150" y2="80" style="animation-delay:0.50s"/><line x1="40" y1="160" x2="150" y2="135" style="animation-delay:0.75s"/><line x1="40" y1="160" x2="150" y2="190" style="animation-delay:1.00s"/><line x1="150" y1="25" x2="260" y2="70" style="animation-delay:1.25s"/><line x1="150" y1="25" x2="260" y2="150" style="animation-delay:1.50s"/><line x1="150" y1="80" x2="260" y2="70" style="animation-delay:0.00s"/><line x1="150" y1="80" x2="260" y2="150" style="animation-delay:0.25s"/><line x1="150" y1="135" x2="260" y2="70" style="animation-delay:0.50s"/><line x1="150" y1="135" x2="260" y2="150" style="animation-delay:0.75s"/><line x1="150" y1="190" x2="260" y2="70" style="animation-delay:1.00s"/><line x1="150" y1="190" x2="260" y2="150" style="animation-delay:1.25s"/><circle cx="40" cy="40" r="6" style="animation-delay:0.0s"/><circle cx="40" cy="100" r="6" style="animation-delay:0.4s"/><circle cx="40" cy="160" r="6" style="animation-delay:0.8s"/><circle cx="150" cy="25" r="6" style="animation-delay:1.2s"/><circle cx="150" cy="80" r="6" style="animation-delay:1.6s"/><circle cx="150" cy="135" r="6" style="animation-delay:0.0s"/><circle cx="150" cy="190" r="6" style="animation-delay:0.4s"/><circle cx="260" cy="70" r="6" style="animation-delay:0.8s"/><circle cx="260" cy="150" r="6" style="animation-delay:1.2s"/></svg>
<span class="badge">&#10024; Essaie : &ccedil;a prend 30 secondes</span>
<h1>Et si tu apprenais &agrave; une <em>machine</em> &agrave; reconna&icirc;tre un chat d'un chien ?</h1>
<p class="sub">Clique dans la zone pour lui donner des exemples. Regarde-la apprendre, en direct.</p>
</div>
<div class="bar">
<button id="b0" class="btn on">&#128049; Chats</button>
<button id="b1" class="btn">&#128054; Chiens</button>
<button id="b2" class="btn">&#128269; Animal myst&egrave;re</button>
<button id="auto" class="btn gold">&#127922; Regarde-la apprendre</button>
<button id="clr" class="btn ghost">&#8634; Effacer</button>
<label class="k">Voisins qui votent : <b id="kv">3</b><input id="k" type="range" min="1" max="7" value="3"></label>
</div>
<div id="wrap"><canvas id="cv"></canvas></div>
<div id="msg" class="msg"></div>
<div class="foot">Rien n'est enregistr&eacute; : tout se passe dans ton navigateur.</div>
<script>
(function () {
  var cv = document.getElementById("cv"), ctx = cv.getContext("2d"), wrap = document.getElementById("wrap");
  var msgEl = document.getElementById("msg");
  var W = 640, H = 352, dpr = window.devicePixelRatio || 1;
  var pts = [], mode = 0, mystery = null, k = 3, confettiDone = false, parts = [], auto = null, winUntil = 0, hes = 0, lastMsg = "";
  var COL = ["229,115,115", "21,101,192"], EMO = ["\uD83D\uDC31", "\uD83D\uDC36"];

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function gauss() { var u = 0, v = 0; while (u === 0) u = Math.random(); while (v === 0) v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function sample(c) {
    var cx = c === 0 ? 0.30 : 0.70, cy = c === 0 ? 0.68 : 0.32;
    return { x: clamp(cx + 0.12 * gauss(), 0.04, 0.96), y: clamp(cy + 0.14 * gauss(), 0.06, 0.94), c: c };
  }
  function pl(n, w) { return n + " " + w + (n > 1 ? "s" : ""); }
  function easeOutBack(x) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); }

  function resize() {
    var w = wrap.clientWidth || document.documentElement.clientWidth || 640;
    W = clamp(Math.floor(w), 260, 760); H = Math.round(W * 0.55);
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    cv.style.width = W + "px"; cv.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // Vote des k plus proches voisins (coordonnees normalisees entre 0 et 1)
  function predict(x, y, kk) {
    var n = pts.length; if (n === 0) return null;
    var d = pts.map(function (p) { return { c: p.c, p: p, d: (p.x - x) * (p.x - x) + (p.y - y) * (p.y - y) }; });
    d.sort(function (a, b) { return a.d - b.d; });
    var m = Math.min(kk, n), v = [0, 0];
    for (var i = 0; i < m; i++) v[d[i].c]++;
    var c = v[0] > v[1] ? 0 : (v[1] > v[0] ? 1 : d[0].c);
    return { c: c, share: v[c] / m, v: v, m: m, near: d.slice(0, m) };
  }

  function addPoint(p) {
    p.b = performance.now(); pts.push(p); checkWin();
  }
  function counts() { var nd = 0; for (var i = 0; i < pts.length; i++) nd += pts[i].c; return { nc: pts.length - nd, nd: nd }; }
  function checkWin() {
    var c = counts();
    if (!confettiDone && c.nc >= 3 && c.nd >= 3) {
      confettiDone = true; winUntil = performance.now() + 4500;
      var cols = ["#F9C74F", "#E57373", "#1565C0", "#0F6E56", "#ffffff"];
      for (var i = 0; i < 90; i++) parts.push({ x: W / 2, y: H * 0.45, vx: (Math.random() - 0.5) * 9, vy: -Math.random() * 8 - 2, life: 90 + Math.random() * 40, col: cols[i % cols.length] });
    }
  }
  function clearAll() {
    if (auto) { clearInterval(auto); auto = null; }
    pts.length = 0; mystery = null; confettiDone = false; parts.length = 0; winUntil = 0;
  }
  function autoFill() {
    if (auto) { clearInterval(auto); auto = null; }
    if (pts.length >= 40) pts.length = 0;
    mystery = null;
    var i = 0, total = 14;
    auto = setInterval(function () {
      addPoint(sample(i % 2 === 0 ? 0 : 1)); i++;
      if (i >= total) { clearInterval(auto); auto = null; }
    }, 280);
  }

  function drawBg() {
    var cell = 12, total = 0, unsure = 0, gx, gy;
    for (gx = 0; gx < W; gx += cell) {
      for (gy = 0; gy < H; gy += cell) {
        var r = predict((gx + cell / 2) / W, (gy + cell / 2) / H, k);
        if (!r) continue;
        total++; if (r.share < 0.75) unsure++;
        var a = 0.10 + 0.38 * Math.max(0, (r.share - 0.5) * 2);
        ctx.fillStyle = "rgba(" + COL[r.c] + "," + a.toFixed(3) + ")";
        ctx.fillRect(gx, gy, cell, cell);
      }
    }
    hes = total ? unsure / total : 0;
  }

  function drawPoint(p, now) {
    var age = clamp((now - p.b) / 320, 0, 1), s = age >= 1 ? 1 : easeOutBack(age);
    var x = p.x * W, y = p.y * H;
    ctx.beginPath(); ctx.arc(x, y, 15 * s, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255,255,255,0.92)"; ctx.fill();
    ctx.lineWidth = 2.5; ctx.strokeStyle = "rgb(" + COL[p.c] + ")"; ctx.stroke();
    ctx.font = Math.round(19 * s) + "px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = "#000"; ctx.fillText(EMO[p.c], x, y + 1);
  }

  function frame(now) {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#F7FBF8"; ctx.fillRect(0, 0, W, H);
    drawBg();
    ctx.font = "12px sans-serif"; ctx.textBaseline = "alphabetic"; ctx.fillStyle = "rgba(10,74,56,0.55)";
    ctx.textAlign = "right"; ctx.fillText("plus grand \u2192", W - 10, H - 8);
    ctx.textAlign = "left"; ctx.fillText("\u2191 plus lourd", 10, 18);
    if (pts.length === 0) {
      ctx.globalAlpha = 0.5 + 0.4 * Math.sin(now / 350);
      ctx.fillStyle = "#0A4A38"; ctx.font = "600 16px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText("Clique ici pour ajouter un animal", W / 2, H / 2);
      ctx.globalAlpha = 1;
    }
    var mr = mystery ? predict(mystery.x, mystery.y, k) : null;
    if (mr) {
      ctx.setLineDash([6, 6]); ctx.lineDashOffset = -now / 40; ctx.lineWidth = 1.6; ctx.strokeStyle = "rgba(10,74,56,0.75)";
      for (var j = 0; j < mr.near.length; j++) {
        ctx.beginPath(); ctx.moveTo(mystery.x * W, mystery.y * H); ctx.lineTo(mr.near[j].p.x * W, mr.near[j].p.y * H); ctx.stroke();
      }
      ctx.setLineDash([]);
    }
    for (var i = 0; i < pts.length; i++) drawPoint(pts[i], now);
    if (mystery) {
      var mx = mystery.x * W, my = mystery.y * H, pulse = 1 + 0.12 * Math.sin(now / 200);
      ctx.beginPath(); ctx.moveTo(mx, my - 17 * pulse); ctx.lineTo(mx + 17 * pulse, my); ctx.lineTo(mx, my + 17 * pulse); ctx.lineTo(mx - 17 * pulse, my); ctx.closePath();
      ctx.fillStyle = "#111"; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = "#F9C74F"; ctx.stroke();
      ctx.fillStyle = "#F9C74F"; ctx.font = "700 15px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("?", mx, my + 1);
      if (mr) { ctx.font = "26px sans-serif"; ctx.fillStyle = "#000"; ctx.fillText(EMO[mr.c], mx, my - 32); }
    }
    for (var q = parts.length - 1; q >= 0; q--) {
      var t = parts[q]; t.vy += 0.25; t.x += t.vx; t.y += t.vy; t.life--;
      if (t.life <= 0) { parts.splice(q, 1); continue; }
      ctx.fillStyle = t.col; ctx.fillRect(t.x, t.y, 7, 4);
    }
    updateMsg(now, mr);
  }

  function updateMsg(now, mr) {
    var c = counts(), s;
    if (now < winUntil && !mr) s = "\uD83C\uDF89 Bravo ! Tu viens d'entra\u00eener ta premi\u00e8re IA. Elle devine maintenant chaque endroit de la zone.";
    else if (pts.length === 0) s = "Choisis \uD83D\uDC31 ou \uD83D\uDC36, puis clique dans la zone pour donner des exemples \u00e0 la machine.";
    else if (c.nc === 0 || c.nd === 0) s = "Bien ! Ajoute maintenant des exemples de l'autre animal.";
    else if (mr) {
      s = "Animal myst\u00e8re : l'IA pense que c'est un " + (mr.c === 0 ? "chat" : "chien") + " (" + mr.v[mr.c] + " voisin" + (mr.v[mr.c] > 1 ? "s" : "") + " sur " + mr.m + ")." + (mr.share < 0.7 ? " Elle h\u00e9site !" : "");
    } else {
      s = "Elle a vu " + pl(c.nc, "chat") + " et " + pl(c.nd, "chien") + ". " +
        (hes > 0.18 ? "Elle h\u00e9site dans la zone claire : ajoute des exemples l\u00e0 pour l'aider." : "Elle est assez s\u00fbre d'elle. Montre-lui un animal myst\u00e8re avec \uD83D\uDD0D !");
    }
    if (s !== lastMsg) { msgEl.textContent = s; lastMsg = s; }
  }

  function setMode(m) {
    mode = m;
    for (var i = 0; i < 3; i++) document.getElementById("b" + i).className = "btn" + (i === m ? " on" : "");
  }
  cv.addEventListener("pointerdown", function (e) {
    var r = cv.getBoundingClientRect();
    var x = clamp((e.clientX - r.left) / r.width, 0.02, 0.98), y = clamp((e.clientY - r.top) / r.height, 0.03, 0.97);
    if (mode === 2) mystery = { x: x, y: y }; else addPoint({ x: x, y: y, c: mode });
  });
  document.getElementById("b0").addEventListener("click", function () { setMode(0); });
  document.getElementById("b1").addEventListener("click", function () { setMode(1); });
  document.getElementById("b2").addEventListener("click", function () { setMode(2); });
  document.getElementById("auto").addEventListener("click", autoFill);
  document.getElementById("clr").addEventListener("click", clearAll);
  document.getElementById("k").addEventListener("input", function (e) { k = parseInt(e.target.value, 10); document.getElementById("kv").textContent = String(k); });
  window.addEventListener("resize", resize);
  if (window.ResizeObserver) new ResizeObserver(resize).observe(wrap);

  window.SABI = { predict: predict, add: addPoint, clear: clearAll, counts: counts, sample: sample, frame: frame, resize: resize,
    state: function () { return { n: pts.length, confettiDone: confettiDone, parts: parts.length, k: k, hes: hes, msg: lastMsg }; },
    setK: function (v) { k = v; }, setMystery: function (m) { mystery = m; } };

  resize();
  function loop() { frame(performance.now()); window.requestAnimationFrame(loop); }
  loop();
})();
</script></body></html>
"""

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def date_francaise(jour):
    return f"{jour.day} {MOIS[jour.month - 1]} {jour.year}"


def diplome_html(pseudo, jour=None):
    """Diplôme symbolique (HTML avec styles en ligne). Le pseudo est échappé."""
    jour = jour or datetime.date.today()
    nom = html_lib.escape(pseudo.strip())[:40]
    return (
        '<div style="border:6px double #0F6E56;border-radius:18px;padding:28px 20px;text-align:center;'
        'background:#F6FBF7;font-family:Georgia,serif;color:#0A4A38;">'
        '<div style="font-size:14px;letter-spacing:3px;font-weight:700;">🧠 AI SABI ACADEMY</div>'
        '<div style="font-size:26px;font-weight:700;margin:14px 0 6px;">Diplôme d\'apprenti·e<br>en intelligence artificielle</div>'
        '<div style="font-size:14px;margin-top:10px;">décerné à</div>'
        f'<div style="font-size:34px;font-weight:700;margin:6px 0 12px;color:#B7791F;">{nom}</div>'
        '<div style="font-size:15px;max-width:520px;margin:0 auto;line-height:1.5;">'
        "pour avoir compris comment une IA apprend à classer, qu'elle peut se tromper, "
        "et qu'il faut garder son esprit critique.</div>"
        f'<div style="font-size:13px;margin-top:16px;">Parcours « Découverte IA » · {date_francaise(jour)}</div>'
        '<div style="font-size:40px;margin-top:8px;">🏅</div></div>'
    )


def diplome_page(pseudo, jour=None):
    """Page HTML complète à télécharger et à imprimer."""
    return (
        '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>Diplôme AI Sabi Academy</title></head>'
        '<body style="margin:0;padding:24px;background:#fff;">' + diplome_html(pseudo, jour) + "</body></html>"
    )


# =====================================================================
# INTERFACE
# =====================================================================

st.set_page_config(page_title="AI Sabi Academy", page_icon="🧠", layout="wide")

st.markdown(
    """
<style>
.stButton>button {border-radius: 99px; font-weight: 600;}
.badge {display:inline-block; background:#E8F5E9; color:#0F6E56; border-radius:99px;
        padding:4px 14px; font-size:13px; font-weight:700; margin-bottom:8px;}
.carte {background:#F4F8F5; border:1px solid #C8E6C9; border-radius:14px; padding:16px; height:100%;}
.carte h4 {margin:0 0 6px 0; color:#0A4A38;}
</style>
""",
    unsafe_allow_html=True,
)


def aller(page):
    """Change de page depuis un bouton (appelé avant le rechargement du script)."""
    st.session_state["nav"] = page


def page_accueil():
    components.html(HTML_WOW, height=800, scrolling=True)

    b1, b2, b3 = st.columns(3)
    b1.button("📘 Voir le parcours des 6 séances", on_click=aller, args=(P_PARCOURS,), use_container_width=True)
    b2.button("🎮 Jouer aux 4 jeux", on_click=aller, args=(P_JEUX,), use_container_width=True)
    b3.button("💶 Demander un pilote gratuit", on_click=aller, args=(P_OFFRE,), use_container_width=True)

    st.markdown("#### Initier les 8-12 ans à l'intelligence artificielle par le jeu et le mouvement, clé en main pour les accueils de loisirs")
    st.markdown('<span class="badge">Prototype de démonstration · version 1 en construction</span>', unsafe_allow_html=True)
    st.info("Les données du tableau de bord de cette démonstration sont fictives.")

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        '<div class="carte"><h4>6 séances de 45 minutes</h4>Un parcours « Découverte IA » prêt à l\'emploi, '
        "de l'accueil des enfants au bilan de fin de cycle.</div>",
        unsafe_allow_html=True,
    )
    c2.markdown(
        '<div class="carte"><h4>La moitié sans écran</h4>Cartes, jeux en équipes, défis de mouvement : '
        "l'IA se comprend aussi en bougeant.</div>",
        unsafe_allow_html=True,
    )
    c3.markdown(
        '<div class="carte"><h4>Fiches animateur et formation</h4>Moins de 15 minutes de préparation par séance, '
        "formation de 2 heures incluse.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Démonstration en 10 minutes")
    st.markdown(
        "1. **Accueil** : entraîne ta première IA avec la démo animée du haut de la page.\n"
        "2. **Parcours** : ouvre la fiche animateur de la séance 1.\n"
        "3. **Jeux** : essaie « Apprendre par cœur » et « Groupes cachés ».\n"
        "4. **Mon diplôme** : crée un diplôme avec un pseudo.\n"
        "5. **Tableau de bord** : regarde le bilan de fin de cycle (données fictives).\n"
        "6. **Offre et pilote** : estime le coût et demande un pilote gratuit de 8 semaines."
    )


def page_parcours():
    st.markdown("# 📘 Parcours « Découverte IA »")
    st.caption("6 séances de 45 minutes pour les 8-12 ans. Contenu proposé, à tester avec quelques animateurs avant d'être figé.")
    for s in SEANCES:
        with st.expander(f"Séance {s['num']} · {s['titre']}"):
            st.markdown(f"**Notion :** {s['notion']}  \n**Format :** {s['format']}")
            st.markdown(f"**Objectif :** {s['objectif']}")
            st.markdown("**Déroulé (45 minutes)**")
            for minutes, texte in s["deroule"]:
                st.markdown(f"- **{minutes} min** : {texte}")
            st.markdown(f"**Matériel :** {s['materiel']}")
            st.success(f"À retenir : {s['retenir']}")


def jeu_voisins():
    st.markdown("### À qui ressemble-t-il ? (séance 1)")
    st.write(
        "Un animal mystérieux arrive. L'IA regarde les animaux les plus proches et vote. "
        "Déplace l'animal mystère, puis change le nombre de voisins."
    )
    df = donnees_voisins()
    c1, c2, c3 = st.columns(3)
    taille = c1.slider("Taille (cm)", 15, 80, 32)
    poids = c2.slider("Poids (kg)", 1.0, 40.0, 6.0, 0.5)
    k = c3.slider("Nombre de voisins qui votent", 1, 7, 3)

    prediction, votes, voisins = knn_predire(df, taille, poids, k)
    couleurs = alt.Scale(domain=["Chat", "Chien"], range=["#E57373", "#1565C0"])
    base = (
        alt.Chart(df)
        .mark_circle(size=130)
        .encode(
            x=alt.X("taille:Q", title="Taille (cm)", scale=alt.Scale(domain=[15, 80])),
            y=alt.Y("poids:Q", title="Poids (kg)", scale=alt.Scale(domain=[0, 42])),
            color=alt.Color("classe:N", scale=couleurs, title="Animal"),
            tooltip=["classe", "taille", "poids"],
        )
    )
    mystere = (
        alt.Chart(pd.DataFrame({"taille": [taille], "poids": [poids]}))
        .mark_point(shape="diamond", size=320, filled=True, color="black")
        .encode(x="taille:Q", y="poids:Q")
    )
    proches = (
        alt.Chart(voisins)
        .mark_point(size=420, filled=False, color="#F9A825", strokeWidth=3)
        .encode(x="taille:Q", y="poids:Q")
    )
    st.altair_chart(base + proches + mystere, use_container_width=True)
    detail = ", ".join(f"{n} voisin(s) {classe}" for classe, n in votes.items())
    st.success(f"L'IA répond : **{prediction}** ({detail}).")
    st.caption("Les voisins qui votent sont entourés en jaune. Essaie la zone où chats et chiens se mélangent : l'IA hésite.")


def jeu_surapprentissage():
    st.markdown("### Apprendre par cœur (séance 3)")
    st.write(
        "L'IA doit retrouver une courbe cachée à partir de 12 points bleus. "
        "Plus tu augmentes sa « mémoire », mieux elle colle aux points bleus. Mais que se passe-t-il avec les nouveaux points gris ?"
    )
    x_app, y_app, x_test, y_test = donnees_surapprentissage()
    degre = st.slider("Mémoire de l'IA (1 = simple, 9 = très détaillée)", 1, 9, 3)
    modele, err_app, err_test = ajuster(x_app, y_app, x_test, y_test, degre)

    xs = np.linspace(0, 1, 200)
    courbe = pd.DataFrame({"x": xs, "y": modele(xs)})
    pts_app = pd.DataFrame({"x": x_app, "y": y_app})
    pts_test = pd.DataFrame({"x": x_test, "y": y_test})
    echelle_y = alt.Scale(domain=[-2, 2])
    ligne = alt.Chart(courbe).mark_line(color="#0F6E56", clip=True).encode(x="x:Q", y=alt.Y("y:Q", scale=echelle_y))
    bleus = alt.Chart(pts_app).mark_circle(size=110, color="#1565C0").encode(x="x:Q", y=alt.Y("y:Q", scale=echelle_y))
    gris = alt.Chart(pts_test).mark_circle(size=60, color="#9E9E9E", opacity=0.7).encode(x="x:Q", y=alt.Y("y:Q", scale=echelle_y))
    st.altair_chart(ligne + bleus + gris, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.metric("Erreur sur les points bleus (appris)", f"{err_app:.3f}")
    c2.metric("Erreur sur les points gris (nouveaux)", f"{err_test:.3f}")
    meilleure = meilleure_erreur_test(x_app, y_app, x_test, y_test)
    if err_app > 0.1:
        st.warning("Trop simple : l'IA se trompe même sur les points bleus. Elle n'a presque rien retenu.")
    elif err_test > 3 * meilleure:
        st.error("Elle a appris par cœur : elle colle aux points bleus mais se trompe sur les nouveaux. C'est le surapprentissage.")
    elif err_test > 1.5 * meilleure:
        st.warning("Attention : elle commence à apprendre par cœur. Elle se trompe un peu plus sur les nouveaux points.")
    else:
        st.success("Bon équilibre : l'IA réussit sur les points appris et sur les nouveaux.")


def jeu_erreurs():
    st.markdown("### Se tromper (séance 4)")
    if "quiz_version" not in st.session_state:
        st.session_state["quiz_version"] = 0
    v = st.session_state["quiz_version"]
    for i, q in enumerate(QUIZ_ERREURS):
        st.radio(q["q"], q["options"], index=None, key=f"quiz_{v}_{i}")
    c1, c2 = st.columns(2)
    if c1.button("Corriger mes réponses"):
        bonnes = 0
        for i, q in enumerate(QUIZ_ERREURS):
            choix = st.session_state.get(f"quiz_{v}_{i}")
            if choix == q["options"][q["reponse"]]:
                bonnes += 1
                st.success(f"Question {i + 1} : bravo ! {q['explication']}")
            elif choix is None:
                st.warning(f"Question {i + 1} : pas de réponse. {q['explication']}")
            else:
                st.error(f"Question {i + 1} : pas tout à fait. {q['explication']}")
        st.markdown(f"**Score : {bonnes} sur {len(QUIZ_ERREURS)}**")
    if c2.button("Recommencer"):
        # Nouvelle version des clés = nouveaux boutons radio vides
        st.session_state["quiz_version"] = v + 1
        st.rerun()


def jeu_groupes():
    st.markdown("### Groupes cachés (séance 5)")
    st.write(
        "Voici des points sans étiquette. L'IA cherche des groupes de points proches. "
        "Choisis le nombre de groupes : y a-t-il une seule bonne réponse ?"
    )
    points = donnees_groupes()
    k = st.slider("Nombre de groupes", 1, 6, 3)
    etiquettes, centres = kmeans(points, k)
    df = pd.DataFrame({"x": points[:, 0], "y": points[:, 1], "groupe": [f"Groupe {e + 1}" for e in etiquettes]})
    graphique = (
        alt.Chart(df)
        .mark_circle(size=130)
        .encode(x=alt.X("x:Q", title=""), y=alt.Y("y:Q", title=""), color=alt.Color("groupe:N", title="Groupe"), tooltip=["groupe"])
    )
    centre_df = pd.DataFrame({"x": centres[:, 0], "y": centres[:, 1]})
    centres_graph = alt.Chart(centre_df).mark_point(shape="cross", size=300, color="black", strokeWidth=3).encode(x="x:Q", y="y:Q")
    st.altair_chart(graphique + centres_graph, use_container_width=True)
    st.caption("Les croix noires sont les « centres » des groupes. Avec 3 groupes, on retrouve les trois nuages cachés ; avec un autre nombre, l'IA découpe autrement.")


def page_jeux():
    st.markdown("# 🎮 Jeux pour les enfants")
    onglets = st.tabs(["À qui ressemble-t-il ?", "Apprendre par cœur", "Se tromper", "Groupes cachés"])
    with onglets[0]:
        jeu_voisins()
    with onglets[1]:
        jeu_surapprentissage()
    with onglets[2]:
        jeu_erreurs()
    with onglets[3]:
        jeu_groupes()


def minuteur(secondes):
    zone = st.empty()
    barre = st.progress(0)
    for i in range(secondes):
        zone.markdown(f"### ⏱️ {secondes - i} s")
        barre.progress((i + 1) / secondes)
        time.sleep(1)
    zone.markdown("### ✅ Terminé !")


def page_mouvement():
    st.markdown("# 🕺 Défis de mouvement (sans caméra)")
    st.caption("Version 1 : aucune caméra, aucune vidéo. Les enfants bougent, l'animateur guide.")
    duree = st.selectbox("Durée du minuteur", [10, 20, 30], index=0, format_func=lambda s: f"{s} secondes")
    for i, (nom, consigne, lien) in enumerate(DEFIS_MOUVEMENT):
        with st.expander(f"{nom}"):
            st.write(consigne)
            st.caption(f"Lien avec l'IA : {lien}")
            if st.button(f"Lancer le minuteur ({duree} s)", key=f"minuteur_{i}"):
                minuteur(duree)


def page_dashboard():
    st.markdown("# 📊 Tableau de bord de l'animateur")
    st.warning("Données fictives, pour la démonstration. Les groupes sont pseudonymisés : aucun nom d'enfant.")
    site = st.selectbox("Site", list(SITES_DEMO.keys()))
    groupes = SITES_DEMO[site]
    total = sum(d["inscrits"] for d in groupes.values())
    toutes = [p for d in groupes.values() for p in d["participation"]]
    c1, c2, c3 = st.columns(3)
    c1.metric("Enfants inscrits", total)
    c2.metric("Séances réalisées", "6 sur 6")
    c3.metric("Participation moyenne", f"{sum(toutes) / len(toutes):.0f} %")

    df = pd.DataFrame({nom: d["participation"] for nom, d in groupes.items()}, index=[f"S{i}" for i in range(1, 7)])
    st.markdown("**Participation par séance (%)**")
    st.bar_chart(df)

    st.markdown("### Bilan de fin de cycle")
    bilan = texte_bilan(site, groupes)
    st.text(bilan)
    st.download_button("Télécharger le bilan (texte)", data=bilan, file_name="bilan_decouverte_IA.txt", mime="text/plain")


def page_offre():
    st.markdown("# 💶 Offre et pilote")
    st.markdown(
        "**Une offre, un prix** : **1 200 € HT par an et par site**, pour jusqu'à 60 enfants et 4 animateurs. "
        "Inclus : le parcours de 6 séances, les fiches animateur, une formation de 2 heures en visioconférence, "
        "le tableau de bord et un bilan de fin de cycle."
    )
    sites = st.slider("Nombre de sites", 1, 20, 3)
    total = sites * 1200
    c1, c2 = st.columns(2)
    c1.metric("Coût annuel", f"{total:,} € HT".replace(",", " "))
    c2.metric("Par enfant (60 enfants par site)", f"{1200 / 60:.0f} €")
    if total < 60000:
        st.caption(
            "Ce montant est inférieur au seuil de 60 000 € HT sous lequel un marché de services peut être conclu "
            "sans publicité ni mise en concurrence (depuis le 1er avril 2026). À confirmer avec votre service de la commande publique."
        )
    st.success("**Pilote gratuit de 8 semaines** sur 3 sites, en échange d'un retour d'expérience.")
    st.markdown(
        "[✉️ Demander un pilote](mailto:zineb@yakdata.fr?subject=Pilote%20AI%20Sabi%20Academy) · "
        "[🌐 Site](https://yakdata-engineering.netlify.app/#contact)"
    )


def page_feuille():
    st.markdown("# 🧭 Feuille de route et conformité")
    st.markdown("### Ce qui est démontré, ce qui ne l'est pas encore")
    tableau = pd.DataFrame(
        [
            ("Démo animée « Entraîne ta première IA » (k plus proches voisins, dans le navigateur)", "Version 1", "Démontré"),
            ("Jeux et puzzles IA", "Version 1", "Démontré"),
            ("Défis de mouvement sans caméra", "Version 1", "Démontré"),
            ("Fiches animateur (6 séances)", "Version 1", "Démontré (contenu à tester avec des animateurs)"),
            ("Tableau de bord et bilan", "Version 1", "Démonstration avec données fictives"),
            ("Moteur de niveaux simple (règles)", "Version 1", "Non implémenté"),
            ("Suivi des connaissances (régression logistique, DKT)", "Version 2", "Étude en cours, nécessite des données de pilotes"),
            ("Reconnaissance de pose par caméra", "Version 2", "Non implémenté (données sensibles)"),
            ("Contes générés par IA", "Plus tard", "Non implémenté (cadre d'usage de l'IA en éducation)"),
            ("Offres familles et écoles", "Phase 2", "Non implémenté"),
        ],
        columns=["Fonction", "Version", "Statut dans cette démonstration"],
    )
    st.dataframe(tableau, use_container_width=True, hide_index=True)
    st.markdown("### Principes de protection des enfants")
    st.markdown(
        "- Pas de compte nominatif obligatoire : les groupes sont pseudonymisés.\n"
        "- Aucune caméra ni vidéo dans la version 1.\n"
        "- Aucune inférence automatique des émotions : si elles apparaissent un jour, elles seront déclarées par l'enfant.\n"
        "- Pas d'IA générative en accès libre pour les enfants.\n"
        "- Hébergement dans l'Union européenne prévu au MVP.\n"
        "- Analyse d'impact RGPD avant tout pilote, et avis juridique sur le classement du moteur adaptatif au regard du règlement européen sur l'IA."
    )


def page_diplome():
    st.markdown("# 🎓 Mon diplôme d'apprenti·e IA")
    st.caption("Un pseudo suffit : aucun vrai nom d'enfant n'est demandé ni enregistré.")
    pseudo = st.text_input("Ton pseudo", max_chars=20, placeholder="Par exemple : Astro42")
    if st.button("Créer mon diplôme", type="primary"):
        if pseudo.strip():
            st.session_state["diplome"] = pseudo.strip()
            st.balloons()
        else:
            st.warning("Écris d'abord un pseudo.")
    nom = st.session_state.get("diplome")
    if nom:
        st.markdown(diplome_html(nom), unsafe_allow_html=True)
        st.download_button(
            "Télécharger mon diplôme", data=diplome_page(nom), file_name="diplome_AI_Sabi_Academy.html", mime="text/html"
        )
        st.caption("Ouvre le fichier téléchargé dans ton navigateur pour l'imprimer.")


P_ACCUEIL = "🏠 Accueil"
P_PARCOURS = "📘 Parcours « Découverte IA »"
P_JEUX = "🎮 Jeux pour les enfants"
P_MOUVEMENT = "🕺 Défis de mouvement"
P_DIPLOME = "🎓 Mon diplôme"
P_DASHBOARD = "📊 Tableau de bord animateur"
P_OFFRE = "💶 Offre et pilote"
P_FEUILLE = "🧭 Feuille de route et conformité"

PAGES = {
    P_ACCUEIL: page_accueil,
    P_PARCOURS: page_parcours,
    P_JEUX: page_jeux,
    P_MOUVEMENT: page_mouvement,
    P_DIPLOME: page_diplome,
    P_DASHBOARD: page_dashboard,
    P_OFFRE: page_offre,
    P_FEUILLE: page_feuille,
}

with st.sidebar:
    st.markdown("## 🧠 AI Sabi Academy")
    st.caption("Prototype de démonstration · données fictives")
    choix = st.radio("Navigation", list(PAGES.keys()), key="nav")
    st.divider()
    st.markdown("**Contact**  \nzineb@yakdata.fr  \n[Site](https://yakdata-engineering.netlify.app/) · [Nous contacter](https://yakdata-engineering.netlify.app/#contact)")

PAGES[choix]()
