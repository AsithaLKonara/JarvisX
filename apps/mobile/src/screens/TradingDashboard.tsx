/**
 * JarvisX Mobile Trading Dashboard
 * Trading interface with AI recommendations and safety controls
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  Dimensions,
} from 'react-native';
import { TrendingUp, TrendingDown, DollarSign, Shield, AlertTriangle } from 'lucide-react-native';

const { width } = Dimensions.get('window');

interface Position {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercentage: number;
}

interface Recommendation {
  id: string;
  symbol: string;
  action: 'buy' | 'sell' | 'hold';
  confidence: number;
  reason: string;
  suggestedSize: number;
  riskLevel: 'low' | 'medium' | 'high';
}

export default function TradingDashboard() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [autonomyLevel, setAutonomyLevel] = useState<'manual' | 'semi' | 'auto'>('manual');

  useEffect(() => {
    loadTradingData();
  }, []);

  const loadTradingData = async () => {
    try {
      // Simulate loading trading data
      setIsConnected(true);
      
      // Mock positions
      setPositions([
        {
          symbol: 'BTCUSDT',
          side: 'long',
          size: 0.1,
          entryPrice: 45000,
          currentPrice: 46000,
          pnl: 100,
          pnlPercentage: 2.22
        }
      ]);

      // Mock recommendations
      setRecommendations([
        {
          id: '1',
          symbol: 'ETHUSDT',
          action: 'buy',
          confidence: 0.85,
          reason: 'Strong upward momentum detected',
          suggestedSize: 50,
          riskLevel: 'medium'
        }
      ]);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const handleExecuteTrade = (recommendation: Recommendation) => {
    Alert.alert(
      'Execute Trade',
      `Execute ${recommendation.action.toUpperCase()} ${recommendation.symbol}?\n\nReason: ${recommendation.reason}`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Execute', 
          style: 'default',
          onPress: () => {
            // Execute trade logic
            console.log('Executing trade:', recommendation);
          }
        }
      ]
    );
  };

  const handleApproval = (approvalId: string, approved: boolean) => {
    Alert.alert(
      'Trade Approval',
      `Trade ${approved ? 'approved' : 'rejected'}`,
      [{ text: 'OK' }]
    );
  };

  const totalPnl = positions.reduce((sum, pos) => sum + pos.pnl, 0);
  const totalPnlPercentage = positions.length > 0 
    ? positions.reduce((sum, pos) => sum + pos.pnlPercentage, 0) / positions.length 
    : 0;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Trading Dashboard</Text>
        <View style={styles.headerRight}>
          <View style={[styles.statusDot, { backgroundColor: isConnected ? '#10B981' : '#EF4444' }]} />
          <Text style={styles.statusText}>
            {autonomyLevel === 'manual' ? 'Manual' : 
             autonomyLevel === 'semi' ? 'Semi-Auto' : 'Auto'}
          </Text>
        </View>
      </View>

      {/* P&L Summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Portfolio Summary</Text>
        <View style={styles.summaryCard}>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Total P&L</Text>
            <Text style={[styles.summaryValue, { color: totalPnl >= 0 ? '#10B981' : '#EF4444' }]}>
              {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Return</Text>
            <Text style={[styles.summaryValue, { color: totalPnlPercentage >= 0 ? '#10B981' : '#EF4444' }]}>
              {totalPnlPercentage >= 0 ? '+' : ''}{totalPnlPercentage.toFixed(2)}%
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Positions</Text>
            <Text style={styles.summaryValue}>{positions.length}</Text>
          </View>
        </View>
      </View>

      {/* Positions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Open Positions</Text>
        {positions.map((position, index) => (
          <View key={index} style={styles.positionCard}>
            <View style={styles.positionHeader}>
              <Text style={styles.positionSymbol}>{position.symbol}</Text>
              <Text style={[styles.positionSide, { color: position.side === 'long' ? '#10B981' : '#EF4444' }]}>
                {position.side.toUpperCase()}
              </Text>
            </View>
            <View style={styles.positionDetails}>
              <Text style={styles.positionSize}>Size: {position.size}</Text>
              <Text style={styles.positionPrice}>Entry: ${position.entryPrice.toFixed(2)}</Text>
              <Text style={styles.positionPrice}>Current: ${position.currentPrice.toFixed(2)}</Text>
            </View>
            <View style={styles.positionPnl}>
              <Text style={[styles.positionPnlValue, { color: position.pnl >= 0 ? '#10B981' : '#EF4444' }]}>
                {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)} ({position.pnlPercentage.toFixed(2)}%)
              </Text>
            </View>
          </View>
        ))}
      </View>

      {/* AI Recommendations */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Recommendations</Text>
        {recommendations.map((rec) => (
          <View key={rec.id} style={styles.recommendationCard}>
            <View style={styles.recommendationHeader}>
              <View style={styles.recommendationSymbol}>
                {rec.action === 'buy' ? (
                  <TrendingUp size={20} color="#10B981" />
                ) : rec.action === 'sell' ? (
                  <TrendingDown size={20} color="#EF4444" />
                ) : (
                  <DollarSign size={20} color="#F59E0B" />
                )}
                <Text style={styles.recommendationSymbolText}>{rec.symbol}</Text>
              </View>
              <View style={styles.recommendationConfidence}>
                <Text style={styles.confidenceText}>{(rec.confidence * 100).toFixed(0)}%</Text>
                <Text style={[styles.riskLevel, { 
                  color: rec.riskLevel === 'low' ? '#10B981' : 
                         rec.riskLevel === 'medium' ? '#F59E0B' : '#EF4444' 
                }]}>
                  {rec.riskLevel.toUpperCase()}
                </Text>
              </View>
            </View>
            
            <Text style={styles.recommendationReason}>{rec.reason}</Text>
            
            <View style={styles.recommendationActions}>
              <TouchableOpacity
                style={[styles.actionButton, { backgroundColor: '#10B981' }]}
                onPress={() => handleExecuteTrade(rec)}
              >
                <Text style={styles.actionButtonText}>Execute</Text>
              </TouchableOpacity>
              
              {rec.riskLevel === 'high' && (
                <View style={styles.highRiskWarning}>
                  <AlertTriangle size={16} color="#EF4444" />
                  <Text style={styles.highRiskText}>High Risk</Text>
                </View>
              )}
            </View>
          </View>
        ))}
      </View>

      {/* Safety Controls */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Safety Controls</Text>
        <TouchableOpacity style={styles.safetyButton}>
          <Shield size={20} color="#EF4444" />
          <Text style={styles.safetyButtonText}>Emergency Stop</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 12,
    color: '#9CA3AF',
    fontWeight: '500',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  summaryCard: {
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  summaryValue: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  positionCard: {
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  positionSymbol: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  positionSide: {
    fontSize: 12,
    fontWeight: '500',
  },
  positionDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  positionSize: {
    color: '#9CA3AF',
    fontSize: 12,
  },
  positionPrice: {
    color: '#9CA3AF',
    fontSize: 12,
  },
  positionPnl: {
    alignItems: 'flex-end',
  },
  positionPnlValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  recommendationCard: {
    backgroundColor: '#1F2937',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#374151',
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationSymbol: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recommendationSymbolText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  recommendationConfidence: {
    alignItems: 'flex-end',
  },
  confidenceText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  riskLevel: {
    fontSize: 10,
    fontWeight: '500',
    marginTop: 2,
  },
  recommendationReason: {
    color: '#9CA3AF',
    fontSize: 14,
    marginBottom: 12,
  },
  recommendationActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  highRiskWarning: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  highRiskText: {
    color: '#EF4444',
    fontSize: 12,
    marginLeft: 4,
  },
  safetyButton: {
    backgroundColor: '#EF4444',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  safetyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});
