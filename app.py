
import os
from io import BytesIO

import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

st.set_page_config(
    page_title="AI Study Companion",
    page_icon="📚",
    layout="centered"
)

st.title("📚 AI Study Companion")
st.write("Upload your study notes and start learning.")

# User name
name = st.text_input("Enter your name")

if name:
    st.success(f"Welcome, {name}!")

st.divider()

# PDF upload
st.header("📄 Upload your study notes")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:
    try:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))

        if reader.is_encrypted:
            st.error("This PDF is password-protected.")
        else:
            extracted_pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]

            extracted_text = "\n\n".join(extracted_pages).strip()

            st.write(f"**Pages:** {len(reader.pages)}")

            if extracted_text:
                st.success("PDF text extracted successfully!")

                with st.expander("View extracted text", expanded=True):
                    st.text_area(
                        "Extracted content",
                        value=extracted_text,
                        height=300
                    )

                st.download_button(
                    "Download extracted text",
                    data=extracted_text,
                    file_name="extracted_notes.txt",
                    mime="text/plain"
                )

                # AI SUMMARY FEATURE
                st.divider()
                st.subheader("✨ AI Summary")

                if st.button("Generate AI Summary"):
                    api_key = os.getenv("GEMINI_API_KEY")

                    if not api_key:
                        st.error("Gemini API key not found in .env")
                    else:
                        try:
                            with st.spinner("Generating your summary..."):
                                client = genai.Client(api_key=api_key)

                                prompt = f"""
                                Summarize these study notes for a student.
                                Use simple language, headings, and bullet points.
                                Highlight important concepts for exam revision.
                                Do not add facts absent from the notes.

                                Notes:
                                {extracted_text[:30000]}
                                """

                                response = client.models.generate_content(
                                    model="gemini-3.5-flash-lite",
                                    contents=prompt
                                )

                            if response.text:
                                st.markdown(response.text)
                            else:
                                st.warning("Gemini returned an empty response.")

                        except Exception as error:
                            st.error(f"AI summary failed: {error}")
            
                # AI-GENERATED MCQ QUIZ
                st.divider()
                st.subheader("📝 Test Your Knowledge")

                if st.button("Generate 10 MCQs"):
                    try:
                        with st.spinner("Creating your quiz..."):
                            client = genai.Client(
                                api_key=os.getenv("GEMINI_API_KEY")
                            )

                            prompt = f"""
                            Create exactly 10 multiple-choice questions
                            based only on the study notes below.

                            Difficulty: mixed (easy, medium, hard).

                            Return ONLY a valid JSON array. Each object
                            must have these keys:
                            question: string
                            options: array of exactly 4 strings
                            answer: integer from 0 to 3, indicating the
                            index of the correct option
                            explanation: string explaining the answer

                            Make the questions educational and avoid
                            repeating the same concept.

                            Notes:
                            {extracted_text[:20000]}
                            """

                            response = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=prompt,
                                config={
                                    "response_mime_type": "application/json"
                                }
                            )

                            import json
                            quiz_data = json.loads(response.text)

                            if not isinstance(quiz_data, list) or len(quiz_data) != 10:
                                raise ValueError(
                                    "Gemini did not return exactly 10 questions. Please try again."
                                )

                            st.session_state.quiz_data = quiz_data
                            st.session_state.quiz_submitted = False
                            st.session_state.quiz_answers = {}

                    except Exception as error:
                        st.error(f"Could not generate quiz: {error}")

                # Display quiz after generation
                if st.session_state.get("quiz_data"):
                    quiz_data = st.session_state.quiz_data

                    with st.form("mcq_quiz_form"):
                        for i, question in enumerate(quiz_data):
                            st.markdown(
                                f"**Q{i + 1}. {question['question']}**"
                            )

                            st.radio(
                                "Choose your answer:",
                                question["options"],
                                key=f"quiz_answer_{i}",
                                index=None
                            )

                        submitted = st.form_submit_button("Submit Quiz")

                    if submitted:
                        score = 0

                        for i, question in enumerate(quiz_data):
                            selected = st.session_state.get(
                                f"quiz_answer_{i}"
                            )

                            if selected is not None:
                                selected_index = question["options"].index(
                                    selected
                                )
                                if selected_index == question["answer"]:
                                    score += 1

                        st.session_state.quiz_score = score
                        st.session_state.quiz_submitted = True

                    if st.session_state.get("quiz_submitted"):
                        score = st.session_state.quiz_score
                        st.success(f"Your score: {score}/10")

                        for i, question in enumerate(quiz_data):
                            selected = st.session_state.get(
                                f"quiz_answer_{i}"
                            )

                            st.markdown(
                                f"**Q{i + 1}. {question['question']}**"
                            )
                            st.write(
                                f"Correct answer: "
                                f"{question['options'][question['answer']]}"
                            )
                            st.caption(question["explanation"])
                

            else:
                st.warning(
                    "No selectable text was found. "
                    "This may be a scanned PDF requiring OCR."
                )

    except Exception as error:
        st.error(f"Could not read this PDF: {error}")
