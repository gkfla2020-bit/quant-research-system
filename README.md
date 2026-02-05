# Quant Auto Research System

AI 기반 투자 분석 자동화 시스템 - 매크로/업종/리스크 분석 및 리포트 자동 생성

## Overview

한국/미국 시장의 매크로 지표, 업종별 동향, 리스크 요인을 자동으로 분석하고 WSJ 스타일의 투자 리포트를 생성합니다.

## Features

### 📊 Multi-Layer Analysis
- **Macro Layer**: 금리, 환율, VIX/MOVE 변동성 분석
- **Industry Layer**: Claude AI 기반 업종별 투자 매력도 분석
- **Risk Layer**: 포트폴리오 리스크 지표 계산
- **Sentiment Layer**: 뉴스 감성 분석 (BigKinds API)

### 📈 QuantLib Integration
- Vasicek 금리 모델 파라미터 추정
- Black-Scholes 옵션 가격 계산
- 채권 듀레이션/컨벡시티 분석

### 📝 Auto Report Generation
- WSJ 스타일 HTML 리포트
- 인터랙티브 Plotly 차트
- 주간/월간 정기 리포트

## Project Structure

```
├── main.py                 # 메인 실행
├── config.py               # 설정 (API keys, 파라미터)
├── macro_layer.py          # 매크로 분석
├── industry_layer.py       # 업종 분석 (Claude AI)
├── risk_layer.py           # 리스크 분석
├── sentiment_layer.py      # 감성 분석
├── quantlib_analyzer.py    # QuantLib 금융 분석
├── report_generator.py     # 리포트 생성
├── reports/                # 생성된 리포트
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Environment Variables

`.env` 파일 생성:
```
ANTHROPIC_API_KEY=your_api_key_here
BIGKINDS_API_KEY=your_api_key_here  # Optional
```

## Usage

```bash
python main.py
```

리포트가 `reports/` 폴더에 생성됩니다.

## Tech Stack

- **Python 3.10+**
- **QuantLib** - 금융 모델링
- **yfinance** - 시장 데이터
- **Claude Sonnet 4** - AI 분석
- **Plotly** - 인터랙티브 차트
- **Jinja2** - 리포트 템플릿

## Sample Output

- `investment_report_YYYYMMDD.html` - 일간 투자 리포트
- `weekly_report_YYYYMMDD.html` - 주간 종합 리포트

## Author

Ha Rim Jung - Sogang University
