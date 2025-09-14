import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import FileUpload from './components/FileUpload'
import CSVPreview from './components/CSVPreview'
import ColumnSelector from './components/ColumnSelector'
import PipelineRunner from './components/PipelineRunner'
import { FileData, ProcessingResult } from './types'

function App() {
  const [fileData, setFileData] = useState<FileData | null>(null)
  const [selectedColumn, setSelectedColumn] = useState<string>('')
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null)

  const handleFileUpload = (data: FileData) => {
    setFileData(data)
    setSelectedColumn('')
    setProcessingResult(null)
  }

  const handleProcessingComplete = (result: ProcessingResult) => {
    setProcessingResult(result)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            CSV Preprocessing Pipeline
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload CSV → Select Target Column → Run LLM Pipeline
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Step 1: Upload CSV File</h2>
            <FileUpload onUploadSuccess={handleFileUpload} />
          </div>

          {fileData && (
            <>
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Step 2: Preview & Select Target Column</h2>
                <div className="mb-6">
                  <ColumnSelector
                    columns={fileData.columns}
                    selectedColumn={selectedColumn}
                    onColumnSelect={setSelectedColumn}
                  />
                </div>
                <CSVPreview data={fileData} />
              </div>

              {selectedColumn && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Step 3: Run Preprocessing Pipeline</h2>
                  <PipelineRunner
                    fileData={fileData}
                    targetColumn={selectedColumn}
                    onProcessingComplete={handleProcessingComplete}
                  />
                </div>
              )}

              {processingResult && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Processing Results</h2>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">Original Shape</p>
                        <p className="text-xl font-semibold">
                          {processingResult.statistics.original_shape[0]} rows × {processingResult.statistics.original_shape[1]} columns
                        </p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">Cleaned Shape</p>
                        <p className="text-xl font-semibold">
                          {processingResult.statistics.cleaned_shape[0]} rows × {processingResult.statistics.cleaned_shape[1]} columns
                        </p>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-medium mb-2">Preprocessing Steps Applied:</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {processingResult.preprocessing_steps.map((step, index) => (
                          <li key={index} className="text-sm text-gray-700">{step}</li>
                        ))}
                      </ul>
                    </div>

                    {processingResult.download_url && (
                      <div className="pt-4">
                        <a
                          href={processingResult.download_url}
                          className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                          download
                        >
                          Download Processed Data
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App