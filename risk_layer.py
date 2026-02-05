"""
RISK Layer - QuantLib 기반 리스크 분석
정하림 MOVE 모형 + Vasicek + Black-Scholes 통합
"""
from datetime import datetime
from typing import Dict
import numpy as np
from quantlib_analyzer import QuantLibAnalyzer


class RiskManager:
    """QuantLib 기반 리스크 관리"""
    
    def __init__(self):
        self.ql_analyzer = QuantLibAnalyzer()
        
        # MOVE 지수 기준점
        self.move_thresholds = {
            "low": 80,
            "medium": 100,
            "high": 120,
            "extreme": 150,
        }
        
        # VIX 기준점
        self.vix_thresholds = {
            "low": 15,
            "medium": 20,
            "high": 25,
            "extreme": 35,
        }
    
    def analyze(self, move_value: float, vix_value: float, 
                portfolio_value: float, market_data: Dict = None) -> Dict:
        """
        종합 리스크 분석
        
        Args:
            move_value: MOVE 지수 (채권 변동성)
            vix_value: VIX 지수 (주식 변동성)
            portfolio_value: 포트폴리오 가치
            market_data: 추가 시장 데이터
        """
        if market_data is None:
            market_data = {}
        
        # 기본 리스크 메트릭
        risk_metrics = self._calculate_risk_metrics(move_value, vix_value)
        
        # 포지션 사이징
        position_sizing = self._calculate_position_sizing(
            risk_metrics["risk_score"], portfolio_value
        )
        
        # QuantLib 분석
        ql_data = {
            "us_10y": market_data.get("us_10y", 0.0427),
            "us_2y": market_data.get("us_2y", 0.0359),
            "us_30y": market_data.get("us_30y", 0.045),
            "vix": vix_value,
            "kospi": market_data.get("kospi", 2650),
        }
        quantlib_analysis = self.ql_analyzer.comprehensive_analysis(ql_data)
        
        # VaR 계산
        var_analysis = self._calculate_var(portfolio_value, vix_value)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "risk_metrics": risk_metrics,
            "position_sizing": position_sizing,
            "var_analysis": var_analysis,
            "quantlib": quantlib_analysis,
        }

    def _calculate_risk_metrics(self, move: float, vix: float) -> Dict:
        """리스크 메트릭 계산"""
        # MOVE 기여도 (0-50점)
        if move < self.move_thresholds["low"]:
            move_score = 10
        elif move < self.move_thresholds["medium"]:
            move_score = 25
        elif move < self.move_thresholds["high"]:
            move_score = 35
        elif move < self.move_thresholds["extreme"]:
            move_score = 45
        else:
            move_score = 50
        
        # VIX 기여도 (0-50점)
        if vix < self.vix_thresholds["low"]:
            vix_score = 10
        elif vix < self.vix_thresholds["medium"]:
            vix_score = 25
        elif vix < self.vix_thresholds["high"]:
            vix_score = 35
        elif vix < self.vix_thresholds["extreme"]:
            vix_score = 45
        else:
            vix_score = 50
        
        # 종합 리스크 점수
        risk_score = move_score + vix_score
        
        # 리스크 레벨
        if risk_score < 40:
            risk_level = "LOW"
        elif risk_score < 60:
            risk_level = "MEDIUM"
        elif risk_score < 80:
            risk_level = "HIGH"
        else:
            risk_level = "EXTREME"
        
        # 변동성 배수 (정규화)
        vol_multiplier = (vix / 20) * (move / 100)
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "move_contribution": move_score,
            "vix_contribution": vix_score,
            "vol_multiplier": round(vol_multiplier, 3),
            "move_value": move,
            "vix_value": vix,
        }
    
    def _calculate_position_sizing(self, risk_score: float, 
                                    portfolio_value: float) -> Dict:
        """리스크 기반 포지션 사이징"""
        # 기본 배분 비율
        base_allocation = 0.1  # 10%
        
        # 리스크 조정
        if risk_score < 40:
            risk_adj = 1.2  # 저위험: 20% 증가
        elif risk_score < 60:
            risk_adj = 1.0  # 중위험: 유지
        elif risk_score < 80:
            risk_adj = 0.7  # 고위험: 30% 감소
        else:
            risk_adj = 0.4  # 극고위험: 60% 감소
        
        adjusted_allocation = base_allocation * risk_adj
        max_position = portfolio_value * adjusted_allocation
        
        # 손절 라인
        if risk_score < 40:
            stop_loss = 0.05  # 5%
        elif risk_score < 60:
            stop_loss = 0.03  # 3%
        else:
            stop_loss = 0.02  # 2%
        
        return {
            "base_allocation": base_allocation,
            "risk_adjustment": risk_adj,
            "adjusted_allocation": round(adjusted_allocation, 3),
            "max_position_value": round(max_position, 0),
            "stop_loss_pct": stop_loss,
            "stop_loss_value": round(max_position * stop_loss, 0),
        }
    
    def _calculate_var(self, portfolio_value: float, vix: float,
                       confidence: float = 0.95) -> Dict:
        """Value at Risk 계산"""
        # 일간 변동성 추정 (VIX는 연간화된 값)
        daily_vol = vix / 100 / np.sqrt(252)
        
        # 정규분포 가정 VaR
        z_score = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
        z = z_score.get(confidence, 1.645)
        
        var_1d = portfolio_value * daily_vol * z
        var_5d = var_1d * np.sqrt(5)
        var_20d = var_1d * np.sqrt(20)
        
        # Expected Shortfall (CVaR) 근사
        es_multiplier = 1.25  # 정규분포 가정
        cvar_1d = var_1d * es_multiplier
        
        return {
            "confidence_level": confidence,
            "daily_volatility": round(daily_vol * 100, 3),
            "var_1d": round(var_1d, 0),
            "var_5d": round(var_5d, 0),
            "var_20d": round(var_20d, 0),
            "cvar_1d": round(cvar_1d, 0),
            "interpretation": f"{confidence*100:.0f}% 신뢰수준에서 1일 최대 손실 {var_1d:,.0f}원",
        }


if __name__ == "__main__":
    rm = RiskManager()
    
    result = rm.analyze(
        move_value=99,
        vix_value=18,
        portfolio_value=100000000,
        market_data={
            "us_10y": 0.0427,
            "us_2y": 0.0359,
            "kospi": 2650,
        }
    )
    
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
