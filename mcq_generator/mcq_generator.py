import os
import json
from dotenv import load_dotenv
from operator import itemgetter
from mcq_generator.utils import read_file, get_table_data
from mcq_generator.logger import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from langchain_core.runnables import RunnablePassthrough, RunnableAssign
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

google_api_key = os.getenv("GEMINI_API_KEY")
if not google_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    google_api_key=google_api_key,
    temperature=0.3,
    model_kwargs={"response_format": {"type": "json_object"}},
)

quiz_generation_template = """
You are an expert MCQ maker. You will be given a text and your job is to create a quiz of {number} multiple-choice questions for {subject} students.
The questions should be in a {tone} tone.

**Instructions:**
1.  Create exactly {number} multiple-choice questions from the provided text.
2.  Ensure questions are diverse and not repetitive.
3.  Each question must have one correct answer.
4.  Format your entire output as a single JSON object.

**Source Text:**
{text}

**Required JSON Format:**
{response_json}
"""

# Second, we use the ChatPromptTemplate class to turn our string blueprint into a usable LangChain prompt object.
# THIS IS THE LINE THAT WAS MISSING FROM THE PREVIOUS SNIPPET.
quiz_generation_prompt = ChatPromptTemplate.from_template(quiz_generation_template)

# --- 2. QUIZ EVALUATION PROMPT ---
# Template for evaluating the generated quiz
quiz_evaluation_template = """
You are an expert English grammarian and writer. Your task is to evaluate a multiple-choice quiz intended for {subject} students.
Analyze the quiz's complexity, clarity, and grammatical correctness.

Provide a concise analysis (max 50 words) on whether the quiz is suitable for the students' cognitive and analytical abilities.

**Quiz to Evaluate:**
```json
{quiz}
""" 
quiz_evaluation_prompt = ChatPromptTemplate.from_template(quiz_evaluation_template)

quiz_chain = quiz_generation_prompt | llm | JsonOutputParser()

review_chain = quiz_evaluation_prompt | llm | StrOutputParser()

format_review_input = {
    "subject": itemgetter("subject"),
    "quiz": lambda x: json.dumps(x["quiz"], indent=2)
}

generate_evaluate_chain = (
    RunnablePassthrough.assign(quiz=quiz_chain)
    | RunnableAssign(
        {"review": format_review_input | review_chain}
    )
)

if __name__ == "__main__":
    logging.info("Running mcq_generator.py directly for testing.")
# The input text for the quiz

    json_format_example = json.dumps(
        {
            "1": {
                "mcq": "Question text here",
                "options": {"a": "Option A", "b": "Option B", "c": "Option C", "d": "Option D"},
                "correct": "c"
            }
        },
        indent=4
    )

    # Define example input text
    source_text = """The mitochondria is often called the powerhouse of the cell because its 
    main job is to generate most of the cell's supply of adenosine triphosphate (ATP), used as a sourc
    e of chemical energy. Unlike plant cells, animal cells do not have a cell wall."""
    # The input dictionary for the chain
    chain_input = {
        "text": source_text,
        "number": 2,
        "subject": "High School Biology",
        "tone": "engaging and clear",
        "response_json": json_format_example
    }

    logging.info("Invoking the full chain for a test run.")
    # Invoke the full chain with the test data
    response = generate_evaluate_chain.invoke(chain_input)
    logging.info("Test run complete.")

    # Print the results
    print("\n------ GENERATED QUIZ (JSON) ------")
    print(response.get("quiz"))

    print("\n------ QUIZ REVIEW ------")
    print(response.get("review"))