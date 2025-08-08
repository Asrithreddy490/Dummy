import streamlit as st
import json
import os
 
JSON_FILE = "questions_master.json"
 
# ----------------------
# Helper functions
# ----------------------
def load_questions():
    """Load questions from local JSON file."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    return []
 
def save_questions(questions):
    """Save questions to local JSON file."""
    with open(JSON_FILE, "w") as f:
        json.dump(questions, f, indent=4)
 
# ----------------------
# Load existing data
# ----------------------
questions = load_questions()
 
st.title("Survey Table Config Manager")
 
# ----------------------
# Sidebar - View / Select Questions
# ----------------------
st.sidebar.header("Stored Questions")
 
if questions:
    question_options = {f"ID {q['id']} - {q['question_text']}": q['id'] for q in questions}
    selected_label = st.sidebar.selectbox("Select Question", list(question_options.keys()))
    selected_id = question_options[selected_label]
 
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Edit"):
        st.session_state.edit_id = selected_id
    if col2.button("Delete"):
        questions = [q for q in questions if q['id'] != selected_id]
        save_questions(questions)
        st.sidebar.success(f"Deleted question ID {selected_id}")
        st.rerun()
else:
    st.sidebar.write("No questions stored yet.")
 
# ----------------------
# Add/Edit Question Form
# ----------------------
st.header("Add / Edit Question")
 
if "edit_id" in st.session_state:
    # Load question for editing
    q_to_edit = next((q for q in questions if q['id'] == st.session_state.edit_id), None)
    if q_to_edit:
        question_var_default = ",".join(q_to_edit['question_var']) if isinstance(q_to_edit['question_var'], list) else q_to_edit['question_var']
        question_text_default = q_to_edit['question_text']
        base_text_default = q_to_edit['base_text']
        display_structure_default = json.dumps(q_to_edit['display_structure'], indent=4)
        base_filter_default = q_to_edit['base_filter'] if q_to_edit['base_filter'] else ""
        question_type_default = q_to_edit['question_type']
        mean_var_default = q_to_edit['mean_var'] if q_to_edit['mean_var'] else ""
    else:
        st.session_state.pop("edit_id", None)
        st.warning("Question not found for editing.")
        st.stop()
else:
    # Defaults for new entry
    question_var_default = ""
    question_text_default = ""
    base_text_default = "Total Respondents"
    # Default example display_structure
    display_structure_default = json.dumps([
        ["code", "Male", 1],
        ["code", "Female", 2],
        ["net", "All Genders", [1, 2]]
    ], indent=4)
    base_filter_default = ""
    question_type_default = "single"
    mean_var_default = ""
 
with st.form("question_form"):
    question_var = st.text_input("Question Variable (e.g., hGender or S3r1,S3r2)", value=question_var_default)
    question_text = st.text_input("Question Text", value=question_text_default)
    base_text = st.text_input("Base Text", value=base_text_default)
    display_structure_text = st.text_area(
        "Display Structure (JSON list of [type, label, code(s)])",
        value=display_structure_default,
        help="Example:\n"
             "[\n"
             "  [\"code\", \"Very Good\", 1],\n"
             "  [\"code\", \"Good\", 2],\n"
             "  [\"net\", \"Top 2 Box (NET)\", [1, 2]]\n"
             "]"
    )
    base_filter = st.text_input("Base Filter (optional)", value=base_filter_default)
    question_type = st.selectbox("Question Type", ["single", "multi", "open_numeric"], index=["single", "multi", "open_numeric"].index(question_type_default))
    mean_var = st.text_input("Mean Var (optional)", value=mean_var_default)
 
    submitted = st.form_submit_button("Save Question")
 
    if submitted:
        try:
            display_structure = json.loads(display_structure_text)
            # Validate structure: must be a list of lists/tuples with at least 3 elements
            if not isinstance(display_structure, list) or not all(isinstance(item, list) and len(item) >= 3 for item in display_structure):
                raise ValueError
        except Exception:
            st.error("Display Structure must be valid JSON in the format: [[\"code\", \"Label\", 1], [\"net\", \"Label\", [1,2]]]")
            st.stop()
 
        if "edit_id" in st.session_state:
            # Update existing question
            for q in questions:
                if q['id'] == st.session_state.edit_id:
                    q['question_var'] = question_var.split(",") if "," in question_var else question_var
                    q['question_text'] = question_text
                    q['base_text'] = base_text
                    q['display_structure'] = display_structure
                    q['base_filter'] = base_filter if base_filter else None
                    q['question_type'] = question_type
                    q['mean_var'] = mean_var if mean_var else None
                    break
            save_questions(questions)
            st.success(f"Question ID {st.session_state.edit_id} updated!")
            st.session_state.pop("edit_id", None)
        else:
            # Create new question
            new_id = max([q['id'] for q in questions], default=0) + 1
            new_question = {
                "id": new_id,
                "question_var": question_var.split(",") if "," in question_var else question_var,
                "question_text": question_text,
                "base_text": base_text,
                "display_structure": display_structure,
                "base_filter": base_filter if base_filter else None,
                "question_type": question_type,
                "mean_var": mean_var if mean_var else None
            }
            questions.append(new_question)
            save_questions(questions)
            st.success(f"Question saved with ID {new_id}!")
 
st.markdown("### Current Questions in Database")
st.json(questions)
 