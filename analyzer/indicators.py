from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import json
import math
from .utils import http_get, utcnow

def fetch_coingecko_market_data() -> Dict:
    """Fetch comprehensive market data from CoinGecko"""
    try:
        # Get top 100 coins by market cap with 24h and 7d data
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h,24h,7d,30d"
        
        status, headers, content = http_get(url + params)
        if status != 200:
            return {}
            
        data = json.loads(content.decode("utf-8"))
        return {"coins": data, "fetched_at": utcnow().isoformat()}
    except Exception:
        return {}

def fetch_fear_greed_detailed() -> Dict:
    """Fetch detailed Fear & Greed Index with historical context"""
    try:
        # Get current and 7-day history
        status, headers, content = http_get("https://api.alternative.me/fng/?limit=7")
        if status != 200:
            return {}
            
        data = json.loads(content.decode("utf-8"))
        if "data" not in data:
            return {}
            
        current = data["data"][0]
        week_data = data["data"]
        
        # Calculate trend
        values = [int(d["value"]) for d in week_data]
        trend = "stable"
        if len(values) >= 2:
            recent_avg = sum(values[:3]) / 3 if len(values) >= 3 else values[0]
            older_avg = sum(values[3:]) / len(values[3:]) if len(values) > 3 else recent_avg
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
        
        return {
            "current_value": int(current["value"]),
            "current_classification": current["value_classification"],
            "trend": trend,
            "week_average": sum(values) / len(values),
            "volatility": max(values) - min(values),
            "fetched_at": utcnow().isoformat()
        }
    except Exception:
        return {}

def calculate_market_regime(coins_data: List[Dict]) -> Dict:
    """Determine market regime (bull, bear, sideways) based on price action and momentum"""
    if not coins_data:
        return {"regime": "unknown", "strength": 0.0, "confidence": 0.0}
    
    try:
        # Focus on top 20 coins for regime detection
        top_coins = coins_data[:20]
        
        # Calculate momentum indicators
        positive_24h = sum(1 for coin in top_coins if coin.get("price_change_percentage_24h", 0) > 0)
        positive_7d = sum(1 for coin in top_coins if coin.get("price_change_percentage_7d", 0) > 0)
        positive_30d = sum(1 for coin in top_coins if coin.get("price_change_percentage_30d", 0) > 0)
        
        # Calculate average changes
        avg_24h = sum(coin.get("price_change_percentage_24h", 0) for coin in top_coins) / len(top_coins)
        avg_7d = sum(coin.get("price_change_percentage_7d", 0) for coin in top_coins) / len(top_coins)
        avg_30d = sum(coin.get("price_change_percentage_30d", 0) for coin in top_coins) / len(top_coins)
        
        # Market cap weighted momentum (focus on BTC, ETH influence)
        total_mcap = sum(coin.get("market_cap", 0) for coin in top_coins)
        if total_mcap > 0:
            weighted_24h = sum(
                coin.get("price_change_percentage_24h", 0) * coin.get("market_cap", 0) 
                for coin in top_coins
            ) / total_mcap
        else:
            weighted_24h = avg_24h
        
        # Determine regime
        bull_score = 0
        bear_score = 0
        
        # Short term momentum (24h)
        if avg_24h > 2: bull_score += 2
        elif avg_24h < -2: bear_score += 2
        
        # Medium term momentum (7d)
        if avg_7d > 5: bull_score += 3
        elif avg_7d < -5: bear_score += 3
        
        # Long term momentum (30d)  
        if avg_30d > 10: bull_score += 4
        elif avg_30d < -10: bear_score += 4
        
        # Breadth (how many coins are positive)
        if positive_24h / len(top_coins) > 0.7: bull_score += 2
        elif positive_24h / len(top_coins) < 0.3: bear_score += 2
        
        if positive_7d / len(top_coins) > 0.6: bull_score += 2
        elif positive_7d / len(top_coins) < 0.4: bear_score += 2
        
        # Determine regime and strength
        if bull_score > bear_score + 2:
            regime = "bull"
            strength = min(1.0, bull_score / 10.0)
        elif bear_score > bull_score + 2:
            regime = "bear" 
            strength = min(1.0, bear_score / 10.0)
        else:
            regime = "sideways"
            strength = 1.0 - abs(bull_score - bear_score) / 10.0
        
        # Confidence based on data quality and consistency
        confidence = min(1.0, len([c for c in top_coins if c.get("market_cap", 0) > 0]) / 20.0)
        
        return {
            "regime": regime,
            "strength": strength,
            "confidence": confidence,
            "bull_score": bull_score,
            "bear_score": bear_score,
            "breadth_24h": positive_24h / len(top_coins),
            "avg_change_24h": avg_24h,
            "avg_change_7d": avg_7d,
            "weighted_change_24h": weighted_24h
        }
    except Exception:
        return {"regime": "unknown", "strength": 0.0, "confidence": 0.0}

def calculate_activity_indicators(coins_data: List[Dict]) -> Dict:
    """Calculate trading activity and momentum indicators"""
    if not coins_data:
        return {}
        
    try:
        # Volume surge detection
        high_volume_coins = []
        total_volume_24h = 0
        
        for coin in coins_data[:50]:  # Top 50 coins
            volume = coin.get("total_volume", 0)
            mcap = coin.get("market_cap", 1)
            total_volume_24h += volume
            
            # Volume/Market cap ratio (activity indicator)
            if mcap > 0:
                vol_mcap_ratio = volume / mcap
                if vol_mcap_ratio > 0.3:  # High activity threshold
                    high_volume_coins.append({
                        "symbol": coin.get("symbol", "").upper(),
                        "volume_mcap_ratio": vol_mcap_ratio,
                        "price_change_24h": coin.get("price_change_percentage_24h", 0)
                    })
        
        # Sort by activity
        high_volume_coins.sort(key=lambda x: x["volume_mcap_ratio"], reverse=True)
        
        # Calculate momentum indicators
        momentum_coins = []
        for coin in coins_data[:30]:
            change_24h = coin.get("price_change_percentage_24h", 0)
            change_7d = coin.get("price_change_percentage_7d", 0)
            
            # Momentum score (acceleration)
            if change_7d != 0:
                momentum = change_24h / 7.0 - change_7d / 7.0  # Daily rate change
                if abs(momentum) > 1.0:  # Significant momentum change
                    momentum_coins.append({
                        "symbol": coin.get("symbol", "").upper(),
                        "momentum": momentum,
                        "change_24h": change_24h
                    })
        
        momentum_coins.sort(key=lambda x: abs(x["momentum"]), reverse=True)
        
        return {
            "total_volume_24h_usd": total_volume_24h,
            "high_activity_count": len(high_volume_coins),
            "high_activity_coins": high_volume_coins[:5],  # Top 5
            "momentum_shifts": momentum_coins[:5],  # Top 5 momentum changes
            "activity_level": "high" if len(high_volume_coins) > 10 else "medium" if len(high_volume_coins) > 5 else "low"
        }
    except Exception:
        return {}

def calculate_dominance_metrics(coins_data: List[Dict]) -> Dict:
    """Calculate Bitcoin dominance and altcoin season indicators"""
    if not coins_data:
        return {}
        
    try:
        btc_data = next((coin for coin in coins_data if coin.get("symbol", "").lower() == "btc"), None)
        eth_data = next((coin for coin in coins_data if coin.get("symbol", "").lower() == "eth"), None)
        
        if not btc_data:
            return {}
        
        # Calculate total market cap
        total_mcap = sum(coin.get("market_cap", 0) for coin in coins_data[:100])
        btc_mcap = btc_data.get("market_cap", 0)
        eth_mcap = eth_data.get("market_cap", 0) if eth_data else 0
        
        # Bitcoin dominance
        btc_dominance = (btc_mcap / total_mcap * 100) if total_mcap > 0 else 0
        eth_dominance = (eth_mcap / total_mcap * 100) if total_mcap > 0 else 0
        alt_dominance = 100 - btc_dominance - eth_dominance
        
        # Altcoin season indicators
        btc_change_24h = btc_data.get("price_change_percentage_24h", 0)
        btc_change_7d = btc_data.get("price_change_percentage_7d", 0)
        
        # Count altcoins outperforming Bitcoin
        alt_outperforming_24h = sum(
            1 for coin in coins_data[1:31]  # Top 30 excluding BTC
            if coin.get("price_change_percentage_24h", 0) > btc_change_24h
        )
        
        alt_outperforming_7d = sum(
            1 for coin in coins_data[1:31]
            if coin.get("price_change_percentage_7d", 0) > btc_change_7d
        )
        
        # Altcoin season score (0-100, 100 = full alt season)
        alt_season_score = (alt_outperforming_7d / 30 * 100) if len(coins_data) > 30 else 0
        
        # Season classification
        if alt_season_score > 75:
            season = "alt_season"
        elif alt_season_score > 50:
            season = "mixed"
        elif btc_dominance > 45:
            season = "btc_dominance"
        else:
            season = "transitional"
        
        return {
            "btc_dominance": round(btc_dominance, 2),
            "eth_dominance": round(eth_dominance, 2),
            "alt_dominance": round(alt_dominance, 2),
            "alt_season_score": round(alt_season_score, 1),
            "season": season,
            "alts_outperforming_24h": alt_outperforming_24h,
            "alts_outperforming_7d": alt_outperforming_7d,
            "btc_performance_24h": btc_change_24h,
            "btc_performance_7d": btc_change_7d
        }
    except Exception:
        return {}

def normalize_change_24h(avg_change: float) -> float:
    """Normalize 24h change to -1 to +1 scale"""
    # Clamp to reasonable bounds and normalize
    clamped = max(-50, min(50, avg_change))
    return clamped / 50.0

def calculate_volatility(coins_data: List[Dict]) -> float:
    """Calculate market volatility (0 to 1)"""
    if not coins_data:
        return 0.5
    
    try:
        # Calculate standard deviation of 24h changes
        changes = [coin.get("price_change_percentage_24h", 0) for coin in coins_data[:20]]
        if not changes:
            return 0.5
        
        mean = sum(changes) / len(changes)
        variance = sum((x - mean) ** 2 for x in changes) / len(changes)
        std_dev = variance ** 0.5
        
        # Normalize volatility (0-1 scale, where 1 = very volatile)
        # Typical crypto volatility ranges from 2% to 15% daily
        normalized = min(1.0, std_dev / 15.0)
        return normalized
    except Exception:
        return 0.5

def calculate_momentum(coins_data: List[Dict]) -> float:
    """Calculate market momentum (-1 to +1)"""
    if not coins_data:
        return 0.0
    
    try:
        # Compare 24h vs 7d performance to detect momentum
        changes_24h = [coin.get("price_change_percentage_24h", 0) for coin in coins_data[:20]]
        changes_7d = [coin.get("price_change_percentage_7d", 0) for coin in coins_data[:20]]
        
        if not changes_24h or not changes_7d:
            return 0.0
        
        avg_24h = sum(changes_24h) / len(changes_24h)
        avg_7d = sum(changes_7d) / len(changes_7d)
        
        # Momentum = acceleration (24h rate vs 7d rate)
        # Normalize to -1 to +1 scale
        momentum_raw = (avg_24h - avg_7d / 7.0) * 7.0  # Daily acceleration
        normalized = max(-1.0, min(1.0, momentum_raw / 20.0))  # Scale factor
        
        return normalized
    except Exception:
        return 0.0

def calculate_onchain_activity() -> float:
    """Calculate on-chain activity level (0 to 1)"""
    try:
        # This would ideally use blockchain data APIs
        # For now, we'll use a proxy based on volume and market activity
        # In a real implementation, you'd fetch:
        # - Daily active addresses
        # - Transaction count
        # - Gas usage
        # - DeFi TVL changes
        
        # Placeholder implementation
        return 0.6  # Moderate activity level
    except Exception:
        return 0.5

def determine_dominance(btc_dominance: float, eth_dominance: float, alt_season_score: float) -> str:
    """Determine market dominance"""
    if btc_dominance > 50:
        return "btc"
    elif eth_dominance > 20 and alt_season_score > 60:
        return "eth"
    else:
        return "mixed"

def generate_market_indicators() -> Dict:
    """Generate comprehensive market indicators combining all data sources"""
    
    # Fetch all data sources
    coingecko_data = fetch_coingecko_market_data()
    fear_greed = fetch_fear_greed_detailed()
    
    coins_data = coingecko_data.get("coins", [])
    
    # Calculate all indicators
    regime = calculate_market_regime(coins_data)
    activity = calculate_activity_indicators(coins_data)
    dominance = calculate_dominance_metrics(coins_data)
    
    # Extract key metrics for display
    btc_data = next((coin for coin in coins_data if coin.get("symbol", "").lower() == "btc"), {})
    eth_data = next((coin for coin in coins_data if coin.get("symbol", "").lower() == "eth"), {})
    
    # Calculate normalized indicators
    avg_change_24h = regime.get("avg_change_24h", 0)
    change24h = normalize_change_24h(avg_change_24h)
    vol = calculate_volatility(coins_data)
    fear_greed_value = fear_greed.get("current_value", 50)
    momentum = calculate_momentum(coins_data)
    regime_type = regime.get("regime", "chop")
    onchain_activity = calculate_onchain_activity()
    dominance_type = determine_dominance(
        dominance.get("btc_dominance", 0),
        dominance.get("eth_dominance", 0),
        dominance.get("alt_season_score", 0)
    )
    
    # Enhanced indicators structure
    indicators = {
        "timestamp": utcnow().isoformat(),
        
        # Normalized indicators (matching your requested format)
        "change24h": round(change24h, 3),
        "vol": round(vol, 3),
        "fearGreed": fear_greed_value,
        "momentum": round(momentum, 3),
        "regime": regime_type,
        "activity": round(onchain_activity, 3),
        "dominance": dominance_type,
        
        # Detailed metrics for UI
        "btc_price": btc_data.get("current_price", 0),
        "btc_change_24h": btc_data.get("price_change_percentage_24h", 0),
        "eth_price": eth_data.get("current_price", 0),
        "eth_change_24h": eth_data.get("price_change_percentage_24h", 0),
        
        # Market Regime
        "market_regime": regime.get("regime", "unknown"),
        "regime_strength": regime.get("strength", 0),
        "regime_confidence": regime.get("confidence", 0),
        "market_breadth_24h": regime.get("breadth_24h", 0),
        "avg_change_24h": regime.get("avg_change_24h", 0),
        
        # Fear & Greed
        "fear_greed_value": fear_greed.get("current_value", 50),
        "fear_greed_classification": fear_greed.get("current_classification", "Neutral"),
        "fear_greed_trend": fear_greed.get("trend", "stable"),
        "fear_greed_volatility": fear_greed.get("volatility", 0),
        
        # Activity & Volume
        "activity_level": activity.get("activity_level", "unknown"),
        "high_activity_count": activity.get("high_activity_count", 0),
        "total_volume_24h": activity.get("total_volume_24h_usd", 0),
        
        # Dominance
        "btc_dominance": dominance.get("btc_dominance", 0),
        "alt_season_score": dominance.get("alt_season_score", 0),
        "market_season": dominance.get("season", "unknown"),
        
        # Top movers and activity
        "high_activity_coins": activity.get("high_activity_coins", [])[:3],
        "momentum_shifts": activity.get("momentum_shifts", [])[:3],
        
        # Data quality
        "data_sources": len([x for x in [coingecko_data, fear_greed] if x]),
        "coins_analyzed": len(coins_data)
    }
    
    return indicators 