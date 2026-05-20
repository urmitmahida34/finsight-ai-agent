import { Download, FileCode2, FileText } from 'lucide-react'
import { useState } from 'react'

export default function DownloadPanel({ report, ticker, company, apiUrl }) {
  const [pdfLoading, setPdfLoading] = useState(false)

  const downloadMarkdown = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${ticker}_analysis.md`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const downloadPdf = async () => {
    setPdfLoading(true)
    try {
      const base = apiUrl || import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const res = await fetch(`${base}/api/report/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, company, report }),
      })
      if (!res.ok) throw new Error('PDF generation failed')
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `${ticker}_analysis.pdf`
      a.click()
      URL.revokeObjectURL(a.href)
    } catch (e) {
      alert(`PDF download failed: ${e.message}`)
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div className="flex flex-wrap gap-3 justify-center">
      <button
        onClick={downloadMarkdown}
        className="flex items-center gap-2 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.1] text-slate-300 hover:text-white px-5 py-2.5 rounded-xl transition-all text-sm font-medium"
      >
        <FileCode2 size={15} />
        Download Markdown
      </button>

      <button
        onClick={downloadPdf}
        disabled={pdfLoading}
        className="flex items-center gap-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 hover:text-blue-200 px-5 py-2.5 rounded-xl transition-all text-sm font-medium disabled:opacity-50"
      >
        {pdfLoading ? (
          <>
            <span className="w-3.5 h-3.5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            Generating PDF…
          </>
        ) : (
          <>
            <FileText size={15} />
            Download PDF
          </>
        )}
      </button>
    </div>
  )
}
