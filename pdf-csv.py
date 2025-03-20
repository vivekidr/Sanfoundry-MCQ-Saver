import pdfplumber
import csv
import sys
import os

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def parse_questions(text):
    """Parses text to extract MCQs and structures them into a list."""
    questions = []
    lines = text.split("\n")
    
    question = None
    choices = []
    answer = None

    for line in lines:
        line = line.strip()
        if line.isdigit():  # New question number detected
            if question and choices:  # Save the previous question
                questions.append([question] + choices + [answer])
            question = ""
            choices = []
            answer = None
        elif line.startswith("Answer:"):
            answer = line.replace("Answer:", "").strip()
        elif line.startswith(("a)", "b)", "c)", "d)")):
            choices.append(line)
        else:
            if question is not None:
                question += " " + line

    if question and choices:  # Save the last question
        questions.append([question] + choices + [answer])

    return questions

def save_to_csv(data, csv_path):
    """Saves extracted MCQs to a CSV file."""
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
    
    print("Parsing questions...")
    questions = parse_questions(text)

    print(f"Saving to CSV: {csv_path}")
    save_to_csv(questions, csv_path)
    
    print("Conversion completed successfully!")

if __name__ == "__main__":
    main()
