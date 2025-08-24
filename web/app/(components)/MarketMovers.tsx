export default function MarketMovers({ movers }: { movers: any }) {
  if (!movers) return null;

  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ fontSize: 18, marginBottom: 16, opacity: 0.9 }}>🚀 Market Movers</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        
        {/* High Activity Coins */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>🔥</span>High Activity Coins
          </div>
          {movers.high_activity && movers.high_activity.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {movers.high_activity.map((coin: any, index: number) => (
                <div key={index} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < movers.high_activity.length - 1 ? '1px solid #1f2937' : 'none'
                }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500 }}>{coin.symbol}</div>
                    <div style={{ fontSize: 12, opacity: 0.7 }}>
                      Vol/MCap: {(coin.volume_mcap_ratio * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: 13, 
                      color: coin.price_change_24h >= 0 ? '#22c55e' : '#ef4444',
                      fontWeight: 500
                    }}>
                      {coin.price_change_24h >= 0 ? '+' : ''}{coin.price_change_24h.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: 13, opacity: 0.6, textAlign: 'center', padding: '16px 0' }}>
              No high activity coins detected
            </div>
          )}
        </div>

        {/* Momentum Shifts */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>⚡</span>Momentum Shifts
          </div>
          {movers.momentum_shifts && movers.momentum_shifts.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {movers.momentum_shifts.map((coin: any, index: number) => (
                <div key={index} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < movers.momentum_shifts.length - 1 ? '1px solid #1f2937' : 'none'
                }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 500 }}>{coin.symbol}</div>
                    <div style={{ fontSize: 12, opacity: 0.7 }}>
                      Momentum: {coin.momentum > 0 ? '📈' : '📉'} {Math.abs(coin.momentum).toFixed(2)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ 
                      fontSize: 13, 
                      color: coin.change_24h >= 0 ? '#22c55e' : '#ef4444',
                      fontWeight: 500
                    }}>
                      {coin.change_24h >= 0 ? '+' : ''}{coin.change_24h.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: 13, opacity: 0.6, textAlign: 'center', padding: '16px 0' }}>
              No significant momentum shifts detected
            </div>
          )}
        </div>

      </div>
    </div>
  );
} 