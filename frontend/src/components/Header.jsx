import { BarChart2, Github } from 'lucide-react'

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.06]"
      style={{ background: 'rgba(7,12,27,0.85)', backdropFilter: 'blur(16px)' }}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <BarChart2 size={18} className="text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight">FinSight</span>
            <span className="font-bold text-lg text-blue-400 tracking-tight"> AI</span>
          </div>
          <span className="hidden sm:block ml-2 text-xs text-slate-500 border border-white/[0.08] px-2.5 py-1 rounded-full">
            Indian Equity Research
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live Market Data
          </div>
          <a
            href="https://github.com/urmitmahida/financial-analysis-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors border border-white/[0.08] hover:border-white/20 px-3 py-1.5 rounded-lg"
          >
            <Github size={15} />
            <span className="hidden sm:block">GitHub</span>
          </a>
        </div>
      </div>
    </header>
  )
}
