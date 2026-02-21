# Faculty Ontology Explorer

A web application to query the Faculty Management Ontology using RDFLib and Flask.

## Project Structure

```
faculty_app/
├── app.py                  # Flask backend with RDFLib
├── requirements.txt        # Python dependencies
├── Faculty_Ontology.ttl # Your ontology file (place here)
└── static/
    └── index.html          # Frontend UI
```

## Setup Instructions

### 1. Place your ontology file

Copy `Faculty_Ontology.ttl` into the `faculty_app/` folder.

### 2. Create a virtual environment

```bash
cd faculty_app
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn app:asgi_app --reload --port 8000
```

### 5. Open in browser

Visit: http://localhost:8000

## Features

- 20 predefined competency questions in the sidebar
- Click any question to run its SPARQL query instantly
- Results tab shows data in a formatted table
- SPARQL tab shows the query that was run
- Custom Query editor for writing your own SPARQL
- Live ontology statistics in the header (triples, courses, programs, etc.)
