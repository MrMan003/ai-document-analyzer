# AI Document Analyzer

Automated analysis of Requests for Proposals (RFPs) and tender documents. The system extracts structured information, generates executive summaries, identifies risks, and provides mitigation recommendations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Authentication](#authentication)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Overview

The AI Document Analyzer is a backend service that automates the review of procurement documents. Users upload PDF files, and the system processes them to extract:

- Scope of work
- Timeline and milestones
- Eligibility and qualification criteria
- Executive summary with key points
- Identified risks with severity ratings and mitigation strategies

The system integrates with Azure Active Directory for authentication and uses Large Language Models for natural language understanding.

---

## Features

| Feature | Description |
|---------|-------------|
| Document Upload | PDF upload with file validation and size limits (25 MB) |
| Text Extraction | Extracts text from PDFs, including OCR for scanned documents |
| Scope Extraction | Identifies and extracts the scope of work |
| Timeline Extraction | Extracts key milestones and deadlines |
| Eligibility Analysis | Identifies qualification criteria, flagging mandatory requirements |
| Executive Summary | Generates a concise summary with key bullet points |
| Risk Identification | Detects risks with severity levels and mitigation recommendations |
| Document History | View, reprocess, or delete previous analyses |
| Audit Logging | Tracks user actions for compliance |
| Secure Authentication | Azure AD single sign-on with JWT session tokens |

---

## Architecture

The system follows a RESTful API architecture with asynchronous background processing.

```
+------------------+
|     Client       |
+------------------+
        |
        v
+------------------+
|   FastAPI API    |
|  (REST Endpoints)|
+------------------+
        |
        v
+------------------+
|  Service Layer   |
| (Business Logic) |
+------------------+
        |
        v
+------------------+
|   Database       |
| (SQLite/PostgreSQL)|
+------------------+
```

### Data Flow

1. User uploads a PDF document via the API endpoint.
2. System validates the file and stores it in the file system.
3. Document record is created in the database with status "UPLOADED".
4. System extracts text from the PDF (OCR fallback for scanned documents).
5. Text is sent to the AI analyzer for processing.
6. Structured results are persisted to the database.
7. User retrieves the analysis results via the API.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Python 3.11+, FastAPI | REST API framework |
| ORM | SQLAlchemy | Database abstraction |
| Database | SQLite (development), PostgreSQL (production) | Data persistence |
| Authentication | Azure AD (MSAL) | Identity management |
| AI / LLM | Anthropic Claude | Natural language analysis |
| PDF Processing | PyPDF2, Tesseract OCR | Text extraction |
| Caching | Redis | Performance optimization |
| Testing | Pytest | Unit and integration testing |
| Logging | Python logging, JSON formatter | Structured logging |

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/MrMan003/ai-document-analyzer.git
   cd ai-document-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Mac/Linux
   # venv\Scripts\activate       # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   ANTHROPIC_API_KEY=your-api-key-here
   DATABASE_URL=sqlite:///./app.db
   SECRET_KEY=your-secret-key
   ```

5. Create the database:
   ```bash
   python -c "
   from app.core.database import engine, Base
   from app.models import *
   Base.metadata.create_all(bind=engine)
   print('Database created successfully')
   "
   ```

6. Start the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

---

## API Usage

### Upload a Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.pdf"
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "status": "PROCESSING"
}
```

### Retrieve Analysis Results

```bash
curl http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "document": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "document.pdf",
    "status": "EXTRACTED"
  },
  "summary": {
    "executive_summary": "This RFP seeks a vendor to provide...",
    "key_points": [
      "Project requires experienced team",
      "Timeline is 3 months",
      "Budget is fixed"
    ]
  },
  "risks": [
    {
      "title": "Tight Timeline",
      "severity": "HIGH",
      "description": "The timeline is aggressive and may impact quality",
      "recommendation": "Negotiate for extended timeline"
    }
  ]
}
```

### List Documents

```bash
curl http://localhost:8000/documents
```

### Reprocess a Document

```bash
curl -X POST http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000/reprocess
```

### Delete a Document

```bash
curl -X DELETE http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

---

## Authentication

The system uses Azure Active Directory (Microsoft Entra ID) for authentication.

### Login Flow

1. Client redirects user to `/auth/login`
2. User is redirected to Microsoft login page
3. After successful authentication, Microsoft redirects back with an authorization code
4. System exchanges the code for user profile information
5. A JWT session token is issued
6. Client includes the token in the `Authorization` header for subsequent requests

### Testing Without Azure AD

During development, the system supports a mock user mode. The default implementation uses a test user ID `test-user-123` when authentication is disabled.

---

## Testing

Run the test suite:

```bash
pytest -v
```

Test coverage includes:
- Database models
- API endpoints
- Authentication flow
- Document processing
- AI analysis (mock mode)

---

## Project Structure

```
ai-document-analyzer/
├── app/
│   ├── core/               # Configuration, database, logging
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic layer
│   │   ├── auth/           # Azure AD authentication
│   │   ├── documents/      # Upload, storage, processing
│   │   └── extraction/     # PDF extraction, AI analysis
│   ├── routers/            # API endpoints
│   ├── middleware/         # Request logging, error handling
│   └── main.py             # Application entry point
├── tests/                  # Unit and integration tests
├── uploads/                # Temporary file storage
├── deployment/             # Docker, Kubernetes configurations
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Troubleshooting

### Module Not Found

```bash
pip install -r requirements.txt
```

### Database Creation Error

```bash
python -c "
from app.core.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
"
```

### Port Already in Use

```bash
uvicorn app.main:app --reload --port 8001
```

### Invalid API Key

Set `ANTHROPIC_API_KEY` to a valid key or leave as `dummy` for mock mode.

---

## License

MIT License. See the LICENSE file for details.

---

