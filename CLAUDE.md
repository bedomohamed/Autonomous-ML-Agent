# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CSV Upload & LLM Preprocessing Interface that uses Claude AI and E2B sandboxing to automatically preprocess datasets for machine learning. The system consists of a Flask backend API and React TypeScript frontend.

## Common Commands

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run Flask development server
python run.py

# Run tests
pytest tests/

# Format code
black app/

# Lint code
flake8 app/
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run type checking
npm run typecheck
```

### Docker Operations
```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service_name]
```

## Architecture

### Backend (Flask)
- **app/routes.py**: Main API endpoints (/upload, /preprocess, /download)
- **app/services/s3_service.py**: AWS S3 file operations
- **app/services/preprocessing_service.py**: Claude AI integration and E2B sandbox execution
- **app/utils/validators.py**: CSV validation logic

The preprocessing flow:
1. CSV uploaded to S3 via /upload endpoint
2. /preprocess endpoint sends data sample to Claude API
3. Claude generates custom preprocessing Python code
4. Code executed in E2B sandbox for security
5. Cleaned dataset returned and stored in S3

### Frontend (React + TypeScript)
- **src/App.tsx**: Main application component with state management
- **src/components/FileUpload.tsx**: Drag-and-drop CSV upload
- **src/components/CSVPreview.tsx**: Table view of uploaded data
- **src/components/ColumnSelector.tsx**: Target column selection dropdown
- **src/components/PipelineRunner.tsx**: Preprocessing pipeline trigger

Component flow:
1. FileUpload → uploads CSV and receives preview data
2. ColumnSelector → user selects target column
3. PipelineRunner → triggers preprocessing and shows results

## Key Integration Points

### Claude API
- Used in `preprocessing_service.py` to generate preprocessing code
- Requires ANTHROPIC_API_KEY environment variable
- Uses claude-3-opus model for code generation

### E2B Sandbox
- Executes generated code in isolated environment
- Requires E2B_API_KEY environment variable
- Captures output and returns cleaned DataFrame

### AWS S3
- Stores uploaded CSV files and processed results
- Requires AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- Generates presigned URLs for secure downloads

## Development Guidelines

1. **API Changes**: When modifying endpoints, update both Flask routes and React API calls
2. **Error Handling**: All API endpoints should return consistent error format: `{error: string}`
3. **File Uploads**: Maximum size is 50MB, enforced in Flask config
4. **CORS**: Configured for localhost:3000 and localhost:5173 (Vite dev server)
5. **Environment Variables**: Use .env.example as template, never commit .env files

## Testing Approach

- Backend: Use pytest for API endpoint testing
- Frontend: Component testing with React Testing Library
- Integration: Test file upload → preprocessing → download flow
- Security: Validate E2B sandbox isolation and S3 access controls