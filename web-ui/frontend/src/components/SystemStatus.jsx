import { useState, useEffect } from 'react'
import { Cpu, HardDrive, MemoryStick } from 'lucide-react'

export default function SystemStatus() {
  const [status, setStatus] = useState({
    cpu: 0,
    memory: { percent: 0, used: 0, total: 0 },
    disk: { percent: 0, used: 0, total: 0 }
  })
  
  // Fetch system status every 2 seconds
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/system-status')
        const data = await response.json()
        setStatus({
          cpu: data.cpu_percent,
          memory: {
            percent: data.memory_percent,
            used: data.memory_used_gb,
            total: data.memory_total_gb
          },
          disk: {
            percent: data.disk_percent,
            used: data.disk_used_gb,
            total: data.disk_total_gb
          }
        })
      } catch (error) {
        console.error('Failed to fetch system status:', error)
      }
    }
    
    fetchStatus()
    const interval = setInterval(fetchStatus, 2000)
    
    return () => clearInterval(interval)
  }, [])
  
  const getColor = (percent) => {
    if (percent < 60) return 'var(--success)'
    if (percent < 80) return 'var(--warning)'
    return 'var(--error)'
  }
  
  return (
    <div className="system-status p-4 border-t" style={{ borderColor: 'var(--border)' }}>
      <h3 className="text-sm font-semibold mb-3 opacity-60">SYSTEM STATUS</h3>
      
      <div className="space-y-3">
        {/* CPU */}
        <div className="stat-item">
          <div className="flex items-center justify-between text-sm mb-1">
            <div className="flex items-center gap-2">
              <Cpu size={16} style={{ color: 'var(--accent-primary)' }} />
              <span style={{ color: 'var(--text-primary)' }}>CPU</span>
            </div>
            <span className="font-mono font-semibold" style={{ color: getColor(status.cpu) }}>
              {status.cpu.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar w-full h-2 overflow-hidden"
               style={{ 
                 backgroundColor: 'var(--bg-tertiary)',
                 borderRadius: 'var(--radius-sm)'
               }}>
            <div 
              className="progress-fill h-full transition-all duration-500"
              style={{ 
                width: `${status.cpu}%`,
                backgroundColor: getColor(status.cpu),
                boxShadow: `0 0 10px ${getColor(status.cpu)}`
              }} />
          </div>
        </div>
        
        {/* Memory */}
        <div className="stat-item">
          <div className="flex items-center justify-between text-sm mb-1">
            <div className="flex items-center gap-2">
              <MemoryStick size={16} style={{ color: 'var(--accent)' }} />
              <span>RAM</span>
            </div>
            <span className="font-mono font-semibold" style={{ color: getColor(status.memory.percent) }}>
              {status.memory.used.toFixed(1)}/{status.memory.total.toFixed(1)} GB
            </span>
          </div>
          <div className="progress-bar w-full h-2 rounded-full overflow-hidden"
               style={{ backgroundColor: 'var(--border)' }}>
            <div 
              className="progress-fill h-full transition-all duration-500"
              style={{ 
                width: `${status.memory.percent}%`,
                backgroundColor: getColor(status.memory.percent)
              }} />
          </div>
        </div>
        
        {/* Disk */}
        <div className="stat-item">
          <div className="flex items-center justify-between text-sm mb-1">
            <div className="flex items-center gap-2">
              <HardDrive size={16} style={{ color: 'var(--accent)' }} />
              <span>Disk</span>
            </div>
            <span className="font-mono font-semibold" style={{ color: getColor(status.disk.percent) }}>
              {status.disk.percent.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar w-full h-2 rounded-full overflow-hidden"
               style={{ backgroundColor: 'var(--border)' }}>
            <div 
              className="progress-fill h-full transition-all duration-500"
              style={{ 
                width: `${status.disk.percent}%`,
                backgroundColor: getColor(status.disk.percent)
              }} />
          </div>
        </div>
      </div>
    </div>
  )
}

