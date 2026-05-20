import { useCallback, useState } from 'react'

const STEPS = [
  { id: 0, name: 'Data Collection',      agent: 'Data Analyst Agent',       desc: 'Fetching live stock data from NSE/BSE' },
  { id: 1, name: 'News Research',        agent: 'News Research Agent',       desc: 'Scanning financial news & sentiment' },
  { id: 2, name: 'Fundamental Analysis', agent: 'Fundamental Analyst',       desc: 'Analysing ratios, valuation & health' },
  { id: 3, name: 'Regulatory Check',     agent: 'RBI Regulatory Agent',      desc: 'Checking RBI/SEBI compliance' },
  { id: 4, name: 'Risk Assessment',      agent: 'Risk Analyst Agent',        desc: 'Building comprehensive risk profile' },
  { id: 5, name: 'Report Generation',    agent: 'Report Writer Agent',       desc: 'Compiling structured research report' },
]

const initSteps = () => STEPS.map(s => ({ ...s, status: 'waiting' }))

export function useAnalysis() {
  const [phase, setPhase]         = useState('idle')   // idle | analyzing | complete | error
  const [steps, setSteps]         = useState(initSteps)
  const [report, setReport]       = useState('')
  const [ticker, setTicker]       = useState('')
  const [company, setCompany]     = useState('')
  const [error, setError]         = useState('')
  const [fromCache, setFromCache] = useState(false)

  const updateStep = (idx, status) => {
    setSteps(prev => prev.map(s => s.id === idx ? { ...s, status } : s))
  }

  const analyze = useCallback((tickerVal, companyVal) => {
    setTicker(tickerVal)
    setCompany(companyVal || tickerVal)
    setPhase('analyzing')
    setSteps(initSteps())
    setReport('')
    setError('')
    setFromCache(false)

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const url = `${apiUrl}/api/analyze?ticker=${encodeURIComponent(tickerVal)}&company=${encodeURIComponent(companyVal || tickerVal)}`

    const evtSource = new EventSource(url)

    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)

        if (data.type === 'started') {
          updateStep(0, 'active')
        }

        if (data.type === 'progress') {
          // Cache hits arrive rapidly — mark all at once for instant animation
          if (data.from_cache) {
            setSteps(prev => prev.map(s => s.id <= data.step ? { ...s, status: 'complete' } : s))
          } else {
            updateStep(data.step, 'complete')
            const next = data.step + 1
            if (next < STEPS.length) updateStep(next, 'active')
          }
        }

        if (data.type === 'complete') {
          setSteps(prev => prev.map(s => ({ ...s, status: 'complete' })))
          setReport(data.report || '')
          setFromCache(!!data.from_cache)
          setPhase('complete')
          evtSource.close()
        }

        if (data.type === 'error') {
          setError(data.message || 'Unknown error occurred')
          setPhase('error')
          evtSource.close()
        }
      } catch {
        // non-JSON keep-alive ping, ignore
      }
    }

    evtSource.onerror = () => {
      setError('Connection to analysis server lost. Ensure the backend is running.')
      setPhase('error')
      evtSource.close()
    }
  }, [])

  const reset = useCallback(() => {
    setPhase('idle')
    setSteps(initSteps())
    setReport('')
    setError('')
    setFromCache(false)
  }, [])

  return { phase, steps, report, ticker, company, error, fromCache, analyze, reset }
}
