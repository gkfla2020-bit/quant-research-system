"""
설정 파일 - API 키 로드 및 전역 설정
"""
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# API Keys
BIGKINDS_KEY = os.getenv("BIGKINDS_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# FRED API (무료, 가입 필요: https://fred.stlouisfed.org/docs/api/api_key.html)
FRED_API_KEY = os.getenv("FRED_API_KEY", "")  # 나중에 추가

# 매크로 지표 설정
MACRO_INDICATORS = {
    "interest_rate": "DFF",      # Federal Funds Rate
    "cpi": "CPIAUCSL",           # Consumer Price Index
    "unemployment": "UNRATE",    # Unemployment Rate
    "gdp": "GDP",                # Gross Domestic Product
    "treasury_10y": "DGS10",     # 10-Year Treasury Rate
    "treasury_2y": "DGS2",       # 2-Year Treasury Rate
}

# 투자 판단 임계값
THRESHOLDS = {
    "move_high": 120,    # MOVE > 120: 공포 상태
    "move_low": 80,      # MOVE < 80: 안정 상태
    "vix_high": 25,      # VIX > 25: 주식시장 공포
    "vix_low": 15,       # VIX < 15: 주식시장 안정
    "dxy_strong": 105,   # DXY > 105: 달러 강세
    "dxy_weak": 100,     # DXY < 100: 달러 약세
}
