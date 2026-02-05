"""
INDUSTRY Layer - 한국 시장 섹터/업종 분석
"""
import yfinance as yf
import json
from datetime import datetime
from typing import Dict, List
from config import CLAUDE_API_KEY


class IndustryAnalyzer:
    """한국 시장 업종 분석"""
    
    def __init__(self):
        # 한국 업종 대표 ETF/종목
        self.kr_sectors = {
            "반도체": ["005930.KS", "000660.KS"],  # 삼성전자, SK하이닉스
            "2차전지": ["373220.KS", "006400.KS"],  # LG에너지솔루션, 삼성SDI
            "바이오": ["207940.KS", "068270.KS"],  # 삼성바이오로직스, 셀트리온
            "자동차": ["005380.KS", "000270.KS"],  # 현대차, 기아
            "조선": ["009540.KS", "010140.KS"],  # 한국조선해양, 삼성중공업
            "금융": ["105560.KS", "055550.KS"],  # KB금융, 신한지주
            "철강": ["005490.KS"],  # POSCO홀딩스
            "화학": ["051910.KS", "010950.KS"],  # LG화학, S-Oil
            "유통": ["004170.KS", "139480.KS"],  # 신세계, 이마트
            "통신": ["017670.KS", "030200.KS"],  # SK텔레콤, KT
            "엔터": ["352820.KS", "041510.KS"],  # 하이브, SM
            "게임": ["036570.KS", "251270.KS"],  # 엔씨소프트, 넷마블
        }
        
        # 미국 섹터 ETF (글로벌 비교용)
        self.us_sectors = {
            "Technology": "XLK",
            "Semiconductor": "SOXX",
            "Healthcare": "XLV",
            "Financial": "XLF",
            "Energy": "XLE",
            "Industrial": "XLI",
            "Consumer": "XLY",
        }
    
    def fetch_kr_sector(self, name: str, tickers: List[str]) -> Dict:
        """한국 업종 데이터"""
        perfs = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                if len(hist) >= 2:
                    latest = hist['Close'].iloc[-1]
                    month_ago = hist['Close'].iloc[0]
                    week_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else month_ago
                    perfs.append({
                        "week": ((latest - week_ago) / week_ago * 100),
                        "month": ((latest - month_ago) / month_ago * 100),
                    })
            except:
                pass
        
        if perfs:
            avg_week = sum(p["week"] for p in perfs) / len(perfs)
            avg_month = sum(p["month"] for p in perfs) / len(perfs)
            return {"name": name, "perf_week": avg_week, "perf_month": avg_month}
        return {"name": name, "perf_week": 0, "perf_month": 0}
    
    def fetch_us_sector(self, name: str, ticker: str) -> Dict:
        """미국 섹터 데이터"""
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period="1mo")
            if len(hist) >= 2:
                latest = hist['Close'].iloc[-1]
                month_ago = hist['Close'].iloc[0]
                week_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else month_ago
                return {
                    "name": name,
                    "perf_week": ((latest - week_ago) / week_ago * 100),
                    "perf_month": ((latest - month_ago) / month_ago * 100),
                }
        except:
            pass
        return {"name": name, "perf_week": 0, "perf_month": 0}

    
    def analyze_with_claude(self, kr_data: List[Dict], us_data: List[Dict], macro: Dict) -> Dict:
        """Claude로 업종 분석"""
        try:
            from config import CLAUDE_API_KEY
            import anthropic
            
            if not CLAUDE_API_KEY:
                return self._basic_analysis(kr_data, us_data, macro)
            
            claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            
            kr_text = "\n".join([f"- {s['name']}: 주간 {s['perf_week']:+.1f}%, 월간 {s['perf_month']:+.1f}%" for s in kr_data])
            us_text = "\n".join([f"- {s['name']}: 주간 {s['perf_week']:+.1f}%, 월간 {s['perf_month']:+.1f}%" for s in us_data])
            
            prompt = f"""한국 증시 섹터 애널리스트로서 분석해주세요.

[한국 업종 퍼포먼스]
{kr_text}

[미국 섹터 퍼포먼스 (참고)]
{us_text}

[매크로 환경]
- 전체: {macro.get('overall', 'N/A')}
- KOSPI: {macro.get('indicators', {}).get('kospi', {}).get('change_pct', 0):.1f}%
- 원/달러: {macro.get('indicators', {}).get('usdkrw', {}).get('value', 0):.0f}원
- VIX: {macro.get('indicators', {}).get('vix', {}).get('value', 0):.1f}

JSON으로 응답:
{{"market_cycle": "EARLY_EXPANSION/MID_EXPANSION/LATE_EXPANSION/RECESSION",
"cycle_reasoning": "사이클 판단 근거 (2문장)",
"top_sectors": [{{"name": "업종명", "score": 85, "reasoning": "추천 이유 (상세히)", "catalysts": ["촉매1", "촉매2"], "target_stocks": ["종목1", "종목2"]}}],
"avoid_sectors": [{{"name": "업종명", "score": 30, "reasoning": "비추천 이유", "risks": ["리스크1"]}}],
"rotation_signal": "RISK_ON/RISK_OFF/NEUTRAL",
"key_themes": ["테마1", "테마2", "테마3"],
"policy_impact": "정책/금리가 한국 업종에 미치는 영향 (2-3문장)",
"trading_idea": "구체적인 트레이딩 아이디어 (2-3문장)",
"foreign_flow_outlook": "외국인 수급 전망 (1-2문장)"}}"""

            msg = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = msg.content[0].text
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.split("```")[0]
            
            result = json.loads(text.strip())
            result["source"] = "claude"
            return result
        except Exception as e:
            print(f"    ⚠️ Claude 오류: {e}")
            return self._basic_analysis(kr_data, us_data, macro)
    
    def _basic_analysis(self, kr_data: List[Dict], us_data: List[Dict], macro: Dict) -> Dict:
        """기본 분석"""
        sorted_kr = sorted(kr_data, key=lambda x: x["perf_month"], reverse=True)
        return {
            "market_cycle": "MID_EXPANSION",
            "cycle_reasoning": "퍼포먼스 기반 분석",
            "top_sectors": [
                {"name": s["name"], "score": 80-i*5, "reasoning": f"월간 {s['perf_month']:+.1f}% 상승", "catalysts": [], "target_stocks": []}
                for i, s in enumerate(sorted_kr[:3])
            ],
            "avoid_sectors": [
                {"name": s["name"], "score": 30+i*5, "reasoning": f"월간 {s['perf_month']:+.1f}%", "risks": []}
                for i, s in enumerate(sorted_kr[-3:])
            ],
            "rotation_signal": "NEUTRAL",
            "key_themes": ["모멘텀"],
            "policy_impact": "기본 분석",
            "trading_idea": f"상위 업종 {sorted_kr[0]['name']} 주목",
            "foreign_flow_outlook": "",
            "source": "basic"
        }
    
    def analyze(self, macro_data: Dict = None) -> Dict:
        """종합 업종 분석"""
        if macro_data is None:
            macro_data = {"overall": "NEUTRAL", "indicators": {}}
        
        print("    → 한국 업종 데이터 수집 중...")
        kr_data = []
        for name, tickers in self.kr_sectors.items():
            data = self.fetch_kr_sector(name, tickers)
            kr_data.append(data)
        kr_data.sort(key=lambda x: x["perf_month"], reverse=True)
        
        print("    → 미국 섹터 데이터 수집 중...")
        us_data = []
        for name, ticker in self.us_sectors.items():
            data = self.fetch_us_sector(name, ticker)
            us_data.append(data)
        us_data.sort(key=lambda x: x["perf_month"], reverse=True)
        
        print("    → Claude 업종 분석 중...")
        analysis = self.analyze_with_claude(kr_data, us_data, macro_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "kr_sectors": kr_data,
            "us_sectors": us_data,
            "claude_analysis": analysis,
        }


if __name__ == "__main__":
    analyzer = IndustryAnalyzer()
    result = analyzer.analyze()
    print(json.dumps(result, indent=2, ensure_ascii=False))