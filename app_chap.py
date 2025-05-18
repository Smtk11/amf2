# Extrait de la structure principale, modifiée pour inclure un "mode examen"
import streamlit as st
import pandas as pd
from datetime import datetime

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
