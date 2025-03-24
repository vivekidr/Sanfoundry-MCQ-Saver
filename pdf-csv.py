import pdfplumber
import csv
import os
import re
import pandas as pd

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def parse_mcqs(text):
    """Parses MCQs from extracted text and returns a structured list."""
    questions = []
    question_pattern = re.compile(r"^\s*(\d+)\.\s*(.*)")  # Matches "1. Question text"
    choice_pattern = re.compile(r"^\s*([a-d])\)\s*(.*)")  # Matches "a) Option"
    answer_pattern = re.compile(r"^Answer:\s*(.*)", re.IGNORECASE)  # Matches "Answer: c"

    current_question = None
    current_choices = {"a": "", "b": "", "c": "", "d": ""}
    current_answer = None

    lines = text.split("\n")
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Check if the line starts a new question
        q_match = question_pattern.match(line)
        if q_match:
            if current_question:
                questions.append([
                    current_question.strip(),
                    current_choices.get("a", "").strip(),
                    current_choices.get("b", "").strip(),
                    current_choices.get("c", "").strip(),
                    current_choices.get("d", "").strip(),
                    current_answer
                ])
            current_question = q_match.group(2)  # Extract question text
            current_choices = {"a": "", "b": "", "c": "", "d": ""}
            current_answer = None
            continue

        # Check if the line is an answer
        a_match = answer_pattern.match(line)
        if a_match:
            current_answer = a_match.group(1).strip()
            continue

        # Check if the line is a choice
        c_match = choice_pattern.match(line)
        if c_match:
            letter = c_match.group(1).lower()
            current_choices[letter] = c_match.group(2).strip()
            continue

        # If it's additional text for the current question, append it
        if current_question:
            current_question += " " + line

    # Save the last question
    if current_question:
        questions.append([
            current_question.strip(),
            current_choices.get("a", "").strip(),
            current_choices.get("b", "").strip(),
            current_choices.get("c", "").strip(),
            current_choices.get("d", "").strip(),
            current_answer
        ])

    return questions

def save_to_csv(data, csv_path, topic_name):
    """Saves the extracted MCQs to a CSV file."""
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Topic", "Question", "Option A", "Option B", "Option C", "Option D", "Answer"])
        for row in data:
            writer.writerow([topic_name] + row)

def process_all_pdfs(pdf_folder, output_folder):
    """Processes each PDF file separately and saves topic-wise CSVs."""
    check_dir(output_folder)

    all_data = []

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            topic_name = os.path.splitext(pdf_file)[0]
            csv_path = os.path.join(output_folder, f"{topic_name}.csv")

            print(f"Extracting text from: {pdf_file}")
            text = extract_text_from_pdf(pdf_path)

            if not text.strip():
                print(f"No text extracted from {pdf_file}. Skipping.")
                continue

            print(f"Parsing questions from {pdf_file}...")
            questions = parse_mcqs(text)

            if not questions:
                print(f"No questions found in {pdf_file}. Skipping.")
                continue

            print(f"Saving data to CSV: {csv_path}")
            save_to_csv(questions, csv_path, topic_name)

            # Append to combined data
            for row in questions:
                all_data.append([topic_name] + row)

    # Save combined CSV
    combined_csv_path = os.path.join(output_folder, "all_topics.csv")
    print(f"Saving all topics data to: {combined_csv_path}")
    pd.DataFrame(all_data, columns=["Topic", "Question", "Option A", "Option B", "Option C", "Option D", "Answer"]).to_csv(combined_csv_path, index=False)

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    PDF_FOLDER = "SanfoundryFiles/"
    OUTPUT_FOLDER = "Processed_CSVs/"
    
    process_all_pdfs(PDF_FOLDER, OUTPUT_FOLDER)
    print("Processing completed successfully!")
