import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Examen AMF par thème", layout="wide")

df = pd.read_csv("questions_amf_structure.csv")

# 🎯 Interface de filtrage
st.sidebar.title("🧠 Paramètres du test")

# Dictionnaire des chapitres
chapitres_dict = {
    "1": "1. Cadre institutionnel et réglementaire français, européen et international",
    "2": "2. Déontologie, conformité et organisation déontologique des établissements",
    "3": "3. Sécurité financière : lutte contre le blanchiment, le terrorisme et la corruption, embargos",
    "4": "4. Réglementation « Abus de marché»",
    "5": "5. Commercialisation d'instruments financiers, démarchage, vente à distance et conseil du client",
    "6": "6. Relation client",
    "7": "7. Instruments financiers, cryptoactifs et leurs risques",
    "8": "8. Gestion collective/Gestion pour comptes de tiers",
    "9": "9. Fonctionnement et organisation des marchés",
    "10": "10. Postmarché",
    "11": "11. Émissions et opérations sur titres",
    "12": "12. Bases comptables et financières"
}

themes_disponibles = sorted(df["theme"].dropna().astype(str).unique())
theme_options = [chapitres_dict.get(ch, ch) for ch in themes_disponibles]
selected_labels = st.sidebar.multiselect("Choisissez le(s) chapitre(s) :", options=theme_options)
label_to_id = {v: k for k, v in chapitres_dict.items()}
selected_themes = [label_to_id[label] for label in selected_labels if label in label_to_id]

if selected_themes:
    sous_themes = df[df["theme"].astype(str).isin(selected_themes)]["sous_theme"].dropna().unique()
    selected_sous_themes = st.sidebar.multiselect("Sous-thèmes (optionnel) :", sorted(sous_themes.astype(str)))
else:
    selected_sous_themes = []

types = df["categorie"].dropna().unique()
selected_types = st.sidebar.multiselect("Type de question :", types, default=types)
nb_questions = st.sidebar.number_input("Nombre de questions à tirer :", min_value=1, max_value=100, value=10)

filtered = df[
    df["theme"].astype(str).isin(selected_themes) &
    df["categorie"].isin(selected_types)
]

if selected_sous_themes:
    filtered = filtered[filtered["sous_theme"].astype(str).isin(selected_sous_themes)]

# Lancer le test
if st.sidebar.button("🚀 Lancer le test") and not filtered.empty:
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.choices = [None] * nb_questions
    st.session_state.feedback = [None] * nb_questions
    st.session_state.validated = [False] * nb_questions
    st.session_state.start_time = datetime.now()
    st.session_state.questions = filtered.sample(min(nb_questions, len(filtered))).reset_index(drop=True)

# Affichage des questions
if "questions" in st.session_state and st.session_state.step < len(st.session_state.questions):
    i = st.session_state.step
    row = st.session_state.questions.iloc[i]

    now = datetime.now()
    elapsed = now - st.session_state.start_time
    minutes = elapsed.seconds // 60
    seconds = elapsed.seconds % 60
    st.markdown(f"⏱️ Temps écoulé : **{minutes} min {seconds:02d} sec**")
    st.markdown(f"### 📝 Question {i+1} / {len(st.session_state.questions)}")

    st.markdown(f"<div style='background-color:#e6f4fa;padding:20px;border-radius:10px;border:1px solid #cce'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:14px;color:#666'>Chapitre {row['theme']} – Sous-thème {row['sous_theme']} – Type {row['categorie']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:20px;font-weight:bold'>{row['question']}</div>", unsafe_allow_html=True)

    choix = st.radio(
        "Choisissez votre réponse :",
        options=["A", "B", "C"],
        format_func=lambda x: f"{x} - {row[f'Choix_{x}']}",
        key=f"radio_{i}"
    )
    st.session_state.choices[i] = choix

    with st.container():
        if st.button("✅ Vérifier", key=f"valider_{i}"):
            if choix == row["bonne_reponse"]:
                st.session_state.feedback[i] = "✅ Bonne réponse !"
            else:
                st.session_state.feedback[i] = f"❌ Mauvaise réponse. La bonne réponse était : {row['bonne_reponse']} - {row[f'Choix_{row['bonne_reponse']}']}"
            st.session_state.validated[i] = True

    if st.session_state.feedback[i]:
        if "✅" in st.session_state.feedback[i]:
            st.success(st.session_state.feedback[i])
        else:
            st.error(st.session_state.feedback[i])
        if isinstance(row["justification"], str) and row["justification"].strip():
            st.info(f"ℹ️ {row['justification']}")

    with st.container():
        if st.button("➡️ Suivante", key=f"next_{i}"):
            if st.session_state.choices[i] == row["bonne_reponse"]:
                st.session_state.score += 1
            st.session_state.step += 1

    st.markdown("</div>", unsafe_allow_html=True)

# Résultat final
if "questions" in st.session_state and st.session_state.step >= len(st.session_state.questions):
    end_time = datetime.now()
    elapsed = end_time - st.session_state.start_time
    minutes = elapsed.seconds // 60
    seconds = elapsed.seconds % 60

    st.header("🎯 Résultat final")
    st.markdown(f"Score : **{st.session_state.score} / {len(st.session_state.questions)}**")
    st.markdown(f"Temps : **{minutes} min {seconds:02d} sec**")

    results = []
    for j, row in st.session_state.questions.iterrows():
        selected = st.session_state.choices[j]
        correct = row["bonne_reponse"]
        is_correct = selected == correct
        results.append({
            "categorie": row["categorie"],
            "sous_theme": row["sous_theme"],
            "question": row["question"],
            "votre réponse": f"{selected} - {row[f'Choix_{selected}']}" if selected else "Aucune",
            "bonne réponse": f"{correct} - {row[f'Choix_{correct}']}",
            "résultat": "✅" if is_correct else "❌"
        })

    st.dataframe(pd.DataFrame(results))

    if st.button("💾 Enregistrer ce score"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score_df = pd.DataFrame([{
            "date": now,
            "score": st.session_state.score,
            "total": len(st.session_state.questions),
            "durée (min:sec)": f"{minutes}:{seconds:02d}"
        }])
        try:
            old = pd.read_csv("scores.csv")
            score_df = pd.concat([old, score_df], ignore_index=True)
        except FileNotFoundError:
            pass
        score_df.to_csv("scores.csv", index=False)
        st.success("Score enregistré avec succès ✅")

    if st.button("📊 Voir mes résultats par type de question"):
        summary_data = []
        for j, row in st.session_state.questions.iterrows():
            selected = st.session_state.choices[j]
            correct = row["bonne_reponse"]
            is_correct = selected == correct
            summary_data.append({
                "categorie": row["categorie"],
                "sous_theme": row["sous_theme"],
                "correct": int(is_correct),
                "total": 1
            })
        df_summary = pd.DataFrame(summary_data)
        df_grouped = df_summary.groupby(["categorie", "sous_theme"]).sum().reset_index()
        df_grouped["score"] = df_grouped["correct"].astype(str) + "/" + df_grouped["total"].astype(str)
        st.markdown("### 🧾 Compte rendu par catégorie et sous-thème")
        st.dataframe(df_grouped[["categorie", "sous_theme", "score"]])

    if st.button("🔁 Refaire un test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

st.set_page_config(page_title="Examen AMF - Mode", layout="wide")

df = pd.read_csv("questions_amf_structure.csv")

# Dictionnaire des chapitres avec noms complets et nombre de questions pour le mode examen
chapitres_exam = {
    "1": ("1. Cadre institutionnel et réglementaire français, européen et international", 14),
    "2": ("2. Déontologie, conformité et organisation déontologique des établissements", 6),
    "3": ("3. Sécurité financière", 3),
    "4": ("4. Réglementation \u00ab Abus de marché\u00bb", 2),
    "5": ("5. Commercialisation d'instruments financiers", 6),
    "6": ("6. Relation client", 25),
    "7": ("7. Instruments financiers et leurs risques", 21),
    "8": ("8. Gestion collective", 25),
    "9": ("9. Fonctionnement des marchés", 7),
    "10": ("10. Postmarché", 3),
    "11": ("11. Émissions et opérations sur titres", 2),
    "12": ("12. Bases comptables et financières", 6)
}

# Choix du mode : examen ou entrainement
mode = st.sidebar.radio("Mode", ["Mode examen", "Mode entraînement"])

if mode == "Mode examen":
    st.title("📝 Mode Examen AMF")
    if st.sidebar.button("🚀 Lancer l'examen complet"):
        # Tirage des questions par chapitre selon répartition
        all_questions = []
        for chap_num, (_, q_count) in chapitres_exam.items():
            questions_chap = df[df["theme"].astype(str) == chap_num]
            if len(questions_chap) >= q_count:
                all_questions.append(questions_chap.sample(q_count))
            else:
                all_questions.append(questions_chap)

        st.session_state.questions = pd.concat(all_questions).sample(frac=1).reset_index(drop=True)
        st.session_state.step = 0
        st.session_state.score = 0
        st.session_state.choices = []
        st.session_state.start_time = datetime.now()

# Affichage question par question (commun)
if "questions" in st.session_state and st.session_state.step < len(st.session_state.questions):
    i = st.session_state.step
    row = st.session_state.questions.iloc[i]

    st.markdown(f"### Question {i+1} / {len(st.session_state.questions)}")
    st.markdown(f"**Chapitre {row['theme']} – {row['sous_theme']}**")
    st.markdown(f"{row['question']}")

    choix = st.radio("Votre réponse :", ["A", "B", "C"], format_func=lambda x: f"{x} - {row[f'Choix_{x}']}", key=f"choix_{i}")

    if st.button("Valider", key=f"valider_{i}"):
        st.session_state.choices.append({
            "question": row["question"],
            "theme": row["theme"],
            "categorie": row["categorie"],
            "sous_theme": row["sous_theme"],
            "selected": choix,
            "correct": row["bonne_reponse"]
        })
        if choix == row["bonne_reponse"]:
            st.session_state.score += 1
        st.session_state.step += 1

# Résultat final et analyse
if "questions" in st.session_state and st.session_state.step >= len(st.session_state.questions):
    st.header("🌟 Résultat de l'examen")
    results_df = pd.DataFrame(st.session_state.choices)
    correct_a = results_df[(results_df["categorie"] == "A") & (results_df["selected"] == results_df["correct"])].shape[0]
    correct_c = results_df[(results_df["categorie"] == "C") & (results_df["selected"] == results_df["correct"])].shape[0]
    total = len(results_df)
    score_pct = round((st.session_state.score / total) * 100, 2)

    st.markdown(f"**Score final : {st.session_state.score} / {total} soit {score_pct}%**")
    st.markdown(f"- 🔹 Bonnes réponses Catégorie A : **{correct_a}**")
    st.markdown(f"- 🔹 Bonnes réponses Catégorie C : **{correct_c}**")

    # Par chapitre
    chap_summary = results_df.copy()
    chap_summary["is_correct"] = chap_summary["selected"] == chap_summary["correct"]
    chap_stat = chap_summary.groupby("theme")["is_correct"].agg(["sum", "count"]).reset_index()
    chap_stat.columns = ["Chapitre", "Bonnes réponses", "Total"]
    chap_stat["Score"] = chap_stat["Bonnes réponses"].astype(str) + "/" + chap_stat["Total"].astype(str)
    st.markdown("### 📊 Score par chapitre")
    st.dataframe(chap_stat[["Chapitre", "Score"]])

    if st.button("🔁 Refaire l'examen"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()
""
