# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Configure (Optional)

Copy `.env.example` to `.env` and fill in your API credentials. **You can skip this step** - the app works in mock mode without credentials!

```bash
cp .env.example .env
# Edit .env with your credentials (optional)
```

### Step 3: Run the Server

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload

# Option 3: Using Docker
docker-compose up
```

The API will be available at `http://localhost:8000`

### Step 4: Test the API

#### Using the Example Script

```bash
python examples/test_api.py
```

#### Using curl

**Classify a ticket:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I cannot access my account",
    "include_suggestion": true
  }'
```

**Route a ticket:**
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

#### Using the Interactive Docs

Open your browser and go to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 Example Workflow

1. **Start the server**
   ```bash
   python run.py
   ```

2. **Classify a ticket**
   - Go to `http://localhost:8000/docs`
   - Use the `/classify` endpoint
   - Enter ticket text: "I cannot log into my account"
   - Click "Execute"

3. **Route a ticket**
   - Use the `/route` endpoint
   - Enter ticket details
   - The system will:
     - Classify the ticket
     - Create a Jira issue (if enabled)
     - Send a Slack notification (if enabled)

## 🐳 Docker Quick Start

```bash
# Build and run
docker-compose up --build

# Or using docker directly
docker build -t ai-triage-agent .
docker run -p 8000:8000 ai-triage-agent
```

## 🧪 Run Tests

```bash
pytest app/tests/
```

## ⚠️ Troubleshooting

### Model Download Issues
If the BERT model fails to download:
- Check your internet connection
- The model will be cached in `./models/` directory
- First run may take a few minutes to download models

### Port Already in Use
If port 8000 is busy:
```bash
uvicorn app.main:app --port 8001
```

### Import Errors
Make sure you're in the project root directory and virtual environment is activated.

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure API credentials in `.env` for production use
- Fine-tune the classification model on your ticket data
- Set up CI/CD with GitHub Actions

