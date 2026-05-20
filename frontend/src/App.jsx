import { AlertCircle, ArrowLeft, RotateCcw } from 'lucide-react'
import AnalysisForm from './components/AnalysisForm'
import DownloadPanel from './components/DownloadPanel'
import Footer from './components/Footer'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import ProgressStepper from './components/ProgressStepper'
import ReportViewer from './components/ReportViewer'
import { useAnalysis } from './hooks/useAnalysis'

export default function App() {
  const { phase, steps, report, ticker, company, error, fromCache, analyze, reset } = useAnalysis()
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  return (
    <div className="min-h-screen bg-navy-900 flex flex-col">
      <Header />

      <main className="flex-1 pt-24 pb-12 px-4 md:px-6">
        <div className="max-w-7xl mx-auto">

          {/* ── IDLE: hero + form ── */}
          {phase === 'idle' && (
            <>
              <HeroSection />
              <AnalysisForm onAnalyze={analyze} disabled={false} />
            </>
          )}

          {/* ── ANALYZING: progress stepper ── */}
          {phase === 'analyzing' && (
            <div className="flex flex-col items-center">
              <div className="mb-8 text-center">
                <h2 className="text-2xl font-bold text-white">
                  Analysing{' '}
                  <span className="text-blue-400">{company || ticker}</span>
                </h2>
                <p className="text-slate-500 text-sm mt-1">{ticker} · {new Date().toLocaleDateString('en-IN')}</p>
              </div>
              <ProgressStepper steps={steps} />
            </div>
          )}

          {/* ── COMPLETE: report ── */}
          {phase === 'complete' && (
            <>
              <div className="flex items-center justify-between mb-8 max-w-4xl mx-auto">
                <div className="flex items-center gap-3">
                  <button onClick={reset} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
                    <ArrowLeft size={15} />
                    New Analysis
                  </button>
                  {fromCache && (
                    <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                      Cached Result
                    </span>
                  )}
                </div>
                <DownloadPanel report={report} ticker={ticker} company={company} apiUrl={apiUrl} />
              </div>
              <ReportViewer report={report} ticker={ticker} company={company} />
              <div className="mt-8 flex justify-center">
                <button onClick={reset} className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-300 border border-white/[0.08] hover:border-white/20 px-5 py-2.5 rounded-xl transition-all">
                  <RotateCcw size={14} />
                  Analyse Another Stock
                </button>
              </div>
            </>
          )}

          {/* ── ERROR ── */}
          {phase === 'error' && (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
              <div className="glass-card p-10 max-w-lg">
                <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
                <h2 className="text-white font-semibold text-xl mb-2">Analysis Failed</h2>
                <p className="text-slate-400 text-sm mb-6 leading-relaxed">{error}</p>
                <div className="bg-navy-900 rounded-xl p-4 text-left text-xs text-slate-500 mb-6 space-y-1.5">
                  <p className="font-medium text-slate-400 mb-2">Common fixes:</p>
                  <p>• Verify ticker uses .NS suffix for NSE (e.g. HDFCBANK.NS)</p>
                  <p>• Ensure the backend Docker container is running on port 8000</p>
                  <p>• Check your GROQ_API_KEY is valid in the .env file</p>
                </div>
                <button onClick={reset} className="btn-primary w-full justify-center">
                  <RotateCcw size={15} />
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
