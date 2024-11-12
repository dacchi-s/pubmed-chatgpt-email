# PubMed Article Summarizer

This Python script retrieves the latest articles from PubMed based on specified search queries, summarizes them using the OpenAI API, and sends the summaries via email.
## Features


- **Automated PubMed Searches**: Fetches recent articles from PubMed using user-defined search terms.
- **AI Summaries**: Utilizes OpenAI’s API to generate concise summaries of each article.
- **Email Notifications**: Sends the summaries to specified email addresses.

## Requirements

- Raspberry Pi (or other server)
- Python 3.x
- OpenAI API Key
- Access to an SMTP server for sending emails

## Installation

1. **Set up Python Environment**:
    ```bash
    python -V
    python3 -m venv project_env
    source project_env/bin/activate
    ```

2. **Install Required Libraries**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up OpenAI API Key**: Create an OpenAI account and get your API key.

Please refer to the following URL:
https://platform.openai.com/docs/quickstart

## Usage

### Environment Variable Configuration

Create a .env file with the following content:
```
OPENAI_API_KEY=your_openai_api_key
SMTP_SERVER=smtp.your-email-provider.com
SMTP_PORT=587
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_email_password
SENDER_EMAIL=your_email@example.com
RECIPIENT_EMAIL=recipient_email@example.com
CC_EMAIL=cc_email@example.com  # Optional
BCC_EMAIL=bcc_email@example.com  # Optional
PUBMED_QUERIES=search_term1,search_term2,search_term3
```

### Crontab Configuration
```
crontab -e
```

add a following line:
```
0 7 * * * /home/user/hoge/venv/bin/python /home/user/fuga/huge/Pubmed_ChatGPI_mail_multiple_keywords.py
```

This will cause the script to run every morning at 7:00 AM.
