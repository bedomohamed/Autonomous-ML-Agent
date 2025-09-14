# 🔑 API Keys Setup Guide - Claude & E2B Integration

This guide will help you set up the required API keys for the full ML Pipeline with AI-powered code generation (Claude) and secure sandbox execution (E2B).

## 📋 Prerequisites

You need accounts for:
1. **Anthropic (Claude API)** - For AI code generation
2. **E2B** - For secure code execution in sandboxes

---

## 🤖 1. Claude API Key Setup

### Step 1: Create Anthropic Account
1. Visit https://console.anthropic.com/
2. Sign up for an account (or sign in if you have one)
3. You may need to add payment method for API access

### Step 2: Generate API Key
1. Go to **API Keys** section in the console
2. Click **"Create Key"**
3. Give it a name like "ML Pipeline"
4. Copy the key (starts with `sk-ant-api...`)

### Step 3: Add to .env File
```bash
cd backend
# Edit the .env file
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
```

---

## 🏗️ 2. E2B API Key Setup

### Step 1: Create E2B Account
1. Visit https://e2b.dev/
2. Click **"Get Started"** or **"Sign Up"**
3. Create your account

### Step 2: Generate API Key
1. Go to your E2B Dashboard
2. Navigate to **Settings** → **API Keys**
3. Click **"Create API Key"**
4. Copy the generated key

### Step 3: Add to .env File
```bash
cd backend
# Edit the .env file
E2B_API_KEY=e2b_YOUR-ACTUAL-KEY-HERE
```

---

## ✅ 3. Verify Your Setup

### Complete .env File Example
```bash
# Flask Configuration
FLASK_ENV=development
PORT=5003

# API Keys - REPLACE WITH YOUR ACTUAL KEYS
ANTHROPIC_API_KEY=sk-ant-api03-abcdef123456...  # Your real Claude key
E2B_API_KEY=e2b_abc123def456...                 # Your real E2B key

# Local Storage Configuration
STORAGE_ROOT=./storage
UPLOAD_FOLDER=/tmp/uploads
MAX_CONTENT_LENGTH=52428800
```

### Test the APIs
```bash
# Start the backend
cd backend
python run.py

# In another terminal, test the health endpoints
curl http://localhost:5003/api/claude/health
curl http://localhost:5003/api/e2b/health
```

### Expected Responses
✅ **Claude Health Check Success:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "api_key_configured": true,
    "model": "claude-3-sonnet-20240229"
  }
}
```

✅ **E2B Health Check Success:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "sandbox_accessible": true,
    "ml_libraries_available": true
  }
}
```

---

## 🚀 4. Using the Full ML Pipeline

Once your API keys are configured:

### Option 1: Use the ML Pipeline Wizard (Recommended)
The ML Pipeline Wizard provides a step-by-step interface with Claude AI and E2B integration:

1. **Upload CSV** → Your data file
2. **Select Target** → Column to predict
3. **Analyze** → AI analyzes your dataset
4. **Preprocess** → Claude generates & E2B executes cleaning code
5. **Train Models** → Claude generates & E2B trains 4 ML models
6. **View Results** → Compare model performance

### Option 2: Use Individual API Endpoints

#### Generate Preprocessing Code (Claude)
```bash
curl -X POST http://localhost:5003/api/generate-preprocessing \
  -H "Content-Type: application/json" \
  -d '{
    "preprocessing_prompt": "Clean this dataset...",
    "dataset_info": {...}
  }'
```

#### Execute Preprocessing (E2B)
```bash
curl -X POST http://localhost:5003/api/execute-preprocessing \
  -H "Content-Type: application/json" \
  -d '{
    "preprocessing_code": "# Python code here",
    "storage_key": "uploads/file.csv"
  }'
```

#### Generate Training Code (Claude)
```bash
curl -X POST http://localhost:5003/api/generate-training-code \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_info": {...}
  }'
```

#### Execute Training (E2B)
```bash
curl -X POST http://localhost:5003/api/execute-training \
  -H "Content-Type: application/json" \
  -d '{
    "training_code": "# Python ML code",
    "cleaned_storage_key": "processed/cleaned.csv"
  }'
```

---

## 💰 5. API Pricing & Limits

### Claude API Pricing
- **Claude 3 Sonnet**: ~$3 per million input tokens
- **Typical preprocessing code generation**: ~$0.01 per request
- **Typical training code generation**: ~$0.02 per request
- See current pricing: https://www.anthropic.com/pricing

### E2B Pricing
- **Free Tier**: 100 sandbox hours/month
- **Typical preprocessing**: ~1-2 minutes per execution
- **Typical training**: ~5-10 minutes per execution
- See current pricing: https://e2b.dev/pricing

### Cost Estimates
For a typical ML pipeline run:
- Claude API: ~$0.03-0.05
- E2B Sandbox: ~10-15 minutes (well within free tier)
- **Total**: Less than $0.10 per complete pipeline run

---

## 🔧 6. Troubleshooting

### "ANTHROPIC_API_KEY not set or is placeholder"
- Make sure you've added your actual API key to `.env`
- Restart the Flask server after updating `.env`

### "E2B_API_KEY not set or is placeholder"
- Verify your E2B key is correctly added to `.env`
- Check that the key starts with `e2b_`

### "Insufficient credits" errors
- Check your account balance on respective platforms
- Claude: https://console.anthropic.com/settings/billing
- E2B: https://e2b.dev/dashboard

### "Sandbox initialization failed"
- Verify E2B API key is valid
- Check E2B service status: https://status.e2b.dev/
- Try the free tier if you haven't already

---

## 🎯 7. Best Practices

1. **Keep API Keys Secure**
   - Never commit `.env` to git
   - Use environment variables in production
   - Rotate keys periodically

2. **Monitor Usage**
   - Track API calls in your provider dashboards
   - Set up billing alerts
   - Use caching where possible

3. **Optimize Costs**
   - Use Claude 3 Haiku for simpler tasks
   - Cache generated code for similar datasets
   - Batch operations when possible

---

## 📚 8. Additional Resources

- **Claude Documentation**: https://docs.anthropic.com/
- **E2B Documentation**: https://e2b.dev/docs
- **ML Pipeline Guide**: See `LOCAL_SETUP_GUIDE.md`
- **Support**: Create issues at your project repository

---

## ✨ Ready to Go!

With both API keys configured, you now have access to:
- 🤖 **AI-powered code generation** with Claude
- 🔒 **Secure sandbox execution** with E2B
- 📊 **Multi-model training** (XGBoost, Random Forest, Decision Tree, Naive Bayes)
- 📈 **Automatic performance comparison**
- 💾 **Local file storage** (no AWS needed!)

Start the application and enjoy your AI-powered AutoML pipeline! 🚀