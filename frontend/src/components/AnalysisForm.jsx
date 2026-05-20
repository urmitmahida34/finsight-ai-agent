import { Search, Sparkles } from 'lucide-react'
import { useState } from 'react'

const POPULAR = [
  { name: 'HDFC Bank',  ticker: 'HDFCBANK.NS' },
  { name: 'Reliance',   ticker: 'RELIANCE.NS' },
  { name: 'Infosys',    ticker: 'INFY.NS' },
  { name: 'TCS',        ticker: 'TCS.NS' },
  { name: 'ICICI Bank', ticker: 'ICICIBANK.NS' },
  { name: 'SBI',        ticker: 'SBIN.NS' },
  { name: 'Wipro',      ticker: 'WIPRO.NS' },
  { name: 'Bajaj Fin',  ticker: 'BAJFINANCE.NS' },
]

export default function AnalysisForm({ onAnalyze, disabled }) {
  const [ticker, setTicker]   = useState('')
  const [company, setCompany] = useState('')

  const handleQuick = (t, c) => {
    setTicker(t)
    setCompany(c)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!ticker.trim()) return
    onAnalyze(ticker.trim().toUpperCase(), company.trim())
  }

  return (
    <div className="glass-card p-8 max-w-2xl mx-auto animate-slide-up">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-2">
            Stock Ticker <span className="text-slate-600">(NSE format)</span>
          </label>
          <div className="relative">
            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={ticker}
              onChange={e => setTicker(e.target.value)}
              placeholder="e.g. HDFCBANK.NS · RELIANCE.NS · TCS.NS"
              className="input-field pl-11"
              disabled={disabled}
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-400 mb-2">
            Company Name <span className="text-slate-600">(optional — improves news search)</span>
          </label>
          <input
            type="text"
            value={company}
            onChange={e => setCompany(e.target.value)}
            placeholder="e.g. HDFC Bank"
            className="input-field"
            disabled={disabled}
          />
        </div>

        <div>
          <p className="text-xs text-slate-500 mb-3">Quick Select</p>
          <div className="flex flex-wrap gap-2">
            {POPULAR.map(({ name, ticker: t }) => (
              <button
                key={t}
                type="button"
                onClick={() => handleQuick(t, name)}
                disabled={disabled}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-all duration-150 disabled:opacity-40
                  ${ticker === t
                    ? 'bg-blue-600/20 border-blue-500/50 text-blue-300'
                    : 'bg-white/[0.04] border-white/[0.08] text-slate-400 hover:text-slate-200 hover:border-white/20'
                  }`}
              >
                {name}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" className="btn-primary w-full justify-center text-base py-4" disabled={disabled}>
          <Sparkles size={17} />
          Run Full Analysis
        </button>
      </form>
    </div>
  )
}
