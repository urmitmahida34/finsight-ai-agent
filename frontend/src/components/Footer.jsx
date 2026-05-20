import { BarChart2 } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-white/[0.06] mt-24 py-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
            <BarChart2 size={13} className="text-white" />
          </div>
          <span className="text-slate-400 text-sm font-medium">FinSight AI</span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-600">
          <span>Llama 3.3 70B</span>
          <span className="w-1 h-1 rounded-full bg-slate-700" />
          <span>CrewAI</span>
          <span className="w-1 h-1 rounded-full bg-slate-700" />
          <span>yfinance</span>
        </div>
      </div>
    </footer>
  )
}
