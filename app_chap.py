
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Examen AMF par thème", layout="wide")

# Chargement de la base
df = pd.read_csv("questions_amf_structuré.csv")

# 🎯 Interface de filtrage
st.sidebar.title("🧠 Paramètres du test")
themes = df["theme"].dropna().unique()
selected_themes = st.sidebar.multiselect("Choisissez le(s) chapitre(s) :", sorted(themes.astype(str)))

# Mise à jour dynamique des sous-thèmes
if selected_themes:
    sous_themes = df[df["theme"].astype(str).isin(selected_themes)]["sous_theme"].dropna().unique()
    selected_sous_themes = st.sidebar.multiselect("Sous-thèmes (optionnel) :", sorted(sous_themes.astype(str)))
else:
    selected_sous_themes = []

# Type de question
types = df["categorie"].dropna().unique()
selected_types = st.sidebar.multiselect("Type de question :", types, default=types)

# Nombre de questions
nb_questions = st.sidebar.number_input("Nombre de questions à tirer :", min_value=1, max_value=100, value=10)

# Filtrage des données
filtered = df[
    df["theme"].astype(str).isin(selected_themes) &
    df["categorie"].isin(selected_types)
]

if selected_sous_themes:
    filtered = filtered[filtered["sous_theme"].astype(str).isin(selected_sous_themes)]

# Lancer le quiz
if st.sidebar.button("🚀 Lancer le test") and not filtered.empty:
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.choices = [None] * nb_questions
    st.session_state.feedback = [None] * nb_questions
    st.session_state.validated = [False] * nb_questions
    st.session_state.start_time = datetime.now()
    st.session_state.questions = filtered.sample(min(nb_questions, len(filtered))).reset_index(drop=True)

# Interface de test
if "questions" in st.session_state and st.session_state.step < len(st.session_state.questions):
    i = st.session_state.step
    row = st.session_state.questions.iloc[i]

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

    col1, col2 = st.columns([1, 1])
    with col1:
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

    with col2:
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
    st.markdown(f"Temps : **{minutes} min {seconds} sec**")

    results = []
    for j, row in st.session_state.questions.iterrows():
        selected = st.session_state.choices[j]
        correct = row["bonne_reponse"]
        is_correct = selected == correct
        results.append({
            "chapitre": row["theme"],
            "sous-thème": row["sous_theme"],
            "question": row["question"],
            "votre réponse": f"{selected} - {row[f'Choix_{selected}']}" if selected else "Aucune",
            "bonne réponse": f"{correct} - {row[f'Choix_{correct}']}",
            "résultat": "✅" if is_correct else "❌"
        })

    st.dataframe(pd.DataFrame(results))

    if st.button("🔁 Refaire un test"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
