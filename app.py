# app.py

import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- Corrected Imports from your custom modules ---
# Ensure your package folder is named 'mcqgenerator'
from mcqgenerator.utils import read_file, get_table_data
from mcqgenerator.mcq_generator import generate_evaluate_chain
from mcqgenerator.logger import logging

# --- Main Application Logic ---

# Load the JSON file that provides the desired response format to the LLM
try:
    with open('response_format_template.json', 'r') as file:
        RESPONSE_JSON_TEMPLATE = json.load(file)
except FileNotFoundError:
    st.error("Error: 'response_format_template.json' not found. Please ensure the file exists in the root directory.")
    st.stop() # Stop the app if the template is missing

# Create a title for the app
st.set_page_config(page_title="MCQ Generator with Gemini", layout="wide")
st.title("📝 MCQ Generator with Google Gemini")
st.markdown("Generate Multiple-Choice Quizzes from your documents using LangChain and Gemini 1.5 Flash.")

# Create a form using st.form for better input handling
with st.form("user_inputs_form"):
    # File Uploader
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=['pdf', 'txt'])

    # Input Fields for Quiz parameters
    col1, col2 = st.columns(2)
    with col1:
        mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=20, value=5)
    with col2:
        subject = st.text_input("Subject", max_chars=50, placeholder="e.g., Biology, History")

    # Quiz Tone
    tone = st.text_input("Tone of Questions", max_chars=50, placeholder="e.g., Simple, Challenging, Technical")

    # Submit Button for the form
    button = st.form_submit_button("✨ Generate MCQs")

    # Check if the button is clicked and all fields have input
    if button and uploaded_file is not None and mcq_count and subject and tone:
        # Use st.session_state to hold the response, preventing re-runs on UI interaction
        with st.spinner("Generating your quiz... This may take a moment."):
            try:
                text = read_file(uploaded_file)
                
                # *** KEY CHANGE: REMOVED get_openai_callback ***
                # The get_openai_callback is specific to OpenAI models and will not work with Gemini.
                # Cost and token tracking for Gemini is handled differently, usually through the Google Cloud Console.
                
                # Prepare the input dictionary for the LCEL chain
                chain_input = {
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON_TEMPLATE)
                }

                # Invoke the refactored LCEL chain
                response = generate_evaluate_chain.invoke(chain_input)
                
                # Store the successful response in the session state
                st.session_state.response = response

            except Exception as e:
                # Log the full error for debugging
                tb_str = traceback.format_exception(type(e), e, e.__traceback__)
                logging.error("".join(tb_str))
                # Display a user-friendly error message
                st.error(f"An error occurred: {e}. Please check the logs for details.")
                st.session_state.response = None # Clear previous results on error

# Display results only if they exist in the session state
if 'response' in st.session_state and st.session_state.response:
    response = st.session_state.response
    
    st.success("Quiz generated successfully!")

    # Extract the quiz data from the response dictionary
    quiz_str = response.get("quiz")
    review_str = response.get("review")
# In app.py

# ... (inside the 'if 'response' in st.session_state' block)
    if quiz_str:
        table_data = get_table_data(quiz_str)
        if table_data:
            # This part works if the JSON is good
            st.subheader("Generated Multiple-Choice Quiz")
            df = pd.DataFrame(table_data)
            df.index = df.index + 1
            st.table(df)
            if review_str:
                st.subheader("Quiz Review & Analysis")
                st.info(review_str)
        else:
            # This part runs when the JSON is bad
            st.error("Failed to parse the generated quiz. The LLM might have returned a malformed JSON.")
            # ADD THIS LINE TO SEE THE RAW OUTPUT:
            st.code(quiz_str) 
    else:
        st.error("The model did not return a quiz. Please try again.")



