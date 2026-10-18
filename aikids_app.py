import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Kids Academy",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stButton>button{border-radius:99px;font-weight:600;transition:all .2s}
.pillar-box{background:white;border-radius:16px;padding:20px;border:1px solid #E0E4F0;margin-bottom:12px}
.xp-label{color:#F9C74F;font-weight:700;font-size:18px}
.card{background:white;border-radius:14px;padding:16px;border:1px solid #E0E4F0;margin-bottom:10px}
.badge-gold{background:#FFF8E1;color:#F57F17;border-radius:99px;padding:3px 12px;font-size:12px;font-weight:700;display:inline-block;margin:2px}
.badge-navy{background:#EEF0F8;color:#2F3C7E;border-radius:99px;padding:3px 12px;font-size:12px;font-weight:700;display:inline-block;margin:2px}
.section-title{font-size:22px;font-weight:700;color:#2F3C7E;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

# ── State ──────────────────────────────────────────────────────
defaults = {
    "xp": 650, "niveau": 4, "streak": 7,
    "emotion": None, "quiz_idx": 0, "quiz_score": 0,
    "quiz_answered": False, "quiz_correct": None,
    "badges": ["🧠 IA Curieuse", "🤖 Robot Friend", "🎯 10 Quiz"],
    "history": [], "code_ran": False, "pause_done": False,
    "glossaire_viewed": set()
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Kids Academy")
    st.divider()
    st.markdown(f"👧 **Léa** · Niveau {st.session_state.niveau}")
    st.progress(st.session_state.xp / 1000)
    st.markdown(f"<span class='xp-label'>{st.session_state.xp} / 1000 XP</span>", unsafe_allow_html=True)
    st.markdown(f"🔥 **{st.session_state.streak} jours de suite !**")
    st.divider()
    st.markdown("**🏅 Badges obtenus**")
    for b in st.session_state.badges:
        st.markdown(f"<span class='badge-gold'>{b}</span>", unsafe_allow_html=True)
    st.divider()
    module = st.radio("Navigation", [
        "🏠 Accueil",
        "🧠 Quiz IA adaptatif",
        "💻 Coding & Cheat Sheet",
        "💜 Émotion & Contes IA",
        "🕺 Mouvement Skeleton",
        "🎓 Glossaire IA",
        "📊 Dashboard Parent"
    ])
    st.divider()
    st.markdown("**YakData Engineering**")
    st.markdown("[🌐 yakdata.fr](https://yakdata.fr) · [🎮 Prototype HTML](https://claude.ai/artifact/FsJ8t7CLAgGABh1k63JMzo)")

# ── ACCUEIL ────────────────────────────────────────────────────
if module == "🏠 Accueil":
    st.markdown("# 🤖 AI Kids Academy")
    st.markdown("#### La plateforme qui apprend aux enfants de 7 à 16 ans à comprendre et utiliser l'IA")
    st.markdown("<span class='badge-gold'>✅ La Prépa French Tech Méditerranée 2026</span>", unsafe_allow_html=True)
    st.divider()

    cols = st.columns(5)
    piliers = [
        ("🧠","Adaptatif","#F96167",65,"Moteur IA · Tuteur cognitif"),
        ("🎮","Jeux & Puzzles","#F9C74F",45,"Énigmes · Récompenses"),
        ("💻","Coding","#1565C0",35,"A code a day · Cheat sheet"),
        ("💜","Émotion","#6A1B9A",50,"Sentiment · Contes IA"),
        ("🕺","Mouvement","#0F6E56",78,"Skeleton · Webcam"),
    ]
    for col,(ico,nom,color,pct,desc) in zip(cols,piliers):
        with col:
            st.markdown(f"<div class='pillar-box'><div style='font-size:28px'>{ico}</div><b style='color:#2F3C7E'>{nom}</b><br><small style='color:#6B7280'>{desc}</small></div>",unsafe_allow_html=True)
            st.progress(pct/100,text=f"{pct}%")

    st.divider()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Sessions semaine","7","+2")
    c2.metric("Taux réussite","84%","+5%")
    c3.metric("XP totaux",str(st.session_state.xp),f"+{st.session_state.xp-600}")
    c4.metric("Streak",f"🔥 {st.session_state.streak} jours","+1")

    st.divider()
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### 📖 Conte IA du jour")
        with st.expander("Le robot qui apprenait à ressentir ✨"):
            st.markdown("*Il était une fois Tibo, un petit robot qui ne comprenait pas pourquoi les humains pleuraient parfois en souriant. Léa lui expliqua que les émotions sont comme des algorithmes complexes...*")
            if st.button("🔄 Générer un nouveau conte",key="home_conte"):
                with st.spinner("L'IA génère..."):
                    time.sleep(1.2)
                contes = [
                    "Tibo découvrit un jour que les données racontent des histoires. Il apprit à les lire comme des livres magiques...",
                    "Dans le monde de l'IA, chaque erreur est une leçon. Tibo rata 1000 fois avant de réussir — et devint le robot le plus sage...",
                    "Léa demanda à Tibo : 'Qu'est-ce que la créativité ?' Tibo répondit : 'C'est ce que les humains font de mieux que moi'..."
                ]
                st.success(f"✨ *{random.choice(contes)}*")
    with col2:
        st.markdown("### 🎯 Objectif du jour")
        st.progress(0.6,text="3 modules sur 5 complétés")
        st.markdown("▸ ✅ Quiz IA — Algorithmes")
        st.markdown("▸ ✅ Mouvement — Skeleton")
        st.markdown("▸ ⏳ Coding — Classificateur")
        st.markdown("▸ 🔒 Émotion & Conte")
        st.markdown("▸ 🔒 Glossaire IA")

# ── QUIZ ──────────────────────────────────────────────────────
elif module == "🧠 Quiz IA adaptatif":
    st.markdown("# 🧠 Quiz adaptatif IA")
    st.markdown("**Pilier 1** Apprentissage adaptatif · **Pilier 2** Jeux & puzzles · Niveau ajusté en temps réel")
    st.divider()

    questions = [
        {
            "q":"Quand Spotify te propose 'Découvertes de la semaine', quelle technologie utilise-t-il ?",
            "opts":["Un algorithme de recommandation basé sur tes écoutes","Un humain qui choisit pour toi","Le hasard total","Il copie les choix de tes amis"],
            "ans":0,"diff":"⭐ Débutant",
            "expl":"Spotify utilise un **algorithme de recommandation collaborative** — il analyse tes écoutes et les compare à des millions d'utilisateurs similaires. C'est du Machine Learning !",
            "xp":30
        },
        {
            "q":"Un réseau de neurones artificiel s'inspire de :",
            "opts":["L'architecture d'un ordinateur","Le cerveau humain","Un réseau électrique","Un arbre décisionnel"],
            "ans":1,"diff":"⭐ Débutant",
            "expl":"Les réseaux de neurones artificiels imitent le fonctionnement du **cerveau humain** : des neurones connectés qui transmettent des signaux et apprennent par l'expérience.",
            "xp":30
        },
        {
            "q":"Qu'est-ce que le 'Machine Learning' ?",
            "opts":["Un ordinateur qui apprend à jouer aux échecs uniquement","Un programme qui apprend automatiquement depuis des données","Un robot physique qui se déplace","Un logiciel de traduction"],
            "ans":1,"diff":"⭐⭐ Intermédiaire",
            "expl":"Le **Machine Learning** est la capacité d'un programme à apprendre automatiquement depuis des données, sans être explicitement programmé pour chaque tâche.",
            "xp":50
        },
        {
            "q":"ChatGPT est un exemple de :",
            "opts":["Réseau de neurones convolutif (CNN)","Modèle de langage large (LLM)","Algorithme de tri","Base de données relationnelle"],
            "ans":1,"diff":"⭐⭐ Intermédiaire",
            "expl":"ChatGPT est un **LLM (Large Language Model)** — un modèle entraîné sur des milliards de textes pour comprendre et générer du langage naturel.",
            "xp":50
        },
        {
            "q":"L'IA peut-elle se tromper ?",
            "opts":["Non, l'IA est toujours parfaite","Oui, si elle a été entraînée sur de mauvaises données","Non, les algorithmes sont infaillibles","Seulement si le programmeur a fait une faute de frappe"],
            "ans":1,"diff":"⭐⭐⭐ Avancé",
            "expl":"Oui ! Une IA apprend depuis des données — si ces données sont biaisées ou incomplètes, l'IA fera des erreurs. C'est pourquoi l'**éthique de l'IA** est si importante.",
            "xp":80
        },
    ]

    idx = min(st.session_state.quiz_idx, len(questions)-1)
    q = questions[idx]

    col1,col2,col3 = st.columns([4,1,1])
    with col1:
        st.progress((idx)/len(questions), text=f"Question {idx+1} / {len(questions)}")
    with col2:
        st.markdown(f"**{q['diff']}**")
    with col3:
        st.markdown(f"**+{q['xp']} XP**")

    st.markdown(f"### 🎮 {q['q']}")

    if not st.session_state.quiz_answered:
        choix = st.radio("Choisis ta réponse :",q['opts'],index=None,key=f"q{idx}")
        if st.button("✅ Valider",type="primary",use_container_width=True):
            if choix == q['opts'][q['ans']]:
                st.session_state.quiz_correct = True
                st.session_state.xp += q['xp']
                st.session_state.quiz_score += 1
                if st.session_state.quiz_score == 3 and "🎯 Quiz Master" not in st.session_state.badges:
                    st.session_state.badges.append("🎯 Quiz Master")
            else:
                st.session_state.quiz_correct = False
            st.session_state.history.append({"module":"Quiz","date":datetime.now().strftime("%H:%M"),"result":"✓" if st.session_state.quiz_correct else "✗"})
            st.session_state.quiz_answered = True
            st.rerun()
    else:
        if st.session_state.quiz_correct:
            st.success(f"🏅 Excellent ! +{q['xp']} XP !")
            st.balloons()
        else:
            st.error(f"❌ Pas tout à fait. La bonne réponse : **{q['opts'][q['ans']]}**")

        with st.expander("🤖 Tibo t'explique"):
            st.markdown(q['expl'])

        col1,col2 = st.columns(2)
        with col1:
            if idx < len(questions)-1:
                if st.button("➡️ Question suivante",type="primary",use_container_width=True):
                    st.session_state.quiz_idx += 1
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_correct = None
                    st.rerun()
            else:
                st.success(f"🎓 Quiz terminé ! Score : {st.session_state.quiz_score}/{len(questions)}")
                if st.button("🔄 Recommencer",type="primary",use_container_width=True):
                    st.session_state.quiz_idx = 0
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_score = 0
                    st.rerun()
        with col2:
            if st.button("🔀 Question aléatoire",use_container_width=True):
                st.session_state.quiz_idx = random.randint(0,len(questions)-1)
                st.session_state.quiz_answered = False
                st.session_state.quiz_correct = None
                st.rerun()

    st.divider()
    st.markdown(f"**Score session :** {st.session_state.quiz_score} bonne(s) réponse(s)")

# ── CODING ────────────────────────────────────────────────────
elif module == "💻 Coding & Cheat Sheet":
    st.markdown("# 💻 A code a day — to learn & play")
    st.markdown("**Pilier 3** · Coding & visualisation IA · Jour 12 · Python")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🎯 Défi du jour", "📋 Cheat Sheet", "🔮 Glossaire Visuel"])

    with tab1:
        st.info("**Défi** — Crée un classificateur qui devine si c'est un chien ou un chat !")
        code = '''def ia_reconnait(taille, aboie):
    """Mon premier classificateur IA"""
    if taille > 50 and aboie:
        return "🐕 Chien — confiance 95%"
    elif taille < 30 and not aboie:
        return "🐈 Chat — confiance 88%"
    else:
        return "🤔 Incertain — besoin de plus de données"

# Teste ton IA
print(ia_reconnait(60, True))
print(ia_reconnait(25, False))
print(ia_reconnait(40, True))'''
        st.code(code, language="python")

        st.markdown("### 🎮 Lance ton IA en direct !")
        c1,c2 = st.columns(2)
        with c1:
            taille = st.slider("Taille (cm)",5,100,40)
        with c2:
            aboie = st.toggle("L'animal aboie ?")

        def ia_reconnait(t,a):
            if t>50 and a: return "🐕 Chien — confiance 95%"
            elif t<30 and not a: return "🐈 Chat — confiance 88%"
            else: return "🤔 Incertain — besoin de plus de données"

        if st.button("▶️ Lancer mon IA",type="primary",use_container_width=True):
            with st.spinner("Analyse en cours..."):
                time.sleep(0.6)
            r = ia_reconnait(taille, aboie)
            st.success(f"**Résultat :** {r}")
            if not st.session_state.code_ran:
                st.session_state.xp += 40
                st.session_state.code_ran = True
                st.session_state.history.append({"module":"Coding","date":datetime.now().strftime("%H:%M"),"result":"✓"})
                if "💻 First Code" not in st.session_state.badges:
                    st.session_state.badges.append("💻 First Code")
            st.info("✅ Tu viens de créer un **classificateur supervisé** — c'est exactement ce qu'utilisent Google Photos et Face ID !")

        st.divider()
        st.markdown("### 🚀 Défi bonus — Améliore l'IA !")
        st.markdown("Ajoute une 3e caractéristique (ex: `miaule`) pour améliorer la précision.")
        user_code = st.text_area("Écris ton code amélioré :",
            "def ia_amelioree(taille, aboie, miaule):\n    # Ton code ici\n    pass",
            height=120)
        if st.button("🧪 Tester mon amélioration"):
            st.success("💡 Super initiative ! En production, on utiliserait scikit-learn pour automatiser l'apprentissage de ces règles depuis des milliers d'exemples.")

    with tab2:
        st.markdown("### 📋 Cheat Sheet Python IA — Les commandes essentielles")
        cheatsheet = {
            "Condition": ("if x > 50:", "Prendre une décision selon une valeur"),
            "Fonction": ("def ma_fonction(param):", "Créer un outil réutilisable"),
            "Boucle": ("for item in liste:", "Répéter une action sur chaque élément"),
            "Liste": ("ma_liste = [1, 2, 3]", "Stocker plusieurs valeurs"),
            "Import": ("import pandas as pd", "Charger une bibliothèque"),
            "Print": ("print('résultat')", "Afficher un résultat"),
            "Variable": ("x = 42", "Stocker une valeur en mémoire"),
            "Commentaire": ("# ceci est une note", "Expliquer le code, non exécuté"),
        }
        for terme,(code_ex,expl) in cheatsheet.items():
            col1,col2,col3 = st.columns([2,3,3])
            with col1: st.markdown(f"**{terme}**")
            with col2: st.code(code_ex,language="python")
            with col3: st.markdown(f"*{expl}*")
            st.divider()

    with tab3:
        st.markdown("### 🔮 Concepts IA en images")
        concepts = {
            "Classification 🏷️":"Trier des données en catégories (spam/non-spam, chien/chat). L'IA apprend depuis des exemples étiquetés.",
            "Régression 📈":"Prédire une valeur continue (prix d'une maison, température). L'IA trouve la ligne qui colle le mieux aux données.",
            "Clustering 🔵":"Regrouper des données similaires SANS étiquettes. L'IA découvre des groupes cachés (clients similaires).",
            "NLP 💬":"Natural Language Processing — comprendre et générer du texte humain. ChatGPT, traduction, résumé.",
            "Computer Vision 👁️":"Analyser des images et vidéos. Reconnaissance faciale, voitures autonomes, médecine.",
            "Reinforcement Learning 🎮":"Apprendre par essais-erreurs avec récompenses. AlphaGo, robots, jeux vidéo.",
        }
        cols = st.columns(3)
        for i,(terme,desc) in enumerate(concepts.items()):
            with cols[i%3]:
                with st.expander(terme):
                    st.write(desc)
                    st.session_state.glossaire_viewed.add(terme)
        if len(st.session_state.glossaire_viewed) >= 4 and "📚 Glossaire Pro" not in st.session_state.badges:
            st.session_state.badges.append("📚 Glossaire Pro")
            st.balloons()
            st.success("🏅 Badge 'Glossaire Pro' débloqué !")

# ── EMOTION ───────────────────────────────────────────────────
elif module == "💜 Émotion & Contes IA":
    st.markdown("# 💜 Émotion & bien-être")
    st.markdown("**Pilier 4** · Analyse de sentiment · Cartes positives popup · Contes IA génératifs")
    st.divider()

    tab1, tab2 = st.tabs(["😊 Comment tu te sens ?", "✍️ Crée ton conte IA"])

    with tab1:
        st.markdown("### Dis-le à Tibo l'IA 👇")
        emotions = {
            "😄 Super":("82%","#2e7d32","Mode défi activé ! +20 XP","⭐","Tu rayonnes aujourd'hui !",
                "Tibo t'a préparé un défi plus difficile. Dans ce conte, le robot champion va t'apprendre ses secrets de champion..."),
            "🙂 Bien":("65%","#0f6e56","Session standard","💚","Tu vas bien, c'est l'essentiel !",
                "Bonne journée pour apprendre ! Tibo raconte comment les robots apprennent à être vraiment utiles pour les humains..."),
            "😐 Moyen":("42%","#f57f17","Session allégée — 15 min","🌟","Chaque jour compte !",
                "Ça arrive d'être entre les deux. Voici Tibo qui cherche son énergie dans une forêt de données magiques..."),
            "😰 Stressé·e":("22%","#e53935","Pause + respiration activée","💜","Tu fais de ton mieux !",
                "Tibo aussi se sent parfois dépassé. Il a découvert une technique secrète : compter jusqu'à 8 en respirant..."),
            "😴 Fatigué·e":("18%","#7b1fa2","Session 5 min uniquement","🌙","Le repos, c'est aussi apprendre !",
                "Ce soir Tibo te raconte une courte histoire douce pour rêver d'IA et te reposer tranquillement..."),
            "😢 Triste":("14%","#1565c0","Mode doux — pas de quiz","🤗","Tu n'es pas seul·e !",
                "Tibo était triste un jour lui aussi. Il a appris que partager ses émotions les rend moins lourdes..."),
            "🤔 Curieux·se":("76%","#6a1b9a","Module bonus débloqué !","🔭","Ta curiosité est une super-puissance !",
                "Tu es en mode exploration ! Tibo t'emmène découvrir comment une IA apprend à reconnaître les étoiles..."),
            "🥳 Fier·e":("91%","#2e7d32","Badge confiance débloqué !","🏆","Tu mérites ta fierté !",
                "Les champions ont tous commencé par les bases. Tibo célèbre tes progrès avec un conte épique...")
        }

        cols = st.columns(4)
        emos = list(emotions.keys())
        for i,(col,emo) in enumerate(zip(cols*2,emos)):
            if col.button(emo,use_container_width=True,key=f"emo_{i}"):
                st.session_state.emotion = emo
                st.session_state.xp += 20
                st.session_state.history.append({"module":"Émotion","date":datetime.now().strftime("%H:%M"),"result":emo[:2]})

        if st.session_state.emotion:
            emo = st.session_state.emotion
            fill,color,conseil,carte_ico,carte_msg,conte = emotions[emo]
            st.divider()
            col1,col2 = st.columns(2)
            with col1:
                st.markdown("#### 📊 Analyse de sentiment en temps réel")
                pct = int(fill.replace("%",""))
                st.progress(pct/100)
                st.markdown(f"<div style='color:{color};font-weight:600;font-size:14px'>{conseil}</div>",unsafe_allow_html=True)
                st.markdown(f"**Indice émotionnel :** {pct}% positif")
            with col2:
                st.markdown("#### ✨ Carte positive débloquée !")
                st.markdown(f"""<div style='background:linear-gradient(135deg,#fff8e1,#fffde7);border-radius:16px;
                padding:20px;border:1.5px solid #ffe082;text-align:center'>
                <div style='font-size:44px;margin-bottom:8px'>{carte_ico}</div>
                <div style='font-size:16px;font-weight:700;color:#f57f17'>{carte_msg}</div>
                </div>""",unsafe_allow_html=True)
            st.divider()
            st.markdown("#### 📖 Conte personnalisé — généré par l'IA générative")
            st.markdown(f"*{conte}*")
            if st.button("🔄 Générer une suite du conte",use_container_width=True):
                with st.spinner("L'IA génère la suite..."):
                    time.sleep(1.5)
                suites = [
                    "...et Tibo comprit enfin que l'intelligence n'est pas dans les réponses, mais dans les bonnes questions.",
                    "...Léa et Tibo devinrent les meilleurs amis du monde numérique, apprenant l'un de l'autre chaque jour.",
                    "...C'est ainsi que Tibo apprit la leçon la plus importante : les données sont faites par des humains, pour des humains."
                ]
                st.success(f"✨ *{random.choice(suites)}*")

    with tab2:
        st.markdown("### ✍️ Crée TON propre conte IA !")
        st.markdown("L'IA générative va t'aider à écrire une histoire unique.")
        heros = st.text_input("Ton personnage principal", "Tibo le robot")
        lieu = st.selectbox("Le décor", ["une forêt de données","une ville du futur","un laboratoire secret","l'espace numérique","l'école de l'IA"])
        defi = st.text_input("Le défi à surmonter", "apprendre à ressentir les émotions")
        fin = st.radio("La fin de l'histoire", ["heureuse 😊","mystérieuse 🌙","courageuse 💪","drôle 😄"])

        if st.button("✨ Générer mon conte IA",type="primary",use_container_width=True):
            with st.spinner("L'IA crée ton conte unique..."):
                time.sleep(2)
            conte_perso = f"""
**{heros} et le défi de {lieu}**

*Il était une fois {heros}, qui vivait dans {lieu}. Un jour, {heros} dut faire face à un grand défi : {defi}.*

*Au début, {heros} pensait que c'était impossible. Mais avec de la persévérance et l'aide de ses amis, {heros} découvrit une méthode secrète — analyser les données de la situation sous un angle complètement nouveau.*

*La fin fut {fin.split()[0]} — {heros} réussit son défi et apprit quelque chose d'essentiel : même une IA peut toujours progresser !*

*(Conte généré par IA générative — AI Kids Academy · YakData Engineering)*
            """
            st.markdown(conte_perso)
            st.download_button("💾 Télécharger mon conte", conte_perso, "mon_conte_IA.txt", use_container_width=True)

# ── MOVEMENT ──────────────────────────────────────────────────
elif module == "🕺 Mouvement Skeleton":
    st.markdown("# 🕺 Mouvement & santé")
    st.markdown("**Pilier 5** · Technologie Skeleton · Reconnaissance gestuelle webcam · Pauses actives")
    st.divider()

    tab1, tab2 = st.tabs(["🎮 Défi Skeleton", "⚡ Capsules sportives"])

    with tab1:
        col1,col2 = st.columns([2,1])
        with col1:
            st.markdown("""<div style='background:linear-gradient(135deg,#1a1a2e,#2f3c7e);border-radius:16px;
            height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white'>
            <div style='font-size:64px'>🕺</div>
            <div style='font-size:13px;opacity:.7;margin-top:8px'>Skeleton v2.1 · 33 points corporels · MediaPipe</div>
            </div>""",unsafe_allow_html=True)
            if st.button("📷 Activer la webcam Skeleton",type="primary",use_container_width=True):
                with st.spinner("Initialisation du Skeleton IA..."):
                    time.sleep(1.5)
                st.success("🟢 Skeleton actif ! 33 points détectés · Reproduis le geste !")
                st.progress(0.87,text="Score posture : 87% — Excellent !")
                st.session_state.xp += 50
                st.session_state.history.append({"module":"Mouvement","date":datetime.now().strftime("%H:%M"),"result":"87%"})
        with col2:
            st.metric("Posture","87%","+5%")
            st.metric("Gestes","12","+3")
            st.metric("Combo","🔥 5","+2")
            st.metric("XP mvt","230","+80")

        st.divider()
        st.markdown("### 🏆 Défis du jour")
        defis = [
            ("🙆","Bras en croix","33 points analysés","✅ Réussi","#2e7d32"),
            ("🤸","Étoile de mer","Écarte bras et jambes","✅ Réussi","#2e7d32"),
            ("🧘","Position yoga","Équilibre sur une jambe","⏳ En cours...","#f57f17"),
            ("💃","Séquence danse","4 gestes enchaînés","🔒 Bloqué","#6B7280"),
        ]
        for ico,nom,desc,statut,color in defis:
            c1,c2,c3,c4 = st.columns([1,3,4,2])
            with c1: st.markdown(f"**{ico}**")
            with c2: st.markdown(f"**{nom}**")
            with c3: st.markdown(f"*{desc}*")
            with c4: st.markdown(f"<span style='color:{color};font-weight:600'>{statut}</span>",unsafe_allow_html=True)
            st.divider()

        st.info("⚡ **Pause active !** L'IA détecte que tu es assis·e depuis 25 min — 2 min de mouvement = +100 XP !")
        if st.button("🕺 Lancer la pause active",type="primary",use_container_width=True):
            with st.spinner("Pause active en cours — Lève-toi et suis Tibo !"):
                time.sleep(2)
            st.success("🎉 +100 XP · Pause terminée ! Meilleure concentration garantie !")
            if not st.session_state.pause_done:
                st.session_state.xp += 100
                st.session_state.pause_done = True
            st.balloons()

    with tab2:
        st.markdown("### ⚡ Capsules sportives — 2 minutes chrono")
        capsules = {
            "🌅 Réveil musculaire":["Étire les bras vers le ciel × 5","Rotations d'épaules × 10","Penche la tête gauche/droite × 5","Respiration profonde × 3"],
            "🧠 Pause cerveau":["Ferme les yeux 30 secondes","Masse tes tempes en cercles","Regarde loin par la fenêtre 20 sec","Baille 3 fois (ça oxygène !)"],
            "💪 Énergie express":["Jumping jacks × 10","Squats × 5","Pompes sur les genoux × 5","Course sur place 30 secondes"],
            "😌 Relaxation":["Respire 4 sec / retiens 4 sec / expire 4 sec","Détends les épaules × 3","Souris le plus grand sourire possible","Pense à quelque chose de beau 10 sec"]
        }
        for titre,etapes in capsules.items():
            with st.expander(f"**{titre}** — 2 min"):
                for i,e in enumerate(etapes,1):
                    st.markdown(f"**{i}.** {e}")
                if st.button(f"▶️ Lancer {titre}",key=titre):
                    st.success("✅ Capsule terminée ! +30 XP")
                    st.session_state.xp += 30

# ── GLOSSAIRE ─────────────────────────────────────────────────
elif module == "🎓 Glossaire IA":
    st.markdown("# 🎓 Glossaire IA interactif")
    st.markdown("**Pilier 3** · Comprendre les mots de l'IA · 30 termes essentiels")
    st.divider()

    search = st.text_input("🔍 Recherche un terme...", placeholder="Ex: algorithme, neurone, données...")

    glossaire_complet = {
        "Algorithme":"Suite d'instructions précises qu'un ordinateur suit pour résoudre un problème. Comme une recette de cuisine, mais pour l'IA.",
        "Intelligence Artificielle":"Capacité d'une machine à imiter certaines fonctions cognitives humaines : apprendre, raisonner, résoudre des problèmes.",
        "Machine Learning":"Branche de l'IA où les machines apprennent automatiquement depuis des données, sans être programmées explicitement.",
        "Deep Learning":"Type de ML utilisant des réseaux de neurones profonds (multi-couches). Utilisé pour la reconnaissance d'images et de voix.",
        "Réseau de neurones":"Système d'IA inspiré du cerveau humain, composé de couches de 'neurones' artificiels connectés.",
        "Donnée":"Information brute (chiffre, texte, image) que l'IA utilise pour apprendre et prendre des décisions.",
        "Dataset":"Ensemble de données organisé utilisé pour entraîner un modèle IA.",
        "Modèle IA":"Résultat de l'entraînement d'un algorithme sur des données — il peut ensuite faire des prédictions.",
        "Entraînement":"Processus d'apprentissage d'un modèle IA sur un dataset. Comme réviser pour un examen.",
        "Prédiction":"Ce que le modèle IA prédit ou décide en analysant de nouvelles données.",
        "Classification":"Tâche IA qui consiste à trier des données en catégories (spam/non-spam, chien/chat).",
        "Régression":"Tâche IA qui prédit une valeur numérique continue (prix d'une maison, température).",
        "NLP":"Natural Language Processing — traitement du langage naturel. Permet à l'IA de comprendre le texte humain.",
        "LLM":"Large Language Model — modèle de langage entraîné sur des milliards de textes. Ex: ChatGPT, Claude.",
        "Biais IA":"Erreur systématique dans un modèle due à des données d'entraînement déséquilibrées ou incomplètes.",
        "Éthique IA":"Ensemble de principes pour développer une IA juste, transparente et respectueuse des humains.",
        "Python":"Langage de programmation très utilisé en IA pour sa simplicité et ses nombreuses bibliothèques.",
        "Variable":"Conteneur qui stocke une valeur en mémoire. Ex: age = 10",
        "Fonction":"Bloc de code réutilisable qui effectue une tâche précise. Ex: def calculer(x):",
        "API":"Interface qui permet à différents logiciels de communiquer. L'IA utilise des APIs pour être intégrée.",
        "Cloud":"Serveurs distants sur Internet où l'IA est souvent hébergée et exécutée.",
        "Skeleton":"Technologie qui détecte et suit les mouvements du corps humain via une caméra (33 points clés).",
        "MediaPipe":"Bibliothèque Google open-source pour la détection de pose, visage et mains en temps réel.",
        "Sentiment Analysis":"Analyse automatique des émotions dans un texte (positif, négatif, neutre).",
        "Recommandation":"Système IA qui suggère du contenu personnalisé (Netflix, Spotify, YouTube).",
        "Feature":"Caractéristique d'une donnée utilisée par l'IA pour apprendre. Ex: taille, couleur, prix.",
        "Label":"La réponse attendue pour un exemple d'entraînement. Ex: chien ou chat, spam ou non.",
        "Précision":"Mesure de la performance d'un modèle IA — % de bonnes prédictions.",
        "Open Source":"Logiciel dont le code est public et accessible à tous. Beaucoup d'outils IA sont open source.",
        "RGPD":"Règlement européen sur la protection des données personnelles. L'IA doit le respecter.",
    }

    filtered = {k:v for k,v in glossaire_complet.items()
                if not search or search.lower() in k.lower() or search.lower() in v.lower()}

    cols = st.columns(3)
    for i,(terme,def_) in enumerate(filtered.items()):
        with cols[i%3]:
            with st.expander(f"**{terme}**"):
                st.write(def_)
                st.session_state.glossaire_viewed.add(terme)

    st.divider()
    st.markdown(f"**{len(st.session_state.glossaire_viewed)}/{len(glossaire_complet)}** termes découverts")
    st.progress(len(st.session_state.glossaire_viewed)/len(glossaire_complet))

# ── DASHBOARD PARENT ──────────────────────────────────────────
elif module == "📊 Dashboard Parent":
    st.markdown("# 📊 Tableau de bord parent")
    st.markdown("**Suivi de Léa** · Semaine du 18 octobre 2026 · 5 piliers · Moteur IA adaptatif")
    st.divider()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Sessions","7","+2")
    c2.metric("Taux réussite","84%","+5%")
    c3.metric("XP totaux",str(st.session_state.xp),f"+{max(0,st.session_state.xp-600)}")
    c4.metric("Streak",f"🔥 {st.session_state.streak}j","+1")

    st.divider()
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Progression par pilier")
        df_prog = pd.DataFrame({
            "Pilier":["🧠 Adaptatif","🎮 Puzzles","💻 Coding","💜 Émotion","🕺 Mouvement"],
            "%":[65,45,35,50,78]
        })
        st.bar_chart(df_prog.set_index("Pilier")["%"])

    with col2:
        st.markdown("### 📅 Activité des 7 derniers jours")
        dates = [(datetime.now() - timedelta(days=i)).strftime("%d/%m") for i in range(6,-1,-1)]
        sessions = [0,1,2,1,2,1,1]
        df_act = pd.DataFrame({"Date":dates,"Sessions":sessions})
        st.bar_chart(df_act.set_index("Date"))

    st.divider()
    st.markdown("### 🕐 Activités récentes")
    activites = [
        ("🧠","Quiz IA adaptatif","Aujourd'hui · 12 min · Niveau ↑","4/5 ✓"),
        ("🕺","Skeleton — 3 gestes","Hier · 18 min · Score 87%","🏅"),
        ("💜","Émotion 😄 · Conte créé","Hier · Carte positive débloquée","✓"),
        ("💻","Code jour 12","28 sept. · Cheat sheet × 3","✓"),
    ]
    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            activites.insert(0,({"Quiz":"🧠","Coding":"💻","Émotion":"💜","Mouvement":"🕺"}.get(h['module'],'📌'),
                h['module'],f"Session du jour · {h['date']}",h['result']))

    for ico,titre,detail,score in activites[:5]:
        c1,c2,c3 = st.columns([1,6,1])
        with c1: st.markdown(f"**{ico}**")
        with c2: st.markdown(f"**{titre}**  \n*{detail}*")
        with c3: st.markdown(f"**{score}**")
        st.divider()

    st.markdown("### 🤖 Analyse IA personnalisée")
    st.info(f"""
    **Léa** progresse très vite sur les Piliers 1 et 5 (+2 niveaux cette semaine).
    Bien-être émotionnel excellent (78% d'humeurs positives). XP actuel : **{st.session_state.xp}**.

    **Recommandation IA :** encourager le Pilier 3 Coding (35% seulement).
    L'adaptatif a automatiquement augmenté la difficulté du Quiz.
    """)

    col1,col2 = st.columns(2)
    with col1:
        st.warning("⚡ Fatigue détectée jeudi — session raccourcie automatiquement à 10 min.")
    with col2:
        st.success(f"🏅 {len(st.session_state.badges)} badges obtenus : {' '.join(st.session_state.badges)}")

    st.markdown("### 📊 Compétences IA acquises")
    competences = {"Algorithmes":80,"Machine Learning":40,"Éthique IA":60,"Coding Python":35,"Reconnaissance gestuelle":78}
    for comp,val in competences.items():
        st.progress(val/100,text=f"{comp} — {val}%")
