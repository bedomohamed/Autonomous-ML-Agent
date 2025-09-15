# Autonomous ML Agent Platform

A complete end-to-end machine learning platform that leverages Claude AI and E2B sandboxing to automatically preprocess datasets, train multiple ML models, and provide comprehensive performance analysis. Transform your raw CSV data into production-ready ML models with just a few clicks.

## Features

### 🚀 **Complete ML Pipeline**
- **5-Step Wizard**: Upload → Analysis → Preprocessing → Training → Results
- **Autonomous Operation**: Minimal user input required
- **Real-time Progress**: Live updates throughout the pipeline

### 📊 **Data Processing**
- 📤 **CSV Upload**: Drag-and-drop with instant validation
- 👀 **Smart Preview**: Automatic data analysis and insights
- 🎯 **Target Selection**: Intelligent column recommendation
- 🤖 **AI Preprocessing**: Claude generates custom cleaning code
- 🔒 **Secure Execution**: Isolated E2B sandbox environment

### 🧠 **Model Training & Evaluation**
- **Multi-Model Training**: XGBoost, Random Forest, Decision Tree, Naive Bayes
- **Performance Metrics**: Accuracy, Precision, Recall, F1-Score, Training Time
- **Hyperparameter Tuning**: Automated optimization with baseline comparison
- **Model Rankings**: Performance leaderboard with downloadable reports

### 📈 **Results & Analytics**
- **Interactive Dashboard**: Comprehensive performance visualization
- **Model Comparison**: Side-by-side baseline vs tuned performance
- **Export Options**: Download models, reports, and training code
- **Time Tracking**: Detailed training duration metrics

## Tech Stack

### Backend
- **Flask** (Python REST API)
- **Claude AI** (Code generation & analysis)
- **E2B** (Secure sandbox execution)
- **Local Storage** (File management)
- **scikit-learn** (ML algorithms)
- **XGBoost** (Gradient boosting)
- **Pandas** (Data processing)

### Frontend
- **React 18** with TypeScript
- **TailwindCSS** (Modern styling)
- **Vite** (Fast build tool)
- **React Hot Toast** (Notifications)
- **Lucide React** (Icons)
- **React Query** (Data fetching)

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Anthropic API key** (Claude AI)
- **E2B API key** (Sandbox execution)
- **Git** (Version control)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/autonomous-ml-agent.git
cd autonomous-ml-agent
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
E2B_API_KEY=your_e2b_api_key_here
FLASK_ENV=development
PORT=5000
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

## Running the Application

### Development Mode

#### Backend
```bash
cd backend
python run.py
```
The backend will start on http://localhost:5000

#### Frontend
```bash
cd frontend
npm run dev
```
The frontend will start on http://localhost:3000

### Docker Mode
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload CSV file |
| POST | `/api/analyze-dataset` | Analyze dataset with Claude AI |
| POST | `/api/preprocess` | Generate preprocessing code |
| POST | `/api/execute-preprocessing` | Execute preprocessing in E2B |
| POST | `/api/generate-training-code` | Generate model training code |
| POST | `/api/execute-training` | Train models in E2B sandbox |
| POST | `/api/tune-hyperparameters` | Generate hyperparameter tuning code |
| POST | `/api/execute-hyperparameter-tuning` | Execute hyperparameter optimization |
| GET | `/api/download-local/<file_key>` | Download processed files |
| GET | `/api/download-model/<model_name>` | Download trained models |

## Usage

### 🎯 **5-Step ML Pipeline**

#### Step 1: Upload Dataset
- Drag and drop your CSV file or click to browse
- Instant file validation and preview
- Automatic column detection and analysis

#### Step 2: Data Analysis
- Claude AI analyzes your dataset structure
- Identifies data quality issues and patterns
- Provides intelligent preprocessing recommendations

#### Step 3: Preprocessing
- AI generates custom preprocessing code
- Handles missing values, outliers, and encoding
- Executes securely in E2B sandbox
- Downloads cleaned dataset

#### Step 4: Model Training
- Trains 4 ML models automatically (XGBoost, Random Forest, Decision Tree, Naive Bayes)
- Tracks training time and performance metrics
- Saves models for deployment
- Generates comprehensive evaluation reports

#### Step 5: Results & Optimization
- Interactive performance leaderboard
- Hyperparameter tuning with baseline comparison
- Model download and deployment options
- Detailed analytics and recommendations

### 🤖 **AI-Powered Preprocessing**

The Claude AI preprocessing pipeline automatically handles:
- **Data Cleaning**: Missing value imputation, duplicate removal
- **Feature Engineering**: Scaling, normalization, encoding
- **Outlier Detection**: Statistical and ML-based outlier removal
- **Categorical Encoding**: One-hot encoding, label encoding
- **Feature Selection**: Correlation analysis and feature importance
- **Data Validation**: Type checking and consistency verification

## Project Structure

```
autonomous-ml-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py                    # API endpoints
│   │   ├── error_handlers.py           # Error handling
│   │   ├── services/
│   │   │   ├── claude_service.py       # Claude AI integration
│   │   │   ├── e2b_service.py          # Sandbox execution
│   │   │   ├── local_storage_service.py # File management
│   │   │   ├── data_analysis_service.py # Data analysis
│   │   │   └── preprocessing_service.py # Preprocessing logic
│   │   └── utils/
│   │       └── validators.py           # Input validation
│   ├── storage/                        # Local file storage
│   │   ├── uploads/                    # Uploaded datasets
│   │   ├── processed/                  # Cleaned datasets
│   │   └── models/                     # Trained models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx          # File upload interface
│   │   │   ├── CSVPreview.tsx          # Data preview
│   │   │   ├── DataAnalysis.tsx        # Analysis step
│   │   │   ├── PreprocessingStep.tsx   # Preprocessing step
│   │   │   ├── ModelTraining.tsx       # Training step
│   │   │   ├── ResultsLeaderboard.tsx  # Results dashboard
│   │   │   └── MLPipelineWizard.tsx    # Main wizard
│   │   ├── hooks/
│   │   │   └── api.ts                  # API hooks
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── CLAUDE.md                          # Claude Code instructions
├── PRD.md                             # Product requirements
├── features.md                        # Feature documentation
└── README.md
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
PORT=5000

# AI Services
ANTHROPIC_API_KEY=your_claude_api_key_here
E2B_API_KEY=your_e2b_api_key_here

# Optional: For production deployments
# AWS_ACCESS_KEY_ID=your_aws_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret
# AWS_REGION=us-east-1
# AWS_BUCKET_NAME=your-bucket
```

### API Key Setup

1. **Anthropic API Key**:
   - Sign up at [console.anthropic.com](https://console.anthropic.com)
   - Create a new API key
   - Add credits to your account

2. **E2B API Key**:
   - Sign up at [e2b.dev](https://e2b.dev)
   - Create a new API key
   - Configure sandbox templates

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### AWS Lambda
The backend can be deployed to AWS Lambda using Zappa or Serverless Framework.

### Docker
Production-ready Docker images are provided for containerized deployment.

## Security Considerations

- **File Validation**: All uploads validated for type, size, and content
- **Sandboxed Execution**: All code runs in isolated E2B containers
- **API Security**: Keys stored securely, never exposed to frontend
- **Input Sanitization**: All user inputs validated and sanitized
- **Local Storage**: Files stored locally with controlled access
- **CORS Protection**: Configured for specific origins only
- **Error Handling**: Comprehensive error handling without information leakage

## Performance & Scalability

- **Asynchronous Processing**: Non-blocking API operations
- **Progress Tracking**: Real-time pipeline status updates
- **Caching**: Intelligent caching of analysis results
- **File Management**: Automatic cleanup of temporary files
- **Resource Optimization**: Efficient memory usage during ML training
- **Concurrent Processing**: Support for multiple users

## Key Features & Benefits

### 🎯 **For Data Scientists**
- **Zero Setup**: No environment configuration required
- **AI-Powered**: Intelligent preprocessing and feature engineering
- **Multiple Models**: Compare 4 different algorithms automatically
- **Hyperparameter Tuning**: Automated optimization with clear results
- **Export Ready**: Download models and code for deployment

### 🚀 **For Businesses**
- **Rapid Prototyping**: From CSV to trained model in minutes
- **No ML Expertise Required**: AI guides the entire process
- **Cost Effective**: Local processing reduces cloud costs
- **Secure**: No data leaves your environment
- **Scalable**: Easy to integrate into existing workflows

### 🔧 **For Developers**
- **Modern Stack**: React, TypeScript, Flask, Docker
- **Modular Design**: Easy to extend and customize
- **API First**: RESTful architecture
- **Documentation**: Comprehensive docs and examples
- **Open Source**: MIT license for commercial use

## Roadmap

### 🚧 **Coming Soon**
- **Deep Learning Models**: TensorFlow/PyTorch integration
- **AutoML**: Automated architecture search
- **Model Monitoring**: Performance tracking and drift detection
- **API Deployment**: One-click model serving
- **Advanced Visualizations**: Interactive model explainability
- **Data Connectors**: Direct database and API integrations

### 💡 **Feature Requests**
- Multi-class classification support
- Regression model training
- Time series forecasting
- Text and image preprocessing
- Custom model architectures
- Distributed training

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the coding standards
4. **Add tests**: Ensure your code is well tested
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**: Describe your changes clearly

### Development Guidelines
- Follow TypeScript/Python best practices
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure backward compatibility
- Use conventional commit messages

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Support & Community

- **Issues**: [GitHub Issues](https://github.com/yourusername/autonomous-ml-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/autonomous-ml-agent/discussions)
- **Documentation**: [Full Documentation](https://docs.yoursite.com)
- **Examples**: Check the `/examples` directory

---

**⭐ Star this repository if you find it useful!**

Made with ❤️ by the Autonomous ML Team
