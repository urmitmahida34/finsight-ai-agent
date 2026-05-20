import { Bot, Database, FileSearch, ShieldCheck } from 'lucide-react'

const stats = [
  { icon: Bot,         label: '6 AI Agents',       sub: 'CrewAI orchestrated' },
  { icon: Database,    label: 'Live NSE/BSE Data',  sub: 'via yfinance' },
  { icon: FileSearch,  label: 'RBI RAG Pipeline',   sub: 'Regulatory checks' },
  { icon: ShieldCheck, label: '60-Second Reports',  sub: 'Institutional grade' },
]

export default function HeroSection() {
  return (
    <div className="text-center mb-12 animate-fade-in">
      <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium px-4 py-2 rounded-full mb-8">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
        Multi-Agent AI · Powered by Gemini 1.5 Flash
      </div>

      <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-5 leading-[1.1]">
        <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-emerald-400 bg-clip-text text-transparent">
          Institutional-Grade
        </span>
        <br />
        <span className="text-white">Stock Research</span>
        <br />
        <span className="text-slate-400 text-4xl md:text-5xl">in 60 Seconds</span>
      </h1>

      <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-12 leading-relaxed">
        Type any NSE/BSE ticker. Six specialist AI agents fetch live data, scan news,
        analyse fundamentals, check RBI compliance, assess risk — and deliver a
        structured research report.
      </p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
        {stats.map(({ icon: Icon, label, sub }) => (
          <div key={label} className="glass-card p-4 flex flex-col items-center gap-2 hover:border-blue-500/20 transition-colors">
            <div className="w-9 h-9 rounded-lg bg-blue-500/15 flex items-center justify-center">
              <Icon size={16} className="text-blue-400" />
            </div>
            <p className="text-white font-semibold text-sm text-center">{label}</p>
            <p className="text-slate-500 text-xs text-center">{sub}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
