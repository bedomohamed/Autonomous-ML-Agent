import { useState } from 'react'
import { PlayIcon } from '@heroicons/react/24/solid'
import toast from 'react-hot-toast'
import axios from 'axios'
import { FileData, ProcessingResult } from '../types'

interface PipelineRunnerProps {
  fileData: FileData
  targetColumn: string
  onProcessingComplete: (result: ProcessingResult) => void
}

export default function PipelineRunner({
  fileData,
  targetColumn,
  onProcessingComplete,
}: PipelineRunnerProps) {
  const [processing, setProcessing] = useState(false)
  const [status, setStatus] = useState<string>('')

  const runPipeline = async () => {
    setProcessing(true)
    setStatus('Initializing preprocessing pipeline...')

    try {
      setStatus('Generating preprocessing code with Claude...')

      const response = await axios.post('/api/preprocess', {
        s3_key: fileData.s3_key,
        target_column: targetColumn,
      })

      if (response.data.success) {
        setStatus('Fetching download URL...')

        const downloadResponse = await axios.get(`/api/download/${response.data.data.processed_s3_key}`)

        const result: ProcessingResult = {
          ...response.data.data,
          download_url: downloadResponse.data.download_url,
        }

        toast.success('Preprocessing completed successfully!')
        onProcessingComplete(result)
        setStatus('')
      }
    } catch (error: any) {
      console.error('Processing error:', error)
      toast.error(error.response?.data?.error || 'Processing failed')
      setStatus('')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">Pipeline Configuration</h3>
        <div className="space-y-1 text-sm text-blue-800">
          <p>• File: {fileData.filename}</p>
          <p>• Target Column: {targetColumn}</p>
          <p>• Original Shape: {fileData.shape.rows} rows × {fileData.shape.columns} columns</p>
        </div>
      </div>

      <div className="space-y-3">
        <button
          onClick={runPipeline}
          disabled={processing}
          className={`w-full flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-md text-white
            ${processing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
            }`}
        >
          {processing ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <PlayIcon className="w-5 h-5 mr-2" />
              Start LLM Pipeline
            </>
          )}
        </button>

        {status && (
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-600">{status}</p>
          </div>
        )}
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h4 className="font-medium text-amber-900 mb-2">What will happen:</h4>
        <ol className="list-decimal list-inside space-y-1 text-sm text-amber-800">
          <li>Claude will analyze your dataset structure</li>
          <li>Generate custom preprocessing code for your data</li>
          <li>Execute the code in a secure E2B sandbox</li>
          <li>Return the cleaned dataset for download</li>
        </ol>
      </div>
    </div>
  )
}