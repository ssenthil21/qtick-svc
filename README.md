# QTick MCP Service Setup Guide

This guide provides instructions for setting up and running the `qtick-svc` Python service locally on a Mac.

## Prerequisites

- **Python 3.9+**: Ensure you have a compatible Python version installed. You can check your version with `python3 --version`.
- **pip**: The Python package installer.

## Local Setup

1. **Clone or Navigate to the Repository**:
   ```bash
   cd /Users/pavya/Documents/Senthil/qtick-svc
   ```

2. **Create a Virtual Environment**:
   It is highly recommended to use a virtual environment to manage dependencies.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file from the `.env.example` template:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and fill in the necessary API keys and configuration:
   - `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI).
   - `GEMINI_API_KEY`: Your Gemini API key (if using Gemini).
   - `LLM_PROVIDER`: Set to `gemini` or `openai`.
   - `USE_MOCK_DATA`: Set to `true` if you want to test without a backend service.

## Running the Service

Start the FastAPI server using `uvicorn`:
```bash
python3 -m app.main
```
Alternatively, you can run:
```bash
uvicorn app.main:app --reload --port 8000
```
The service will be available at `http://localhost:8000`. You can view the API documentation (Swagger UI) at `http://localhost:8000/docs`.

## Testing

The project includes several test scripts in the `tests/` directory. You can run them individually:

- **Mock Flow Test**:
  ```bash
  python3 -m tests.test_flow
  ```
- **Gemini Connection Test**:
  ```bash
  python3 -m tests.test_gemini_connection
  ```
- **Website Chat Test**:
  ```bash
  python3 -m tests.test_website_chat
  ```

### Health Check
You can verify the service is running by hitting the health endpoint:
```bash
curl http://localhost:8000/health
```
