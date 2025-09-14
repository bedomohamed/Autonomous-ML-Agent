import { useState, useEffect, useCallback, useRef } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  BarChart3,
  Target,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Database,
  Zap,
  FileText,
  Brain
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAnalyzeDataset } from '../hooks/api'

interface DataAnalysisProps {
  storageKey: string
  targetColumn: string
  onAnalysisComplete: (analysisData: any) => void
}

interface AnalysisData {
  experiment_id: string
  analysis: any
  preprocessing_prompt: string
  dataset_info: any
}

export default function DataAnalysis({
  storageKey,
  targetColumn,
  onAnalysisComplete
}: DataAnalysisProps) {
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [currentStep, setCurrentStep] = useState('')
  const isAnalyzing = useRef(false)

  const analyzeMutation = useAnalyzeDataset()

  const startAnalysis = useCallback(async () => {
    if (isAnalyzing.current) return // Prevent duplicate calls

    isAnalyzing.current = true
    setAnalysisProgress(0)
    setCurrentStep('Initializing dataset analysis...')

    // Simulate progress steps
    const progressSteps = [
      { progress: 10, step: 'Loading dataset from S3...' },
      { progress: 25, step: 'Analyzing data types and structure...' },
      { progress: 40, step: 'Detecting missing data patterns...' },
      { progress: 55, step: 'Identifying data quality issues...' },
      { progress: 70, step: 'Analyzing target variable distribution...' },
      { progress: 85, step: 'Generating feature recommendations...' },
      { progress: 100, step: 'Finalizing analysis report...' }
    ]

    for (const { progress, step } of progressSteps) {
      setAnalysisProgress(progress)
      setCurrentStep(step)
      await new Promise(resolve => setTimeout(resolve, 800))
    }

    console.log('DataAnalysis - sending request with:', { storage_key: storageKey, target_column: targetColumn })

    analyzeMutation.mutate(
      {
        storageKey,
        targetColumn
      },
      {
        onSuccess: (response) => {
          if (response.success && response.data) {
            setAnalysisData(response.data)
            onAnalysisComplete(response.data)
            toast.success('Dataset analysis completed!')
          }
        },
        onError: (error: any) => {
          console.error('Analysis error:', error)
          toast.error(error.response?.data?.error || 'Analysis failed')
        },
        onSettled: () => {
          setAnalysisProgress(0)
          setCurrentStep('')
          isAnalyzing.current = false
        }
      }
    )
  }, [storageKey, targetColumn, onAnalysisComplete, analyzeMutation])

  useEffect(() => {
    if (storageKey && targetColumn && !analyzeMutation.isPending && !isAnalyzing.current) {
      startAnalysis()
    }
  }, [storageKey, targetColumn, startAnalysis])

  if (analyzeMutation.isPending) {
    return (
      <Card className="p-8 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 rounded-apple-lg">
        <div className="text-center space-y-6">
          <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
            <Brain size={32} className="text-blue-600 animate-pulse" />
          </div>

          <div className="space-y-2">
            <h3 className="text-title2 font-semibold text-blue-900">Analyzing Dataset</h3>
            <p className="text-body text-blue-700">{currentStep}</p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-caption text-blue-600">
              <span>Analysis Progress</span>
              <span>{analysisProgress}%</span>
            </div>
            <Progress value={analysisProgress} className="w-full h-3" />
          </div>

          <div className="flex justify-center space-x-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      </Card>
    )
  }

  if (!analysisData) return null

  const { analysis, dataset_info } = analysisData

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
            <BarChart3 size={20} className="text-green-600" />
          </div>
          <div>
            <h2 className="text-title2 font-bold text-foreground">Dataset Analysis Complete</h2>
            <p className="text-footnote text-muted-foreground">
              Experiment ID: {analysisData.experiment_id}
            </p>
          </div>
        </div>

        <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
          <CheckCircle size={14} className="mr-1" />
          Analysis Ready
        </Badge>
      </div>

      {/* Dataset Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 bg-gradient-to-br from-card to-card/50 rounded-apple">
          <div className="flex items-center space-x-3">
            <Database size={20} className="text-blue-600" />
            <div>
              <p className="text-caption text-muted-foreground">Dataset Size</p>
              <p className="text-callout font-semibold">
                {analysis.basic_info.shape.rows.toLocaleString()} rows × {analysis.basic_info.shape.columns} columns
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-card to-card/50 rounded-apple">
          <div className="flex items-center space-x-3">
            <Target size={20} className="text-purple-600" />
            <div>
              <p className="text-caption text-muted-foreground">Target Variable</p>
              <p className="text-callout font-semibold">{dataset_info.target_column}</p>
              <Badge variant="outline" className="mt-1 text-caption">
                {dataset_info.task_type}
              </Badge>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-card to-card/50 rounded-apple">
          <div className="flex items-center space-x-3">
            <FileText size={20} className="text-green-600" />
            <div>
              <p className="text-caption text-muted-foreground">Memory Usage</p>
              <p className="text-callout font-semibold">
                {analysis.basic_info.memory_usage_mb} MB
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Data Quality Overview */}
      <Card className="p-6 rounded-apple-lg">
        <h3 className="text-headline font-semibold mb-4 flex items-center">
          <AlertTriangle size={20} className="mr-2 text-orange-600" />
          Data Quality Assessment
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Missing Data */}
          <div className="space-y-3">
            <h4 className="text-callout font-medium">Missing Data</h4>
            {analysis.missing_data_info.total_missing === 0 ? (
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle size={16} />
                <span className="text-footnote">No missing data detected</span>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-footnote text-muted-foreground">
                  {analysis.missing_data_info.total_missing} missing values
                  ({analysis.missing_data_info.percentage_missing}%)
                </p>
                {Object.entries(analysis.missing_data_info.columns_with_missing || {})
                  .slice(0, 3)
                  .map(([col, info]: [string, any]) => (
                    <div key={col} className="flex justify-between text-caption">
                      <span>{col}</span>
                      <span className="text-orange-600">{info.percentage}%</span>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Data Quality Issues */}
          <div className="space-y-3">
            <h4 className="text-callout font-medium">Quality Issues</h4>
            {analysis.data_quality_issues.length === 0 ? (
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle size={16} />
                <span className="text-footnote">No major issues detected</span>
              </div>
            ) : (
              <div className="space-y-2">
                {analysis.data_quality_issues.slice(0, 3).map((issue: any, idx: number) => (
                  <div key={idx} className="flex items-start space-x-2">
                    <AlertTriangle size={14} className="text-orange-500 mt-0.5" />
                    <div>
                      <p className="text-caption font-medium">{issue.type}</p>
                      <p className="text-caption text-muted-foreground">
                        {issue.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Target Variable Analysis */}
      <Card className="p-6 rounded-apple-lg">
        <h3 className="text-headline font-semibold mb-4 flex items-center">
          <TrendingUp size={20} className="mr-2 text-blue-600" />
          Target Variable Analysis
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-callout font-medium">Task Type</span>
              <Badge variant={analysis.target_analysis.task_type === 'classification' ? 'default' : 'secondary'}>
                {analysis.target_analysis.task_type}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-footnote text-muted-foreground">Unique Values</span>
              <span className="text-footnote font-medium">
                {analysis.target_analysis.unique_values}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-footnote text-muted-foreground">Missing Values</span>
              <span className="text-footnote font-medium">
                {analysis.target_analysis.null_count} ({analysis.target_analysis.null_percentage}%)
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {analysis.target_analysis.task_type === 'classification' ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-footnote text-muted-foreground">Number of Classes</span>
                  <span className="text-footnote font-medium">
                    {analysis.target_analysis.num_classes}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-footnote text-muted-foreground">Class Balance</span>
                  <Badge variant={analysis.target_analysis.is_balanced ? 'default' : 'destructive'}>
                    {analysis.target_analysis.is_balanced ? 'Balanced' : 'Imbalanced'}
                  </Badge>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-footnote text-muted-foreground">Range</span>
                  <span className="text-footnote font-medium">
                    {analysis.target_analysis.min_value?.toFixed(2)} - {analysis.target_analysis.max_value?.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-footnote text-muted-foreground">Distribution</span>
                  <span className="text-footnote font-medium">
                    {analysis.target_analysis.distribution_type}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Feature Recommendations */}
      {analysis.feature_recommendations && analysis.feature_recommendations.length > 0 && (
        <Card className="p-6 rounded-apple-lg">
          <h3 className="text-headline font-semibold mb-4 flex items-center">
            <Zap size={20} className="mr-2 text-yellow-600" />
            Feature Engineering Recommendations
          </h3>

          <div className="space-y-3">
            {analysis.feature_recommendations.slice(0, 3).map((rec: any, idx: number) => (
              <div key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded-apple">
                <div className="flex items-start space-x-2">
                  <Badge variant="outline" className="mt-0.5 text-caption">
                    {rec.priority}
                  </Badge>
                  <div>
                    <p className="text-footnote font-medium">{rec.type}</p>
                    <p className="text-caption text-muted-foreground mt-1">
                      {rec.suggestion}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Next Steps */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          className="px-8 bg-primary hover:bg-primary/90 text-primary-foreground rounded-apple shadow-apple hover:shadow-apple-lg transition-all duration-200"
          onClick={() => {
            toast.success('Ready for preprocessing!')
            // This would trigger the next step in the pipeline
          }}
        >
          <Brain size={20} className="mr-2" />
          Proceed to Preprocessing
        </Button>
      </div>
    </div>
  )
}