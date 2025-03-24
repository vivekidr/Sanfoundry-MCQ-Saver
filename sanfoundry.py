import os
import cloudscraper
from xhtml2pdf import pisa
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import tqdm
from utils.sanCleaner import Cleaner

# Load URLs from CSV
df = pd.read_csv('/content/links.csv')
url_list = df['Link'].tolist()

# Create directory if not exists
def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Convert HTML to PDF
def convert_html_to_pdf(source_html, output_filename, source_url):
    with open(output_filename, "w+b") as result_file:
        html_with_source = f"<p>Source: {source_url}</p>\n{source_html}"
        pisa.CreatePDF(html_with_source, dest=result_file)

# Scrape and save as individual PDF
def scrape(url, save_path):
    with cloudscraper.CloudScraper() as s:
        r = s.get(url)
        soup = bs(r.content, "html5lib")
        html, mathjax = Cleaner().clean(soup)

        # Extract topic name from URL
        filename = url.rstrip("/").split("/")[-1]
        pdf_filename = os.path.join(save_path, f"{filename}.pdf")

        check_dir(save_path)
        convert_html_to_pdf(html, pdf_filename, url)

# Main Execution
if __name__ == '__main__':
    SAVE_PATH = "SanfoundryFiles/"

    for url in tqdm(url_list, desc="Saving MCQs"):
        scrape(url, SAVE_PATH)

    print("All PDFs saved successfully (without merging).")
