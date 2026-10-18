import streamlit as st

st.set_page_config(
    page_title="AI Study Companion",
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI Study Companion")

st.write(
    "Your personal assistant for learning, "
    "summarising notes, and practising quizzes."
)

name = st.text_input("Enter your name")

if name:
    st.success(f"Welcome, {name}! Let's start learning.")