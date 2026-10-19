
import streamlit as st
from pypdf import PdfReader
from io import BytesIO

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
            else:
                st.warning(
                    "No selectable text was found. "
                    "This may be a scanned PDF requiring OCR."
                )

    except Exception as error:
        st.error(f"Could not read this PDF: {error}")
