# SadakWatch AI

SadakWatch AI is a Streamlit-based road accountability chatbot for India. It helps citizens look up road details, understand public spending, check contractor accountability, and route complaints to the correct road authority.

## Features

- Road lookup by highway, state, district, or road type
- Budget and spending transparency with source document references
- Contractor accountability score and ranking
- Complaint routing with authority, engineer, phone, email, and SLA details
- Complaint logging with generated complaint IDs
- Interactive map view using Folium
- English and Hindi chat suggestions
- Offline rule-based mode when no API key is configured
- Optional online AI response mode using Groq

## Tech Stack

- Python
- Streamlit
- SQLite
- Folium and streamlit-folium
- Groq API for optional LLM responses

## Project Structure

```text
sadakwatch/
|-- app.py                     # Streamlit frontend
|-- requirements.txt           # Python dependencies
|-- .env                       # Local environment variables
|-- database/
|   |-- schema.py              # SQLite table schema
|   |-- seed_data.py           # Demo/sample data seeding
|   |-- db_helpers.py          # Database query helpers
|   `-- sadakwatch.db          # SQLite database
`-- chatbot/
    |-- chatbot.py             # Main chatbot pipeline
    |-- intent_classifier.py   # Intent and entity extraction
    `-- db_query_handler.py    # Intent to database response logic
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create or reset the database if needed.

```bash
python database/schema.py
python database/seed_data.py
```

4. Add the Groq API key for online AI mode.

The app reads the key from the `GROQ_API_KEY` environment variable. You can set it in the terminal before running the app:

```bash
set GROQ_API_KEY=your_groq_api_key_here
```

You can also keep the key in a `.env` file inside the `sadakwatch` folder:

```text
GROQ_API_KEY=your_groq_api_key_here
```

If `.env` is not picked up automatically, use the terminal command above or load the file with `python-dotenv`.

## Run the App

From inside the `sadakwatch` folder, run:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit in your browser.

## How It Works

1. The user asks a road-related question in the Streamlit chat UI.
2. `intent_classifier.py` detects the intent and extracts entities like road name, state, complaint type, or contractor name.
3. `db_query_handler.py` maps the intent to database helper functions.
4. `db_helpers.py` fetches structured road, budget, authority, complaint, or contractor data from SQLite.
5. If `GROQ_API_KEY` is available, `chatbot.py` sends the structured context to Groq for a polished AI response.
6. If no API key is available, the app falls back to offline rule-based responses.

## Example Questions

- Tell me about NH-44
- How much was spent on NH-48 Pune?
- Who should I complain to for SH-18 in MP?
- What is Ashoka Buildcon's accountability score?
- Show all contractors ranked by score

## Important Note About API Key

The project expects the API key in this variable:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do not commit real API keys to GitHub. Keep them only in `.env` or your local environment.

## Current Limitations

- The project uses demo/sample SQLite data.
- Online AI mode depends on a valid Groq API key and internet access.
- Complaint submission is stored locally in SQLite, not sent to a real government portal.
- The current app is a prototype for hackathon/demo use.

## Future Improvements

- Add real government road and complaint portal integrations
- Add user authentication for complaint tracking
- Add photo upload support for road complaints
- Add admin dashboard for authorities
- Improve Hindi and multilingual support
- Deploy the Streamlit app publicly
"# sadakwatch" 
