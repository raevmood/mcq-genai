# mcqgenerator/utils.py

import os
import pypdf # Changed from PyPDF2
import json
import traceback
import logging

def read_file(file):
    """
    Reads the content of a file (PDF or TXT) and returns it as a string.
    """
    filename = file.name
    if filename.endswith(".pdf"):
        try:
            # Use pypdf.PdfReader which is the modern standard
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or "" # Add 'or ""' to handle empty pages
            return text
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}")
            raise Exception("Error reading the PDF file. It might be corrupted or password-protected.")

    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception("Unsupported file format. Only PDF and TXT files are supported.")

# In mcqgenerator/utils.py

# ... (read_file function stays the same) ...

# Change the function signature to reflect it now accepts a dictionary
def get_table_data(quiz_dict: dict): # Changed from quiz_str
    """
    Parses a quiz dictionary and formats it for table display.
    """
    try:
        # REMOVED: quiz_dict = json.loads(quiz_str) -> This is no longer needed!
        
        quiz_table_data = []

        # Iterate over the quiz dictionary and extract the required information
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "N/A")
            options_dict = value.get("options", {})
            
            options = " || ".join(
                [f"{option} -> {option_value}" for option, option_value in options_dict.items()]
            )

            correct = value.get("correct", "N/A")
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    # This error is less likely now, but we'll keep the handler for robustness
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_table_data: {e}")
        traceback.print_exc()
        return False


