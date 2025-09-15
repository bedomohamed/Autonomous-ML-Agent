import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Brain, CheckCircle, Play, AlertCircle, Download, Code, Zap, Cpu, BarChart3, Target, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface ModelTrainingProps {
  preprocessingData: any
  experimentId: string | null
  onTrainingComplete: (data: any) => void
}

interface ModelState {
  name: string
  status: 'pending' | 'training' | 'completed' | 'error'
  accuracy: number
  training_time: number
  metrics?: any
}

export default function ModelTraining({
  preprocessingData,
  experimentId,
  onTrainingComplete
}: ModelTrainingProps) {
  const [state, setState] = useState({
    training: false,
    completed: false,
    generatingCode: false,
    progress: 0,
    currentModel: '',
    trainingCode: '',
    executionResult: null as any,
    actualTime: 0,
    overallProgress: 0,
    modelResults: [
      { name: 'XGBoost', status: 'pending' as const, accuracy: 0, training_time: 0 },
      { name: 'Random Forest', status: 'pending' as const, accuracy: 0, training_time: 0 },
      { name: 'Decision Tree', status: 'pending' as const, accuracy: 0, training_time: 0 },
      { name: 'Naive Bayes', status: 'pending' as const, accuracy: 0, training_time: 0 }
    ] as ModelState[]
  })

  useEffect(() => {
    if (preprocessingData && preprocessingData.cleaned_storage_key) {
      generateTrainingCode()
    }
  }, [preprocessingData, experimentId])

  const generateTrainingCode = async () => {
    try {
      setState(prev => ({ ...prev, generatingCode: true }))
      toast.loading('🤖 AI is writing your training code...', { id: 'generate-code' })

      const targetColumn = preprocessingData?.target_column || preprocessingData?.targetColumn || 'Exited'

      const payload = {
        dataset_info: {
          storage_key: preprocessingData.cleaned_storage_key,
          target_column: targetColumn,
          task_type: 'classification',
          experiment_id: experimentId
        }
      }

      const response = await fetch('/api/generate-training-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to generate training code: ${response.statusText} - ${errorText}`)
      }

      const result = await response.json()

      // Extract training code from the nested data structure
      const trainingCode = result.data?.training_code || result.training_code

      setState(prev => ({
        ...prev,
        trainingCode: trainingCode,
        generatingCode: false
      }))

      toast.success('✅ Training code ready! Click "Start Training" to begin.', { id: 'generate-code' })
    } catch (error) {
      setState(prev => ({ ...prev, generatingCode: false }))
      toast.error('❌ Failed to generate training code. Please try again.', { id: 'generate-code' })
    }
  }

  const executeTraining = async () => {
    if (!state.trainingCode) {
      toast.error('Training code not available. Please wait for code generation to complete.')
      return
    }

    if (!preprocessingData?.cleaned_storage_key) {
      toast.error('Cleaned dataset not available. Please complete preprocessing first.')
      return
    }

    const targetColumn = preprocessingData?.target_column || preprocessingData?.targetColumn || 'Exited'

    try {
      setState(prev => ({
        ...prev,
        training: true,
        progress: 0,
        currentModel: 'Initializing...',
        overallProgress: 0,
        modelResults: prev.modelResults.map(model => ({ ...model, status: 'pending' as const }))
      }))

      toast.loading('🚀 Training 4 ML models in parallel...', { id: 'training' })

      // Prepare payload for local storage (not S3)
      const payload = {
        training_code: state.trainingCode,
        cleaned_storage_key: preprocessingData.cleaned_storage_key,
        target_column: targetColumn,
        experiment_id: experimentId
      }

      const response = await fetch('/api/execute-training', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let errorMessage = `Training failed: ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.message || errorMessage
        } catch (parseError) {
          const errorText = await response.text()
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const result = await response.json()
      const executionResult = result?.data?.execution_result || {}
      const apiModelResults = executionResult.model_results || executionResult.model_performance || executionResult.results

      setState(prev => ({
        ...prev,
        training: false,
        completed: true,
        executionResult: executionResult,
        actualTime: result.execution_time || 0,
        overallProgress: 100,
        modelResults: apiModelResults ?
          (Array.isArray(apiModelResults) ?
            // Handle new array format from server
            apiModelResults.map((model: any) => ({
              name: model.name,
              accuracy: model.accuracy || 0,
              training_time: model.training_time || 0,
              status: 'completed' as const,
              metrics: model
            })) :
            // Handle legacy object format
            Object.entries(apiModelResults).map(([name, data]: [string, any]) => ({
              name,
              accuracy: data.accuracy || 0,
              training_time: data.training_time || 0,
              status: 'completed' as const,
              metrics: data
            }))
          ) : prev.modelResults
      }))

      toast.success('🎉 All models trained successfully! View results below.', { id: 'training' })

      const trainingData = {
        execution_result: executionResult,  // This already contains model_results from server
        model_results: apiModelResults || state.modelResults,  // Keep for backward compatibility
        training_code: state.trainingCode,
        execution_time: result.execution_time || 0
      }

      onTrainingComplete(trainingData)

    } catch (error: any) {
      setState(prev => ({ ...prev, training: false }))
      toast.error(error.message || 'Training failed', { id: 'training' })
    }
  }

  const downloadTrainingCode = () => {
    const blob = new Blob([state.trainingCode], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `training_code_${experimentId || 'experiment'}.py`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getModelIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'training':
        return <Brain className="w-5 h-5 text-blue-600 animate-pulse" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200'
      case 'training': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (!preprocessingData) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <AlertCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Preprocessing Data</h3>
          <p className="text-gray-600">Complete the preprocessing step first to generate training code.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">

      {/* Training Status */}
      <Card className={`border-2 ${state.completed ? 'border-green-200 bg-green-50/50' : state.training ? 'border-blue-200 bg-blue-50/50' : state.generatingCode ? 'border-purple-200 bg-purple-50/50' : 'border-border'}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {state.generatingCode ? (
                <div className="relative">
                  <Code className="w-6 h-6 text-purple-600" />
                  <Loader2 className="w-4 h-4 text-purple-600 animate-spin absolute -top-1 -right-1" />
                </div>
              ) : state.training ? (
                <Zap className="w-6 h-6 text-blue-600 animate-pulse" />
              ) : state.completed ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <Brain className="w-6 h-6 text-gray-600" />
              )}
              <div>
                <CardTitle className="text-lg">
                  {state.generatingCode ? 'Preparing Training Code' :
                   state.training ? 'Training Models' :
                   state.completed ? 'Training Complete' :
                   'Ready to Train Models'}
                </CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  {state.generatingCode ? 'AI is writing custom training code for your data' :
                   state.training ? 'Training 4 ML algorithms in parallel' :
                   state.completed ? 'All models trained and evaluated' :
                   'Train XGBoost, Random Forest, Decision Tree & Naive Bayes'}
                </p>
              </div>
            </div>
            {state.completed && (
              <Badge className="bg-green-100 text-green-800 border-green-200">
                <CheckCircle className="w-3 h-3 mr-1" />
                Completed
              </Badge>
            )}
            {state.generatingCode && (
              <Badge className="bg-purple-100 text-purple-800 border-purple-200">
                <Code className="w-3 h-3 mr-1" />
                Generating Code
              </Badge>
            )}
          </div>
          {state.generatingCode && (
            <div className="space-y-3 mt-4">
              <p className="text-sm text-purple-700 flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Claude AI is writing custom training code...</span>
              </p>
              <div className="w-full bg-purple-100 rounded-full h-2">
                <div className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full animate-pulse" style={{width: '70%'}}></div>
              </div>
              <p className="text-xs text-purple-600">Analyzing your dataset and generating optimized code</p>
            </div>
          )}
          {state.training && (
            <div className="space-y-2">
              <p className="text-sm text-blue-700">Training models: {state.currentModel}</p>
              <Progress value={state.overallProgress} className="w-full" />
              <p className="text-xs text-blue-600">Overall Progress: {state.overallProgress}%</p>
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {state.modelResults.map((model, index) => {
              const modelIcons = {
                'XGBoost': <Zap className="w-5 h-5" />,
                'Random Forest': <Brain className="w-5 h-5" />,
                'Decision Tree': <BarChart3 className="w-5 h-5" />,
                'Naive Bayes': <Target className="w-5 h-5" />
              }

              return (
                <div key={model.name} className={`relative text-center p-4 bg-white/80 rounded-lg border border-gray-200 hover:shadow-lg transition-all duration-200 ${state.generatingCode ? 'opacity-60' : ''}`}>
                  {state.generatingCode && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-lg">
                      <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
                    </div>
                  )}
                  <div className="flex justify-center mb-3">
                    <div className={`p-2 rounded-lg ${
                      model.status === 'completed' ? 'bg-green-100 text-green-600' :
                      model.status === 'training' ? 'bg-blue-100 text-blue-600' :
                      state.generatingCode ? 'bg-purple-100 text-purple-600' :
                      'bg-gray-100 text-gray-400'
                    }`}>
                      {modelIcons[model.name as keyof typeof modelIcons] || <Brain className="w-5 h-5" />}
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-900 text-sm mb-2">{model.name}</h4>
                  <Badge variant="outline" className={`text-xs mb-2 ${state.generatingCode ? 'bg-purple-100 text-purple-800 border-purple-200' : getStatusColor(model.status)}`}>
                    {state.generatingCode ? 'Preparing...' :
                     model.status === 'pending' ? 'Ready' :
                     model.status === 'training' ? 'Training...' :
                     model.status === 'completed' ? 'Complete' : model.status}
                  </Badge>
                  {model.status === 'completed' && !state.generatingCode && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs font-semibold text-green-600">
                        {(model.accuracy * 100).toFixed(1)}% accuracy
                      </p>
                      <p className="text-xs text-gray-500">
                        {model.training_time.toFixed(1)}s training
                      </p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-gray-500" />
                <p className="text-sm text-gray-600">
                  Target: <span className="font-semibold text-gray-900">{preprocessingData?.target_column || 'Exited'}</span>
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-gray-500" />
                <p className="text-sm text-gray-600">
                  Dataset: <span className="font-medium text-gray-800">Cleaned & Ready</span>
                </p>
              </div>
            </div>
            <div className="flex space-x-3">
              {state.trainingCode && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadTrainingCode}
                  className="border-gray-300 hover:bg-gray-50"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Code
                </Button>
              )}
              <Button
                onClick={executeTraining}
                disabled={state.training || state.generatingCode || !state.trainingCode}
                className={`px-6 py-2 font-semibold ${
                  state.training ? 'bg-blue-600 hover:bg-blue-700' :
                  state.generatingCode ? 'bg-purple-600 hover:bg-purple-700' :
                  'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                } shadow-lg transform transition-all duration-200 hover:scale-105`}
              >
                {state.training ? (
                  <>
                    <Cpu className="w-4 h-4 mr-2 animate-spin" />
                    Training Models...
                  </>
                ) : state.generatingCode ? (
                  <>
                    <Code className="w-4 h-4 mr-2 animate-pulse" />
                    Preparing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Start Training
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Generated Training Code */}
      {state.trainingCode && (
        <Card className="border-purple-200 bg-purple-50/30">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Code className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">AI-Generated Training Code</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">Custom Python code optimized for your dataset</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Badge variant="outline" className="bg-gradient-to-r from-blue-100 to-purple-100 text-purple-700 border-purple-200">
                  🤖 Claude AI Generated
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadTrainingCode}
                  className="border-purple-300 hover:bg-purple-50"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Code
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-gray-100 whitespace-pre-wrap">
                <code>{state.trainingCode}</code>
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Training Results */}
      {state.completed && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-900">Training Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-2xl font-bold text-green-600">{state.modelResults.length}</div>
                <div className="text-sm text-gray-600">models trained</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.max(...state.modelResults.map(m => m.accuracy * 100)).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">best accuracy</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{state.actualTime.toFixed(1)}s</div>
                <div className="text-sm text-gray-600">total time</div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <p className="text-sm text-green-700">
                ✅ Ready for hyperparameter tuning and results comparison
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}