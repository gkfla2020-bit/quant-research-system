"""
SENTIMENT Layer - 빅카인즈 뉴스 + Claude 감성 분석
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import anthropic
from config import BIGKINDS_KEY, CLAUDE_API_KEY


class SentimentAnalyzer:
    """빅카인즈 뉴스 + Claude 감성 분석"""
    
    def __init__(self):
        self.bigkinds_url = "https://tools.kinds.or.kr:8443/search/news"
        self.claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
    
    def fetch_bigkinds(self, keyword: str, days: int = 3) -> List[Dict]:
        """빅카인즈 API 뉴스 검색"""
        if not BIGKINDS_KEY:
            print("    ⚠️ 빅카인즈 API 키 없음")
            return []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        payload = {
            "access_key": BIGKINDS_KEY,
            "argument": {
                "query": keyword,
                "published_at": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "until": end_date.strftime("%Y-%m-%d")
                },
                "provider": [],
                "category": ["경제", "IT_과학"],
                "sort": {"date": "desc"},
                "return_from": 0,
                "return_size": 10,
                "fields": ["title", "content", "published_at", "provider", "category"]
            }
        }
        
        try:
            response = requests.post(
                self.bigkinds_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            data = response.json()
            
            if data.get("result") == 0:
                docs = data.get("return_object", {}).get("documents", [])
                return [
                    {
                        "title": d.get("title", ""),
                        "content": d.get("content", "")[:500],
                        "date": d.get("published_at", "")[:10],
                        "provider": d.get("provider", ""),
                        "category": d.get("category", [""])[0] if d.get("category") else ""
                    }
                    for d in docs
                ]
        except Exception as e:
            print(f"    ⚠️ 빅카인즈 오류: {e}")
        
        return []
    
    def analyze_with_claude(self, news_list: List[Dict]) -> Dict:
        """Claude로 뉴스 감성 분석"""
        if not self.claude or not news_list:
            return self._basic_analysis(news_list)
        
        news_text = "\n\n".join([
            f"[{i+1}] {n['title']}\n{n['content'][:300]}"
            for i, n in enumerate(news_list[:7])
        ])
        
        prompt = f"""금융 애널리스트로서 다음 한국 경제 뉴스를 분석해주세요.

{news_text}

JSON 형식으로 응답:
{{"overall_sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
"confidence": 0.0~1.0,
"market_impact": "시장 영향 분석 (2-3문장)",
"key_themes": ["테마1", "테마2", "테마3"],
"risk_factors": ["리스크1", "리스크2"],
"opportunities": ["기회1", "기회2"],
"sector_impact": {{"반도체": "POSITIVE/NEGATIVE/NEUTRAL", "2차전지": "...", "바이오": "..."}},
"investment_implications": "투자 시사점 (2-3문장)"}}"""

        try:
            msg = self.claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
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
            print(f"    ⚠️ Claude 분석 오류: {e}")
            return self._basic_analysis(news_list)
    
    def _basic_analysis(self, news_list: List[Dict]) -> Dict:
        """기본 키워드 기반 분석"""
        pos_words = ["상승", "호재", "성장", "개선", "회복", "강세", "매수", "기대", "돌파", "신고가"]
        neg_words = ["하락", "악재", "위기", "우려", "침체", "약세", "매도", "불안", "급락", "손실"]
        
        pos, neg = 0, 0
        for n in news_list:
            text = n["title"] + " " + n["content"]
            pos += sum(1 for w in pos_words if w in text)
            neg += sum(1 for w in neg_words if w in text)
        
        if pos > neg * 1.5:
            sentiment = "POSITIVE"
            conf = min(0.9, 0.5 + (pos - neg) * 0.05)
        elif neg > pos * 1.5:
            sentiment = "NEGATIVE"
            conf = min(0.9, 0.5 + (neg - pos) * 0.05)
        else:
            sentiment = "NEUTRAL"
            conf = 0.5
        
        return {
            "overall_sentiment": sentiment,
            "confidence": round(conf, 2),
            "market_impact": "키워드 기반 기본 분석입니다.",
            "key_themes": [],
            "risk_factors": [],
            "opportunities": [],
            "sector_impact": {},
            "investment_implications": "",
            "source": "basic"
        }
    
    def analyze(self, keywords: List[str] = None) -> Dict:
        """종합 감성 분석"""
        if keywords is None:
            keywords = ["증시", "코스피", "반도체", "금리", "환율"]
        
        print("    → 빅카인즈 뉴스 수집 중...")
        all_news = []
        for kw in keywords:
            news = self.fetch_bigkinds(kw, days=3)
            all_news.extend(news)
        
        # 중복 제거
        seen = set()
        unique = []
        for n in all_news:
            if n["title"] not in seen:
                seen.add(n["title"])
                unique.append(n)
        
        print(f"    → {len(unique)}개 뉴스 수집 완료")
        print("    → Claude 감성 분석 중...")
        
        sentiment = self.analyze_with_claude(unique[:10])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords,
            "news_count": len(unique),
            "news_sample": unique[:5],
            "sentiment": sentiment,
        }


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze()
    print(json.dumps(result, indent=2, ensure_ascii=False))