from openai import OpenAI
import os
import requests
import xmltodict
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Email settings
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
CC_EMAIL = os.getenv("CC_EMAIL", "")  # Email addresses for CC (multiple addresses can be specified, separated by commas)
BCC_EMAIL = os.getenv("BCC_EMAIL", "")  # Email addresses for BCC (multiple addresses can be specified, separated by commas)

# PubMed search settings
PUBMED_QUERIES = os.getenv("PUBMED_QUERIES").split(',')

PUBMED_PUBTYPES = [
    "Journal Article",
    "Books and Documents",
    "Clinical Trial",
    "Meta-Analysis",
    "Randomized Controlled Trial",
    "Review",
    "Systematic Review",
]
PUBMED_TERM = 1

PROMPT_PREFIX = (
    "You are a highly educated and trained researcher. Please explain the following paper in Japanese, separating the title and summary with line breaks. Be sure to write the main points in bullet-point format."
)

def main():
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    today = datetime.now()
    yesterday = today - timedelta(days=PUBMED_TERM)

    for query in PUBMED_QUERIES:
        while True:
            try:
                ids = get_paper_ids_on(yesterday, query)
                print(f"Number of paper IDs for {query}: {len(ids)}")
                output = ""
                paper_count = 0
                for i, id in enumerate(ids):
                    summary = get_paper_summary_by_id(id)
                    pubtype_check_result = check_pubtype(summary["pubtype"])
                    print(f"Pubtype for ID {id}: {summary['pubtype']}, Check result: {pubtype_check_result}")
                    if not pubtype_check_result:
                        continue
                    paper_count += 1
                    abstract = get_paper_abstract_by_id(id)
                    print(f"Title for ID {id}: {summary['title']}")
                    print(f"Abstract for ID {id}: {abstract}\n")
                    input_text = f"\ntitle: {summary['title']}\nabstract: {abstract}"

                    response = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": PROMPT_PREFIX + "\n" + input_text,
                            },
                        ],
                        model="gpt-4o-mini",  # or specify the correct model name available, such as "gpt-4"
                    )
                    
                    content = response.choices[0].message.content.strip()
                    
                    pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{id}"
                    output += f"Notification of new PubMed papers ({query})\n\n{content}\n\n{pubmed_url}\n\n\n"

                if output:
                    send_email(query, output, to_yyyymmdd(yesterday))
                else:
                    print(f"No new papers for query: {query}")

                break
                
            except openai.RateLimitError as e:
                print("Rate limit exceeded. Waiting for 300 seconds before retrying.")
                time.sleep(300)
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(60)

def to_yyyymmdd(date):
    return date.strftime("%Y/%m/%d")

def get_paper_ids_on(date, query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&sort=pub_date&term={query}&mindate={to_yyyymmdd(date)}&maxdate={to_yyyymmdd(date)}&retmax=1000&retstart=0"
    res = requests.get(url).json()
    return res["esearchresult"]["idlist"]

def get_paper_summary_by_id(id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={id}"
    res = requests.get(url).json()
    return res["result"][id]

def get_paper_abstract_by_id(id):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={id}"
    res = requests.get(url).text
    xml_dict = xmltodict.parse(res)
    abstract = xml_dict["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", "")
    return abstract if abstract else ""

def check_pubtype(pubtypes):
    return any(pubtype in PUBMED_PUBTYPES for pubtype in pubtypes)

def send_email(query, content, search_date):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Notification of new papers ({query}) - Search date: {search_date}'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    if CC_EMAIL:
        msg['Cc'] = CC_EMAIL
    
    # BCC is not included in the message header

    # Prepare plain text content
    text = content

    # Prepare HTML content
    html = content.replace('\n', '<br>')
    html = f'<html><body>{html}</body></html>'

    # Attach both plain text and HTML versions
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            recipients = [RECIPIENT_EMAIL]
            if CC_EMAIL:
                recipients.extend(CC_EMAIL.split(','))
            if BCC_EMAIL:
                recipients.extend(BCC_EMAIL.split(','))
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        print(f"Email sent for query: {query}")
    except Exception as e:
        print(f"Failed to send email for query {query}. Error: {e}")

if __name__ == "__main__":
    main()