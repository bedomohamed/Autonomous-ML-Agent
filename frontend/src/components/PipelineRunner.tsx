import { useState } from 'react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { FileData, ProcessingResult } from '../types'
import { Play, FileText, Target, BarChart3, Brain, CheckCircle, Info } from 'lucide-react'

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
  const [currentStep, setCurrentStep] = useState<number>(0)

  const steps = [
    'Analyzing dataset structure',
    'Generating preprocessing code with Claude AI',
    'Executing code in secure sandbox',
    'Preparing cleaned dataset',
    'Finalizing results'
  ]

  const runPipeline = async () => {
    setProcessing(true)
    setCurrentStep(0)
    setStatus('Initializing preprocessing pipeline...')

    try {
      setCurrentStep(1)
      setStatus('Generating preprocessing code with Claude...')
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing time

      setCurrentStep(2)
      const response = await axios.post('/api/preprocess', {
        storage_key: fileData.storage_key,
        target_column: targetColumn,
      })

      if (response.data.success) {
        setCurrentStep(3)
        setStatus('Fetching download URL...')

        const downloadResponse = await axios.get(`/api/download/${encodeURIComponent(response.data.data.processed_storage_key.replace('/', '__'))}`)

        setCurrentStep(4)
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
      setCurrentStep(0)
    }
  }

  return (
    <div className="space-y-6">
      {/* Configuration Card */}
      <Card className="rounded-apple-lg shadow-apple-lg border-primary/20 bg-primary/5">
        <CardHeader className="pb-3">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
              <FileText size={16} className="text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-headline text-foreground">Pipeline Configuration</h3>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-primary/10 last:border-b-0">
              <span className="text-callout text-muted-foreground">Dataset</span>
              <Badge variant="outline" className="font-medium">{fileData.filename}</Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-primary/10 last:border-b-0">
              <span className="text-callout text-muted-foreground">Target Column</span>
              <Badge className="bg-primary text-primary-foreground">{targetColumn}</Badge>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-callout text-muted-foreground">Data Size</span>
              <span className="text-callout text-foreground font-medium">
                {fileData.shape.rows.toLocaleString()} × {fileData.shape.columns}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Button */}
      <div className="space-y-4">
        <Button
          onClick={runPipeline}
          disabled={processing}
          size="lg"
          className="group w-full rounded-apple shadow-apple hover:shadow-apple-lg active:scale-[0.98] transition-all duration-200"
        >
          {processing ? (
            <div className="flex items-center space-x-3">
              <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-primary-foreground rounded-full animate-pulse"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
              <span>Processing Your Data...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Play size={20} className="transition-transform duration-200 group-hover:scale-110" />
              <span>Start AI Preprocessing</span>
            </div>
          )}
        </Button>

        {/* Progress Steps */}
        {processing && (
          <Card className="animate-fade-in rounded-apple-lg shadow-apple bg-muted/50">
            <CardContent className="p-5">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-callout text-foreground font-medium">Processing Steps</p>
                  <Badge variant="secondary">{currentStep + 1}/{steps.length}</Badge>
                </div>

                <div className="space-y-3">
                  {steps.map((step, index) => (
                    <div key={step} className="flex items-center space-x-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                        index < currentStep
                          ? 'bg-chart-2 text-white'
                          : index === currentStep
                          ? 'bg-primary text-primary-foreground animate-pulse'
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {index < currentStep ? (
                          <CheckCircle size={14} />
                        ) : (
                          <span className="text-caption font-bold">{index + 1}</span>
                        )}
                      </div>
                      <p className={`text-callout transition-colors duration-300 ${
                        index <= currentStep ? 'text-foreground' : 'text-muted-foreground'
                      }`}>
                        {step}
                      </p>
                    </div>
                  ))}
                </div>

                {status && (
                  <div className="pt-3 border-t border-border">
                    <p className="text-footnote text-muted-foreground italic">{status}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Information Panel */}
      <Card className="rounded-apple-lg shadow-apple-lg bg-gradient-to-r from-primary/5 to-chart-4/5 border-border">
        <CardContent className="p-5">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary to-chart-4 rounded-full flex items-center justify-center flex-shrink-0">
              <Brain size={16} className="text-white" />
            </div>
            <div className="flex-1">
              <h4 className="text-headline text-foreground mb-3">AI Preprocessing Pipeline</h4>
              <div className="space-y-2 text-callout text-muted-foreground">
                <p className="text-foreground">Our intelligent system will automatically:</p>
                <ul className="space-y-1.5 ml-4">
                  <li className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-primary rounded-full mt-2.5 flex-shrink-0" />
                    <span>Analyze your dataset structure and data types</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-primary rounded-full mt-2.5 flex-shrink-0" />
                    <span>Handle missing values with intelligent imputation</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-primary rounded-full mt-2.5 flex-shrink-0" />
                    <span>Detect and remove outliers using statistical methods</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1 h-1 bg-primary rounded-full mt-2.5 flex-shrink-0" />
                    <span>Standardize features for optimal model performance</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}