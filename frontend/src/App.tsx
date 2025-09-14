import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import MLPipelineWizard from './components/MLPipelineWizard'
import { Zap, Sparkles } from 'lucide-react'

function App() {
  const [pipelineMode, setPipelineMode] = useState<'wizard' | 'simple' | null>(null)

  if (pipelineMode === 'wizard') {
    return (
      <>
        <Toaster
          position="top-center"
          toastOptions={{
            style: {
              background: 'rgba(0, 0, 0, 0.8)',
              color: 'white',
              borderRadius: '10px',
              fontSize: '15px',
              padding: '12px 16px',
            },
          }}
        />
        <MLPipelineWizard />
      </>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            borderRadius: '10px',
            fontSize: '15px',
            padding: '12px 16px',
          },
        }}
      />

      {/* Modern header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
              AutoML Pipeline Platform
            </h1>
            <p className="text-lg text-gray-600">
              AI-Powered Data Science with Claude & E2B Integration
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Mode Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* ML Pipeline Wizard Card */}
          <Card className="relative overflow-hidden border-2 border-transparent hover:border-indigo-500 transition-all duration-300 cursor-pointer group"
                onClick={() => setPipelineMode('wizard')}>
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            <CardHeader className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <Badge className="bg-green-100 text-green-800 border-green-200">Recommended</Badge>
              </div>
              <CardTitle className="text-2xl mb-2">Full ML Pipeline Wizard</CardTitle>
              <p className="text-gray-600">Complete AutoML solution with AI assistance</p>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-indigo-600 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Claude AI Code Generation</p>
                    <p className="text-sm text-gray-600">Intelligent preprocessing & training code</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-purple-600 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">E2B Secure Sandbox</p>
                    <p className="text-sm text-gray-600">Safe code execution environment</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Multi-Model Training</p>
                    <p className="text-sm text-gray-600">XGBoost, Random Forest, Decision Tree, Naive Bayes</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-green-600 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Performance Leaderboard</p>
                    <p className="text-sm text-gray-600">Compare models & download results</p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Requires API Keys</span>
                  <Button className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700">
                    Launch Wizard →
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Simple Pipeline Card */}
          <Card className="relative overflow-hidden border-2 border-transparent hover:border-gray-300 transition-all duration-300 opacity-50 cursor-not-allowed">
            <CardHeader className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-gray-400 to-gray-500 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <Badge variant="secondary">Basic</Badge>
              </div>
              <CardTitle className="text-2xl mb-2">Simple Pipeline</CardTitle>
              <p className="text-gray-600">Basic preprocessing without AI features</p>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Basic Data Cleaning</p>
                    <p className="text-sm text-gray-500">Simple imputation & duplicate removal</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Local Processing</p>
                    <p className="text-sm text-gray-500">No external API dependencies</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Quick Results</p>
                    <p className="text-sm text-gray-500">Fast but limited preprocessing</p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">No API Keys Required</span>
                  <Button disabled variant="secondary">
                    Coming Soon
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* API Keys Setup Info */}
        <Card className="bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">🔑</span>
              <span>API Keys Required for Full Features</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-700">
              To use the ML Pipeline Wizard with AI features, you'll need:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 border border-amber-200">
                <h3 className="font-semibold text-gray-900 mb-2">Claude API Key</h3>
                <p className="text-sm text-gray-600 mb-3">For AI-powered code generation</p>
                <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer"
                   className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                  Get Claude API Key →
                </a>
              </div>
              <div className="bg-white rounded-lg p-4 border border-amber-200">
                <h3 className="font-semibold text-gray-900 mb-2">E2B API Key</h3>
                <p className="text-sm text-gray-600 mb-3">For secure code execution</p>
                <a href="https://e2b.dev/" target="_blank" rel="noopener noreferrer"
                   className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                  Get E2B API Key →
                </a>
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-amber-200">
              <p className="text-sm text-gray-600">
                <strong>Setup Instructions:</strong> Check <code className="bg-gray-100 px-2 py-1 rounded">API_KEYS_SETUP.md</code> for detailed setup guide.
                Add your keys to <code className="bg-gray-100 px-2 py-1 rounded">backend/.env</code> file.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Features Overview */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-indigo-200 bg-indigo-50/50">
              <CardHeader>
                <CardTitle className="text-lg">📊 Data Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Comprehensive dataset profiling with statistics, distributions, and correlations
                </p>
              </CardContent>
            </Card>
            <Card className="border-purple-200 bg-purple-50/50">
              <CardHeader>
                <CardTitle className="text-lg">🤖 AI Code Generation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Claude AI generates optimized preprocessing and training code for your data
                </p>
              </CardContent>
            </Card>
            <Card className="border-green-200 bg-green-50/50">
              <CardHeader>
                <CardTitle className="text-lg">🏆 Model Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Train multiple models and compare performance with interactive leaderboard
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App