# Quick Start Guide

Get the Member QA System running in under 5 minutes!

## Prerequisites

- Python 3.11+ or Docker
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Option 1: Local Python (Fastest for Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 3. Run the service
python main.py
```

Service will be available at `http://localhost:8080`

## Option 2: Docker (Recommended for Production)

```bash
# 1. Build and run with docker-compose
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
docker-compose up -d

# Or build and run manually
docker build -t member-qa .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY="sk-ant-your-key-here" member-qa
```

## Testing the Service

### 1. Check if it's running

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Ask a question

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

Expected response:
```json
{"answer": "Layla is planning her trip to London..."}
```

### 3. Run comprehensive tests

```bash
python test_api.py
```

## Analyze the Data (Bonus 2)

Run the data analysis script to see detailed insights:

```bash
python analyze_data.py
```

This will:
- Fetch all member messages from the API
- Check for data quality issues
- Identify anomalies and inconsistencies
- Generate a detailed report
- Save findings to `data_analysis_results.json`

## Deploy to Production

### Google Cloud Run (Easiest)

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project"

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/member-qa
gcloud run deploy member-qa \
  --image gcr.io/$PROJECT_ID/member-qa \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
```

### Other Platforms

The service works with any platform that supports Docker containers:

- **Heroku**: `heroku container:push web && heroku container:release web`
- **Railway**: Connect your GitHub repo and deploy
- **Render**: Create a new Web Service from your repo
- **AWS ECS**: Deploy as a container with the Dockerfile

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `PORT` | No | Port to run on (default: 8080) |

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Failed to fetch member data"
Check that the member API is accessible:
```bash
curl https://november7-730026606190.europe-west1.run.app/messages
```

### "Claude API error"
- Verify your `ANTHROPIC_API_KEY` is set correctly
- Check you have API credits available at console.anthropic.com
- Ensure the key starts with `sk-ant-`

### Service not responding
- Check if the port is already in use: `lsof -i :8080`
- Try a different port: `PORT=8081 python main.py`
- Check logs: `docker logs member-qa-system`

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Review the [alternative approaches](README.md#bonus-1-alternative-approaches-considered) considered
- Explore the [data analysis findings](README.md#bonus-2-data-insights--anomalies)
- Customize the prompts in `main.py` for your use case
- Add authentication if deploying publicly
- Set up monitoring and logging

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review the code comments in `main.py`
3. Run `python analyze_data.py` to check data quality
