import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  Code,
  Play,
  Download,
  CheckCircle,
  AlertCircle,
  Clock,
  FileText,
  Zap,
  Terminal,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useGeneratePreprocessing, useExecutePreprocessing, useDownloadUrl } from '../hooks/api'

interface PreprocessingStepProps {
  analysisData: any
  onPreprocessingComplete: (preprocessingData: any) => void
}

interface PreprocessingState {
  generatingCode: boolean
  executing: boolean
  completed: boolean
  error: string | null
  code: string | null
  explanation: string | null
  executionResult: any | null
  cleanedStorageKey: string | null
  estimatedTime: number
  actualTime: number
}

export default function PreprocessingStep({
  analysisData,
  onPreprocessingComplete
}: PreprocessingStepProps) {
  const [state, setState] = useState<PreprocessingState>({
    generatingCode: false,
    executing: false,
    completed: false,
    error: null,
    code: null,
    explanation: null,
    executionResult: null,
    cleanedStorageKey: null,
    estimatedTime: 0,
    actualTime: 0
  })

  const [executionProgress, setExecutionProgress] = useState(0)
  const [currentOperation, setCurrentOperation] = useState('')
  const [triggerDownload, setTriggerDownload] = useState(false)

  const generateMutation = useGeneratePreprocessing()
  const executeMutation = useExecutePreprocessing()

  // Only fetch download URL when needed
  const { data: downloadData, isLoading: downloadLoading } = useDownloadUrl(
    state.cleanedStorageKey ? state.cleanedStorageKey.replace('/', '__') : '',
    triggerDownload && !!state.cleanedStorageKey
  )

  useEffect(() => {
    if (analysisData && !state.code && !generateMutation.isPending) {
      generatePreprocessingCode()
    }
  }, [analysisData])

  const generatePreprocessingCode = async () => {
    setState(prev => ({ ...prev, generatingCode: true, error: null }))

    generateMutation.mutate(
      analysisData,
      {
        onSuccess: (response) => {
          if (response.success && response.data) {
            setState(prev => ({
              ...prev,
              generatingCode: false,
              code: response.data.preprocessing_code,
              explanation: response.data.code_explanation,
              estimatedTime: response.data.estimated_execution_time
            }))
            toast.success('Preprocessing code generated successfully!')
          }
        },
        onError: (error: any) => {
          console.error('Code generation error:', error)
          setState(prev => ({
            ...prev,
            generatingCode: false,
            error: error.response?.data?.error || 'Failed to generate preprocessing code'
          }))
          toast.error('Code generation failed')
        }
      }
    )
  }

  const executePreprocessingCode = async () => {
    if (!state.code) return

    setState(prev => ({ ...prev, executing: true, error: null }))
    setExecutionProgress(0)
    setCurrentOperation('Initializing sandbox environment...')

    const startTime = Date.now()

    // Simulate execution progress
    const progressSteps = [
      { progress: 10, operation: 'Setting up secure sandbox...' },
      { progress: 25, operation: 'Loading dataset...' },
      { progress: 40, operation: 'Executing preprocessing steps...' },
      { progress: 60, operation: 'Handling missing data...' },
      { progress: 80, operation: 'Encoding categorical variables...' },
      { progress: 95, operation: 'Finalizing cleaned dataset...' }
    ]

    for (const step of progressSteps) {
      setExecutionProgress(step.progress)
      setCurrentOperation(step.operation)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    executeMutation.mutate(
      {
        preprocessingCode: state.code,
        storageKey: analysisData.dataset_info.storage_key
      },
      {
        onSuccess: (response) => {
          const endTime = Date.now()
          const actualTime = Math.round((endTime - startTime) / 1000)

          setExecutionProgress(100)
          setCurrentOperation('Preprocessing completed!')

          if (response.success && response.data) {
            setState(prev => ({
              ...prev,
              executing: false,
              completed: true,
              executionResult: response.data.execution_result,
              cleanedStorageKey: response.data.cleaned_storage_key,
              actualTime
            }))

            toast.success('Data preprocessing completed successfully!')

            // Call completion callback
            onPreprocessingComplete({
              cleaned_storage_key: response.data.cleaned_storage_key,
              execution_result: response.data.execution_result,
              preprocessing_code: state.code,
              execution_time: actualTime
            })
          }
        },
        onError: (error: any) => {
          console.error('Execution error:', error)
          setState(prev => ({
            ...prev,
            executing: false,
            error: error.response?.data?.error || 'Failed to execute preprocessing'
          }))
          toast.error('Preprocessing execution failed')
        }
      }
    )
  }

  const downloadCode = () => {
    if (!state.code) return

    const blob = new Blob([state.code], { type: 'text/python' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `preprocessing_${analysisData.experiment_id}.py`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success('Code downloaded successfully!')
  }

  const downloadCleanedData = async () => {
    if (!state.cleanedStorageKey) return

    setTriggerDownload(true)
  }

  // Handle download URL response
  useEffect(() => {
    if (triggerDownload && downloadData?.success && downloadData.data?.download_url) {
      window.open(downloadData.data.download_url, '_blank')
      toast.success('Download started!')
      setTriggerDownload(false)
    }
  }, [triggerDownload, downloadData])

  if (state.generatingCode) {
    return (
      <Card className="p-8 bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200 rounded-apple-lg">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 mx-auto bg-purple-100 rounded-full flex items-center justify-center">
            <Code size={32} className="text-purple-600 animate-pulse" />
          </div>

          <div className="space-y-2">
            <h3 className="text-title2 font-semibold text-purple-900">Generating Preprocessing Code</h3>
            <p className="text-body text-purple-700">
              Claude AI is analyzing your dataset and generating optimized preprocessing code...
            </p>
          </div>

          <div className="flex justify-center space-x-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      </Card>
    )
  }

  if (state.error) {
    return (
      <Card className="p-6 bg-gradient-to-br from-red-50 to-red-100 border-red-200 rounded-apple-lg">
        <div className="flex items-start space-x-3">
          <AlertCircle size={24} className="text-red-600 mt-1" />
          <div className="flex-1">
            <h3 className="text-headline font-semibold text-red-900 mb-2">Preprocessing Error</h3>
            <p className="text-body text-red-700 mb-4">{state.error}</p>
            <Button
              onClick={generatePreprocessingCode}
              variant="outline"
              className="border-red-300 text-red-700 hover:bg-red-100"
            >
              <RefreshCw size={16} className="mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <Code size={20} className="text-blue-600" />
          </div>
          <div>
            <h2 className="text-title2 font-bold text-foreground">Data Preprocessing</h2>
            <p className="text-footnote text-muted-foreground">
              {state.completed ? 'Preprocessing completed successfully' : 'AI-generated preprocessing code ready'}
            </p>
          </div>
        </div>

        <Badge variant={state.completed ? 'default' : 'secondary'} className={
          state.completed ? 'bg-green-100 text-green-800 border-green-200' : ''
        }>
          {state.completed ? (
            <>
              <CheckCircle size={14} className="mr-1" />
              Completed
            </>
          ) : (
            <>
              <Clock size={14} className="mr-1" />
              Ready to Execute
            </>
          )}
        </Badge>
      </div>

      {/* Code Display */}
      {state.code && (
        <Card className="p-6 rounded-apple-lg">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-headline font-semibold flex items-center">
                <Terminal size={20} className="mr-2 text-blue-600" />
                Generated Preprocessing Code
              </h3>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-caption">
                  Python
                </Badge>
                <Button
                  onClick={downloadCode}
                  variant="outline"
                  size="sm"
                  className="text-caption"
                >
                  <Download size={14} className="mr-1" />
                  Download
                </Button>
              </div>
            </div>

            {state.explanation && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-apple">
                <p className="text-footnote text-blue-800">
                  <strong>Code Explanation:</strong> {state.explanation}
                </p>
              </div>
            )}

            <div className="bg-slate-900 rounded-apple p-4 overflow-x-auto">
              <pre className="text-sm text-slate-100 font-mono whitespace-pre-wrap">
                {state.code}
              </pre>
            </div>

            {state.estimatedTime > 0 && !state.executing && !state.completed && (
              <div className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-apple">
                <div className="flex items-center space-x-2">
                  <Clock size={16} className="text-amber-600" />
                  <span className="text-footnote text-amber-800">
                    Estimated execution time: {state.estimatedTime} seconds
                  </span>
                </div>
                <Button
                  onClick={executePreprocessingCode}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground"
                >
                  <Play size={16} className="mr-2" />
                  Execute Code
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Execution Progress */}
      {state.executing && (
        <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 rounded-apple-lg">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Zap size={20} className="text-green-600 animate-pulse" />
              </div>
              <div>
                <h3 className="text-headline font-semibold text-green-900">Executing in Secure Sandbox</h3>
                <p className="text-footnote text-green-700">{currentOperation}</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-caption text-green-700">
                <span>Execution Progress</span>
                <span>{executionProgress}%</span>
              </div>
              <Progress value={executionProgress} className="w-full h-3 bg-green-100" />
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Environment</p>
                <p className="text-footnote font-medium">E2B Sandbox</p>
              </div>
              <div className="p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Security</p>
                <p className="text-footnote font-medium">Isolated</p>
              </div>
              <div className="p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Timeout</p>
                <p className="text-footnote font-medium">5 min</p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Execution Results */}
      {state.completed && state.executionResult && (
        <Card className="p-6 rounded-apple-lg">
          <div className="space-y-4">
            <h3 className="text-headline font-semibold flex items-center">
              <CheckCircle size={20} className="mr-2 text-green-600" />
              Preprocessing Results
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-apple">
                <div className="flex items-center space-x-2">
                  <Clock size={16} className="text-green-600" />
                  <div>
                    <p className="text-caption text-muted-foreground">Execution Time</p>
                    <p className="text-footnote font-medium">{state.actualTime}s</p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-apple">
                <div className="flex items-center space-x-2">
                  <FileText size={16} className="text-blue-600" />
                  <div>
                    <p className="text-caption text-muted-foreground">Status</p>
                    <p className="text-footnote font-medium text-green-600">Success</p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-apple">
                <div className="flex items-center space-x-2">
                  <Download size={16} className="text-purple-600" />
                  <div>
                    <p className="text-caption text-muted-foreground">Cleaned Data</p>
                    <Button
                      onClick={downloadCleanedData}
                      variant="ghost"
                      size="sm"
                      disabled={downloadLoading}
                      className="text-footnote h-auto p-0 text-purple-600"
                    >
                      {downloadLoading ? 'Preparing...' : 'Download CSV'}
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Execution Output */}
            {state.executionResult.stdout && (
              <div className="space-y-2">
                <h4 className="text-callout font-medium">Execution Output:</h4>
                <div className="bg-slate-900 rounded-apple p-4 overflow-x-auto">
                  <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
                    {state.executionResult.stdout}
                  </pre>
                </div>
              </div>
            )}

            <div className="flex justify-center pt-4">
              <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
                Ready for model training
              </Badge>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}