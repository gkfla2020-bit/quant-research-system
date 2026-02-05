"""
QuantLib 기반 금융 분석 모듈
- Vasicek 금리 모형
- Black-Scholes 옵션 분석
- 채권 가격/듀레이션
- 금리 기간구조
"""
import QuantLib as ql
from datetime import datetime, date
from typing import Dict, List, Tuple
import numpy as np


class QuantLibAnalyzer:
    """QuantLib 기반 고급 금융 분석"""
    
    def __init__(self):
        self.today = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = self.today
        self.calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        self.day_count = ql.Actual365Fixed()
    
    def vasicek_analysis(self, r0: float, kappa: float = 0.3, theta: float = 0.04, 
                         sigma: float = 0.01) -> Dict:
        """
        Vasicek 금리 모형 분석
        dr = kappa * (theta - r) * dt + sigma * dW
        
        Args:
            r0: 현재 단기금리 (예: 0.0425 = 4.25%)
            kappa: 평균회귀 속도
            theta: 장기 평균 금리
            sigma: 변동성
        """
        # Vasicek 모형 파라미터
        a = kappa
        b = theta
        
        # 기대 금리 경로 (1년)
        times = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
        expected_rates = []
        rate_std = []
        
        for t in times:
            # E[r(t)] = r0 * exp(-a*t) + b * (1 - exp(-a*t))
            exp_rate = r0 * np.exp(-a * t) + b * (1 - np.exp(-a * t))
            # Var[r(t)] = (sigma^2 / 2a) * (1 - exp(-2*a*t))
            var_rate = (sigma**2 / (2 * a)) * (1 - np.exp(-2 * a * t))
            std_rate = np.sqrt(var_rate)
            
            expected_rates.append(round(exp_rate * 100, 3))
            rate_std.append(round(std_rate * 100, 3))
        
        # 제로쿠폰 채권 가격 (Vasicek closed-form)
        def vasicek_zcb_price(r, t, a, b, sigma):
            B = (1 - np.exp(-a * t)) / a
            A = np.exp((b - sigma**2 / (2 * a**2)) * (B - t) - (sigma**2 / (4 * a)) * B**2)
            return A * np.exp(-B * r)
        
        zcb_prices = {}
        for t in [1, 2, 5, 10]:
            price = vasicek_zcb_price(r0, t, a, b, sigma)
            ytm = -np.log(price) / t
            zcb_prices[f"{t}Y"] = {"price": round(price, 4), "yield": round(ytm * 100, 3)}
        
        # 금리 시나리오 분석
        scenarios = {
            "base": {"rate": round(r0 * 100, 2), "prob": 0.5},
            "up_1std": {"rate": round((r0 + sigma) * 100, 2), "prob": 0.25},
            "down_1std": {"rate": round((r0 - sigma) * 100, 2), "prob": 0.25},
        }
        
        # 평균회귀 시간
        half_life = np.log(2) / a
        
        return {
            "model": "Vasicek",
            "parameters": {
                "r0": round(r0 * 100, 3),
                "kappa": kappa,
                "theta": round(theta * 100, 3),
                "sigma": round(sigma * 100, 3),
            },
            "expected_path": dict(zip([f"{t}Y" for t in times], expected_rates)),
            "rate_volatility": dict(zip([f"{t}Y" for t in times], rate_std)),
            "zcb_prices": zcb_prices,
            "scenarios": scenarios,
            "half_life_years": round(half_life, 2),
            "long_term_rate": round(theta * 100, 3),
        }

    def black_scholes_analysis(self, spot: float, strike: float, rate: float,
                                volatility: float, maturity_days: int = 30,
                                option_type: str = "call") -> Dict:
        """
        Black-Scholes 옵션 분석
        
        Args:
            spot: 현재가
            strike: 행사가
            rate: 무위험 이자율
            volatility: 내재변동성
            maturity_days: 만기일수
        """
        maturity = self.today + maturity_days
        
        # QuantLib 설정
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
        rate_handle = ql.YieldTermStructureHandle(
            ql.FlatForward(self.today, rate, self.day_count)
        )
        div_handle = ql.YieldTermStructureHandle(
            ql.FlatForward(self.today, 0.0, self.day_count)
        )
        vol_handle = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.today, self.calendar, volatility, self.day_count)
        )
        
        # BSM 프로세스
        bsm_process = ql.BlackScholesMertonProcess(
            spot_handle, div_handle, rate_handle, vol_handle
        )
        
        # 옵션 설정
        if option_type.lower() == "call":
            payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
        else:
            payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike)
        
        exercise = ql.EuropeanExercise(maturity)
        option = ql.VanillaOption(payoff, exercise)
        
        # 분석 엔진
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
        
        # 그릭스 계산
        try:
            price = option.NPV()
            delta = option.delta()
            gamma = option.gamma()
            theta = option.theta() / 365  # 일간 세타
            vega = option.vega() / 100    # 1% 변동성 변화당
            rho = option.rho() / 100      # 1% 금리 변화당
        except:
            price = delta = gamma = theta = vega = rho = 0
        
        # 손익분기점
        if option_type.lower() == "call":
            breakeven = strike + price
        else:
            breakeven = strike - price
        
        # 내가격/외가격 상태
        if option_type.lower() == "call":
            moneyness = "ITM" if spot > strike else "OTM" if spot < strike else "ATM"
            intrinsic = max(0, spot - strike)
        else:
            moneyness = "ITM" if spot < strike else "OTM" if spot > strike else "ATM"
            intrinsic = max(0, strike - spot)
        
        time_value = price - intrinsic
        
        return {
            "model": "Black-Scholes",
            "inputs": {
                "spot": spot,
                "strike": strike,
                "rate": round(rate * 100, 2),
                "volatility": round(volatility * 100, 2),
                "maturity_days": maturity_days,
                "type": option_type,
            },
            "price": round(price, 4),
            "greeks": {
                "delta": round(delta, 4),
                "gamma": round(gamma, 6),
                "theta": round(theta, 4),
                "vega": round(vega, 4),
                "rho": round(rho, 4),
            },
            "analysis": {
                "moneyness": moneyness,
                "intrinsic_value": round(intrinsic, 4),
                "time_value": round(time_value, 4),
                "breakeven": round(breakeven, 2),
            },
        }

    def yield_curve_analysis(self, rates: Dict[str, float]) -> Dict:
        """
        금리 기간구조 분석
        
        Args:
            rates: {"3M": 0.045, "6M": 0.046, "1Y": 0.044, "2Y": 0.042, ...}
        """
        # 기간 매핑
        tenor_map = {
            "1M": 1/12, "3M": 0.25, "6M": 0.5, "1Y": 1.0,
            "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0, "30Y": 30.0
        }
        
        # 데이터 정리
        tenors = []
        yields = []
        for tenor, rate in rates.items():
            if tenor in tenor_map:
                tenors.append(tenor_map[tenor])
                yields.append(rate)
        
        if len(tenors) < 2:
            return {"error": "Insufficient data"}
        
        # 정렬
        sorted_data = sorted(zip(tenors, yields))
        tenors = [x[0] for x in sorted_data]
        yields = [x[1] for x in sorted_data]
        
        # 기울기 분석
        if len(tenors) >= 2:
            short_rate = yields[0]
            long_rate = yields[-1]
            slope = long_rate - short_rate
            
            if slope > 0.5:
                curve_shape = "STEEP"
                interpretation = "경기 확장 기대, 성장주 유리"
            elif slope > 0:
                curve_shape = "NORMAL"
                interpretation = "정상적 경기 환경"
            elif slope > -0.5:
                curve_shape = "FLAT"
                interpretation = "경기 둔화 우려, 방어적 포지션 권고"
            else:
                curve_shape = "INVERTED"
                interpretation = "경기 침체 신호, 안전자산 선호"
        else:
            curve_shape = "UNKNOWN"
            interpretation = "데이터 부족"
            slope = 0
        
        # 포워드 레이트 계산 (단순화)
        forward_rates = {}
        for i in range(len(tenors) - 1):
            t1, t2 = tenors[i], tenors[i+1]
            r1, r2 = yields[i], yields[i+1]
            # f(t1, t2) = (r2*t2 - r1*t1) / (t2 - t1)
            fwd = (r2 * t2 - r1 * t1) / (t2 - t1)
            forward_rates[f"{t1}Y-{t2}Y"] = round(fwd * 100, 3)
        
        return {
            "curve_shape": curve_shape,
            "slope_bps": round(slope * 10000, 1),
            "interpretation": interpretation,
            "short_rate": round(short_rate * 100, 3),
            "long_rate": round(long_rate * 100, 3),
            "forward_rates": forward_rates,
            "data_points": len(tenors),
        }
    
    def bond_analysis(self, face_value: float, coupon_rate: float, 
                      ytm: float, years_to_maturity: float,
                      frequency: int = 2) -> Dict:
        """
        채권 가격 및 듀레이션 분석
        
        Args:
            face_value: 액면가
            coupon_rate: 쿠폰금리
            ytm: 만기수익률
            years_to_maturity: 잔존만기
            frequency: 이자지급 빈도 (2=반기)
        """
        # 채권 가격 계산
        n_periods = int(years_to_maturity * frequency)
        coupon = face_value * coupon_rate / frequency
        ytm_period = ytm / frequency
        
        # 현재가치 계산
        pv_coupons = sum([coupon / (1 + ytm_period)**t for t in range(1, n_periods + 1)])
        pv_face = face_value / (1 + ytm_period)**n_periods
        price = pv_coupons + pv_face
        
        # Macaulay Duration
        weighted_cf = sum([t * coupon / (1 + ytm_period)**t for t in range(1, n_periods + 1)])
        weighted_cf += n_periods * face_value / (1 + ytm_period)**n_periods
        mac_duration = weighted_cf / price / frequency
        
        # Modified Duration
        mod_duration = mac_duration / (1 + ytm_period)
        
        # Convexity
        convexity_sum = sum([t * (t + 1) * coupon / (1 + ytm_period)**(t + 2) 
                           for t in range(1, n_periods + 1)])
        convexity_sum += n_periods * (n_periods + 1) * face_value / (1 + ytm_period)**(n_periods + 2)
        convexity = convexity_sum / (price * frequency**2)
        
        # 금리 민감도 분석
        rate_changes = [-0.01, -0.005, 0.005, 0.01]  # ±50bp, ±100bp
        price_changes = {}
        for dr in rate_changes:
            # 1차 근사: dP/P ≈ -D * dr
            # 2차 근사: dP/P ≈ -D * dr + 0.5 * C * dr^2
            approx_change = -mod_duration * dr + 0.5 * convexity * dr**2
            new_price = price * (1 + approx_change)
            price_changes[f"{int(dr*10000)}bp"] = {
                "price": round(new_price, 2),
                "change_pct": round(approx_change * 100, 3),
            }
        
        return {
            "inputs": {
                "face_value": face_value,
                "coupon_rate": round(coupon_rate * 100, 2),
                "ytm": round(ytm * 100, 2),
                "years_to_maturity": years_to_maturity,
            },
            "price": round(price, 2),
            "premium_discount": "Premium" if price > face_value else "Discount" if price < face_value else "Par",
            "current_yield": round((coupon * frequency / price) * 100, 3),
            "macaulay_duration": round(mac_duration, 3),
            "modified_duration": round(mod_duration, 3),
            "convexity": round(convexity, 3),
            "rate_sensitivity": price_changes,
        }

    def volatility_surface_analysis(self, spot: float, rate: float,
                                     vol_data: Dict = None) -> Dict:
        """
        변동성 표면 분석 (VIX 기반 추정)
        
        Args:
            spot: 현재 지수
            rate: 무위험 이자율
            vol_data: {"ATM": 0.18, "25D_Put": 0.22, "25D_Call": 0.16} 등
        """
        if vol_data is None:
            # 기본 변동성 구조 (VIX 기반 추정)
            atm_vol = 0.18
            vol_data = {
                "10D_Put": atm_vol * 1.3,
                "25D_Put": atm_vol * 1.15,
                "ATM": atm_vol,
                "25D_Call": atm_vol * 0.95,
                "10D_Call": atm_vol * 0.90,
            }
        
        # 변동성 스큐 분석
        put_vol = vol_data.get("25D_Put", vol_data.get("ATM", 0.18))
        call_vol = vol_data.get("25D_Call", vol_data.get("ATM", 0.18))
        atm_vol = vol_data.get("ATM", 0.18)
        
        skew = put_vol - call_vol
        risk_reversal = call_vol - put_vol
        butterfly = (put_vol + call_vol) / 2 - atm_vol
        
        # 스큐 해석
        if skew > 0.03:
            skew_interpretation = "강한 하방 리스크 프리미엄 - 시장 불안 신호"
        elif skew > 0.01:
            skew_interpretation = "정상적 하방 헤지 수요"
        elif skew > -0.01:
            skew_interpretation = "균형 잡힌 변동성 구조"
        else:
            skew_interpretation = "상방 기대감 - 콜옵션 수요 증가"
        
        # 기간별 변동성 추정 (VIX 기반)
        term_structure = {
            "1W": round(atm_vol * 1.1, 4),
            "1M": round(atm_vol, 4),
            "3M": round(atm_vol * 0.95, 4),
            "6M": round(atm_vol * 0.92, 4),
            "1Y": round(atm_vol * 0.90, 4),
        }
        
        # 변동성 콘탱고/백워데이션
        if term_structure["1W"] > term_structure["1M"]:
            term_shape = "BACKWARDATION"
            term_interpretation = "단기 불확실성 높음 - 이벤트 리스크"
        else:
            term_shape = "CONTANGO"
            term_interpretation = "정상적 변동성 기간구조"
        
        return {
            "spot": spot,
            "atm_volatility": round(atm_vol * 100, 2),
            "volatility_smile": {k: round(v * 100, 2) for k, v in vol_data.items()},
            "skew_metrics": {
                "skew": round(skew * 100, 2),
                "risk_reversal": round(risk_reversal * 100, 2),
                "butterfly": round(butterfly * 100, 2),
            },
            "skew_interpretation": skew_interpretation,
            "term_structure": {k: round(v * 100, 2) for k, v in term_structure.items()},
            "term_shape": term_shape,
            "term_interpretation": term_interpretation,
        }
    
    def comprehensive_analysis(self, market_data: Dict) -> Dict:
        """
        종합 QuantLib 분석
        
        Args:
            market_data: {
                "us_10y": 0.0427,
                "us_2y": 0.0359,
                "vix": 18.0,
                "kospi": 2650,
                ...
            }
        """
        results = {}
        
        # 1. Vasicek 금리 분석
        r0 = market_data.get("us_10y", 0.0427)
        results["vasicek"] = self.vasicek_analysis(
            r0=r0,
            kappa=0.25,
            theta=0.035,  # 장기 평균 3.5%
            sigma=0.01
        )
        
        # 2. 금리 기간구조
        rates = {
            "3M": market_data.get("us_3m", 0.045),
            "2Y": market_data.get("us_2y", 0.0359),
            "10Y": market_data.get("us_10y", 0.0427),
            "30Y": market_data.get("us_30y", 0.045),
        }
        results["yield_curve"] = self.yield_curve_analysis(rates)
        
        # 3. 변동성 분석
        vix = market_data.get("vix", 18.0)
        spot = market_data.get("kospi", 2650)
        results["volatility"] = self.volatility_surface_analysis(
            spot=spot,
            rate=r0,
            vol_data={
                "10D_Put": vix / 100 * 1.3,
                "25D_Put": vix / 100 * 1.15,
                "ATM": vix / 100,
                "25D_Call": vix / 100 * 0.95,
                "10D_Call": vix / 100 * 0.90,
            }
        )
        
        # 4. 샘플 채권 분석 (10년 국채)
        results["bond_10y"] = self.bond_analysis(
            face_value=10000,
            coupon_rate=0.04,
            ytm=r0,
            years_to_maturity=10
        )
        
        # 5. ATM 옵션 분석
        results["option_atm"] = self.black_scholes_analysis(
            spot=spot,
            strike=spot,
            rate=r0,
            volatility=vix / 100,
            maturity_days=30,
            option_type="call"
        )
        
        return results


if __name__ == "__main__":
    analyzer = QuantLibAnalyzer()
    
    # 테스트
    market_data = {
        "us_10y": 0.0427,
        "us_2y": 0.0359,
        "us_30y": 0.045,
        "vix": 18.0,
        "kospi": 2650,
    }
    
    results = analyzer.comprehensive_analysis(market_data)
    
    import json
    print(json.dumps(results, indent=2, ensure_ascii=False))
