"""
투자 판단 자동화 시스템 - 메인 모듈
Macro → Industry → Risk → Sentiment 통합 분석
Claude Sonnet 4 + Finviz + 정하림 MOVE 모형
"""
from datetime import datetime
from typing import Dict
import json
import os

from macro_layer import MacroAnalyzer
from industry_layer import IndustryAnalyzer
from risk_layer import RiskManager
from sentiment_layer import SentimentAnalyzer
from report_generator import ReportGenerator


class InvestmentAdvisor:
    """
    투자 판단 자동화 시스템
    
    5개 레이어 통합:
    1. MACRO: 거시경제 지표 분석
    2. INDUSTRY: 섹터 로테이션
    3. RISK: 리스크 관리 (정하림 MOVE 모형)
    4. SENTIMENT: 뉴스 감성 분석
    5. DECISION: 최종 투자 판단
    """
    
    def __init__(self, portfolio_value: float = 100000000):
        self.macro = MacroAnalyzer()
        self.industry = IndustryAnalyzer()
        self.risk = RiskManager()
        self.sentiment = SentimentAnalyzer()
        self.report_gen = ReportGenerator()
        self.portfolio_value = portfolio_value
    
    def analyze_all(self) -> Dict:
        """전체 분석 실행"""
        print("\n🔄 분석 시작...")
        
        # 1. MACRO 분석
        print("  [1/4] MACRO 분석 중...")
        macro_result = self.macro.analyze()
        
        # 2. INDUSTRY 분석 (매크로 결과 활용)
        print("  [2/4] INDUSTRY 분석 중...")
        industry_result = self.industry.analyze(macro_result)
        
        # 3. RISK 분석
        print("  [3/4] RISK 분석 중...")
        move_value = macro_result["indicators"]["move"]["value"]
        vix_value = macro_result["indicators"]["vix"].get("value", 18)
        
        # QuantLib 분석을 위한 market_data 전달
        market_data = {
            "us_10y": macro_result["indicators"]["us_10y"].get("value", 0.0427) / 100,
            "us_2y": macro_result["indicators"]["us_2y"].get("value", 0.0359) / 100,
            "us_30y": macro_result["indicators"].get("us_30y", {}).get("value", 0.045) / 100,
            "vix": vix_value,
            "kospi": macro_result["indicators"]["kospi"].get("value", 2650),
        }
        risk_result = self.risk.analyze(move_value, vix_value, self.portfolio_value, market_data)
        
        # 4. SENTIMENT 분석
        print("  [4/4] SENTIMENT 분석 중...")
        sentiment_result = self.sentiment.analyze(["금리", "증시", "경제"])
        
        print("✅ 분석 완료!")
        
        return {
            "macro": macro_result,
            "industry": industry_result,
            "risk": risk_result,
            "sentiment": sentiment_result,
        }
    
    def make_decision(self, analysis: Dict) -> Dict:
        """
        최종 투자 판단
        
        Args:
            analysis: 전체 분석 결과
        
        Returns:
            최종 투자 판단 및 추천
        """
        # 각 레이어 시그널 추출
        macro_signal = analysis["macro"]["overall"]
        risk_level = analysis["risk"]["risk_metrics"]["risk_level"]
        risk_score = analysis["risk"]["risk_metrics"]["risk_score"]
        sentiment = analysis["sentiment"]["sentiment"]["overall_sentiment"]
        
        # industry 구조 변경 반영
        claude_analysis = analysis["industry"].get("claude_analysis", {})
        top_sectors = claude_analysis.get("top_sectors", [])
        top_sector = top_sectors[0].get("name", "N/A") if top_sectors else "N/A"
        top_sector_catalysts = top_sectors[0].get("catalysts", []) if top_sectors else []
        rotation_signal = claude_analysis.get("rotation_signal", "NEUTRAL")
        
        # 점수 계산 (100점 만점)
        score = 50  # 기본
        
        # 매크로 반영 (±20)
        if macro_signal == "BULLISH":
            score += 20
        elif macro_signal == "BEARISH":
            score -= 20
        
        # 리스크 반영 (±15)
        if risk_level == "LOW":
            score += 15
        elif risk_level == "HIGH":
            score -= 15
        
        # 감성 반영 (±15)
        if sentiment == "POSITIVE":
            score += 15
        elif sentiment == "NEGATIVE":
            score -= 15
        
        # 로테이션 시그널 반영 (±10)
        if rotation_signal == "RISK_ON":
            score += 10
        elif rotation_signal == "RISK_OFF":
            score -= 10
        
        # 최종 판단
        if score >= 70:
            decision = "STRONG_BUY"
            action = "위험자산 적극 매수"
            allocation = {"주식": 70, "채권": 20, "현금": 10}
        elif score >= 55:
            decision = "BUY"
            action = "위험자산 비중 확대"
            allocation = {"주식": 60, "채권": 30, "현금": 10}
        elif score >= 45:
            decision = "HOLD"
            action = "현재 포지션 유지"
            allocation = {"주식": 50, "채권": 35, "현금": 15}
        elif score >= 30:
            decision = "REDUCE"
            action = "위험자산 비중 축소"
            allocation = {"주식": 35, "채권": 45, "현금": 20}
        else:
            decision = "SELL"
            action = "위험자산 대폭 축소"
            allocation = {"주식": 20, "채권": 50, "현금": 30}
        
        # 포지션 사이징 적용
        position_adj = analysis["risk"]["position_sizing"]["adjusted_allocation"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "decision": decision,
            "action": action,
            "allocation": allocation,
            "signals": {
                "macro": macro_signal,
                "risk": risk_level,
                "sentiment": sentiment,
                "rotation": rotation_signal,
            },
            "recommendations": {
                "primary_sector": top_sector,
                "catalysts": top_sector_catalysts,
                "position_size": f"{position_adj:.1%}",
            },
            "risk_warning": risk_score > 70,
        }
    
    def generate_report(self, analysis: Dict, decision: Dict) -> str:
        """분석 리포트 생성"""
        report = []
        report.append("=" * 70)
        report.append("📊 투자 판단 자동화 시스템 - 분석 리포트")
        report.append("=" * 70)
        report.append(f"⏰ 생성 시간: {decision['timestamp']}")
        report.append(f"💰 포트폴리오: {self.portfolio_value:,.0f}원")
        report.append("")
        
        # 1. 매크로 요약
        report.append("─" * 70)
        report.append("📈 [MACRO] 거시경제 환경")
        report.append("─" * 70)
        macro = analysis["macro"]
        ind = macro["indicators"]
        report.append(f"  • KOSPI: {ind['kospi'].get('value', 0):,.2f} ({ind['kospi'].get('week_change_pct', 0):+.2f}%)")
        report.append(f"  • KOSDAQ: {ind['kosdaq'].get('value', 0):,.2f} ({ind['kosdaq'].get('week_change_pct', 0):+.2f}%)")
        report.append(f"  • USD/KRW: {ind['usdkrw'].get('value', 0):,.0f}원 ({ind['usdkrw'].get('week_change_pct', 0):+.2f}%)")
        report.append(f"  • US 10Y: {ind['us_10y'].get('value', 0):.2f}%")
        report.append(f"  • VIX: {ind['vix'].get('value', 0):.1f}")
        report.append(f"  • MOVE (추정): {ind['move'].get('value', 0):.1f}")
        report.append(f"  → 판단: {macro['overall']} - {macro['recommendation']}")
        report.append("")
        
        # 2. 섹터 요약
        report.append("─" * 70)
        report.append("🏭 [INDUSTRY] 업종 분석")
        report.append("─" * 70)
        industry = analysis["industry"]
        claude = industry.get("claude_analysis", {})
        report.append(f"  시장 사이클: {claude.get('market_cycle', 'N/A')}")
        report.append(f"  로테이션: {claude.get('rotation_signal', 'N/A')}")
        report.append("  추천 업종:")
        for s in claude.get("top_sectors", [])[:3]:
            report.append(f"    🟢 {s.get('name', 'N/A')} ({s.get('score', 0)}점) - {s.get('reasoning', '')[:40]}")
        report.append("")
        
        # 3. 리스크 요약
        report.append("─" * 70)
        report.append("⚠️ [RISK] 리스크 분석")
        report.append("─" * 70)
        risk = analysis["risk"]
        rm = risk["risk_metrics"]
        report.append(f"  • 리스크 레벨: {rm['risk_level']}")
        report.append(f"  • 리스크 점수: {rm['risk_score']}/100")
        report.append(f"  • 변동성 배수: {rm['vol_multiplier']:.2f}x")
        report.append("")
        
        # 4. 감성 분석 요약
        report.append("─" * 70)
        report.append("📰 [SENTIMENT] 뉴스 감성")
        report.append("─" * 70)
        sent = analysis["sentiment"]["sentiment"]
        report.append(f"  • 감성: {sent.get('overall_sentiment', 'N/A')}")
        report.append(f"  • 신뢰도: {sent.get('confidence', 0)*100:.0f}%")
        report.append(f"  • 뉴스 수: {analysis['sentiment'].get('news_count', 0)}건")
        report.append("")
        
        # 5. 최종 판단
        report.append("=" * 70)
        report.append("🎯 [DECISION] 최종 투자 판단")
        report.append("=" * 70)
        report.append(f"  📊 종합 점수: {decision['score']}/100")
        report.append(f"  🚦 판단: {decision['decision']}")
        report.append(f"  💡 액션: {decision['action']}")
        report.append("")
        report.append("  📌 추천 자산배분:")
        for asset, pct in decision["allocation"].items():
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            report.append(f"     {asset}: {bar} {pct}%")
        report.append("")
        report.append(f"  🎯 주력 업종: {decision['recommendations']['primary_sector']}")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run(self) -> str:
        """전체 시스템 실행"""
        analysis = self.analyze_all()
        decision = self.make_decision(analysis)
        
        # 텍스트 리포트
        text_report = self.generate_report(analysis, decision)
        
        # HTML 리포트 생성
        html_report = self.report_gen.generate_html_report(analysis, decision, self.portfolio_value)
        html_path = self.report_gen.save_report(html_report)
        
        return text_report, html_path


if __name__ == "__main__":
    # 시스템 실행
    advisor = InvestmentAdvisor(portfolio_value=100000000)  # 1억원
    text_report, html_path = advisor.run()
    
    print(text_report)
    print(f"\n📄 HTML 리포트: {html_path}")
    print("브라우저에서 열어보세요!")
    
    # 텍스트 리포트 저장
    with open("investment_report.txt", "w", encoding="utf-8") as f:
        f.write(text_report)
    print("📄 텍스트 리포트: investment_report.txt")
