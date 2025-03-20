import pdfplumber
import csv
import sys
import os
import re

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
                # Save the previous question
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

def save_to_csv(data, csv_path):
    """Saves the extracted MCQs to a CSV file."""
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Option A", "Option B", "Option C", "Option D", "Answer"])
        writer.writerows(data)

def main():
    """Main function to handle CLI input and process the PDF."""
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_csv.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)

    csv_path = os.path.splitext(pdf_path)[0] + ".csv"
    
    print(f"Extracting text from: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)

    if not text.strip():
        print("No text extracted from the PDF. Please check the file.")
        sys.exit(1)
    
    print("Parsing questions...")
    questions = parse_mcqs(text)

    if not questions:
        print("No questions found. Check the PDF format.")
        sys.exit(1)

    print(f"Saving data to CSV: {csv_path}")
    save_to_csv(questions, csv_path)

    print("Conversion completed successfully!")

if __name__ == "__main__":
    main()
