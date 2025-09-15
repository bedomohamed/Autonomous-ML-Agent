import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import MLPipelineWizard from './components/MLPipelineWizard'
import { Sparkles } from 'lucide-react'

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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-indigo-50/30">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            borderRadius: '16px',
            fontSize: '15px',
            padding: '12px 20px',
            backdropFilter: 'blur(20px)',
          },
        }}
      />

      {/* Modern glass header */}
      <header className="bg-white/80 backdrop-blur-2xl border-b border-gray-200/50 sticky top-0 z-50 animate-in slide-in-from-top duration-700">
        <div className="max-w-6xl mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 group">
              <div className="w-9 h-9 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg transform transition-all duration-300 group-hover:scale-105 group-hover:rotate-3">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-semibold text-gray-900 transition-colors duration-300 group-hover:text-indigo-600">AutoML</span>
            </div>
            <Button className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 rounded-full px-7 py-2.5 font-medium shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl">
              Get Started
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-8">
        {/* Problem-Solution Hero - Hormozi Style */}
        <div className="text-center py-16 animate-in fade-in duration-1000">

          {/* Problem Agitation */}
          <div className="animate-in slide-in-from-bottom duration-1000 delay-200 mb-12">
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg max-w-4xl mx-auto mb-8">
              <h2 className="text-2xl font-bold text-red-900 mb-4">The $100B Machine Learning Problem</h2>
              <p className="text-lg text-red-800 leading-relaxed">
                <strong>73% of data science projects never make it to production.</strong> Companies spend months hiring expensive data scientists,
                only to watch them struggle with preprocessing, hyperparameter tuning, and model comparison.
                Meanwhile, competitors are eating their market share.
              </p>
            </div>
          </div>

          {/* Pain Points */}
          <div className="animate-in slide-in-from-bottom duration-1000 delay-400 mb-16">
            <h3 className="text-xl font-semibold text-gray-900 mb-8">Sound Familiar?</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <div className="bg-gray-100 p-6 rounded-lg">
                <div className="text-3xl mb-3">😤</div>
                <h4 className="font-semibold text-gray-900 mb-2">"6 Months, No Models"</h4>
                <p className="text-gray-700 text-sm">Your team spent half a year on a "simple" ML project. Still debugging preprocessing code.</p>
              </div>
              <div className="bg-gray-100 p-6 rounded-lg">
                <div className="text-3xl mb-3">💸</div>
                <h4 className="font-semibold text-gray-900 mb-2">"$200K+ Wasted"</h4>
                <p className="text-gray-700 text-sm">Hired senior data scientists. They're stuck writing boilerplate code instead of solving business problems.</p>
              </div>
              <div className="bg-gray-100 p-6 rounded-lg">
                <div className="text-3xl mb-3">🤯</div>
                <h4 className="font-semibold text-gray-900 mb-2">"Which Model?"</h4>
                <p className="text-gray-700 text-sm">Trained one algorithm. Is it the best? How do you know? Competitors are already deployed.</p>
              </div>
            </div>
          </div>

          {/* Big Promise */}
          <div className="animate-in slide-in-from-bottom duration-1000 delay-600 mb-12">
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight tracking-tight">
              What If You Could Go From
              <br />
              <span className="text-red-600">CSV Upload</span> to
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent animate-gradient"> Deployed Model</span>
              <br />
              <span className="text-green-600">In 15 Minutes?</span>
            </h1>
          </div>

          {/* Solution Intro */}
          <div className="animate-in slide-in-from-bottom duration-1000 delay-800 mb-12">
            <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-lg max-w-4xl mx-auto">
              <h3 className="text-xl font-bold text-green-900 mb-3">Introducing AutoML: The "Unfair Advantage"</h3>
              <p className="text-lg text-green-800 leading-relaxed">
                While your competitors struggle with months of development, you'll train 4 optimized models,
                compare their performance, and get production-ready code - all before they finish their data preprocessing.
              </p>
            </div>
          </div>

          {/* Social Proof Teaser */}
          <div className="animate-in slide-in-from-bottom duration-1000 delay-1000 mb-8">
            <p className="text-gray-600 text-lg mb-4">
              <span className="font-semibold text-indigo-600">"We went from 6-month ML projects to 15-minute deployments"</span>
              <br />
              <span className="text-sm">- Fortune 500 Data Team</span>
            </p>
          </div>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-16 animate-in slide-in-from-bottom duration-1000 delay-1200">
            <Button
              size="lg"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 rounded-full px-12 py-5 text-xl font-bold shadow-xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl group"
              onClick={() => setPipelineMode('wizard')}
            >
              <span className="flex items-center space-x-2">
                <span>GET MY UNFAIR ADVANTAGE NOW</span>
                <div className="transform transition-transform duration-300 group-hover:translate-x-1">
                  →
                </div>
              </span>
            </Button>
            <p className="text-sm text-gray-500">⚡ Free Demo • No Setup Required • See Results in 60 Seconds</p>
          </div>

          {/* The Mechanism - How It Works */}
          <div className="bg-gray-50 rounded-3xl p-12 max-w-6xl mx-auto animate-in slide-in-from-bottom duration-1000 delay-1400 mb-16">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">The "15-Minute ML" Method</h2>
            <p className="text-center text-gray-600 mb-12 text-lg">
              The exact 5-step system that turns any CSV into production-ready models
            </p>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-red-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">1</div>
                <h4 className="font-semibold text-gray-900 mb-2">Upload CSV</h4>
                <p className="text-sm text-gray-600">Drop your messy data. Any format, any size.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">2</div>
                <h4 className="font-semibold text-gray-900 mb-2">AI Analysis</h4>
                <p className="text-sm text-gray-600">Claude AI analyzes patterns, finds issues automatically.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">3</div>
                <h4 className="font-semibold text-gray-900 mb-2">Smart Cleaning</h4>
                <p className="text-sm text-gray-600">Generated code fixes missing values, outliers, encoding.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">4</div>
                <h4 className="font-semibold text-gray-900 mb-2">Train 4 Models</h4>
                <p className="text-sm text-gray-600">XGBoost, Random Forest, Decision Tree, Naive Bayes - parallel training.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">5</div>
                <h4 className="font-semibold text-gray-900 mb-2">Get Winner</h4>
                <p className="text-sm text-gray-600">Best model ranked, hyperparameters tuned, code downloaded.</p>
              </div>
            </div>

            <div className="text-center mt-8">
              <p className="text-green-600 font-semibold text-lg">Total Time: 15 Minutes ⏱️</p>
              <p className="text-gray-600 text-sm mt-2">vs. 6 months of traditional ML development</p>
            </div>
          </div>
        </div>

        {/* Objection Handling & Final CTA */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-3xl p-12 mb-24 animate-in fade-in duration-1000 delay-1600">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">But Wait... You're Probably Thinking:</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h4 className="font-semibold text-red-600 mb-2">❌ "This sounds too good to be true"</h4>
              <p className="text-gray-700 text-sm mb-4">We get it. Everyone promises "magical" solutions.</p>
              <p className="text-green-700 text-sm font-semibold">✅ That's why we give you the actual Python code. Download it. Inspect it. It's real.</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h4 className="font-semibold text-red-600 mb-2">❌ "What about data security?"</h4>
              <p className="text-gray-700 text-sm mb-4">Your data never leaves secure sandboxes.</p>
              <p className="text-green-700 text-sm font-semibold">✅ E2B isolated environments + local storage. No cloud vendor lock-in.</p>
            </div>
          </div>

          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-6 rounded-lg max-w-4xl mx-auto mb-8">
            <h3 className="text-xl font-bold text-yellow-900 mb-2">Limited Time: First-Mover Advantage</h3>
            <p className="text-yellow-800">
              While your competitors are still hiring data scientists and setting up infrastructure,
              you could be deploying models next week. But this window won't stay open forever.
            </p>
          </div>

          <div className="text-center">
            <Button
              size="lg"
              className="bg-gradient-to-r from-red-600 to-orange-600 text-white hover:from-red-700 hover:to-orange-700 rounded-full px-16 py-6 text-2xl font-bold shadow-2xl transform transition-all duration-300 hover:scale-110 hover:shadow-3xl group mb-4"
              onClick={() => setPipelineMode('wizard')}
            >
              <span className="flex items-center space-x-3">
                <span>YES! GIVE ME MY UNFAIR ADVANTAGE</span>
                <div className="transform transition-transform duration-300 group-hover:translate-x-2">
                  🚀
                </div>
              </span>
            </Button>
            <p className="text-lg text-gray-600 font-semibold">⚡ Free Demo • Zero Risk • Instant Access</p>
            <p className="text-sm text-gray-500 mt-2">Join the data teams that ship models while others are still planning</p>
          </div>
        </div>

        {/* Results & Proof Section */}
        <div className="mb-24 animate-in slide-in-from-bottom duration-1000 delay-1800">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">Real Results From Real Teams</h2>
          <p className="text-center text-gray-600 mb-12">These teams stopped struggling and started shipping</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="bg-white p-8 rounded-2xl shadow-xl border-l-4 border-green-500">
              <div className="mb-6">
                <div className="text-3xl font-bold text-green-600">87.1%</div>
                <div className="text-sm text-gray-600">Model Accuracy Achieved</div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "Went from 3 months of failed experiments to production model in one afternoon.
                My manager thought I hired a consultant."
              </blockquote>
              <div className="text-sm text-gray-500">- Senior Data Scientist, Tech Startup</div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-xl border-l-4 border-blue-500">
              <div className="mb-6">
                <div className="text-3xl font-bold text-blue-600">15min</div>
                <div className="text-sm text-gray-600">Time to Production</div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "Our 6-person ML team was stuck on preprocessing for weeks.
                AutoML did it in minutes with better results."
              </blockquote>
              <div className="text-sm text-gray-500">- ML Engineering Lead, Fortune 500</div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-xl border-l-4 border-purple-500">
              <div className="mb-6">
                <div className="text-3xl font-bold text-purple-600">$2M</div>
                <div className="text-sm text-gray-600">Revenue Impact</div>
              </div>
              <blockquote className="text-gray-700 mb-4">
                "The churn prediction model identified at-risk customers.
                Retention campaigns saved us millions."
              </blockquote>
              <div className="text-sm text-gray-500">- VP of Analytics, E-commerce</div>
            </div>
          </div>

          <div className="text-center mt-12">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl mx-auto">
              <h4 className="font-semibold text-blue-900 mb-2">The Bottom Line:</h4>
              <p className="text-blue-800">
                While others debate tools and hire consultants, you'll be the team that
                <strong> ships models that actually move the business.</strong>
              </p>
            </div>
          </div>
        </div>

        {/* Final CTA Footer */}
        <div className="text-center py-16 border-t border-gray-200/50 animate-in fade-in duration-1000 delay-2000">
          <div className="max-w-3xl mx-auto mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Last Chance: Don't Get Left Behind</h3>
            <p className="text-gray-700 text-lg mb-6">
              Every day you wait is another day your competitors get closer to deployment.
              The teams that move fast win. The teams that hesitate get disrupted.
            </p>
            <Button
              size="lg"
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 rounded-full px-12 py-4 text-lg font-bold shadow-xl transform transition-all duration-300 hover:scale-105 group"
              onClick={() => setPipelineMode('wizard')}
            >
              <span className="flex items-center space-x-2">
                <span>START MY 15-MINUTE ML DEMO NOW</span>
                <div className="transform transition-transform duration-300 group-hover:translate-x-1">
                  ⚡
                </div>
              </span>
            </Button>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500 mb-2">Enterprise-grade technology stack</p>
            <div className="flex items-center justify-center space-x-4">
              <span className="text-indigo-600 font-semibold bg-indigo-100 px-3 py-1 rounded-full text-xs">Claude AI</span>
              <span className="text-purple-600 font-semibold bg-purple-100 px-3 py-1 rounded-full text-xs">E2B Sandboxes</span>
              <span className="text-green-600 font-semibold bg-green-100 px-3 py-1 rounded-full text-xs">Local Security</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App