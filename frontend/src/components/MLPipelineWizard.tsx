import { useState, useCallback } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  CheckCircle,
  Circle,
  ArrowRight,
  ArrowLeft,
  Upload,
  Target,
  BarChart3,
  Code,
  Brain,
  Trophy,
  AlertCircle
} from 'lucide-react'
import FileUpload from './FileUpload'
import ColumnSelector from './ColumnSelector'
import DataAnalysis from './DataAnalysis'
import PreprocessingStep from './PreprocessingStep'
import ModelTraining from './ModelTraining'
import ResultsLeaderboard from './ResultsLeaderboard'
import { FileData } from '../types'

export interface MLPipelineState {
  currentStep: number
  fileData: FileData | null
  targetColumn: string
  analysisData: any | null
  preprocessingData: any | null
  trainingData: any | null
  resultsData: any | null
  experimentId: string | null
}

const PIPELINE_STEPS = [
  {
    id: 1,
    name: 'Upload',
    title: 'Upload Dataset',
    description: 'Upload your CSV file',
    icon: Upload,
    component: 'FileUpload'
  },
  {
    id: 2,
    name: 'Target',
    title: 'Select Target',
    description: 'Choose target column',
    icon: Target,
    component: 'ColumnSelector'
  },
  {
    id: 3,
    name: 'Analyze',
    title: 'Data Analysis',
    description: 'Comprehensive analysis',
    icon: BarChart3,
    component: 'DataAnalysis'
  },
  {
    id: 4,
    name: 'Preprocess',
    title: 'Data Preprocessing',
    description: 'Clean and prepare data',
    icon: Code,
    component: 'PreprocessingStep'
  },
  {
    id: 5,
    name: 'Train',
    title: 'Model Training',
    description: 'Train ML models',
    icon: Brain,
    component: 'ModelTraining'
  },
  {
    id: 6,
    name: 'Results',
    title: 'Results',
    description: 'View model performance',
    icon: Trophy,
    component: 'ResultsLeaderboard'
  }
]

export default function MLPipelineWizard() {
  const [pipelineState, setPipelineState] = useState<MLPipelineState>({
    currentStep: 1,
    fileData: null,
    targetColumn: '',
    analysisData: null,
    preprocessingData: null,
    trainingData: null,
    resultsData: null,
    experimentId: null
  })

  const [stepStates, setStepStates] = useState<Record<number, 'pending' | 'current' | 'completed' | 'error'>>({
    1: 'current',
    2: 'pending',
    3: 'pending',
    4: 'pending',
    5: 'pending',
    6: 'pending'
  })

  const updateStepState = useCallback((stepId: number, state: 'pending' | 'current' | 'completed' | 'error') => {
    setStepStates(prev => ({
      ...prev,
      [stepId]: state
    }))
  }, [])

  const goToStep = useCallback((stepId: number) => {
    // Check if step is accessible
    const canAccess = stepId === 1 || stepStates[stepId - 1] === 'completed'

    if (canAccess) {
      // Update current step
      setPipelineState(prev => ({
        ...prev,
        currentStep: stepId
      }))

      // Update step states
      setStepStates(prev => {
        const newStates = { ...prev }
        Object.keys(newStates).forEach(key => {
          const id = parseInt(key)
          if (id === stepId) {
            newStates[id] = 'current'
          } else if (id < stepId && newStates[id] === 'current') {
            newStates[id] = 'completed'
          }
        })
        return newStates
      })
    }
  }, [stepStates])

  const nextStep = useCallback(() => {
    const nextStepId = pipelineState.currentStep + 1
    if (nextStepId <= PIPELINE_STEPS.length) {
      goToStep(nextStepId)
    }
  }, [pipelineState.currentStep, goToStep])

  const prevStep = useCallback(() => {
    const prevStepId = pipelineState.currentStep - 1
    if (prevStepId >= 1) {
      goToStep(prevStepId)
    }
  }, [pipelineState.currentStep, goToStep])

  const handleFileUpload = useCallback((fileData: FileData) => {
    setPipelineState(prev => ({
      ...prev,
      fileData
    }))
    updateStepState(1, 'completed')
    nextStep()
  }, [updateStepState, nextStep])

  const handleTargetSelection = useCallback((targetColumn: string) => {
    setPipelineState(prev => ({
      ...prev,
      targetColumn
    }))
    updateStepState(2, 'completed')
    nextStep()
  }, [updateStepState, nextStep])

  const handleAnalysisComplete = useCallback((analysisData: any) => {
    setPipelineState(prev => ({
      ...prev,
      analysisData,
      experimentId: analysisData.experiment_id
    }))
    updateStepState(3, 'completed')
    nextStep()
  }, [updateStepState, nextStep])

  const handlePreprocessingComplete = useCallback((preprocessingData: any) => {
    setPipelineState(prev => ({
      ...prev,
      preprocessingData
    }))
    updateStepState(4, 'completed')
    nextStep()
  }, [updateStepState, nextStep])

  const handleTrainingComplete = useCallback((trainingData: any) => {
    setPipelineState(prev => ({
      ...prev,
      trainingData
    }))
    updateStepState(5, 'completed')
    nextStep()
  }, [updateStepState, nextStep])

  const handleResultsComplete = useCallback((resultsData: any) => {
    setPipelineState(prev => ({
      ...prev,
      resultsData
    }))
    updateStepState(6, 'completed')
  }, [updateStepState])

  const currentStepData = PIPELINE_STEPS.find(step => step.id === pipelineState.currentStep)

  const getStepIcon = (step: any, state: string) => {
    const IconComponent = step.icon

    if (state === 'completed') {
      return <CheckCircle size={20} className="text-green-600" />
    } else if (state === 'current') {
      return <IconComponent size={20} className="text-primary" />
    } else if (state === 'error') {
      return <AlertCircle size={20} className="text-red-600" />
    } else {
      return <Circle size={20} className="text-muted-foreground" />
    }
  }

  const getStepColor = (state: string) => {
    switch (state) {
      case 'completed': return 'bg-green-100 border-green-300 text-green-800'
      case 'current': return 'bg-primary/10 border-primary text-primary'
      case 'error': return 'bg-red-100 border-red-300 text-red-800'
      default: return 'bg-muted border-border text-muted-foreground'
    }
  }

  const renderCurrentStep = () => {
    const { currentStep, fileData, targetColumn, analysisData, preprocessingData, trainingData } = pipelineState

    switch (currentStep) {
      case 1:
        return <FileUpload onUploadSuccess={handleFileUpload} />

      case 2:
        return fileData ? (
          <ColumnSelector
            columns={fileData.columns}
            selectedColumn={targetColumn}
            onColumnSelect={handleTargetSelection}
          />
        ) : null

      case 3:
        return fileData && targetColumn ? (
          <DataAnalysis
            storageKey={fileData.storage_key}
            targetColumn={targetColumn}
            onAnalysisComplete={handleAnalysisComplete}
          />
        ) : null

      case 4:
        return analysisData ? (
          <PreprocessingStep
            analysisData={analysisData}
            onPreprocessingComplete={handlePreprocessingComplete}
          />
        ) : null

      case 5:
        return preprocessingData ? (
          <ModelTraining
            preprocessingData={preprocessingData}
            experimentId={pipelineState.experimentId}
            onTrainingComplete={handleTrainingComplete}
          />
        ) : null

      case 6:
        return trainingData ? (
          <ResultsLeaderboard
            trainingData={trainingData}
            experimentId={pipelineState.experimentId}
            onResultsComplete={handleResultsComplete}
          />
        ) : null

      default:
        return <div>Invalid step</div>
    }
  }

  const completedSteps = Object.values(stepStates).filter(state => state === 'completed').length
  const progressPercentage = (completedSteps / PIPELINE_STEPS.length) * 100

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Progress Header */}
      <Card className="p-6 bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20 rounded-apple-lg">
        <div className="space-y-4">
          {/* Overall Progress */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-title font-bold text-foreground">ML Pipeline Wizard</h1>
              <p className="text-body text-muted-foreground">
                {pipelineState.experimentId && (
                  <span className="text-caption mr-2">Experiment: {pipelineState.experimentId}</span>
                )}
                Step {pipelineState.currentStep} of {PIPELINE_STEPS.length}: {currentStepData?.title}
              </p>
            </div>
            <div className="text-right">
              <p className="text-caption text-muted-foreground">Overall Progress</p>
              <p className="text-headline font-bold text-primary">{Math.round(progressPercentage)}%</p>
            </div>
          </div>

          {/* Progress Bar */}
          <Progress value={progressPercentage} className="h-3" />

          {/* Step Navigation */}
          <div className="flex items-center justify-between space-x-2 overflow-x-auto">
            {PIPELINE_STEPS.map((step, index) => {
              const state = stepStates[step.id]
              const isClickable = step.id === 1 || stepStates[step.id - 1] === 'completed'

              return (
                <div key={step.id} className="flex items-center">
                  <button
                    onClick={() => isClickable && goToStep(step.id)}
                    disabled={!isClickable}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-apple border-2 transition-all duration-200 ${getStepColor(state)} ${
                      isClickable ? 'hover:shadow-apple cursor-pointer' : 'cursor-not-allowed opacity-50'
                    }`}
                  >
                    {getStepIcon(step, state)}
                    <div className="text-left">
                      <p className="text-caption font-medium">{step.name}</p>
                      <p className="text-caption-2 opacity-75">{step.description}</p>
                    </div>
                  </button>

                  {index < PIPELINE_STEPS.length - 1 && (
                    <ArrowRight size={16} className="mx-2 text-muted-foreground flex-shrink-0" />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </Card>

      {/* Current Step Content */}
      <div className="min-h-[400px]">
        {renderCurrentStep()}
      </div>

      {/* Navigation Controls */}
      <Card className="p-4 bg-card/50 rounded-apple">
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={pipelineState.currentStep === 1}
            className="flex items-center space-x-2"
          >
            <ArrowLeft size={16} />
            <span>Previous</span>
          </Button>

          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-caption">
              Step {pipelineState.currentStep}/{PIPELINE_STEPS.length}
            </Badge>
          </div>

          <Button
            onClick={nextStep}
            disabled={pipelineState.currentStep === PIPELINE_STEPS.length || stepStates[pipelineState.currentStep] !== 'completed'}
            className="flex items-center space-x-2"
          >
            <span>Next</span>
            <ArrowRight size={16} />
          </Button>
        </div>
      </Card>
    </div>
  )
}