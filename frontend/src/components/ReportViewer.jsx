import { CheckCircle2, TrendingDown, TrendingUp, Minus } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const REC_CONFIG = {
  BUY:          { cls: 'badge-buy',  icon: TrendingUp,   label: 'BUY' },
  'STRONG BUY': { cls: 'badge-buy',  icon: TrendingUp,   label: 'STRONG BUY' },
  ACCUMULATE:   { cls: 'badge-buy',  icon: TrendingUp,   label: 'ACCUMULATE' },
  HOLD:         { cls: 'badge-hold', icon: Minus,        label: 'HOLD' },
  REDUCE:       { cls: 'badge-sell', icon: TrendingDown, label: 'REDUCE' },
  SELL:         { cls: 'badge-sell', icon: TrendingDown, label: 'SELL' },
  'STRONG SELL':{ cls: 'badge-sell', icon: TrendingDown, label: 'STRONG SELL' },
}

function parseRecommendation(text) {
  const m = text.match(/\b(STRONG BUY|STRONG SELL|ACCUMULATE|REDUCE|BUY|HOLD|SELL)\b/)
  return m ? REC_CONFIG[m[1]] : null
}

function parseSentiment(text) {
  const m = text.match(/News Sentiment[:\s]+\**(POSITIVE|NEUTRAL|NEGATIVE)\**/i)
  if (!m) return null
  const map = { POSITIVE: 'badge-pos', NEUTRAL: 'badge-neu', NEGATIVE: 'badge-neg' }
  return { label: m[1].toUpperCase(), cls: map[m[1].toUpperCase()] }
}

function parseRisk(text) {
  const m = text.match(/Overall Risk[:\s]+\**(?:Level[:\s]+)?\**(VERY HIGH|HIGH|MODERATE|LOW)\**/i)
  if (!m) return null
  const map = { LOW: 'badge-low', MODERATE: 'badge-mod', HIGH: 'badge-high', 'VERY HIGH': 'badge-high' }
  return { label: m[1].toUpperCase(), cls: map[m[1].toUpperCase()] }
}

const mdComponents = {
  h1: ({ children }) => <h1 className="text-xl font-bold text-blue-400 mt-8 mb-3 pb-2 border-b border-white/[0.08]">{children}</h1>,
  h2: ({ children }) => <h2 className="text-lg font-bold text-blue-400 mt-8 mb-3 pb-2 border-b border-white/[0.08]">{children}</h2>,
  h3: ({ children }) => <h3 className="text-base font-semibold text-slate-200 mt-5 mb-2">{children}</h3>,
  p:  ({ children }) => <p className="text-slate-300 leading-relaxed mb-3">{children}</p>,
  li: ({ children }) => (
    <li className="flex gap-2 items-start text-slate-300 mb-1.5">
      <span className="text-blue-400 mt-1 shrink-0">•</span>
      <span>{children}</span>
    </li>
  ),
  ul: ({ children }) => <ul className="mb-4 space-y-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-4 list-decimal list-inside text-slate-300 space-y-1">{children}</ol>,
  strong: ({ children }) => <strong className="text-slate-100 font-semibold">{children}</strong>,
  table: ({ children }) => (
    <div className="overflow-x-auto mb-4">
      <table className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="bg-navy-700 text-slate-300 font-semibold px-4 py-2 text-left border border-white/[0.08]">{children}</th>,
  td: ({ children }) => <td className="px-4 py-2 border border-white/[0.06] text-slate-300">{children}</td>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-blue-500/50 pl-4 text-slate-400 italic my-4">{children}</blockquote>
  ),
  code: ({ children }) => <code className="bg-navy-900 text-blue-300 px-1.5 py-0.5 rounded text-xs">{children}</code>,
  hr: () => <hr className="border-white/[0.08] my-6" />,
}

export default function ReportViewer({ report, ticker, company }) {
  const rec       = parseRecommendation(report)
  const sentiment = parseSentiment(report)
  const risk      = parseRisk(report)

  return (
    <div className="max-w-4xl mx-auto animate-slide-up">
      {/* Summary banner */}
      <div className="glass-card p-6 mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle2 size={18} className="text-emerald-400" />
            <h2 className="text-white font-semibold text-lg">Analysis Complete</h2>
          </div>
          <p className="text-slate-500 text-sm">
            {company} · {ticker} · {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {sentiment && (
            <div className="flex flex-col items-center gap-1">
              <p className="text-[10px] text-slate-600 uppercase tracking-widest">Sentiment</p>
              <span className={`badge ${sentiment.cls}`}>{sentiment.label}</span>
            </div>
          )}
          {risk && (
            <div className="flex flex-col items-center gap-1">
              <p className="text-[10px] text-slate-600 uppercase tracking-widest">Risk</p>
              <span className={`badge ${risk.cls}`}>{risk.label}</span>
            </div>
          )}
          {rec && (() => {
            const Icon = rec.icon
            return (
              <div className="flex flex-col items-center gap-1">
                <p className="text-[10px] text-slate-600 uppercase tracking-widest">Rating</p>
                <span className={`badge text-sm px-4 py-1.5 ${rec.cls}`}>
                  <Icon size={13} />
                  {rec.label}
                </span>
              </div>
            )
          })()}
        </div>
      </div>

      {/* Full report */}
      <div className="glass-card p-8">
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
          {report}
        </ReactMarkdown>
      </div>
    </div>
  )
}
