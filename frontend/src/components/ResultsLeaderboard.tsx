import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Trophy,
  Medal,
  Award,
  Download,
  BarChart3,
  TrendingUp,
  Clock,
  Target,
  Zap,
  FileText,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface ResultsLeaderboardProps {
  trainingData: any
  experimentId: string | null
  onResultsComplete: (resultsData: any) => void
}

interface ModelRanking {
  rank: number
  name: string
  accuracy: number
  precision?: number
  recall?: number
  f1_score?: number
  training_time: number
  improvement?: string
  badge?: string
}

export default function ResultsLeaderboard({
  trainingData,
  experimentId,
  onResultsComplete
}: ResultsLeaderboardProps) {
  const [selectedMetric, setSelectedMetric] = useState<'accuracy' | 'f1_score' | 'training_time'>('accuracy')
  const [modelResults, setModelResults] = useState<ModelRanking[]>([])

  // Update model results when trainingData changes
  useEffect(() => {
    const parsedResults = parseModelResults()
    setModelResults(parsedResults)
  }, [trainingData])

  // Parse real results from trainingData
  const parseModelResults = (): ModelRanking[] => {
    const results: ModelRanking[] = []

    // First, check for hyperparameter tuning results (baseline + tuned)
    // Try multiple possible paths for the tuning data
    const tunedResults = trainingData?.tuning_execution?.tuning_summary?.detailed_results ||
                        trainingData?.tuning_summary?.detailed_results ||
                        trainingData?.detailed_results ||
                        trainingData?.tuning_data?.detailed_results ||
                        trainingData?.hyperparameter_results?.detailed_results

    if (tunedResults) {
      Object.entries(tunedResults).forEach(([modelName, data]: [string, any]) => {

        if (data && !data.error) {
          // Add baseline model if exists
          const baseline = data.baseline_results || data.baseline
          if (baseline) {
            results.push({
              rank: results.length + 1,
              name: `${modelName} (Baseline)`,
              accuracy: baseline.accuracy || 0,
              precision: baseline.precision || 0,
              recall: baseline.recall || 0,
              f1_score: baseline.f1_score || 0,
              training_time: baseline.training_time || 0,
              improvement: 'Original',
              badge: 'Baseline'
            })
          }

          // Add tuned model if exists
          const tuned = data.tuned_results || data.tuned
          if (tuned) {
            const baselineF1 = baseline?.f1_score || 0
            const tunedF1 = tuned?.f1_score || 0
            const improvementValue = tunedF1 - baselineF1
            const improvementText = `${improvementValue > 0 ? '+' : ''}${(improvementValue * 100).toFixed(1)}%`

            results.push({
              rank: results.length + 1,
              name: `${modelName} (Tuned)`,
              accuracy: tuned.accuracy || 0,
              precision: tuned.precision || 0,
              recall: tuned.recall || 0,
              f1_score: tuned.f1_score || 0,
              training_time: tuned.training_time || 0,
              improvement: improvementText,
              badge: improvementValue > 0 ? 'Improved' : 'Regressed'
            })
          }
        }
      })
    } else if (trainingData?.execution_result?.model_results) {
      // Use clean parsed model results from server
      const modelResults = trainingData.execution_result.model_results

      // Handle array format (clean parsed results from server)
      if (Array.isArray(modelResults)) {
        modelResults.forEach((model: any) => {
          if (model && model.name) {
            results.push({
              rank: results.length + 1,
              name: model.name,
              accuracy: model.accuracy || 0,
              precision: model.precision || 0,
              recall: model.recall || 0,
              f1_score: model.f1_score || 0,
              training_time: model.training_time || 0,
              improvement: 'Original',
              badge: 'Trained'
            })
          }
        })
      } else if (typeof modelResults === 'object') {
        Object.entries(modelResults).forEach(([modelName, data]: [string, any]) => {
          if (data && typeof data === 'object') {
            results.push({
              rank: results.length + 1,
              name: modelName,
              accuracy: data.accuracy || 0,
              precision: data.precision || 0,
              recall: data.recall || 0,
              f1_score: data.f1_score || 0,
              training_time: data.training_time || 0,
              improvement: 'Original',
              badge: 'Trained'
            })
          }
        })
      }
    } else if (trainingData?.model_results && Array.isArray(trainingData.model_results)) {
      // Handle array format from ModelTraining component

      // Check if all models have zero accuracy (training failed)
      const allZero = trainingData.model_results.every((m: any) => m.accuracy === 0)

      if (allZero) {
        // Return empty array to show proper empty state
        return []
      }

      trainingData.model_results.forEach((model: any) => {
        if (model && model.name) {
          results.push({
            rank: results.length + 1,
            name: model.name,
            accuracy: model.metrics?.accuracy || model.accuracy || 0,
            precision: model.metrics?.precision || 0,
            recall: model.metrics?.recall || 0,
            f1_score: model.metrics?.f1_score || model.metrics?.f1 || 0,
            training_time: model.training_time || 0,
            improvement: 'Original',
            badge: 'Trained'
          })
        }
      })
    }

    // No results found - return empty array

    if (results.length > 0) {
      // Sort by f1_score descending
      results.sort((a, b) => (b.f1_score || 0) - (a.f1_score || 0))
      // Update ranks and assign best badge
      results.forEach((result, index) => {
        result.rank = index + 1
        if (index === 0) {
          result.badge = result.badge === 'Baseline' ? 'Best Baseline' :
                       result.badge === 'Trained' ? 'Best Overall' : 'Best Tuned'
        }
      })
      return results
    }

    return []
  }


  const downloadModelReport = () => {
    const report = `
# ML Model Training Report
Experiment ID: ${experimentId}
Generated: ${new Date().toLocaleString()}

## Model Performance Summary

${modelResults.map(model => `
### ${model.name} (Rank #${model.rank})
- Accuracy: ${(model.accuracy * 100).toFixed(1)}%
- Precision: ${(model.precision! * 100).toFixed(1)}%
- Recall: ${(model.recall! * 100).toFixed(1)}%
- F1-Score: ${(model.f1_score! * 100).toFixed(1)}%
- Training Time: ${model.training_time}s
- Badge: ${model.badge}
`).join('')}

## Training Summary
- Total Models Trained: ${modelResults.length}
- Best Performing Model: ${modelResults[0].name}
- Fastest Training: ${modelResults.reduce((fastest, current) =>
    current.training_time < fastest.training_time ? current : fastest
  ).name}
- Average Accuracy: ${((modelResults.reduce((sum, model) => sum + model.accuracy, 0) / modelResults.length) * 100).toFixed(1)}%
    `

    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `model_report_${experimentId}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success('Model report downloaded!')
  }

  const downloadModel = async (modelName: string) => {
    try {
      toast.loading(`Downloading ${modelName} model...`, { id: 'model-download' })

      // Extract the actual model name from the display name (remove "(Baseline)" or "(Tuned)")
      const actualModelName = modelName.replace(/ \((Baseline|Tuned)\)/, '')

      const response = await fetch(`/api/download-model/${actualModelName}`, {
        method: 'GET',
      })

      if (!response.ok) {
        throw new Error(`Failed to download model: ${response.statusText}`)
      }

      // Get the file blob
      const blob = await response.blob()

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${modelName}_model.pkl`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      toast.success(`${modelName} model downloaded successfully!`, { id: 'model-download' })

    } catch (error) {
      console.error('Error downloading model:', error)
      toast.error(`Failed to download ${modelName} model: ${error instanceof Error ? error.message : 'Unknown error'}`,
        { id: 'model-download' })
    }
  }

  const downloadBestModel = () => {
    downloadModel(modelResults[0].name)
  }


  const tuneHyperparameters = async () => {
    if (!experimentId) {
      toast.error('No experiment ID available')
      return
    }

    try {
      toast.loading('Generating hyperparameter tuning code...', { id: 'tune-loading' })

      // Get top 2 models for hyperparameter tuning
      const topModels = modelResults
        .slice(0, 2)
        .map(model => model.name)

      // Prepare baseline results for the API
      const baselineResults = modelResults.reduce((acc, model) => {
        acc[model.name] = {
          accuracy: model.accuracy,
          f1_score: model.f1_score,
          precision: model.precision,
          recall: model.recall,
          training_time: model.training_time
        }
        return acc
      }, {} as Record<string, any>)

      const response = await fetch('/api/tune-hyperparameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          baseline_results: baselineResults,
          top_models: topModels,
          experiment_id: experimentId
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to generate hyperparameter tuning code: ${response.statusText}`)
      }

      const result = await response.json()

      toast.success('Hyperparameter tuning code generated!', { id: 'tune-loading' })

      // Now execute the hyperparameter tuning code in E2B
      toast.loading('Executing hyperparameter tuning...', { id: 'tune-execution' })

      const executionResponse = await fetch('/api/execute-hyperparameter-tuning', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tuning_storage_key: result.tuning_storage_key,
          cleaned_data_key: 'cleaned_data.csv',
          experiment_id: experimentId
        }),
      })

      if (!executionResponse.ok) {
        throw new Error(`Failed to execute hyperparameter tuning: ${executionResponse.statusText}`)
      }

      const executionResult = await executionResponse.json()

      if (executionResult.execution_status === 'completed') {
        toast.success('Hyperparameter tuning completed successfully!', { id: 'tune-execution' })

        // Show improvement results if available
        if (executionResult.tuning_summary?.improvements?.average_f1_improvement) {
          const avgImprovement = (executionResult.tuning_summary.improvements.average_f1_improvement * 100).toFixed(2)
          toast.success(`Average F1-Score improved by ${avgImprovement}%!`)
        }

        // Update parent component with both generation and execution results
        if (onResultsComplete) {
          const updatedData = {
            ...trainingData,
            hyperparameter_tuning: result,
            tuning_execution: executionResult
          }
          onResultsComplete(updatedData)
        }
      } else {
        toast.error('Hyperparameter tuning execution failed', { id: 'tune-execution' })
        console.error('Tuning execution failed:', executionResult)
      }

    } catch (error) {
      console.error('Error generating hyperparameter tuning code:', error)
      toast.error(`Failed to generate tuning code: ${error instanceof Error ? error.message : 'Unknown error'}`,
        { id: 'tune-loading' })
    }
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Trophy size={20} className="text-yellow-600" />
      case 2: return <Medal size={20} className="text-gray-500" />
      case 3: return <Award size={20} className="text-amber-600" />
      default: return <div className="w-5 h-5 rounded-full bg-slate-300 flex items-center justify-center text-xs font-bold text-slate-600">
        {rank}
      </div>
    }
  }

  const getBadgeColor = (badge: string) => {
    switch (badge) {
      case 'Best Overall': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'Best Baseline': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'Best Tuned': return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'Trained': return 'bg-slate-100 text-slate-800 border-slate-200'
      case 'Improved': return 'bg-green-100 text-green-800 border-green-200'
      case 'Regressed': return 'bg-red-100 text-red-800 border-red-200'
      case 'Baseline': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'Baseline Better': return 'bg-red-100 text-red-800 border-red-200'
      case 'Tuned': return 'bg-green-100 text-green-800 border-green-200'
      case 'Most Stable': return 'bg-green-100 text-green-800 border-green-200'
      case 'Fastest': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const bestModel = modelResults.length > 0 ? modelResults[0] : null
  const avgAccuracy = modelResults.length > 0 ? (modelResults.reduce((sum, model) => sum + model.accuracy, 0) / modelResults.length) * 100 : 0
  const totalTrainingTime = modelResults.reduce((sum, model) => sum + model.training_time, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <Trophy size={20} className="text-yellow-600" />
          </div>
          <div>
            <h2 className="text-title2 font-bold text-foreground">Results Leaderboard</h2>
            <p className="text-footnote text-muted-foreground">
              Model performance comparison and rankings
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button onClick={downloadModelReport} variant="outline" size="sm">
            <FileText size={14} className="mr-1" />
            Report
          </Button>
          <Button onClick={downloadBestModel} size="sm">
            <Download size={14} className="mr-1" />
            Best Model
          </Button>
        </div>
      </div>

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200 rounded-apple">
          <div className="flex items-center space-x-2 mb-2">
            <Trophy size={16} className="text-yellow-600" />
            <h3 className="text-callout font-medium">Champion</h3>
          </div>
          <p className="text-headline font-bold text-yellow-700">
            {bestModel ? bestModel.name : 'No training results'}
          </p>
          <p className="text-caption text-muted-foreground">
            {bestModel ? `${(bestModel.accuracy * 100).toFixed(1)}% accuracy` : 'Complete ML pipeline first'}
          </p>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200 rounded-apple">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp size={16} className="text-green-600" />
            <h3 className="text-callout font-medium">Avg Performance</h3>
          </div>
          <p className="text-headline font-bold text-green-600">{avgAccuracy.toFixed(1)}%</p>
          <p className="text-caption text-muted-foreground">Across all models</p>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 rounded-apple">
          <div className="flex items-center space-x-2 mb-2">
            <Clock size={16} className="text-blue-600" />
            <h3 className="text-callout font-medium">Total Time</h3>
          </div>
          <p className="text-headline font-bold text-blue-600">{totalTrainingTime.toFixed(1)}s</p>
          <p className="text-caption text-muted-foreground">Training duration</p>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200 rounded-apple">
          <div className="flex items-center space-x-2 mb-2">
            <Zap size={16} className="text-purple-600" />
            <h3 className="text-callout font-medium">Models Trained</h3>
          </div>
          <p className="text-headline font-bold text-purple-600">{modelResults.length}</p>
          <p className="text-caption text-muted-foreground">
            {modelResults.length > 0 ? 'Models trained' : 'Training pending'}
          </p>
        </Card>
      </div>

      {/* Metric Selector */}
      <Card className="p-4 rounded-apple">
        <div className="flex items-center justify-between">
          <h3 className="text-headline font-medium flex items-center">
            <BarChart3 size={16} className="mr-2" />
            Sort by Metric
          </h3>
          <div className="flex items-center space-x-2">
            {['accuracy', 'f1_score', 'training_time'].map((metric) => (
              <Button
                key={metric}
                onClick={() => setSelectedMetric(metric as any)}
                variant={selectedMetric === metric ? 'default' : 'outline'}
                size="sm"
                className="text-caption"
              >
                {metric === 'accuracy' && <Target size={12} className="mr-1" />}
                {metric === 'f1_score' && <TrendingUp size={12} className="mr-1" />}
                {metric === 'training_time' && <Clock size={12} className="mr-1" />}
                {metric.replace('_', ' ').toUpperCase()}
              </Button>
            ))}
          </div>
        </div>
      </Card>

      {/* Model Rankings */}
      <Card className="p-6 rounded-apple-lg">
        <div className="space-y-4">
          <h3 className="text-headline font-semibold">Model Performance Rankings</h3>

          {modelResults.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Trophy size={24} className="text-gray-400" />
              </div>
              <p className="text-body text-muted-foreground mb-2">No model training results yet</p>
              <p className="text-caption text-muted-foreground">
                Complete the ML pipeline training to see model performance rankings here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
            {modelResults
              .sort((a, b) => {
                if (selectedMetric === 'training_time') {
                  return a.training_time - b.training_time // Faster is better
                }
                return (b[selectedMetric] || 0) - (a[selectedMetric] || 0) // Higher is better
              })
              .map((model, index) => {
                const displayRank = index + 1
                return (
                  <div
                    key={model.name}
                    className={`p-4 rounded-apple border-2 transition-all duration-200 ${
                      displayRank === 1
                        ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200 shadow-apple-lg'
                        : displayRank === 2
                        ? 'bg-gradient-to-r from-slate-50 to-gray-50 border-gray-200'
                        : displayRank === 3
                        ? 'bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200'
                        : 'bg-card border-border'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getRankIcon(displayRank)}
                          <div>
                            <h4 className="text-callout font-semibold">{model.name}</h4>
                            <Badge variant="outline" className={`text-caption ${getBadgeColor(model.badge!)}`}>
                              {model.badge}
                            </Badge>
                          </div>
                        </div>

                        {model.improvement && (
                          <Badge variant="secondary" className="bg-green-100 text-green-800 text-caption">
                            {model.improvement}
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center space-x-6">
                        {/* Metrics Display */}
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <p className="text-caption text-muted-foreground">Accuracy</p>
                            <p className="text-footnote font-bold text-green-600">
                              {(model.accuracy * 100).toFixed(1)}%
                            </p>
                            <Progress
                              value={model.accuracy * 100}
                              className="w-16 h-1 mt-1"
                            />
                          </div>

                          <div>
                            <p className="text-caption text-muted-foreground">F1-Score</p>
                            <p className="text-footnote font-bold text-blue-600">
                              {(model.f1_score! * 100).toFixed(1)}%
                            </p>
                            <Progress
                              value={model.f1_score! * 100}
                              className="w-16 h-1 mt-1"
                            />
                          </div>

                          <div>
                            <p className="text-caption text-muted-foreground">Time (s)</p>
                            <p className="text-footnote font-bold text-purple-600">
                              {model.training_time.toFixed(1)}s
                            </p>
                            <div className="w-16 h-1 bg-purple-100 rounded-full mt-1">
                              <div
                                className="h-full bg-purple-500 rounded-full"
                                style={{
                                  width: `${Math.min(100, (model.training_time / Math.max(...modelResults.map(m => m.training_time))) * 100)}%`
                                }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Detailed Metrics */}
                    <div className="mt-3 pt-3 border-t border-border/50">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div>
                          <p className="text-caption text-muted-foreground">Precision</p>
                          <p className="text-footnote font-medium">{(model.precision! * 100).toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-caption text-muted-foreground">Recall</p>
                          <p className="text-footnote font-medium">{(model.recall! * 100).toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-caption text-muted-foreground">Rank</p>
                          <p className="text-footnote font-medium">#{displayRank}</p>
                        </div>
                        <div>
                          <p className="text-caption text-muted-foreground">Download</p>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-auto p-0 text-footnote text-primary flex items-center space-x-1"
                            onClick={() => downloadModel(model.name)}
                          >
                            <Download size={12} />
                            <span>Model</span>
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </Card>

      {/* Next Steps */}
      <Card className="p-6 bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20 rounded-apple-lg">
        <div className="text-center space-y-4">
          <h3 className="text-headline font-semibold">
            {modelResults.length > 0 ? '🎉 Training Complete!' : '🚀 Ready for ML Training'}
          </h3>
          <p className="text-body text-muted-foreground">
            {modelResults.length > 0
              ? `Your ML pipeline has successfully trained ${modelResults.length} model${modelResults.length > 1 ? 's' : ''}. The best performing model is ${bestModel?.name} with ${(bestModel?.accuracy * 100).toFixed(1)}% accuracy.`
              : 'Complete the ML pipeline training first, then use "Tune Hyperparameters" to optimize your models and compare baseline vs tuned performance.'
            }
          </p>

          <div className="flex items-center justify-center space-x-3">
            <Button
              variant="outline"
              className="flex items-center space-x-2"
              onClick={tuneHyperparameters}
            >
              <RefreshCw size={16} />
              <span>Tune Hyperparameters</span>
            </Button>
            <Button className="flex items-center space-x-2">
              <Download size={16} />
              <span>Deploy Best Model</span>
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}