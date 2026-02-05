"""
MACRO Layer - 한국/미국 시장 거시경제 지표 + 상관관계 분석
"""
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class MacroAnalyzer:
    """거시경제 분석 + 자산간 상관관계"""
    
    def __init__(self):
        self.tickers = {
            # 한국 시장
            "kospi": "^KS11",
            "kosdaq": "^KQ11",
            # 미국 시장
            "sp500": "^GSPC",
            "nasdaq": "^IXIC",
            "dow": "^DJI",
            "russell": "^RUT",
            # 금리/채권
            "us_10y": "^TNX",
            "us_2y": "^IRX",
            "us_30y": "^TYX",
            # 변동성
            "vix": "^VIX",
            # 환율
            "usdkrw": "KRW=X",
            "dxy": "DX-Y.NYB",
            "eurusd": "EURUSD=X",
            "usdjpy": "JPY=X",
            # 원자재
            "gold": "GC=F",
            "silver": "SI=F",
            "oil": "CL=F",
            "copper": "HG=F",
            "natgas": "NG=F",
            # 크립토
            "btc": "BTC-USD",
            "eth": "ETH-USD",
        }
        
        # 상관관계 분석용 주요 자산
        self.correlation_assets = {
            "KOSPI": "^KS11",
            "S&P500": "^GSPC",
            "NASDAQ": "^IXIC",
            "US10Y": "^TNX",
            "DXY": "DX-Y.NYB",
            "Gold": "GC=F",
            "Oil": "CL=F",
            "VIX": "^VIX",
            "BTC": "BTC-USD",
        }
    
    def fetch_data(self, ticker: str, period: str = "5d") -> Dict:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period=period)
            if len(hist) >= 2:
                latest = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                week_ago = float(hist['Close'].iloc[0]) if len(hist) >= 5 else prev
                return {
                    "value": latest,
                    "prev": prev,
                    "change": latest - prev,
                    "change_pct": ((latest - prev) / prev * 100) if prev else 0,
                    "week_change_pct": ((latest - week_ago) / week_ago * 100) if week_ago else 0,
                }
        except:
            pass
        return {"value": 0, "prev": 0, "change": 0, "change_pct": 0, "week_change_pct": 0}
    
    def fetch_weekly_data(self, ticker: str) -> Dict:
        """주간 데이터 (1개월치)"""
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1mo")
            if len(hist) >= 5:
                latest = float(hist['Close'].iloc[-1])
                week_ago = float(hist['Close'].iloc[-5]) if len(hist) >= 5 else latest
                month_ago = float(hist['Close'].iloc[0])
                high = float(hist['High'].max())
                low = float(hist['Low'].min())
                return {
                    "value": latest,
                    "week_ago": week_ago,
                    "month_ago": month_ago,
                    "week_change_pct": ((latest - week_ago) / week_ago * 100) if week_ago else 0,
                    "month_change_pct": ((latest - month_ago) / month_ago * 100) if month_ago else 0,
                    "high_1m": high,
                    "low_1m": low,
                    "range_pct": ((high - low) / low * 100) if low else 0,
                }
        except:
            pass
        return {"value": 0, "week_change_pct": 0, "month_change_pct": 0, "high_1m": 0, "low_1m": 0, "range_pct": 0}
    
    def calculate_correlations(self, period: str = "3mo") -> Dict:
        """자산간 상관관계 계산"""
        print("    → 상관관계 분석 중...")
        prices = {}
        
        for name, ticker in self.correlation_assets.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period=period)
                if len(hist) >= 20:
                    prices[name] = hist['Close'].pct_change().dropna()
            except:
                pass
        
        if len(prices) < 2:
            return {}
        
        # 공통 날짜로 정렬
        import pandas as pd
        df = pd.DataFrame(prices)
        df = df.dropna()
        
        if len(df) < 20:
            return {}
        
        # 상관관계 행렬
        corr_matrix = df.corr()
        
        # 주요 상관관계 추출
        correlations = {}
        assets = list(corr_matrix.columns)
        for i, a1 in enumerate(assets):
            for a2 in assets[i+1:]:
                key = f"{a1}_vs_{a2}"
                correlations[key] = round(corr_matrix.loc[a1, a2], 3)
        
        # KOSPI 기준 상관관계
        kospi_corr = {}
        if "KOSPI" in corr_matrix.columns:
            for col in corr_matrix.columns:
                if col != "KOSPI":
                    kospi_corr[col] = round(corr_matrix.loc["KOSPI", col], 3)
        
        return {
            "matrix": corr_matrix.round(3).to_dict(),
            "pairs": correlations,
            "kospi_correlations": kospi_corr,
            "period": period,
            "data_points": len(df),
        }
    
    def get_economic_calendar(self) -> Dict:
        """주간 경제 캘린더 (하드코딩 - 실제로는 API 연동 필요)"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        # 샘플 캘린더 (실제로는 경제 캘린더 API 연동)
        us_events = [
            {"date": (week_start + timedelta(days=1)).strftime("%m/%d"), "event": "ISM 제조업 PMI", "importance": "HIGH"},
            {"date": (week_start + timedelta(days=2)).strftime("%m/%d"), "event": "ADP 고용보고서", "importance": "MEDIUM"},
            {"date": (week_start + timedelta(days=3)).strftime("%m/%d"), "event": "ISM 서비스업 PMI", "importance": "HIGH"},
            {"date": (week_start + timedelta(days=4)).strftime("%m/%d"), "event": "비농업 고용지표 (NFP)", "importance": "HIGH"},
            {"date": (week_start + timedelta(days=4)).strftime("%m/%d"), "event": "실업률", "importance": "HIGH"},
        ]
        
        kr_events = [
            {"date": (week_start + timedelta(days=0)).strftime("%m/%d"), "event": "수출입 동향", "importance": "HIGH"},
            {"date": (week_start + timedelta(days=2)).strftime("%m/%d"), "event": "소비자물가지수 (CPI)", "importance": "HIGH"},
            {"date": (week_start + timedelta(days=3)).strftime("%m/%d"), "event": "금융통화위원회", "importance": "HIGH"},
        ]
        
        earnings = [
            {"date": (week_start + timedelta(days=1)).strftime("%m/%d"), "company": "삼성전자", "market": "KR"},
            {"date": (week_start + timedelta(days=2)).strftime("%m/%d"), "company": "Apple", "market": "US"},
            {"date": (week_start + timedelta(days=2)).strftime("%m/%d"), "company": "Amazon", "market": "US"},
            {"date": (week_start + timedelta(days=3)).strftime("%m/%d"), "company": "SK하이닉스", "market": "KR"},
        ]
        
        return {
            "week_of": week_start.strftime("%Y-%m-%d"),
            "us_events": us_events,
            "kr_events": kr_events,
            "earnings": earnings,
        }
    
    def fetch_korea_rates(self) -> Dict:
        """한국 금리 데이터 (한국은행 기준금리 + 국고채)"""
        # 한국 금리는 yfinance에서 직접 제공하지 않음
        # 실제 운영시에는 한국은행 API나 금융투자협회 API 연동 필요
        # 현재는 최근 데이터 기준 추정치 사용
        
        # 2026년 2월 기준 추정 (실제로는 API 연동 필요)
        # 한국은행 기준금리: 3.00% (2024년 10월 인하 후)
        # 국고채 3년: 약 2.8~3.0%
        # 국고채 10년: 약 3.0~3.2%
        
        return {
            "bok_base": {
                "value": 3.00,
                "prev": 3.00,
                "change": 0.0,
                "change_pct": 0.0,
                "description": "한국은행 기준금리"
            },
            "kr_3y": {
                "value": 2.85,
                "prev": 2.90,
                "change": -0.05,
                "change_pct": -1.72,
                "description": "국고채 3년"
            },
            "kr_10y": {
                "value": 3.05,
                "prev": 3.10,
                "change": -0.05,
                "change_pct": -1.61,
                "description": "국고채 10년"
            },
            "kr_spread": {
                "value": 0.20,  # 10년 - 3년
                "description": "국고채 10Y-3Y 스프레드"
            },
            "kr_us_spread": {
                "value": -1.22,  # 한국 10년 - 미국 10년 (역전 상태)
                "description": "한미 금리차 (10Y)"
            }
        }
    
    def analyze(self) -> Dict:
        print("    → 시장 데이터 수집 중...")
        
        # 주요 지수 (주간 데이터)
        kospi = self.fetch_weekly_data("^KS11")
        kosdaq = self.fetch_weekly_data("^KQ11")
        sp500 = self.fetch_weekly_data("^GSPC")
        nasdaq = self.fetch_weekly_data("^IXIC")
        dow = self.fetch_weekly_data("^DJI")
        russell = self.fetch_weekly_data("^RUT")
        
        # 미국 금리
        us_10y = self.fetch_data("^TNX")
        us_2y = self.fetch_data("^IRX")
        us_30y = self.fetch_data("^TYX")
        
        # 한국 금리
        kr_rates = self.fetch_korea_rates()
        # 한미 금리차 업데이트 (실시간 미국 금리 반영)
        kr_rates["kr_us_spread"]["value"] = round(kr_rates["kr_10y"]["value"] - us_10y.get("value", 4.27), 2)
        
        # 변동성
        vix = self.fetch_weekly_data("^VIX")
        
        # 환율
        usdkrw = self.fetch_weekly_data("KRW=X")
        dxy = self.fetch_weekly_data("DX-Y.NYB")
        eurusd = self.fetch_weekly_data("EURUSD=X")
        usdjpy = self.fetch_weekly_data("JPY=X")
        
        # 원자재
        gold = self.fetch_weekly_data("GC=F")
        silver = self.fetch_weekly_data("SI=F")
        oil = self.fetch_weekly_data("CL=F")
        copper = self.fetch_weekly_data("HG=F")
        
        # 크립토
        btc = self.fetch_weekly_data("BTC-USD")
        eth = self.fetch_weekly_data("ETH-USD")
        
        # MOVE 추정
        move = {"value": vix.get("value", 0) * 5.5}
        
        # 스프레드
        yield_spread = us_10y.get("value", 0) - us_2y.get("value", 0)
        
        # 상관관계 분석
        correlations = self.calculate_correlations()
        
        # 경제 캘린더
        calendar = self.get_economic_calendar()
        
        # 시그널 분석
        signals = []
        
        # KOSPI 추세
        if kospi.get("week_change_pct", 0) > 2:
            signals.append(("KOSPI 강세", f"주간 {kospi['week_change_pct']:.1f}% 상승", "POSITIVE"))
        elif kospi.get("week_change_pct", 0) < -2:
            signals.append(("KOSPI 약세", f"주간 {kospi['week_change_pct']:.1f}% 하락", "NEGATIVE"))
        
        # 미국 시장
        if sp500.get("week_change_pct", 0) > 2:
            signals.append(("S&P500 강세", f"주간 {sp500['week_change_pct']:.1f}% 상승", "POSITIVE"))
        elif sp500.get("week_change_pct", 0) < -2:
            signals.append(("S&P500 약세", f"주간 {sp500['week_change_pct']:.1f}% 하락", "NEGATIVE"))
        
        # 환율
        if usdkrw.get("week_change_pct", 0) > 1:
            signals.append(("원화 약세", "수출주 유리, 외국인 이탈 우려", "MIXED"))
        elif usdkrw.get("week_change_pct", 0) < -1:
            signals.append(("원화 강세", "외국인 유입 기대", "POSITIVE"))
        
        # VIX
        if vix.get("value", 0) > 25:
            signals.append(("VIX 고점", "글로벌 불안, 위험회피", "RISK_OFF"))
        elif vix.get("value", 0) < 15:
            signals.append(("VIX 저점", "위험선호 환경", "RISK_ON"))
        
        # 금리
        if us_10y.get("change", 0) < -0.1:
            signals.append(("미국 금리 하락", "성장주/기술주 우호", "POSITIVE"))
        elif us_10y.get("change", 0) > 0.1:
            signals.append(("미국 금리 상승", "가치주/금융주 우호", "NEGATIVE"))
        
        # 종합 판단
        pos = sum(1 for s in signals if s[2] in ["POSITIVE", "RISK_ON"])
        neg = sum(1 for s in signals if s[2] in ["NEGATIVE", "RISK_OFF"])
        
        if pos > neg:
            overall = "BULLISH"
            recommendation = "위험자산 비중 확대, 성장주 중심 포트폴리오 권고"
        elif neg > pos:
            overall = "BEARISH"
            recommendation = "방어적 포지션, 현금 및 채권 비중 확대 권고"
        else:
            overall = "NEUTRAL"
            recommendation = "균형 포트폴리오 유지, 선별적 접근 권고"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                # 주요 지수
                "kospi": kospi, "kosdaq": kosdaq,
                "sp500": sp500, "nasdaq": nasdaq, "dow": dow, "russell": russell,
                # 한국 금리
                "bok_base": kr_rates["bok_base"],
                "kr_3y": kr_rates["kr_3y"],
                "kr_10y": kr_rates["kr_10y"],
                "kr_spread": kr_rates["kr_spread"],
                "kr_us_spread": kr_rates["kr_us_spread"],
                # 미국 금리
                "us_10y": us_10y, "us_2y": us_2y, "us_30y": us_30y,
                "yield_spread": yield_spread,
                # 변동성
                "vix": vix, "move": move,
                # 환율
                "usdkrw": usdkrw, "dxy": dxy, "eurusd": eurusd, "usdjpy": usdjpy,
                # 원자재
                "gold": gold, "silver": silver, "oil": oil, "copper": copper,
                # 크립토
                "btc": btc, "eth": eth,
            },
            "correlations": correlations,
            "calendar": calendar,
            "signals": signals,
            "overall": overall,
            "recommendation": recommendation,
        }
