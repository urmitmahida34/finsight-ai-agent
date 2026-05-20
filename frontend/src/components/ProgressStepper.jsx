import { AlertTriangle, BarChart2, Check, FileText, Loader2, Newspaper, Shield, TrendingUp } from 'lucide-react'

const ICONS = [BarChart2, Newspaper, TrendingUp, Shield, AlertTriangle, FileText]

const statusConfig = {
  waiting:  { ring: 'border-white/10',   bg: 'bg-navy-900',      text: 'text-slate-600' },
  active:   { ring: 'border-blue-500/60', bg: 'bg-blue-600/15',   text: 'text-blue-400' },
  complete: { ring: 'border-emerald-500/50', bg: 'bg-emerald-500/15', text: 'text-emerald-400' },
  error:    { ring: 'border-red-500/50',  bg: 'bg-red-500/15',    text: 'text-red-400' },
}

function StepIcon({ status, Icon }) {
  const cfg = statusConfig[status]
  return (
    <div className={`w-10 h-10 rounded-xl border-2 flex items-center justify-center shrink-0 transition-all duration-500 ${cfg.ring} ${cfg.bg}`}>
      {status === 'complete'
        ? <Check size={16} className="text-emerald-400" />
        : status === 'active'
          ? <Loader2 size={16} className="text-blue-400 animate-spin" />
          : <Icon size={16} className={cfg.text} />
      }
    </div>
  )
}

export default function ProgressStepper({ steps }) {
  const completedCount = steps.filter(s => s.status === 'complete').length

  return (
    <div className="glass-card p-8 max-w-2xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-white font-semibold text-lg">Analysing your stock</h2>
          <p className="text-slate-500 text-sm mt-0.5">Multi-agent pipeline in progress…</p>
        </div>
        <div className="text-right">
          <span className="text-3xl font-bold text-white">{completedCount}</span>
          <span className="text-slate-500 text-lg">/{steps.length}</span>
          <p className="text-xs text-slate-600 mt-0.5">agents done</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-navy-900 rounded-full h-1.5 mb-8">
        <div
          className="bg-gradient-to-r from-blue-600 to-emerald-500 h-1.5 rounded-full transition-all duration-700"
          style={{ width: `${(completedCount / steps.length) * 100}%` }}
        />
      </div>

      <div className="space-y-3">
        {steps.map((step, i) => {
          const Icon = ICONS[i]
          const isActive = step.status === 'active'
          return (
            <div
              key={step.id}
              className={`flex items-center gap-4 p-3.5 rounded-xl border transition-all duration-500
                ${isActive
                  ? 'bg-blue-600/[0.08] border-blue-500/20'
                  : step.status === 'complete'
                    ? 'bg-emerald-500/[0.05] border-emerald-500/10'
                    : 'bg-transparent border-transparent'
                }`}
            >
              <StepIcon status={step.status} Icon={Icon} />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className={`font-medium text-sm transition-colors ${
                    isActive ? 'text-white' : step.status === 'complete' ? 'text-slate-300' : 'text-slate-600'
                  }`}>{step.name}</p>
                  {isActive && (
                    <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-medium animate-pulse-slow">
                      Running
                    </span>
                  )}
                  {step.status === 'complete' && (
                    <span className="text-[10px] bg-emerald-500/15 text-emerald-500 px-2 py-0.5 rounded-full font-medium">
                      Done
                    </span>
                  )}
                </div>
                <p className={`text-xs mt-0.5 transition-colors ${isActive ? 'text-slate-400' : 'text-slate-600'}`}>
                  {step.desc}
                </p>
              </div>

              {/* Step number */}
              <span className={`text-xs font-mono ${step.status === 'waiting' ? 'text-slate-700' : 'text-slate-500'}`}>
                {String(i + 1).padStart(2, '0')}
              </span>
            </div>
          )
        })}
      </div>

      <p className="text-center text-xs text-slate-600 mt-6">
        Typically takes 60–90 seconds · Do not close this tab
      </p>
    </div>
  )
}
