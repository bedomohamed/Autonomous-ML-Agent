import { useState } from 'react'
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

  // Mock model results - in real implementation, this would come from trainingData
  const mockResults: ModelRanking[] = [
    {
      rank: 1,
      name: 'XGBoost',
      accuracy: 0.892,
      precision: 0.876,
      recall: 0.908,
      f1_score: 0.892,
      training_time: 8.4,
      improvement: '+5.2%',
      badge: 'Best Overall'
    },
    {
      rank: 2,
      name: 'Random_Forest',
      accuracy: 0.867,
      precision: 0.854,
      recall: 0.881,
      f1_score: 0.867,
      training_time: 12.1,
      improvement: '+2.8%',
      badge: 'Most Stable'
    },
    {
      rank: 3,
      name: 'Decision_Tree',
      accuracy: 0.834,
      precision: 0.821,
      recall: 0.847,
      f1_score: 0.834,
      training_time: 3.7,
      improvement: '+1.4%',
      badge: 'Fastest'
    },
    {
      rank: 4,
      name: 'Naive_Bayes',
      accuracy: 0.798,
      precision: 0.785,
      recall: 0.812,
      f1_score: 0.798,
      training_time: 2.1,
      improvement: '+0.8%',
      badge: 'Baseline'
    }
  ]

  const [modelResults] = useState<ModelRanking[]>(mockResults)

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

  const downloadBestModel = () => {
    // In real implementation, this would download the actual .pkl file
    toast.success(`${modelResults[0].name} model download started!`)
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
      case 'Most Stable': return 'bg-green-100 text-green-800 border-green-200'
      case 'Fastest': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const bestModel = modelResults[0]
  const avgAccuracy = (modelResults.reduce((sum, model) => sum + model.accuracy, 0) / modelResults.length) * 100
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
          <p className="text-headline font-bold text-yellow-700">{bestModel.name}</p>
          <p className="text-caption text-muted-foreground">
            {(bestModel.accuracy * 100).toFixed(1)}% accuracy
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
          <p className="text-caption text-muted-foreground">Complete pipeline</p>
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
                          <p className="text-caption text-muted-foreground">Model</p>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-auto p-0 text-footnote text-primary"
                            onClick={() => toast.success(`${model.name} model details opened!`)}
                          >
                            View Details
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      </Card>

      {/* Next Steps */}
      <Card className="p-6 bg-gradient-to-r from-primary/5 to-primary/10 border-primary/20 rounded-apple-lg">
        <div className="text-center space-y-4">
          <h3 className="text-headline font-semibold">🎉 Training Complete!</h3>
          <p className="text-body text-muted-foreground">
            Your ML pipeline has successfully trained {modelResults.length} models.
            The best performing model is <strong>{bestModel.name}</strong> with {(bestModel.accuracy * 100).toFixed(1)}% accuracy.
          </p>

          <div className="flex items-center justify-center space-x-3">
            <Button variant="outline" className="flex items-center space-x-2">
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