import streamlit as st
import time
import random

# ── Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Kids Academy",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background: #F4F5FB; }
  .stButton>button {
    border-radius: 99px;
    font-weight: 600;
    transition: all 0.2s;
  }
  .pillar-box {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #E0E4F0;
    margin-bottom: 12px;
  }
  .badge {
    background: #EEF0F8;
    color: #2F3C7E;
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin: 2px;
  }
  .xp-label { color: #F9C74F; font-weight: 700; font-size: 18px; }
  .metric-card {
    background: white;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #E0E4F0;
    text-align: center;
  }
</style>
""", unsafe_allow_html=True)

# ── State ───────────────────────────────────────────────────────
if "xp" not in st.session_state:
    st.session_state.xp = 650
if "niveau" not in st.session_state:
    st.session_state.niveau = 4
if "emotion" not in st.session_state:
    st.session_state.emotion = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "quiz_correct" not in st.session_state:
    st.session_state.quiz_correct = None

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Kids Academy")
    st.markdown("---")
    st.markdown(f"👧 **Léa** · Niveau {st.session_state.niveau}")
    st.progress(st.session_state.xp / 1000)
    st.markdown(f"<span class='xp-label'>{st.session_state.xp} / 1000 XP</span>", unsafe_allow_html=True)
    st.markdown("🔥 **7 jours de suite !**")
    st.markdown("---")

    module = st.radio("Navigation", [
        "🏠 Accueil",
        "🧠 Pilier 1&2 — Quiz IA",
        "💻 Pilier 3 — Coding",
        "💜 Pilier 4 — Émotion",
        "🕺 Pilier 5 — Mouvement",
        "📊 Dashboard Parent"
    ])

    st.markdown("---")
    st.markdown("""
    **YakData Engineering**
    *AI Kids Academy — Prototype Streamlit*
    [yakdata.fr](https://yakdata.fr)
    """)

# ── ACCUEIL ─────────────────────────────────────────────────────
if module == "🏠 Accueil":
    st.markdown("# 🤖 AI Kids Academy")
    st.markdown("#### Apprendre l'IA par le jeu, les émotions et le mouvement")
    st.divider()

    cols = st.columns(5)
    piliers = [
        ("🧠", "Adaptatif", "#F96167", 65),
        ("🎮", "Jeux & Puzzles", "#F9C74F", 45),
        ("💻", "Coding", "#1565C0", 35),
        ("💜", "Émotion", "#6A1B9A", 50),
        ("🕺", "Mouvement", "#0F6E56", 78),
    ]
    for col, (ico, nom, color, pct) in zip(cols, piliers):
        with col:
            st.markdown(f"<div class='pillar-box'><div style='font-size:28px'>{ico}</div><div style='font-weight:700;color:#2F3C7E'>{nom}</div></div>", unsafe_allow_html=True)
            st.progress(pct / 100, text=f"{pct}%")

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions cette semaine", "7", "+2")
    with col2:
        st.metric("Taux de réussite", "84%", "+5%")
    with col3:
        st.metric("Temps d'apprentissage", "3h12", "+28min")

    st.divider()
    st.markdown("### 📖 Conte IA du jour")
    with st.expander("Le robot qui apprenait à ressentir ✨"):
        st.markdown("""
        *Il était une fois Tibo, un petit robot qui ne comprenait pas pourquoi les humains pleuraient parfois en souriant.
        Un jour, il rencontra Léa qui lui expliqua que les émotions sont comme des algorithmes complexes —
        même les machines essaient de les apprendre...*

        *(Conte généré par IA selon ton émotion du jour — Pilier 4)*
        """)

# ── QUIZ ─────────────────────────────────────────────────────────
elif module == "🧠 Pilier 1&2 — Quiz IA":
    st.markdown("# 🧠 Quiz adaptatif IA")
    st.markdown("**Pilier 1** — Apprentissage adaptatif &nbsp;|&nbsp; **Pilier 2** — Jeux & puzzles IA")
    st.divider()

    # Progress
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.progress(0.8, text="Question 4 / 5")
    with col2:
        st.markdown("⭐ **Intermédiaire**")
    with col3:
        st.markdown(f"**{st.session_state.xp} XP**")

    st.markdown("### 🎮 Situation réelle — Reconnais l'IA autour de toi")
    st.info("Quand Spotify te propose « Découvertes de la semaine », quelle technologie IA utilise-t-il ?")

    if not st.session_state.quiz_answered:
        options = {
            "A": "Un algorithme de recommandation basé sur tes écoutes",
            "B": "Un humain qui choisit pour toi",
            "C": "Le hasard total",
            "D": "Il copie les choix de tes amis uniquement"
        }
        choix = st.radio("Choisis ta réponse :", list(options.values()), index=None)

        if st.button("✅ Valider ma réponse", type="primary", use_container_width=True):
            if choix == options["A"]:
                st.session_state.quiz_correct = True
                st.session_state.xp += 50
            else:
                st.session_state.quiz_correct = False
            st.session_state.quiz_answered = True
            st.rerun()
    else:
        if st.session_state.quiz_correct:
            st.success("🏅 Excellent ! +50 XP débloqués !")
            st.balloons()
        else:
            st.error("❌ Pas tout à fait — la bonne réponse était A !")

        with st.expander("🤖 Tibo t'explique — Recommandation par similarité"):
            st.markdown("""
            Spotify utilise un **algorithme de recommandation collaborative** :
            - Il analyse **tes écoutes** et les compare à des millions d'autres utilisateurs similaires
            - Il prédit ce que tu vas aimer grâce au **Machine Learning**
            - C'est le cœur du **Pilier 1 d'AI Kids Academy** !
            """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️ Question suivante", type="primary", use_container_width=True):
                st.session_state.quiz_answered = False
                st.session_state.quiz_correct = None
                st.rerun()
        with col2:
            if st.button("🔄 Recommencer", use_container_width=True):
                st.session_state.quiz_answered = False
                st.session_state.quiz_correct = None
                st.rerun()

# ── CODING ────────────────────────────────────────────────────────
elif module == "💻 Pilier 3 — Coding":
    st.markdown("# 💻 A code a day — to learn & play")
    st.markdown("**Pilier 3** — Coding & visualisation IA · Jour 12 · Python débutant")
    st.divider()

    st.info("🎯 **Défi du jour** — Crée un classificateur qui devine si c'est un chien ou un chat !")

    code = '''# Mon premier classificateur IA
def ia_reconnait(taille, aboie):
    """L'IA apprend des règles depuis les données"""
    if taille > 50 and aboie:
        return "🐕 Chien — confiance 95%"
    elif taille < 30 and not aboie:
        return "🐈 Chat — confiance 88%"
    else:
        return "🤔 Incertain — besoin de plus de données !"

# Tests de notre IA
print(ia_reconnait(60, True))
print(ia_reconnait(25, False))
print(ia_reconnait(40, True))'''

    st.code(code, language="python")

    st.markdown("### 🎮 Teste ton IA en direct !")
    col1, col2 = st.columns(2)
    with col1:
        taille = st.slider("Taille de l'animal (cm)", 5, 100, 40)
    with col2:
        aboie = st.toggle("L'animal aboie ?")

    def ia_reconnait(taille, aboie):
        if taille > 50 and aboie:
            return "🐕 Chien — confiance 95%"
        elif taille < 30 and not aboie:
            return "🐈 Chat — confiance 88%"
        else:
            return "🤔 Incertain — besoin de plus de données !"

    if st.button("▶️ Lancer mon IA", type="primary", use_container_width=True):
        with st.spinner("L'IA analyse..."):
            time.sleep(0.8)
        result = ia_reconnait(taille, aboie)
        st.success(f"**Résultat :** {result}")
        st.session_state.xp += 30
        st.info("✅ Tu viens de créer un **classificateur supervisé** — c'est exactement ce qu'utilisent Google Photos et FaceID !")

    st.divider()
    st.markdown("### 📋 Cheat Sheet IA interactive")
    glossaire = {
        "Classification": "Trier des données en catégories (chien/chat, spam/non-spam)",
        "Features": "Les infos que l'IA analyse (taille, aboie, couleur...)",
        "Label": "La réponse attendue (chien ou chat)",
        "Confidence": "Certitude de l'IA sur sa réponse (95% = très sûre)",
        "Algorithme": "Suite d'instructions que l'IA suit pour prendre une décision",
        "Machine Learning": "L'IA qui apprend automatiquement depuis des exemples"
    }
    for terme, definition in glossaire.items():
        with st.expander(f"**{terme}**"):
            st.write(definition)

# ── EMOTION ─────────────────────────────────────────────────────
elif module == "💜 Pilier 4 — Émotion":
    st.markdown("# 💜 Émotion & bien-être")
    st.markdown("**Pilier 4** — Analyse de sentiment en temps réel · Cartes positives · Contes IA génératifs")
    st.divider()

    st.markdown("### Dis-le à Tibo l'IA 👇")

    emotions = {
        "😄 Super": ("82%", "#2e7d32", "Tu es en pleine forme ! L'IA active le mode défi bonus.", "⭐", "Tu rayonnes aujourd'hui !",
                     "Tu es plein·e d'énergie ! Tibo t'a préparé un défi plus difficile. Dans ce conte, le robot champion va t'apprendre ses secrets..."),
        "🙂 Bien": ("65%", "#0f6e56", "Parfait pour apprendre ! Session équilibrée.", "💚", "Tu vas bien, c'est l'essentiel !",
                    "Bonne journée pour apprendre ! Tibo a préparé un conte sur comment les robots apprennent à être utiles..."),
        "😐 Moyen": ("42%", "#f57f17", "Session allégée. Exercices courts et fun.", "🌟", "Chaque jour compte !",
                     "Ça arrive d'être entre les deux. Voici Tibo qui cherche son énergie dans une forêt de données magiques..."),
        "😰 Stressé·e": ("22%", "#e53935", "Pause recommandée. Exercice de respiration activé.", "💜", "Tu fais de ton mieux !",
                         "Tibo aussi se sent parfois dépassé par trop d'informations. Il a découvert une technique secrète pour se calmer..."),
        "😴 Fatigué·e": ("18%", "#7b1fa2", "Session ultra-courte. Juste un conte ce soir.", "🌙", "Le repos, c'est aussi apprendre !",
                         "Ce soir, Tibo te raconte une courte histoire douce pour rêver d'IA et te reposer tranquillement..."),
        "😢 Triste": ("14%", "#1565c0", "Mode doux activé. Pas de quiz ce soir.", "🤗", "Tu n'es pas seul·e !",
                      "Tibo était triste un jour, lui aussi. Il a appris que partager ses émotions les rend moins lourdes..."),
        "🤔 Curieux·se": ("76%", "#6a1b9a", "Mode exploration ! Module bonus débloqué.", "🔭", "Ta curiosité est une super-puissance !",
                          "Tu es en mode exploration ! Tibo t'emmène découvrir comment une IA apprend à reconnaître les galaxies..."),
        "🥳 Fier·e": ("91%", "#2e7d32", "Niveau maximum ! Badge confiance débloqué.", "🏆", "Tu mérites ta fierté !",
                      "Les champions ont tous commencé par les bases. Tibo célèbre tes progrès avec un conte sur les robots champions...")
    }

    cols = st.columns(4)
    emos = list(emotions.keys())
    for i, (col, emo) in enumerate(zip(cols * 2, emos)):
        if col.button(emo, use_container_width=True, key=f"emo_{i}"):
            st.session_state.emotion = emo

    if st.session_state.emotion:
        emo = st.session_state.emotion
        fill, color, conseil, carte_ico, carte_msg, conte = emotions[emo]

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Analyse de sentiment en temps réel")
            pct_val = int(fill.replace("%",""))
            st.progress(pct_val / 100)
            st.markdown(f"<div style='color:{color};font-weight:600'>{conseil}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("#### ✨ Carte positive")
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#fff8e1,#fffde7);border-radius:16px;padding:20px;border:1.5px solid #ffe082;text-align:center'>
                <div style='font-size:40px;margin-bottom:8px'>{carte_ico}</div>
                <div style='font-size:16px;font-weight:700;color:#f57f17'>{carte_msg}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 📖 Conte personnalisé — créé par l'IA générative")
        with st.container():
            st.markdown(f"*{conte}*")
            if st.button("🔄 Générer un nouveau conte", use_container_width=True):
                with st.spinner("L'IA génère ton conte..."):
                    time.sleep(1.5)
                st.success("✨ Nouveau conte généré !")

# ── MOVEMENT ─────────────────────────────────────────────────────
elif module == "🕺 Pilier 5 — Mouvement":
    st.markdown("# 🕺 Mouvement & santé")
    st.markdown("**Pilier 5** — Technologie Skeleton · Reconnaissance gestuelle webcam · Pauses actives")
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📷 Zone Skeleton — Reconnaissance gestuelle")
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a1a2e,#2f3c7e);border-radius:16px;height:220px;
        display:flex;flex-direction:column;align-items:center;justify-content:center;color:white'>
            <div style='font-size:64px'>🕺</div>
            <div style='font-size:13px;opacity:.7;margin-top:8px'>Skeleton v2.1 · 33 points corporels</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📷 Activer la webcam Skeleton", type="primary", use_container_width=True):
            with st.spinner("Skeleton IA en cours d'initialisation..."):
                time.sleep(1.5)
            st.success("🟢 Skeleton actif — 33 points détectés ! Reproduis le geste de Tibo !")
            st.progress(0.87, text="Score posture : 87% — Excellent !")

    with col2:
        st.markdown("### 📊 Scores")
        st.metric("Posture", "87%", "+5%")
        st.metric("Gestes réussis", "12", "+3")
        st.metric("Combo", "🔥 5", "+2")
        st.metric("XP Mouvement", "230", "+80")

    st.divider()
    st.markdown("### 🏆 Défi Skeleton du jour")
    defis = [
        ("🙆", "Bras en croix", "Skeleton analyse 33 points du corps", "✅ Réussi"),
        ("🤸", "Étoile de mer", "Écarter bras et jambes", "✅ Réussi"),
        ("🧘", "Position yoga", "Équilibre sur une jambe", "⏳ En cours..."),
        ("💃", "Séquence danse", "4 gestes enchaînés", "🔒 Bloqué"),
    ]
    for ico, nom, desc, statut in defis:
        col1, col2, col3 = st.columns([1, 5, 2])
        with col1:
            st.markdown(f"<div style='font-size:24px'>{ico}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{nom}** — *{desc}*")
        with col3:
            st.markdown(statut)

    st.divider()
    st.warning("⚡ **Pause active !** L'IA détecte que tu es assis·e depuis 25 min. 2 minutes de mouvement = +100 XP !")
    if st.button("🕺 Lancer la pause active", type="primary", use_container_width=True):
        with st.spinner("Pause active lancée ! Lève-toi et suis Tibo..."):
            time.sleep(2)
        st.success("🎉 Pause terminée ! +100 XP · Meilleure concentration garantie !")
        st.session_state.xp += 100
        st.balloons()

# ── PARENT DASHBOARD ─────────────────────────────────────────────
elif module == "📊 Dashboard Parent":
    st.markdown("# 📊 Tableau de bord parent")
    st.markdown("**Suivi de Léa** · Semaine du 18 octobre 2026 · 5 piliers")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessions", "7", "+2 cette semaine")
    col2.metric("Taux de réussite", "84%", "+5%")
    col3.metric("Temps appris", "3h12", "+28min")
    col4.metric("XP totaux", str(st.session_state.xp), f"+{st.session_state.xp - 600}")

    st.divider()
    st.markdown("### 📈 Progression par pilier")

    import pandas as pd
    data = {
        "Pilier": ["🧠 Adaptatif", "🎮 Jeux & Puzzles", "💻 Coding", "💜 Émotion", "🕺 Mouvement"],
        "Progression (%)": [65, 45, 35, 50, 78],
        "Couleur": ["#F96167","#F9C74F","#1565C0","#6A1B9A","#0F6E56"]
    }
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("Pilier")["Progression (%)"])

    st.divider()
    st.markdown("### 🕐 Activités récentes")
    activites = [
        ("🧠", "Quiz adaptatif — Algorithmes", "Aujourd'hui · 12 min · Niveau augmenté ↑", "4/5 ✓"),
        ("🕺", "Skeleton — 3 gestes réussis", "Hier · 18 min · Score posture 87%", "🏅"),
        ("💜", "Émotion 😄 · Conte IA créé", "Hier · Carte positive débloquée", "✓"),
        ("💻", "Code jour 12 — Classificateur IA", "28 sept. · Cheat sheet consultée 3×", "✓"),
    ]
    for ico, titre, detail, score in activites:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.markdown(f"**{ico}**")
        with col2:
            st.markdown(f"**{titre}**  \n*{detail}*")
        with col3:
            st.markdown(f"**{score}**")
        st.divider()

    st.markdown("### 🤖 Analyse IA personnalisée")
    st.info("""
    **Léa** progresse très vite sur les **Piliers 1 et 5** (+2 niveaux cette semaine).
    Son bien-être émotionnel est excellent (78% d'humeurs positives, cartes positives débloquées).

    **Recommandation :** encourager le **Pilier 3 Coding** — encore en retard.
    L'IA adaptatif a augmenté la difficulté du Quiz automatiquement.
    """)

    st.warning("⚡ **Alerte bien-être** : Léa a montré des signes de fatigue jeudi (émotion 😴 détectée). La session a été automatiquement raccourcie à 10 min.")
