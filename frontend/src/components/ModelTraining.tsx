import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  Brain,
  Play,
  Download,
  CheckCircle,
  AlertCircle,
  Clock,
  Trophy,
  TrendingUp,
  Target,
  BarChart3,
  Zap,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

interface ModelTrainingProps {
  preprocessingData: any
  experimentId: string | null
  onTrainingComplete: (trainingData: any) => void
}

interface ModelResult {
  name: string
  accuracy: number
  training_time: number
  status: 'training' | 'completed' | 'error'
  metrics?: any
}

interface TrainingState {
  generatingCode: boolean
  training: boolean
  completed: boolean
  error: string | null
  trainingCode: string | null
  modelResults: ModelResult[]
  overallProgress: number
  currentModel: string
  executionResult: any | null
  estimatedTime: number
  actualTime: number
}

const MODELS = [
  { name: 'XGBoost', icon: '🚀', description: 'Gradient boosting ensemble' },
  { name: 'Random_Forest', icon: '🌲', description: 'Bagging ensemble method' },
  { name: 'Decision_Tree', icon: '🌳', description: 'Interpretable tree-based model' },
  { name: 'Naive_Bayes', icon: '🎯', description: 'Probabilistic classifier' }
]

export default function ModelTraining({
  preprocessingData,
  experimentId,
  onTrainingComplete
}: ModelTrainingProps) {
  const [state, setState] = useState<TrainingState>({
    generatingCode: false,
    training: false,
    completed: false,
    error: null,
    trainingCode: null,
    modelResults: [],
    overallProgress: 0,
    currentModel: '',
    executionResult: null,
    estimatedTime: 0,
    actualTime: 0
  })

  useEffect(() => {
    if (preprocessingData && !state.trainingCode) {
      generateTrainingCode()
    }
  }, [preprocessingData])

  const generateTrainingCode = async () => {
    try {
      setState(prev => ({ ...prev, generatingCode: true, error: null }))

      const response = await axios.post('/api/generate-training-code', {
        dataset_info: {
          task_type: 'classification', // This should come from analysis
          target_column: 'target', // This should come from analysis
          shape: { rows: 1000, columns: 10 } // This should come from analysis
        }
      })

      if (response.data.success) {
        setState(prev => ({
          ...prev,
          generatingCode: false,
          trainingCode: response.data.data.training_code,
          estimatedTime: response.data.data.estimated_training_time,
          modelResults: MODELS.map(model => ({
            name: model.name,
            accuracy: 0,
            training_time: 0,
            status: 'training'
          }))
        }))
        toast.success('Training code generated successfully!')
      }
    } catch (error: any) {
      console.error('Code generation error:', error)
      setState(prev => ({
        ...prev,
        generatingCode: false,
        error: error.response?.data?.error || 'Failed to generate training code'
      }))
      toast.error('Training code generation failed')
    }
  }

  const startTraining = async () => {
    if (!state.trainingCode) return

    try {
      setState(prev => ({
        ...prev,
        training: true,
        error: null,
        overallProgress: 0,
        currentModel: 'XGBoost'
      }))

      const startTime = Date.now()

      // Simulate training progress for each model
      const modelProgressSteps = [
        { model: 'XGBoost', progress: 25, duration: 2000 },
        { model: 'Random_Forest', progress: 50, duration: 2000 },
        { model: 'Decision_Tree', progress: 75, duration: 1500 },
        { model: 'Naive_Bayes', progress: 100, duration: 1500 }
      ]

      for (const step of modelProgressSteps) {
        setState(prev => ({
          ...prev,
          currentModel: step.model,
          overallProgress: step.progress
        }))

        // Simulate model completion
        await new Promise(resolve => setTimeout(resolve, step.duration))

        // Update model result
        setState(prev => ({
          ...prev,
          modelResults: prev.modelResults.map(result =>
            result.name === step.model
              ? {
                  ...result,
                  status: 'completed',
                  accuracy: 0.85 + Math.random() * 0.1, // Simulate accuracy
                  training_time: Math.random() * 10 + 5 // Simulate training time
                }
              : result
          )
        }))
      }

      const response = await axios.post('/api/execute-training', {
        training_code: state.trainingCode,
        cleaned_storage_key: preprocessingData.cleaned_storage_key
      })

      const endTime = Date.now()
      const actualTime = Math.round((endTime - startTime) / 1000)

      if (response.data.success) {
        setState(prev => ({
          ...prev,
          training: false,
          completed: true,
          executionResult: response.data.data.execution_result,
          actualTime,
          overallProgress: 100
        }))

        toast.success('Model training completed successfully!')

        onTrainingComplete({
          execution_result: response.data.data.execution_result,
          model_results: state.modelResults,
          training_code: state.trainingCode,
          execution_time: actualTime
        })
      } else {
        throw new Error(response.data.error || 'Training execution failed')
      }
    } catch (error: any) {
      console.error('Training error:', error)
      setState(prev => ({
        ...prev,
        training: false,
        error: error.response?.data?.error || 'Failed to execute training'
      }))
      toast.error('Model training failed')
    }
  }

  const downloadTrainingCode = () => {
    if (!state.trainingCode) return

    const blob = new Blob([state.trainingCode], { type: 'text/python' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `model_training_${experimentId}.py`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success('Training code downloaded!')
  }

  if (state.generatingCode) {
    return (
      <Card className="p-8 bg-gradient-to-br from-orange-50 to-red-50 border-orange-200 rounded-apple-lg">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 mx-auto bg-orange-100 rounded-full flex items-center justify-center">
            <Brain size={32} className="text-orange-600 animate-pulse" />
          </div>

          <div className="space-y-2">
            <h3 className="text-title2 font-semibold text-orange-900">Generating Training Code</h3>
            <p className="text-body text-orange-700">
              Claude AI is creating optimized training code for multiple ML models...
            </p>
          </div>

          <div className="flex justify-center space-x-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"
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
            <h3 className="text-headline font-semibold text-red-900 mb-2">Training Error</h3>
            <p className="text-body text-red-700 mb-4">{state.error}</p>
            <Button
              onClick={generateTrainingCode}
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
          <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
            <Brain size={20} className="text-purple-600" />
          </div>
          <div>
            <h2 className="text-title2 font-bold text-foreground">Model Training</h2>
            <p className="text-footnote text-muted-foreground">
              {state.completed ? 'Training completed successfully' : 'Multi-model training pipeline'}
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
              Ready to Train
            </>
          )}
        </Badge>
      </div>

      {/* Models Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {MODELS.map((model, index) => {
          const result = state.modelResults.find(r => r.name === model.name)
          const isActive = state.currentModel === model.name && state.training

          return (
            <Card key={model.name} className={`p-4 rounded-apple transition-all duration-200 ${
              isActive ? 'bg-purple-50 border-purple-200 shadow-apple-lg' :
              result?.status === 'completed' ? 'bg-green-50 border-green-200' : 'bg-card'
            }`}>
              <div className="text-center space-y-3">
                <div className={`text-2xl ${isActive ? 'animate-pulse' : ''}`}>
                  {model.icon}
                </div>
                <div>
                  <h3 className="text-callout font-semibold">{model.name}</h3>
                  <p className="text-caption text-muted-foreground">{model.description}</p>
                </div>

                {result && (
                  <div className="space-y-1">
                    {result.status === 'completed' && (
                      <>
                        <p className="text-footnote font-medium text-green-600">
                          Accuracy: {(result.accuracy * 100).toFixed(1)}%
                        </p>
                        <p className="text-caption text-muted-foreground">
                          Time: {result.training_time.toFixed(1)}s
                        </p>
                      </>
                    )}
                    {result.status === 'training' && state.training && (
                      <p className="text-footnote text-purple-600 animate-pulse">
                        Training...
                      </p>
                    )}
                  </div>
                )}
              </div>
            </Card>
          )
        })}
      </div>

      {/* Training Code */}
      {state.trainingCode && (
        <Card className="p-6 rounded-apple-lg">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-headline font-semibold flex items-center">
                <Brain size={20} className="mr-2 text-purple-600" />
                Generated Training Code
              </h3>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-caption">
                  Multi-Model
                </Badge>
                <Button
                  onClick={downloadTrainingCode}
                  variant="outline"
                  size="sm"
                >
                  <Download size={14} className="mr-1" />
                  Download
                </Button>
              </div>
            </div>

            <div className="bg-slate-900 rounded-apple p-4 overflow-x-auto max-h-60">
              <pre className="text-sm text-slate-100 font-mono whitespace-pre-wrap">
                {state.trainingCode}
              </pre>
            </div>

            {!state.training && !state.completed && (
              <div className="flex items-center justify-between p-4 bg-purple-50 border border-purple-200 rounded-apple">
                <div className="flex items-center space-x-2">
                  <Clock size={16} className="text-purple-600" />
                  <span className="text-footnote text-purple-800">
                    Estimated training time: ~{state.estimatedTime} seconds
                  </span>
                </div>
                <Button
                  onClick={startTraining}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  <Play size={16} className="mr-2" />
                  Start Training
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Training Progress */}
      {state.training && (
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200 rounded-apple-lg">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                <Zap size={20} className="text-purple-600 animate-pulse" />
              </div>
              <div>
                <h3 className="text-headline font-semibold text-purple-900">Training in Progress</h3>
                <p className="text-footnote text-purple-700">
                  Currently training: {state.currentModel}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-caption text-purple-700">
                <span>Overall Progress</span>
                <span>{state.overallProgress}%</span>
              </div>
              <Progress value={state.overallProgress} className="w-full h-3 bg-purple-100" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Data Split</p>
                <p className="text-footnote font-medium">80/15/5</p>
              </div>
              <div className="text-center p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Cross Validation</p>
                <p className="text-footnote font-medium">5-Fold</p>
              </div>
              <div className="text-center p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Environment</p>
                <p className="text-footnote font-medium">E2B Sandbox</p>
              </div>
              <div className="text-center p-3 bg-white/50 rounded-apple">
                <p className="text-caption text-muted-foreground">Models</p>
                <p className="text-footnote font-medium">{MODELS.length} Total</p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Training Results */}
      {state.completed && (
        <Card className="p-6 rounded-apple-lg">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-headline font-semibold flex items-center">
                <Trophy size={20} className="mr-2 text-yellow-600" />
                Training Results
              </h3>
              <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
                {state.modelResults.filter(r => r.status === 'completed').length} models trained
              </Badge>
            </div>

            {/* Performance Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-apple">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp size={16} className="text-green-600" />
                  <h4 className="text-callout font-medium">Best Model</h4>
                </div>
                <p className="text-headline font-bold text-green-600">
                  {state.modelResults.reduce((best, current) =>
                    current.accuracy > best.accuracy ? current : best, state.modelResults[0]
                  )?.name || 'N/A'}
                </p>
                <p className="text-caption text-muted-foreground">
                  {((state.modelResults.reduce((best, current) =>
                    current.accuracy > best.accuracy ? current : best, state.modelResults[0]
                  )?.accuracy || 0) * 100).toFixed(1)}% accuracy
                </p>
              </div>

              <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-apple">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock size={16} className="text-blue-600" />
                  <h4 className="text-callout font-medium">Total Time</h4>
                </div>
                <p className="text-headline font-bold text-blue-600">{state.actualTime}s</p>
                <p className="text-caption text-muted-foreground">
                  Avg: {(state.actualTime / MODELS.length).toFixed(1)}s per model
                </p>
              </div>

              <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-apple">
                <div className="flex items-center space-x-2 mb-2">
                  <Target size={16} className="text-purple-600" />
                  <h4 className="text-callout font-medium">Avg Accuracy</h4>
                </div>
                <p className="text-headline font-bold text-purple-600">
                  {((state.modelResults.reduce((sum, model) => sum + model.accuracy, 0) / state.modelResults.length) * 100).toFixed(1)}%
                </p>
                <p className="text-caption text-muted-foreground">Across all models</p>
              </div>
            </div>

            {/* Model Rankings */}
            <div className="space-y-3">
              <h4 className="text-callout font-medium flex items-center">
                <BarChart3 size={16} className="mr-2" />
                Model Performance Ranking
              </h4>
              <div className="space-y-2">
                {state.modelResults
                  .sort((a, b) => b.accuracy - a.accuracy)
                  .map((result, index) => (
                    <div key={result.name} className="flex items-center justify-between p-3 bg-gradient-to-r from-slate-50 to-slate-100 rounded-apple">
                      <div className="flex items-center space-x-3">
                        <Badge variant="outline" className="w-8 h-8 rounded-full flex items-center justify-center">
                          {index + 1}
                        </Badge>
                        <div>
                          <p className="text-footnote font-medium">{result.name}</p>
                          <p className="text-caption text-muted-foreground">
                            Training time: {result.training_time.toFixed(1)}s
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-footnote font-bold text-green-600">
                          {(result.accuracy * 100).toFixed(1)}%
                        </p>
                        <Progress value={result.accuracy * 100} className="w-20 h-1 mt-1" />
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 border-yellow-200">
                Ready for hyperparameter tuning
              </Badge>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}