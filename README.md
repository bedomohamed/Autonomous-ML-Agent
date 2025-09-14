# CSV Upload & LLM Preprocessing Interface

A web-based tool that leverages Claude AI and E2B sandboxing to automatically preprocess CSV datasets for machine learning. Upload your data, select a target column, and let AI generate and execute custom preprocessing code.

## Features

- 📤 **CSV Upload**: Drag-and-drop CSV file upload with validation
- 👀 **Data Preview**: View first 50 rows of your dataset instantly
- 🎯 **Target Selection**: Choose prediction column via intuitive dropdown
- 🤖 **AI-Powered Preprocessing**: Claude generates custom preprocessing code
- 🔒 **Secure Execution**: Code runs in isolated E2B sandbox environment
- ☁️ **Cloud Storage**: Files stored securely in AWS S3
- 📥 **Download Results**: Get cleaned dataset ready for ML

## Tech Stack

### Backend
- Flask (Python REST API)
- AWS S3 (File storage)
- Claude API (Code generation)
- E2B (Sandbox execution)
- Pandas (Data processing)

### Frontend
- React 18 with TypeScript
- TailwindCSS (Styling)
- Vite (Build tool)
- Axios (API calls)
- React Dropzone (File uploads)

## Prerequisites

- Python 3.11+
- Node.js 18+
- AWS Account with S3 access
- Anthropic API key (Claude)
- E2B API key

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/csv-preprocessing-pipeline.git
cd csv-preprocessing-pipeline
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
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
| POST | `/api/preprocess` | Run preprocessing pipeline |
| GET | `/api/download/<s3_key>` | Get download URL |

## Usage

1. **Upload CSV**: Drag and drop or click to upload your CSV file
2. **Select Target**: Choose the column you want to predict from the dropdown
3. **Run Pipeline**: Click "Start LLM Pipeline" to begin preprocessing
4. **Download Results**: Get your cleaned dataset when processing completes

## Preprocessing Pipeline

The AI-powered preprocessing includes:
- Missing value imputation
- Outlier detection and removal
- Feature standardization/normalization
- Categorical encoding
- Target column separation

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── error_handlers.py
│   │   ├── services/
│   │   │   ├── s3_service.py
│   │   │   └── preprocessing_service.py
│   │   └── utils/
│   │       └── validators.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── CSVPreview.tsx
│   │   │   ├── ColumnSelector.tsx
│   │   │   └── PipelineRunner.tsx
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=development
PORT=5000

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket

# APIs
ANTHROPIC_API_KEY=your_claude_key
E2B_API_KEY=your_e2b_key
```

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

- All file uploads are validated for type and size
- Code execution happens in isolated E2B sandboxes
- API keys should never be exposed to frontend
- S3 presigned URLs expire after 1 hour
- CORS configured for specific origins only

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open a GitHub issue.
