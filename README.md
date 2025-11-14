# AI Support Ticket Triage Agent (MVP)

An intelligent support ticket classification and routing system built with FastAPI, Hugging Face Transformers, IBM watsonx.ai, and integrated with Gmail, Jira, and Slack APIs.

## 🎯 Features

- **AI-Powered Classification**: Uses BERT-based transformer models to classify tickets into categories (billing, technical, access, general, etc.)
- **Automated Routing**: Automatically creates Jira issues and sends Slack notifications based on ticket category
- **LLM Response Generation**: Uses IBM watsonx.ai to generate suggested replies and ticket summaries
- **Gmail Integration**: Fetches support tickets from Gmail (with mock mode for testing)
- **RESTful API**: FastAPI-based endpoints for classification and routing
- **Docker Support**: Containerized application for easy deployment

## 🏗️ Architecture

```
ai-triage-agent/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── routes/                 # API route handlers
│   │   ├── classify.py        # Classification endpoint
│   │   └── route.py           # Routing endpoint
│   ├── services/               # External service integrations
│   │   ├── model_service.py   # Hugging Face BERT classifier
│   │   ├── gmail_service.py  # Gmail API integration
│   │   ├── jira_service.py    # Jira REST API integration
│   │   ├── slack_service.py   # Slack Web API integration
│   │   └── watsonx_service.py # IBM watsonx.ai integration
│   ├── utils/                  # Utilities
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Logging setup
│   └── tests/                 # Test suite
│       ├── test_classification.py
│       └── test_routing.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)
- API credentials for:
  - Gmail API (optional, mock mode available)
  - Jira (optional, mock mode available)
  - Slack (optional, mock mode available)
  - IBM watsonx.ai (optional, mock mode available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ai-Triage-Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t ai-triage-agent .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 --env-file .env ai-triage-agent
   ```

## 📡 API Endpoints

### POST `/classify`
Classify a support ticket into categories.

**Request:**
```json
{
  "text": "I cannot access my account. My password is not working.",
  "include_suggestion": false,
  "include_summary": false
}
```

**Response:**
```json
{
  "category": "access",
  "confidence": 0.85,
  "scores": {
    "billing": 0.05,
    "technical": 0.10,
    "access": 0.85,
    "general": 0.00
  },
  "model": "bert-base-uncased"
}
```

### POST `/route`
Classify and route a ticket (creates Jira issue and sends Slack notification).

**Request:**
```json
{
  "ticket_id": "TICKET-001",
  "text": "I cannot access my account.",
  "subject": "Access Issue",
  "from_email": "user@example.com",
  "create_jira": true,
  "send_slack": true
}
```

**Response:**
```json
{
  "ticket_id": "TICKET-001",
  "category": "access",
  "confidence": 0.85,
  "jira_issue": {
    "success": true,
    "issue_key": "SUP-123",
    "url": "https://your-domain.atlassian.net/browse/SUP-123"
  },
  "slack_message": {
    "success": true,
    "channel": "#access",
    "ts": "1234567890.123456"
  },
  "routing_config": {
    "jira_priority": "High",
    "slack_channel": "#access"
  }
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "classifier": "available",
    "model": "bert-base-uncased"
  }
}
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- **Gmail API**: `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`
- **Jira**: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`
- **Slack**: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`
- **IBM watsonx.ai**: `WATSONX_API_KEY`, `WATSONX_URL`, `WATSONX_PROJECT_ID`, `WATSONX_MODEL_ID`
- **Model**: `MODEL_NAME`, `MODEL_CACHE_DIR`

### Category Routing

Configure routing rules in `app/utils/config.py`:

```python
CATEGORY_ROUTING = {
    "billing": {"jira_priority": "High", "slack_channel": "#billing"},
    "technical": {"jira_priority": "Medium", "slack_channel": "#technical"},
    "access": {"jira_priority": "High", "slack_channel": "#access"},
    "general": {"jira_priority": "Low", "slack_channel": "#general"},
}
```

## 🧪 Testing

Run the test suite:

```bash
pytest app/tests/
```

Or run specific test files:

```bash
pytest app/tests/test_classification.py
pytest app/tests/test_routing.py
```

## 📊 Test Flow

1. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Classify a ticket**
   ```bash
   curl -X POST "http://localhost:8000/classify" \
     -H "Content-Type: application/json" \
     -d '{"text": "I cannot access my account"}'
   ```

3. **Route a ticket**
   ```bash
   curl -X POST "http://localhost:8000/route" \
     -H "Content-Type: application/json" \
     -d '{
       "ticket_id": "TEST-001",
       "text": "Billing issue with my invoice",
       "create_jira": true,
       "send_slack": true
     }'
   ```

## 🔐 API Credentials Setup

### Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API
3. Create OAuth 2.0 credentials
4. Use OAuth flow to get refresh token

### Jira API
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create an API token
3. Use your email and API token for authentication

### Slack API
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Install app to workspace
4. Get Bot User OAuth Token

### IBM watsonx.ai
1. Go to [IBM Cloud](https://cloud.ibm.com/)
2. Create a watsonx.ai service instance
3. Get API key and project ID
4. Configure model ID

## 🎯 Mock Mode

The application operates in mock mode when API credentials are not configured:
- Gmail service returns sample tickets
- Jira service returns mock issue keys
- Slack service returns mock message confirmations
- watsonx service returns generic responses

This allows testing the full workflow without external API dependencies.

## 🚀 Stretch Goals

- [ ] GitHub Actions CI/CD pipeline
- [ ] watsonx Orchestrate integration for workflow automation
- [ ] Enhanced entity extraction with spaCy
- [ ] Performance metrics dashboard
- [ ] Multi-language support
- [ ] Fine-tuned classification model on custom ticket data

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.
