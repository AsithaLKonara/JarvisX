/**
 * JarvisX Trading Dashboard
 * Real-time trading interface with safety controls and approval workflows
 */

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Lock,
  Eye,
  EyeOff
} from 'lucide-react';

// Types
interface Position {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercentage: number;
  timestamp: string;
}

interface TradingRecommendation {
  id: string;
  symbol: string;
  action: 'buy' | 'sell' | 'hold';
  confidence: number;
  reason: string;
  suggestedSize: number;
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: string;
}

interface TradingDashboardProps {
  orchestratorUrl: string;
  onClose?: () => void;
}

export function TradingDashboard({ orchestratorUrl, onClose }: TradingDashboardProps) {
  // State
  const [positions, setPositions] = useState<Position[]>([]);
  const [recommendations, setRecommendations] = useState<TradingRecommendation[]>([]);
  const [autonomyLevel, setAutonomyLevel] = useState<'manual' | 'semi' | 'auto'>('manual');
  const [isConnected, setIsConnected] = useState(false);
  const [showSensitiveData, setShowSensitiveData] = useState(false);
  const [pendingApprovals, setPendingApprovals] = useState<any[]>([]);
  const [riskLimits, setRiskLimits] = useState({
    maxPositionSize: 1000,
    maxDailyLoss: 500,
    maxExposure: 5000,
    currentExposure: 0
  });

  // Fetch trading data
  const fetchTradingData = useCallback(async () => {
    try {
      const response = await fetch(`${orchestratorUrl}/trade/summary`);
      if (response.ok) {
        const data = await response.json();
        setPositions(data.positions || []);
        setRecommendations(data.recommendations || []);
        setRiskLimits(prev => ({
          ...prev,
          currentExposure: data.currentExposure || 0
        }));
      }
    } catch (error) {
      console.error('❌ Failed to fetch trading data:', error);
    }
  }, [orchestratorUrl]);

  // Initialize trading dashboard
  useEffect(() => {
    fetchTradingData();
    const interval = setInterval(fetchTradingData, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, [fetchTradingData]);

  // Handle trading actions
  const handleExecuteTrade = useCallback(async (recommendation: TradingRecommendation, autoApprove: boolean = false) => {
    try {
      // Check risk limits
      if (recommendation.suggestedSize > riskLimits.maxPositionSize) {
        alert(`Position size exceeds limit: ${riskLimits.maxPositionSize}`);
        return;
      }

      if (recommendation.riskLevel === 'high' && !autoApprove) {
        const confirmed = window.confirm(
          `High-risk trade detected: ${recommendation.symbol} ${recommendation.action}\n` +
          `Size: ${recommendation.suggestedSize}\n` +
          `Risk Level: ${recommendation.riskLevel}\n\n` +
          `Do you want to proceed?`
        );
        if (!confirmed) return;
      }

      // Execute trade
      const response = await fetch(`${orchestratorUrl}/trade/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recommendation,
          dry_run: false,
          auto_approve: autoApprove
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Trade executed:', result);
        
        // Refresh data
        await fetchTradingData();
      } else {
        const error = await response.json();
        alert(`Trade execution failed: ${error.message}`);
      }

    } catch (error: any) {
      console.error('❌ Trade execution failed:', error);
      alert(`Trade execution failed: ${error.message}`);
    }
  }, [orchestratorUrl, riskLimits]);

  // Handle approval
  const handleApproval = useCallback(async (approvalId: string, approved: boolean) => {
    try {
      const response = await fetch(`${orchestratorUrl}/trade/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approvalId, approved })
      });

      if (response.ok) {
        setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
        await fetchTradingData();
      }
    } catch (error) {
      console.error('❌ Approval failed:', error);
    }
  }, [orchestratorUrl, fetchTradingData]);

  // Calculate total P&L
  const totalPnl = positions.reduce((sum, pos) => sum + pos.pnl, 0);
  const totalPnlPercentage = positions.length > 0 
    ? positions.reduce((sum, pos) => sum + pos.pnlPercentage, 0) / positions.length 
    : 0;

  return (
    <motion.div
      className="trading-dashboard fixed inset-4 z-50 bg-black/20 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/10"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center">
            <TrendingUp size={24} className="text-white" />
          </div>
          <div>
            <div className="text-white text-lg font-semibold">Trading Dashboard</div>
            <div className="text-white/60 text-sm">
              {autonomyLevel === 'manual' ? 'Manual Mode' : 
               autonomyLevel === 'semi' ? 'Semi-Auto Mode' : 'Auto Mode'}
            </div>
          </div>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSensitiveData(!showSensitiveData)}
            className={`p-2 rounded-lg transition-colors ${
              showSensitiveData ? 'bg-green-500/20 text-green-400' : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            {showSensitiveData ? <Eye size={20} /> : <EyeOff size={20} />}
          </button>
          
          <select
            value={autonomyLevel}
            onChange={(e) => setAutonomyLevel(e.target.value as any)}
            className="px-3 py-2 rounded-lg bg-white/10 text-white border border-white/20"
          >
            <option value="manual">Manual</option>
            <option value="semi">Semi-Auto</option>
            <option value="auto">Auto</option>
          </select>
          
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
            >
              <XCircle size={20} />
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex h-full">
        {/* Left Panel - Positions */}
        <aside className="w-80 p-4 border-r border-white/10 bg-black/10">
          <h3 className="text-white text-sm font-medium uppercase tracking-wide mb-4">Positions</h3>
          
          <div className="space-y-3">
            {positions.map((position) => (
              <motion.div
                key={position.symbol}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-3 rounded-lg border ${
                  position.pnl >= 0 
                    ? 'bg-green-500/10 border-green-500/30' 
                    : 'bg-red-500/10 border-red-500/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="text-white font-medium">{position.symbol}</div>
                  <div className={`text-sm font-medium ${
                    position.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {position.pnl >= 0 ? '+' : ''}{position.pnl.toFixed(2)}
                  </div>
                </div>
                
                <div className="text-white/60 text-xs space-y-1">
                  <div>Side: {position.side.toUpperCase()}</div>
                  <div>Size: {position.size}</div>
                  <div>Entry: ${position.entryPrice.toFixed(2)}</div>
                  <div>Current: ${position.currentPrice.toFixed(2)}</div>
                  <div className={position.pnlPercentage >= 0 ? 'text-green-400' : 'text-red-400'}>
                    {position.pnlPercentage >= 0 ? '+' : ''}{position.pnlPercentage.toFixed(2)}%
                  </div>
                </div>
              </motion.div>
            ))}
            
            {positions.length === 0 && (
              <div className="text-center text-white/40 py-8">
                <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
                <div>No open positions</div>
              </div>
            )}
          </div>

          {/* P&L Summary */}
          <div className="mt-6 p-3 rounded-lg bg-white/5 border border-white/10">
            <div className="text-white text-sm font-medium mb-2">Total P&L</div>
            <div className={`text-lg font-bold ${
              totalPnl >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
            </div>
            <div className={`text-sm ${
              totalPnlPercentage >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {totalPnlPercentage >= 0 ? '+' : ''}{totalPnlPercentage.toFixed(2)}%
            </div>
          </div>
        </aside>

        {/* Center Panel - Recommendations */}
        <section className="flex-1 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white text-lg font-semibold">AI Recommendations</h3>
            <div className="text-white/60 text-sm">
              {recommendations.length} recommendations
            </div>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {recommendations.map((rec) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`p-4 rounded-lg border ${
                    rec.action === 'buy' ? 'bg-green-500/10 border-green-500/30' :
                    rec.action === 'sell' ? 'bg-red-500/10 border-red-500/30' :
                    'bg-yellow-500/10 border-yellow-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        rec.action === 'buy' ? 'bg-green-500' :
                        rec.action === 'sell' ? 'bg-red-500' :
                        'bg-yellow-500'
                      }`}>
                        {rec.action === 'buy' ? <TrendingUp size={16} className="text-white" /> :
                         rec.action === 'sell' ? <TrendingDown size={16} className="text-white" /> :
                         <DollarSign size={16} className="text-white" />}
                      </div>
                      
                      <div>
                        <div className="text-white font-medium">{rec.symbol}</div>
                        <div className="text-white/60 text-sm capitalize">{rec.action}</div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-white font-medium">{rec.confidence}%</div>
                      <div className={`text-xs ${
                        rec.riskLevel === 'low' ? 'text-green-400' :
                        rec.riskLevel === 'medium' ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {rec.riskLevel.toUpperCase()} RISK
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-white/80 text-sm mb-3">{rec.reason}</div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-white/60 text-sm">
                      Size: {rec.suggestedSize} • {new Date(rec.timestamp).toLocaleTimeString()}
                    </div>
                    
                    <div className="flex gap-2">
                      {rec.riskLevel === 'high' && (
                        <div className="flex items-center gap-1 text-red-400 text-xs">
                          <AlertTriangle size={12} />
                          <span>2FA Required</span>
                        </div>
                      )}
                      
                      <button
                        onClick={() => handleExecuteTrade(rec, autonomyLevel === 'auto')}
                        className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                          rec.action === 'buy' ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' :
                          rec.action === 'sell' ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' :
                          'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                        }`}
                      >
                        {autonomyLevel === 'manual' ? 'Execute' : 'Auto Execute'}
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {recommendations.length === 0 && (
              <div className="text-center text-white/40 py-8">
                <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
                <div>No recommendations available</div>
              </div>
            )}
          </div>
        </section>

        {/* Right Panel - Risk & Controls */}
        <aside className="w-80 p-4 border-l border-white/10 bg-black/10">
          <h3 className="text-white text-sm font-medium uppercase tracking-wide mb-4">Risk Management</h3>
          
          {/* Risk Limits */}
          <div className="space-y-3 mb-6">
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <div className="text-white text-sm font-medium mb-2">Position Size Limit</div>
              <div className="text-white/60 text-xs">
                Current: {riskLimits.currentExposure.toFixed(0)} / {riskLimits.maxPositionSize}
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 mt-2">
                <div 
                  className="bg-blue-400 h-2 rounded-full"
                  style={{ width: `${Math.min((riskLimits.currentExposure / riskLimits.maxPositionSize) * 100, 100)}%` }}
                />
              </div>
            </div>
            
            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <div className="text-white text-sm font-medium mb-2">Daily Loss Limit</div>
              <div className="text-white/60 text-xs">
                Used: {Math.abs(Math.min(totalPnl, 0)).toFixed(2)} / {riskLimits.maxDailyLoss}
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 mt-2">
                <div 
                  className="bg-red-400 h-2 rounded-full"
                  style={{ width: `${Math.min((Math.abs(Math.min(totalPnl, 0)) / riskLimits.maxDailyLoss) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>

          {/* Safety Controls */}
          <div className="space-y-3">
            <h4 className="text-white text-sm font-medium">Safety Controls</h4>
            
            <button className="w-full p-3 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors flex items-center gap-3">
              <Shield size={16} />
              <span className="text-sm">Emergency Stop All</span>
            </button>
            
            <button className="w-full p-3 rounded-lg bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 transition-colors flex items-center gap-3">
              <Lock size={16} />
              <span className="text-sm">Lock Trading</span>
            </button>
            
            <button className="w-full p-3 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors flex items-center gap-3">
              <AlertTriangle size={16} />
              <span className="text-sm">Risk Alert</span>
            </button>
          </div>

          {/* Pending Approvals */}
          {pendingApprovals.length > 0 && (
            <div className="mt-6">
              <h4 className="text-white text-sm font-medium mb-3">Pending Approvals</h4>
              <div className="space-y-2">
                {pendingApprovals.map((approval) => (
                  <div key={approval.id} className="p-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
                    <div className="text-yellow-400 text-xs mb-1">{approval.action}</div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleApproval(approval.id, true)}
                        className="flex-1 px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30"
                      >
                        ✓
                      </button>
                      <button
                        onClick={() => handleApproval(approval.id, false)}
                        className="flex-1 px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30"
                      >
                        ✗
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>
      </main>
    </motion.div>
  );
}

export default TradingDashboard;
