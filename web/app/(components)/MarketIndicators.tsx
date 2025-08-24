export default function MarketIndicators({ indicators }: { indicators: any }) {
  if (!indicators) return null;

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return `$${(price / 1000).toFixed(1)}K`;
    }
    return `$${price.toFixed(2)}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) {
      return `$${(volume / 1e9).toFixed(1)}B`;
    }
    if (volume >= 1e6) {
      return `$${(volume / 1e6).toFixed(1)}M`;
    }
    return `$${volume.toFixed(0)}`;
  };

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'bull': return '#22c55e';
      case 'bear': return '#ef4444';
      case 'sideways': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getFearGreedColor = (value: number) => {
    if (value >= 75) return '#22c55e';
    if (value >= 55) return '#84cc16';
    if (value >= 45) return '#f59e0b';
    if (value >= 25) return '#f97316';
    return '#ef4444';
  };

  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ fontSize: 18, marginBottom: 16, opacity: 0.9 }}>📊 Market Indicators</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        
        {/* Price Performance */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>💰</span>Price Performance
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>BTC</span>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 15, fontWeight: 500 }}>{formatPrice(indicators.btc_price)}</div>
                <div style={{ 
                  fontSize: 12, 
                  color: indicators.btc_change_24h >= 0 ? '#22c55e' : '#ef4444' 
                }}>
                  {indicators.btc_change_24h >= 0 ? '+' : ''}{indicators.btc_change_24h.toFixed(2)}%
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>ETH</span>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 15, fontWeight: 500 }}>{formatPrice(indicators.eth_price)}</div>
                <div style={{ 
                  fontSize: 12, 
                  color: indicators.eth_change_24h >= 0 ? '#22c55e' : '#ef4444' 
                }}>
                  {indicators.eth_change_24h >= 0 ? '+' : ''}{indicators.eth_change_24h.toFixed(2)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Market Regime */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>📈</span>Market Regime
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Regime</span>
              <span style={{ 
                fontSize: 14, 
                fontWeight: 500, 
                color: getRegimeColor(indicators.regime),
                textTransform: 'capitalize'
              }}>
                {indicators.regime}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Strength</span>
              <span style={{ fontSize: 14 }}>{(indicators.regime_strength * 100).toFixed(0)}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Breadth</span>
              <span style={{ fontSize: 14 }}>{(indicators.market_breadth * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Fear & Greed */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>😰</span>Fear & Greed
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Index</span>
              <span style={{ 
                fontSize: 16, 
                fontWeight: 500, 
                color: getFearGreedColor(indicators.fear_greed.value)
              }}>
                {indicators.fear_greed.value}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Status</span>
              <span style={{ 
                fontSize: 13, 
                color: getFearGreedColor(indicators.fear_greed.value)
              }}>
                {indicators.fear_greed.classification}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Trend</span>
              <span style={{ fontSize: 13, textTransform: 'capitalize' }}>
                {indicators.fear_greed.trend === 'improving' ? '📈' : 
                 indicators.fear_greed.trend === 'declining' ? '📉' : '➡️'} {indicators.fear_greed.trend}
              </span>
            </div>
          </div>
        </div>

        {/* Activity & Volume */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>🔥</span>Market Activity
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Level</span>
              <span style={{ 
                fontSize: 14, 
                fontWeight: 500,
                color: indicators.activity.level === 'high' ? '#22c55e' : 
                       indicators.activity.level === 'medium' ? '#f59e0b' : '#6b7280'
              }}>
                {indicators.activity.level.toUpperCase()}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Volume 24h</span>
              <span style={{ fontSize: 13 }}>{formatVolume(indicators.activity.volume_24h)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Active Coins</span>
              <span style={{ fontSize: 13 }}>{indicators.activity.high_activity_coins}</span>
            </div>
          </div>
        </div>

        {/* Dominance & Seasons */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>👑</span>Dominance
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>BTC Dominance</span>
              <span style={{ fontSize: 14, fontWeight: 500 }}>{indicators.dominance.btc_dominance}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Alt Season</span>
              <span style={{ fontSize: 13 }}>{indicators.dominance.alt_season_score}%</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Season</span>
              <span style={{ 
                fontSize: 13, 
                color: indicators.dominance.season === 'alt_season' ? '#22c55e' : 
                       indicators.dominance.season === 'btc_dominance' ? '#f59e0b' : '#6b7280',
                textTransform: 'capitalize'
              }}>
                {indicators.dominance.season.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>

        {/* Data Quality */}
        <div style={{ padding: 16, background: '#0f172a', border: '1px solid #1f2937', borderRadius: 8 }}>
          <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>📡</span>Data Quality
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Data Sources</span>
              <span style={{ fontSize: 14, fontWeight: 500 }}>{indicators.data_quality.sources}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 13 }}>Coins Analyzed</span>
              <span style={{ fontSize: 14 }}>{indicators.data_quality.coins_analyzed}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
} 