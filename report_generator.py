"""
Weekly Investment Strategy Report - WSJ Style + QuantLib + Macro Focus
"""
from datetime import datetime, timedelta
from typing import Dict, List
import os


class ReportGenerator:
    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def save_report(self, html: str, filename: str = None) -> str:
        if not filename:
            filename = f"weekly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(self.report_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return path

    def generate_html_report(self, analysis: Dict, decision: Dict, portfolio_value: float) -> str:
        ts = datetime.now()
        week_start = ts - timedelta(days=ts.weekday())
        week_end = week_start + timedelta(days=4)
        
        macro = analysis.get("macro", {})
        industry = analysis.get("industry", {})
        risk = analysis.get("risk", {})
        sentiment = analysis.get("sentiment", {})
        
        ind = macro.get("indicators", {})
        corr = macro.get("correlations", {})
        calendar = macro.get("calendar", {})
        claude = industry.get("claude_analysis", {})
        risk_m = risk.get("risk_metrics", {})
        quantlib = risk.get("quantlib", {})
        kr_sectors = industry.get("kr_sectors", [])
        alloc = decision.get("allocation", {})
        
        html = self._get_styles()
        html += self._build_header(ts, week_start, week_end, decision)
        html += self._build_executive_summary(macro, claude, decision)
        html += self._build_macro_dashboard(ind, quantlib)
        html += self._build_macro_analysis(ind, macro)
        html += self._build_cycle_chart(claude, ind)
        html += self._build_calendar_section(calendar)
        html += self._build_sector_section(kr_sectors, claude)
        html += self._build_quantlib_section(quantlib)
        html += self._build_risk_section(risk_m, quantlib)
        html += self._build_recommendation_section(alloc, decision)
        html += self._build_footer(ts)
        
        return html

    def _get_styles(self) -> str:
        return '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Investment Report</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700&family=Roboto+Mono:wght@400;500&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Noto Serif KR', Georgia, serif; background: #f5f5f5; color: #222; line-height: 1.7; font-size: 14px; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 60px; background: #fff; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
.masthead { text-align: center; border-bottom: 3px double #222; padding-bottom: 15px; margin-bottom: 25px; }
.masthead-title { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; }
.masthead-date { font-size: 12px; color: #666; margin-top: 6px; letter-spacing: 1px; }
.headline { font-family: 'Playfair Display', 'Noto Serif KR', serif; font-size: 32px; font-weight: 700; line-height: 1.2; margin: 25px 0 12px; text-align: center; }
.subheadline { font-size: 16px; color: #444; text-align: center; margin-bottom: 25px; font-style: italic; }
.byline { text-align: center; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #ddd; }
.section { margin-bottom: 35px; }
.section-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #222; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #222; }
.lead { font-size: 16px; line-height: 1.8; margin-bottom: 20px; }
.body-text { margin-bottom: 12px; text-align: justify; }
.two-column { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
.three-column { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.four-column { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
.five-column { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }
.data-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }
.data-table th { text-align: left; padding: 8px 10px; border-bottom: 2px solid #222; font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }
.data-table td { padding: 8px 10px; border-bottom: 1px solid #e0e0e0; }
.data-table tr:hover { background: #fafafa; }
.number { font-family: 'Roboto Mono', monospace; font-size: 13px; }
.positive { color: #1a5f2a; }
.negative { color: #b71c1c; }
.highlight-box { background: #f8f8f8; padding: 20px; margin: 20px 0; border-left: 3px solid #222; }
.highlight-title { font-weight: 700; margin-bottom: 8px; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
.stat-box { text-align: center; padding: 15px 10px; border: 1px solid #e0e0e0; background: #fff; }
.stat-value { font-size: 18px; font-weight: 700; font-family: 'Playfair Display', serif; }
.stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #666; margin-top: 4px; }
.stat-change { font-size: 11px; margin-top: 3px; }
.macro-card { background: #fafafa; padding: 18px; border-left: 3px solid #222; margin-bottom: 15px; }
.macro-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #666; margin-bottom: 8px; }
.macro-value { font-size: 24px; font-weight: 700; font-family: 'Playfair Display', serif; }
.macro-detail { font-size: 12px; color: #666; margin-top: 5px; }
.calendar-item { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
.calendar-date { font-weight: 600; color: #222; }
.importance-high { color: #b71c1c; font-weight: 600; }
.sector-item { padding: 10px; border: 1px solid #e0e0e0; text-align: center; }
.sector-name { font-size: 11px; font-weight: 600; margin-bottom: 4px; }
.sector-perf { font-size: 13px; font-weight: 700; }
.allocation-bar { display: flex; height: 6px; margin: 12px 0; background: #eee; }
.allocation-segment { height: 100%; }
.footer { margin-top: 35px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #888; }
.disclaimer { font-size: 10px; color: #888; line-height: 1.5; margin-top: 15px; padding: 12px; background: #fafafa; }
.mini-table { font-size: 12px; }
.mini-table td { padding: 5px 8px; }
.cycle-chart { position: relative; width: 100%; height: 280px; margin: 20px 0; }
.cycle-circle { position: relative; width: 240px; height: 240px; margin: 0 auto; border: 2px solid #ddd; border-radius: 50%; }
.cycle-phase { position: absolute; width: 80px; text-align: center; font-size: 11px; }
.cycle-phase-name { font-weight: 700; margin-bottom: 3px; }
.cycle-phase-desc { font-size: 10px; color: #666; }
.cycle-indicator { position: absolute; width: 12px; height: 12px; background: #222; border-radius: 50%; transform: translate(-50%, -50%); }
.cycle-arrow { position: absolute; font-size: 20px; color: #999; }
.signal-box { display: inline-block; padding: 3px 8px; font-size: 10px; font-weight: 600; border-radius: 2px; text-transform: uppercase; }
.signal-bullish { background: #e8f5e9; color: #1a5f2a; }
.signal-bearish { background: #ffebee; color: #b71c1c; }
.signal-neutral { background: #f5f5f5; color: #666; }
.indicator-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.indicator-item { padding: 12px; background: #fafafa; border-left: 3px solid #ddd; }
.indicator-item.bullish { border-left-color: #1a5f2a; }
.indicator-item.bearish { border-left-color: #b71c1c; }
.indicator-name { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #888; margin-bottom: 5px; }
.indicator-value { font-size: 18px; font-weight: 700; font-family: 'Roboto Mono', monospace; }
.indicator-signal { font-size: 11px; margin-top: 5px; }
</style>
</head>
<body>
<div class="container">
'''

    def _build_header(self, ts, week_start, week_end, decision) -> str:
        decision_text = {
            "STRONG_BUY": "Risk-On: 위험자산 적극 매수 권고",
            "BUY": "Overweight: 위험자산 비중 확대 권고",
            "HOLD": "Neutral: 현 포지션 유지 권고",
            "REDUCE": "Underweight: 위험자산 비중 축소 권고",
            "SELL": "Risk-Off: 방어적 포지션 전환 권고"
        }
        headline = decision_text.get(decision.get('decision', ''), 'Weekly Market Review')
        
        return f'''
<div class="masthead">
    <div class="masthead-title">Weekly Investment Report</div>
    <div class="masthead-date">Week of {week_start.strftime("%B %d")} - {week_end.strftime("%d, %Y")} | Seoul</div>
</div>
<div class="headline">{headline}</div>
<div class="subheadline">Score {decision.get('score', 0)}/100 · {decision.get('decision', 'N/A')}</div>
<div class="byline">AI Investment Research · Macro + QuantLib Analysis</div>
'''

    def _build_executive_summary(self, macro, claude, decision) -> str:
        rec = macro.get("recommendation", "")
        cycle = claude.get("market_cycle", "N/A").replace("_", " ")
        cycle_reason = claude.get("cycle_reasoning", "")
        trading_idea = claude.get("trading_idea", "")
        policy = claude.get("policy_impact", "")
        
        return f'''
<div class="section">
    <div class="section-title">Executive Summary</div>
    <p class="lead">{rec}</p>
    <p class="body-text"><strong>Market Cycle:</strong> {cycle}. {cycle_reason}</p>
    <p class="body-text">{trading_idea}</p>
    <p class="body-text">{policy}</p>
</div>
'''

    def _build_macro_dashboard(self, ind, quantlib) -> str:
        """매크로 대시보드 - 핵심 지표 한눈에"""
        def fmt(v, suffix=""):
            if v > 0: return f'<span class="positive">+{v:.2f}{suffix}</span>'
            elif v < 0: return f'<span class="negative">{v:.2f}{suffix}</span>'
            return f'{v:.2f}{suffix}'
        
        kospi = ind.get("kospi", {})
        sp500 = ind.get("sp500", {})
        usdkrw = ind.get("usdkrw", {})
        dxy = ind.get("dxy", {})
        vix = ind.get("vix", {})
        us10y = ind.get("us_10y", {})
        gold = ind.get("gold", {})
        oil = ind.get("oil", {})
        
        # 한국 금리
        bok_base = ind.get("bok_base", {})
        kr_10y = ind.get("kr_10y", {})
        kr_us_spread = ind.get("kr_us_spread", {})
        
        # Yield curve from quantlib
        yc = quantlib.get("yield_curve", {}) if quantlib else {}
        yc_shape = yc.get("curve_shape", "N/A")
        yc_slope = yc.get("slope_bps", 0)
        
        return f'''
<div class="section">
    <div class="section-title">Macro Dashboard</div>
    <div class="five-column">
        <div class="stat-box">
            <div class="stat-value">{kospi.get("value", 0):,.0f}</div>
            <div class="stat-label">KOSPI</div>
            <div class="stat-change">{fmt(kospi.get("week_change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{sp500.get("value", 0):,.0f}</div>
            <div class="stat-label">S&P 500</div>
            <div class="stat-change">{fmt(sp500.get("week_change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{bok_base.get("value", 0):.2f}%</div>
            <div class="stat-label">한은 기준금리</div>
            <div class="stat-change">{fmt(bok_base.get("change", 0), "%p")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{kr_10y.get("value", 0):.2f}%</div>
            <div class="stat-label">국고채 10Y</div>
            <div class="stat-change">{fmt(kr_10y.get("change", 0), "%p")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{kr_us_spread.get("value", 0):.2f}%p</div>
            <div class="stat-label">한미 금리차</div>
            <div class="stat-change">{'<span class="negative">역전</span>' if kr_us_spread.get("value", 0) < 0 else '<span class="positive">정상</span>'}</div>
        </div>
    </div>
    <div class="five-column" style="margin-top: 12px;">
        <div class="stat-box">
            <div class="stat-value">{us10y.get("value", 0):.2f}%</div>
            <div class="stat-label">US 10Y</div>
            <div class="stat-change">{fmt(us10y.get("change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{usdkrw.get("value", 0):,.0f}</div>
            <div class="stat-label">USD/KRW</div>
            <div class="stat-change">{fmt(usdkrw.get("week_change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{dxy.get("value", 0):.1f}</div>
            <div class="stat-label">DXY</div>
            <div class="stat-change">{fmt(dxy.get("week_change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{vix.get("value", 0):.1f}</div>
            <div class="stat-label">VIX</div>
            <div class="stat-change">{fmt(vix.get("week_change_pct", 0), "%")}</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">${gold.get("value", 0):,.0f}</div>
            <div class="stat-label">Gold</div>
            <div class="stat-change">{fmt(gold.get("week_change_pct", 0), "%")}</div>
        </div>
    </div>
</div>
'''

    def _build_macro_analysis(self, ind, macro) -> str:
        """상세 매크로 분석"""
        def fmt(v, suffix=""):
            if v > 0: return f'<span class="positive">+{v:.2f}{suffix}</span>'
            elif v < 0: return f'<span class="negative">{v:.2f}{suffix}</span>'
            return f'{v:.2f}{suffix}'
        
        def get_signal(name, value, change=0):
            signals = {
                "us_10y": ("BEARISH", "금리 상승 → 성장주 부담") if value > 4.5 else ("BULLISH", "금리 안정 → 성장주 우호") if value < 4.0 else ("NEUTRAL", "금리 중립"),
                "dxy": ("BEARISH", "달러 강세 → EM 자금 이탈") if value > 105 else ("BULLISH", "달러 약세 → EM 자금 유입") if value < 100 else ("NEUTRAL", "달러 중립"),
                "vix": ("BEARISH", "변동성 확대 → Risk-Off") if value > 25 else ("BULLISH", "변동성 축소 → Risk-On") if value < 15 else ("NEUTRAL", "변동성 보통"),
                "usdkrw": ("MIXED", "원화 약세 → 수출 유리, 외인 이탈") if value > 1400 else ("BULLISH", "원화 강세 → 외인 유입") if value < 1300 else ("NEUTRAL", "환율 안정"),
                "gold": ("BEARISH", "안전자산 선호 → Risk-Off") if change > 3 else ("BULLISH", "위험자산 선호") if change < -3 else ("NEUTRAL", "중립"),
                "oil": ("BULLISH", "유가 상승 → 인플레 우려") if change > 5 else ("BEARISH", "유가 하락 → 경기 둔화 우려") if change < -5 else ("NEUTRAL", "유가 안정"),
                "kr_us_spread": ("BEARISH", "한미 금리 역전 → 외인 이탈 압력") if value < -1.0 else ("BULLISH", "한미 금리 정상화 → 외인 유입") if value > 0 else ("NEUTRAL", "한미 금리차 중립"),
            }
            return signals.get(name, ("NEUTRAL", ""))
        
        # 한국 금리
        bok_base = ind.get("bok_base", {})
        kr_3y = ind.get("kr_3y", {})
        kr_10y = ind.get("kr_10y", {})
        kr_spread = ind.get("kr_spread", {})
        kr_us_spread = ind.get("kr_us_spread", {})
        
        # 미국 금리
        us10y = ind.get("us_10y", {})
        us2y = ind.get("us_2y", {})
        us30y = ind.get("us_30y", {})
        dxy = ind.get("dxy", {})
        vix = ind.get("vix", {})
        usdkrw = ind.get("usdkrw", {})
        gold = ind.get("gold", {})
        oil = ind.get("oil", {})
        copper = ind.get("copper", {})
        btc = ind.get("btc", {})
        
        # 시그널 계산
        sig_10y = get_signal("us_10y", us10y.get("value", 0))
        sig_dxy = get_signal("dxy", dxy.get("value", 0))
        sig_vix = get_signal("vix", vix.get("value", 0))
        sig_krw = get_signal("usdkrw", usdkrw.get("value", 0))
        sig_gold = get_signal("gold", 0, gold.get("week_change_pct", 0))
        sig_oil = get_signal("oil", 0, oil.get("week_change_pct", 0))
        sig_kr_us = get_signal("kr_us_spread", kr_us_spread.get("value", 0))
        
        def signal_class(sig):
            return "bullish" if sig == "BULLISH" else "bearish" if sig == "BEARISH" else ""
        
        def signal_box(sig):
            cls = "signal-bullish" if sig == "BULLISH" else "signal-bearish" if sig == "BEARISH" else "signal-neutral"
            return f'<span class="signal-box {cls}">{sig}</span>'
        
        return f'''
<div class="section">
    <div class="section-title">Macro Indicators Analysis</div>
    
    <div class="two-column">
        <div>
            <div class="macro-card">
                <div class="macro-title">Interest Rates (Korea)</div>
                <table class="mini-table" style="width: 100%;">
                    <tr><td>한은 기준금리</td><td class="number">{bok_base.get("value", 0):.2f}%</td><td>{fmt(bok_base.get("change", 0), "%p")}</td></tr>
                    <tr><td>국고채 3년</td><td class="number">{kr_3y.get("value", 0):.2f}%</td><td>{fmt(kr_3y.get("change", 0), "%p")}</td></tr>
                    <tr><td>국고채 10년</td><td class="number">{kr_10y.get("value", 0):.2f}%</td><td>{fmt(kr_10y.get("change", 0), "%p")}</td></tr>
                    <tr><td>10Y-3Y 스프레드</td><td class="number">{kr_spread.get("value", 0):.2f}%</td><td>{'<span class="positive">정상</span>' if kr_spread.get("value", 0) > 0 else '<span class="negative">역전</span>'}</td></tr>
                    <tr><td><strong>한미 금리차 (10Y)</strong></td><td class="number"><strong>{kr_us_spread.get("value", 0):.2f}%p</strong></td><td>{'<span class="negative">역전</span>' if kr_us_spread.get("value", 0) < 0 else '<span class="positive">정상</span>'}</td></tr>
                </table>
                <div class="macro-detail" style="margin-top: 10px;">
                    {signal_box(sig_kr_us[0])} {sig_kr_us[1]}
                </div>
            </div>
            
            <div class="macro-card">
                <div class="macro-title">Interest Rates (US Treasury)</div>
                <table class="mini-table" style="width: 100%;">
                    <tr><td>2Y Yield</td><td class="number">{us2y.get("value", 0):.2f}%</td><td>{fmt(us2y.get("change_pct", 0), "%")}</td></tr>
                    <tr><td>10Y Yield</td><td class="number">{us10y.get("value", 0):.2f}%</td><td>{fmt(us10y.get("change_pct", 0), "%")}</td></tr>
                    <tr><td>30Y Yield</td><td class="number">{us30y.get("value", 0):.2f}%</td><td>{fmt(us30y.get("change_pct", 0), "%")}</td></tr>
                    <tr><td>10Y-2Y Spread</td><td class="number">{ind.get("yield_spread", 0):.2f}%</td><td>{'<span class="negative">역전</span>' if ind.get("yield_spread", 0) < 0 else '<span class="positive">정상</span>'}</td></tr>
                </table>
                <div class="macro-detail" style="margin-top: 10px;">
                    {signal_box(sig_10y[0])} {sig_10y[1]}
                </div>
            </div>
        </div>
        
        <div>
            <div class="macro-card">
                <div class="macro-title">Currency & Dollar Index</div>
                <table class="mini-table" style="width: 100%;">
                    <tr><td>DXY (Dollar Index)</td><td class="number">{dxy.get("value", 0):.2f}</td><td>{fmt(dxy.get("week_change_pct", 0), "%")}</td></tr>
                    <tr><td>USD/KRW</td><td class="number">{usdkrw.get("value", 0):,.0f}</td><td>{fmt(usdkrw.get("week_change_pct", 0), "%")}</td></tr>
                    <tr><td>EUR/USD</td><td class="number">{ind.get("eurusd", {}).get("value", 0):.4f}</td><td>{fmt(ind.get("eurusd", {}).get("week_change_pct", 0), "%")}</td></tr>
                    <tr><td>USD/JPY</td><td class="number">{ind.get("usdjpy", {}).get("value", 0):.2f}</td><td>{fmt(ind.get("usdjpy", {}).get("week_change_pct", 0), "%")}</td></tr>
                </table>
                <div class="macro-detail" style="margin-top: 10px;">
                    {signal_box(sig_dxy[0])} {sig_dxy[1]}<br>
                    {signal_box(sig_krw[0])} {sig_krw[1]}
                </div>
            </div>
            
            <div class="macro-card">
                <div class="macro-title">Volatility & Risk Sentiment</div>
                <table class="mini-table" style="width: 100%;">
                    <tr><td>VIX (Fear Index)</td><td class="number">{vix.get("value", 0):.2f}</td><td>{fmt(vix.get("week_change_pct", 0), "%")}</td></tr>
                    <tr><td>MOVE (Bond Vol)</td><td class="number">{ind.get("move", {}).get("value", 0):.1f}</td><td>-</td></tr>
                    <tr><td>1M Range (KOSPI)</td><td class="number" colspan="2">{ind.get("kospi", {}).get("low_1m", 0):,.0f} - {ind.get("kospi", {}).get("high_1m", 0):,.0f}</td></tr>
                </table>
                <div class="macro-detail" style="margin-top: 10px;">
                    {signal_box(sig_vix[0])} {sig_vix[1]}
                </div>
            </div>
        </div>
    </div>
    
    <div class="two-column" style="margin-top: 15px;">
        <div class="macro-card">
            <div class="macro-title">Commodities & Crypto</div>
            <table class="mini-table" style="width: 100%;">
                <tr><td>Gold</td><td class="number">${gold.get("value", 0):,.2f}</td><td>{fmt(gold.get("week_change_pct", 0), "%")}</td></tr>
                <tr><td>WTI Crude</td><td class="number">${oil.get("value", 0):.2f}</td><td>{fmt(oil.get("week_change_pct", 0), "%")}</td></tr>
                <tr><td>Copper</td><td class="number">${copper.get("value", 0):.2f}</td><td>{fmt(copper.get("week_change_pct", 0), "%")}</td></tr>
                <tr><td>Bitcoin</td><td class="number">${btc.get("value", 0):,.0f}</td><td>{fmt(btc.get("week_change_pct", 0), "%")}</td></tr>
                </table>
                <div class="macro-detail" style="margin-top: 10px;">
                    {signal_box(sig_gold[0])} Gold: {sig_gold[1]}<br>
                    {signal_box(sig_oil[0])} Oil: {sig_oil[1]}
                </div>
            </div>
        </div>
    </div>
    
    <div class="highlight-box" style="margin-top: 20px;">
        <div class="highlight-title">Macro Signal Summary</div>
        <div class="indicator-grid">
            <div class="indicator-item {signal_class(sig_kr_us[0])}">
                <div class="indicator-name">한미 금리차</div>
                <div class="indicator-value">{kr_us_spread.get("value", 0):.2f}%p</div>
                <div class="indicator-signal">{sig_kr_us[1]}</div>
            </div>
            <div class="indicator-item {signal_class(sig_10y[0])}">
                <div class="indicator-name">US 10Y</div>
                <div class="indicator-value">{us10y.get("value", 0):.2f}%</div>
                <div class="indicator-signal">{sig_10y[1]}</div>
            </div>
            <div class="indicator-item {signal_class(sig_dxy[0])}">
                <div class="indicator-name">Dollar (DXY)</div>
                <div class="indicator-value">{dxy.get("value", 0):.1f}</div>
                <div class="indicator-signal">{sig_dxy[1]}</div>
            </div>
            <div class="indicator-item {signal_class(sig_krw[0])}">
                <div class="indicator-name">USD/KRW</div>
                <div class="indicator-value">{usdkrw.get("value", 0):,.0f}</div>
                <div class="indicator-signal">{sig_krw[1]}</div>
            </div>
            <div class="indicator-item {signal_class(sig_vix[0])}">
                <div class="indicator-name">Volatility (VIX)</div>
                <div class="indicator-value">{vix.get("value", 0):.1f}</div>
                <div class="indicator-signal">{sig_vix[1]}</div>
            </div>
            <div class="indicator-item {signal_class(sig_gold[0])}">
                <div class="indicator-name">Gold</div>
                <div class="indicator-value">${gold.get("value", 0):,.0f}</div>
                <div class="indicator-signal">{sig_gold[1]}</div>
            </div>
        </div>
    </div>
</div>
'''

    def _build_cycle_chart(self, claude, ind) -> str:
        """산업 사이클 차트"""
        cycle = claude.get("market_cycle", "MID_EXPANSION")
        rotation = claude.get("rotation_signal", "NEUTRAL")
        
        # 사이클 위치 계산 (시계 방향: 12시=EARLY_EXPANSION)
        cycle_positions = {
            "EARLY_EXPANSION": {"angle": 0, "x": 120, "y": 20},
            "MID_EXPANSION": {"angle": 45, "x": 200, "y": 60},
            "LATE_EXPANSION": {"angle": 90, "x": 220, "y": 120},
            "PEAK": {"angle": 135, "x": 200, "y": 180},
            "EARLY_CONTRACTION": {"angle": 180, "x": 120, "y": 220},
            "MID_CONTRACTION": {"angle": 225, "x": 40, "y": 180},
            "LATE_CONTRACTION": {"angle": 270, "x": 20, "y": 120},
            "TROUGH": {"angle": 315, "x": 40, "y": 60},
            "RECESSION": {"angle": 180, "x": 120, "y": 220},
        }
        
        pos = cycle_positions.get(cycle, cycle_positions["MID_EXPANSION"])
        
        # 각 사이클 단계별 추천 섹터
        cycle_sectors = {
            "EARLY_EXPANSION": "기술주, 소비재, 금융",
            "MID_EXPANSION": "산업재, 소재, 에너지",
            "LATE_EXPANSION": "에너지, 소재, 필수소비재",
            "PEAK": "필수소비재, 헬스케어, 유틸리티",
            "EARLY_CONTRACTION": "유틸리티, 헬스케어, 채권",
            "RECESSION": "채권, 현금, 방어주",
        }
        
        rec_sectors = cycle_sectors.get(cycle, "균형 포트폴리오")
        
        return f'''
<div class="section">
    <div class="section-title">Business Cycle Analysis</div>
    
    <div class="two-column">
        <div>
            <div style="position: relative; width: 260px; height: 260px; margin: 0 auto;">
                <!-- 사이클 원 -->
                <svg width="260" height="260" style="position: absolute; top: 0; left: 0;">
                    <circle cx="130" cy="130" r="100" fill="none" stroke="#ddd" stroke-width="2"/>
                    <circle cx="130" cy="130" r="60" fill="none" stroke="#eee" stroke-width="1"/>
                    
                    <!-- 사분면 라인 -->
                    <line x1="130" y1="30" x2="130" y2="230" stroke="#eee" stroke-width="1"/>
                    <line x1="30" y1="130" x2="230" y2="130" stroke="#eee" stroke-width="1"/>
                    
                    <!-- 화살표 (시계방향) -->
                    <path d="M 130 35 L 135 45 L 125 45 Z" fill="#999"/>
                    <path d="M 225 130 L 215 135 L 215 125 Z" fill="#999"/>
                    <path d="M 130 225 L 125 215 L 135 215 Z" fill="#999"/>
                    <path d="M 35 130 L 45 125 L 45 135 Z" fill="#999"/>
                    
                    <!-- 현재 위치 표시 -->
                    <circle cx="{pos['x']}" cy="{pos['y']}" r="8" fill="#222"/>
                    <circle cx="{pos['x']}" cy="{pos['y']}" r="12" fill="none" stroke="#222" stroke-width="2"/>
                </svg>
                
                <!-- 라벨 -->
                <div style="position: absolute; top: 5px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; text-align: center;">
                    EARLY<br>EXPANSION
                </div>
                <div style="position: absolute; top: 50%; right: 0; transform: translateY(-50%); font-size: 10px; font-weight: 600; text-align: center;">
                    LATE<br>EXPANSION
                </div>
                <div style="position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; text-align: center;">
                    CONTRACTION
                </div>
                <div style="position: absolute; top: 50%; left: 0; transform: translateY(-50%); font-size: 10px; font-weight: 600; text-align: center;">
                    RECOVERY
                </div>
                
                <!-- 중앙 텍스트 -->
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <div style="font-size: 11px; font-weight: 700; color: #222;">CURRENT</div>
                    <div style="font-size: 14px; font-weight: 700; color: #222; margin-top: 3px;">{cycle.replace("_", " ")}</div>
                </div>
            </div>
        </div>
        
        <div>
            <div class="macro-card">
                <div class="macro-title">Current Cycle Position</div>
                <div class="macro-value" style="font-size: 18px;">{cycle.replace("_", " ")}</div>
                <div class="macro-detail" style="margin-top: 10px;">
                    <strong>Rotation Signal:</strong> 
                    <span class="signal-box {'signal-bullish' if rotation == 'RISK_ON' else 'signal-bearish' if rotation == 'RISK_OFF' else 'signal-neutral'}">{rotation}</span>
                </div>
            </div>
            
            <div class="macro-card">
                <div class="macro-title">Recommended Sectors</div>
                <div class="macro-detail">{rec_sectors}</div>
            </div>
            
            <div class="macro-card">
                <div class="macro-title">Cycle Characteristics</div>
                <div class="macro-detail" style="font-size: 12px; line-height: 1.6;">
                    {'• GDP 성장 가속<br>• 기업이익 개선<br>• 금리 상승 초기<br>• 주식 > 채권' if 'EXPANSION' in cycle else 
                     '• GDP 성장 둔화<br>• 기업이익 정체<br>• 금리 고점<br>• 방어주 선호' if 'CONTRACTION' in cycle or 'RECESSION' in cycle else
                     '• 경기 바닥 확인<br>• 정책 완화 기대<br>• 선행지표 개선<br>• 성장주 매수 기회'}
                </div>
            </div>
        </div>
    </div>
</div>
'''

    def _build_calendar_section(self, calendar) -> str:
        us_events = calendar.get("us_events", [])
        kr_events = calendar.get("kr_events", [])
        earnings = calendar.get("earnings", [])
        
        us_html = ""
        for e in us_events[:5]:
            imp_class = "importance-high" if e.get("importance") == "HIGH" else ""
            us_html += f'<div class="calendar-item"><span class="calendar-date">{e.get("date", "")}</span> <span class="calendar-event {imp_class}">{e.get("event", "")}</span></div>'
        
        kr_html = ""
        for e in kr_events[:5]:
            imp_class = "importance-high" if e.get("importance") == "HIGH" else ""
            kr_html += f'<div class="calendar-item"><span class="calendar-date">{e.get("date", "")}</span> <span class="calendar-event {imp_class}">{e.get("event", "")}</span></div>'
        
        earn_html = ""
        for e in earnings[:6]:
            earn_html += f'<div class="calendar-item"><span class="calendar-date">{e.get("date", "")}</span> {e.get("company", "")} ({e.get("market", "")})</div>'
        
        return f'''
<div class="section">
    <div class="section-title">Economic Calendar</div>
    <div class="three-column">
        <div>
            <p class="body-text"><strong>US Events</strong></p>
            {us_html if us_html else '<p style="color: #888;">No events</p>'}
        </div>
        <div>
            <p class="body-text"><strong>Korea Events</strong></p>
            {kr_html if kr_html else '<p style="color: #888;">No events</p>'}
        </div>
        <div>
            <p class="body-text"><strong>Earnings</strong></p>
            {earn_html if earn_html else '<p style="color: #888;">No earnings</p>'}
        </div>
    </div>
</div>
'''

    def _build_sector_section(self, kr_sectors, claude) -> str:
        top_sectors = claude.get("top_sectors", [])
        avoid_sectors = claude.get("avoid_sectors", [])
        themes = claude.get("key_themes", [])
        
        sector_html = ""
        for s in kr_sectors[:12]:
            perf = s.get("perf_month", 0)
            color_class = "positive" if perf > 0 else "negative" if perf < 0 else ""
            sector_html += f'''
            <div class="sector-item">
                <div class="sector-name">{s.get("name", "")}</div>
                <div class="sector-perf {color_class}">{perf:+.1f}%</div>
            </div>'''
        
        top_html = ""
        for s in top_sectors[:3]:
            top_html += f'''
            <tr>
                <td><strong>{s.get("name", "")}</strong></td>
                <td class="number">{s.get("score", 0)}</td>
                <td style="font-size: 12px;">{s.get("reasoning", "")[:70]}...</td>
            </tr>'''
        
        avoid_html = ""
        for s in avoid_sectors[:2]:
            avoid_html += f'''
            <tr>
                <td><strong>{s.get("name", "")}</strong></td>
                <td class="number">{s.get("score", 0)}</td>
                <td style="font-size: 12px;">{s.get("reasoning", "")[:50]}...</td>
            </tr>'''
        
        themes_text = " · ".join(themes) if themes else "-"
        
        return f'''
<div class="section">
    <div class="section-title">Sector Analysis</div>
    <p class="body-text"><strong>Monthly Performance</strong></p>
    <div class="four-column" style="margin-bottom: 20px;">
        {sector_html}
    </div>
    
    <div class="two-column">
        <div>
            <p class="body-text"><strong>Overweight</strong></p>
            <table class="data-table">
                <tr><th>Sector</th><th>Score</th><th>Rationale</th></tr>
                {top_html if top_html else '<tr><td colspan="3">-</td></tr>'}
            </table>
        </div>
        <div>
            <p class="body-text"><strong>Underweight</strong></p>
            <table class="data-table">
                <tr><th>Sector</th><th>Score</th><th>Risk</th></tr>
                {avoid_html if avoid_html else '<tr><td colspan="3">-</td></tr>'}
            </table>
        </div>
    </div>
    
    <p class="body-text" style="margin-top: 15px;"><strong>Key Themes:</strong> {themes_text}</p>
</div>
'''

    def _build_quantlib_section(self, quantlib) -> str:
        if not quantlib:
            return ""
        
        vasicek = quantlib.get("vasicek", {})
        yield_curve = quantlib.get("yield_curve", {})
        volatility = quantlib.get("volatility", {})
        bond = quantlib.get("bond_10y", {})
        
        vas_params = vasicek.get("parameters", {})
        vas_path = vasicek.get("expected_path", {})
        
        vol_atm = volatility.get("atm_volatility", 0)
        vol_skew = volatility.get("skew_metrics", {})
        vol_interp = volatility.get("skew_interpretation", "")
        
        return f'''
<div class="section">
    <div class="section-title">Quantitative Analysis (QuantLib)</div>
    
    <div class="three-column">
        <div class="macro-card">
            <div class="macro-title">Vasicek Rate Model</div>
            <table class="mini-table" style="width: 100%;">
                <tr><td>Current (r₀)</td><td class="number">{vas_params.get("r0", 0)}%</td></tr>
                <tr><td>Long-term (θ)</td><td class="number">{vas_params.get("theta", 0)}%</td></tr>
                <tr><td>Mean Rev. (κ)</td><td class="number">{vas_params.get("kappa", 0)}</td></tr>
                <tr><td>Half-life</td><td class="number">{vasicek.get("half_life_years", 0)}Y</td></tr>
            </table>
        </div>
        
        <div class="macro-card">
            <div class="macro-title">Yield Curve</div>
            <table class="mini-table" style="width: 100%;">
                <tr><td>Shape</td><td><strong>{yield_curve.get("curve_shape", "N/A")}</strong></td></tr>
                <tr><td>Slope</td><td class="number">{yield_curve.get("slope_bps", 0):.0f} bps</td></tr>
                <tr><td>Short Rate</td><td class="number">{yield_curve.get("short_rate", 0)}%</td></tr>
                <tr><td>Long Rate</td><td class="number">{yield_curve.get("long_rate", 0)}%</td></tr>
            </table>
            <div class="macro-detail" style="margin-top: 8px; font-size: 11px;">{yield_curve.get("interpretation", "")}</div>
        </div>
        
        <div class="macro-card">
            <div class="macro-title">Volatility Surface</div>
            <table class="mini-table" style="width: 100%;">
                <tr><td>ATM Vol</td><td class="number">{vol_atm}%</td></tr>
                <tr><td>Skew</td><td class="number">{vol_skew.get("skew", 0)}%</td></tr>
                <tr><td>Risk Rev.</td><td class="number">{vol_skew.get("risk_reversal", 0)}%</td></tr>
                <tr><td>Term</td><td>{volatility.get("term_shape", "N/A")}</td></tr>
            </table>
            <div class="macro-detail" style="margin-top: 8px; font-size: 11px;">{vol_interp}</div>
        </div>
    </div>
    
    <div class="highlight-box" style="margin-top: 15px;">
        <div class="highlight-title">Rate Path Forecast (Vasicek)</div>
        <p class="body-text" style="font-size: 12px;">
            {' → '.join([f"{k}: {v}%" for k, v in list(vas_path.items())[:5]])}
        </p>
        <p class="body-text" style="font-size: 11px; color: #666; margin-top: 5px;">
            10Y Bond: Price {bond.get("price", 0):,.0f} | Duration {bond.get("modified_duration", 0):.2f} | Convexity {bond.get("convexity", 0):.1f}
        </p>
    </div>
</div>
'''

    def _build_risk_section(self, risk_m, quantlib) -> str:
        level = risk_m.get("risk_level", "MEDIUM")
        score = risk_m.get("risk_score", 50)
        move = risk_m.get("move_value", 0)
        vix = risk_m.get("vix_value", 0)
        vol_mult = risk_m.get("vol_multiplier", 1.0)
        
        return f'''
<div class="section">
    <div class="section-title">Risk Assessment</div>
    <div class="two-column">
        <div>
            <table class="data-table">
                <tr><td>Risk Level</td><td><strong>{level}</strong></td></tr>
                <tr><td>Risk Score</td><td class="number">{score}/100</td></tr>
                <tr><td>VIX</td><td class="number">{vix:.1f}</td></tr>
                <tr><td>MOVE (est.)</td><td class="number">{move:.1f}</td></tr>
                <tr><td>Vol Multiplier</td><td class="number">{vol_mult:.3f}x</td></tr>
            </table>
        </div>
        <div>
            <div class="highlight-box">
                <div class="highlight-title">Risk Commentary</div>
                <p class="body-text" style="font-size: 12px;">
                    {'현재 시장 변동성이 높습니다. 포지션 규모를 축소하고 손절 라인을 타이트하게 설정하십시오.' if score >= 70 else 
                     '변동성이 보통 수준입니다. 기존 포지션을 유지하되 주요 지표를 모니터링하십시오.' if score >= 40 else
                     '시장 변동성이 낮습니다. 적극적인 포지션 확대를 고려할 수 있습니다.'}
                </p>
            </div>
        </div>
    </div>
</div>
'''


    def _build_recommendation_section(self, alloc, decision) -> str:
        """투자 추천 섹션"""
        score = decision.get("score", 50)
        dec = decision.get("decision", "HOLD")
        action = decision.get("action", "")
        signals = decision.get("signals", {})
        recs = decision.get("recommendations", {})
        
        # 자산배분 바 색상
        colors = {
            "주식": "#222",
            "채권": "#666",
            "현금": "#bbb",
        }
        
        alloc_bar = ""
        for asset, pct in alloc.items():
            color = colors.get(asset, "#999")
            alloc_bar += f'<div class="allocation-segment" style="width: {pct}%; background: {color};"></div>'
        
        alloc_legend = " · ".join([f"{k} {v}%" for k, v in alloc.items()])
        
        # 시그널 요약
        signal_html = ""
        signal_labels = {
            "macro": "Macro",
            "risk": "Risk",
            "sentiment": "Sentiment",
            "rotation": "Rotation",
        }
        for key, label in signal_labels.items():
            val = signals.get(key, "N/A")
            cls = "signal-bullish" if val in ["BULLISH", "LOW", "POSITIVE", "RISK_ON"] else \
                  "signal-bearish" if val in ["BEARISH", "HIGH", "NEGATIVE", "RISK_OFF"] else "signal-neutral"
            signal_html += f'<span class="signal-box {cls}" style="margin-right: 8px;">{label}: {val}</span>'
        
        # 결정 색상
        dec_class = "positive" if dec in ["STRONG_BUY", "BUY"] else "negative" if dec in ["SELL", "REDUCE"] else ""
        
        return f'''
<div class="section">
    <div class="section-title">Investment Recommendation</div>
    
    <div class="highlight-box" style="text-align: center; padding: 25px;">
        <div style="font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #666; margin-bottom: 10px;">Composite Score</div>
        <div style="font-size: 48px; font-weight: 700; font-family: 'Playfair Display', serif;">{score}<span style="font-size: 24px; color: #888;">/100</span></div>
        <div style="font-size: 20px; font-weight: 700; margin-top: 10px;" class="{dec_class}">{dec}</div>
        <div style="font-size: 14px; color: #666; margin-top: 8px;">{action}</div>
    </div>
    
    <div style="margin-top: 20px;">
        <p class="body-text"><strong>Signal Summary</strong></p>
        <div style="margin: 10px 0;">{signal_html}</div>
    </div>
    
    <div style="margin-top: 20px;">
        <p class="body-text"><strong>Recommended Allocation</strong></p>
        <div class="allocation-bar">{alloc_bar}</div>
        <p style="font-size: 12px; color: #666; text-align: center;">{alloc_legend}</p>
    </div>
    
    <div class="two-column" style="margin-top: 20px;">
        <div>
            <p class="body-text"><strong>Primary Sector</strong></p>
            <p style="font-size: 16px; font-weight: 600;">{recs.get("primary_sector", "N/A")}</p>
            <p style="font-size: 12px; color: #666; margin-top: 5px;">Position Size: {recs.get("position_size", "10%")}</p>
        </div>
        <div>
            <p class="body-text"><strong>Key Catalysts</strong></p>
            <ul style="font-size: 12px; color: #444; padding-left: 18px; margin-top: 5px;">
                {"".join([f"<li>{c}</li>" for c in recs.get("catalysts", [])[:3]]) or "<li>-</li>"}
            </ul>
        </div>
    </div>
    
    {f'<div class="highlight-box" style="margin-top: 20px; border-left-color: #b71c1c;"><div class="highlight-title" style="color: #b71c1c;">Risk Warning</div><p class="body-text" style="font-size: 12px;">현재 리스크 점수가 높습니다. 포지션 규모를 축소하고 손절 라인을 엄격히 준수하십시오.</p></div>' if decision.get("risk_warning") else ""}
</div>
'''

    def _build_footer(self, ts) -> str:
        """푸터 섹션"""
        return f'''
<div class="footer">
    <div class="two-column">
        <div>
            <p>Generated: {ts.strftime("%Y-%m-%d %H:%M:%S KST")}</p>
            <p>AI Investment Research System v2.0</p>
        </div>
        <div style="text-align: right;">
            <p>Powered by QuantLib + Claude Sonnet 4</p>
            <p>Data: yfinance, BigKinds</p>
        </div>
    </div>
    
    <div class="disclaimer">
        <strong>Disclaimer:</strong> 본 리포트는 AI 기반 자동화 시스템에 의해 생성되었으며, 투자 권유가 아닌 참고 자료입니다. 
        모든 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다. 
        과거 성과가 미래 수익을 보장하지 않으며, 투자에는 원금 손실의 위험이 있습니다.
        본 자료에 포함된 정보의 정확성이나 완전성을 보장하지 않습니다.
    </div>
</div>
</div>
</body>
</html>
'''
