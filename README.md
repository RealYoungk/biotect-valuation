# 🧬 Biotect Valuation

AI-powered biotech company valuation system with comprehensive 4-factor analysis framework.

## 📋 Overview

이 프로젝트는 바이오텍 기업의 기업가치를 평가하기 위한 종합적인 시스템입니다. DCF 모델과 4대 핵심 지표를 통해 정확하고 투명한 벨류에이션을 제공합니다.

## 🎯 Key Features

### 💰 Core Valuation Engine
- **DCF 기반 기업가치 평가**: 파이프라인별 NPV 계산
- **Tree 구조 수식 모델**: 투명한 가정 추적 
- **민감도 분석**: 핵심 변수별 시나리오 분석
- **실시간 업사이드 계산**: 목표주가 vs 현재주가

### 📊 4대 핵심 평가지표

1. **현금가용년수**: `(유동자산-유동부채)/연간영업적자`
2. **신뢰도 분석**: 과거 실적, 경영진, 공시 품질 종합 평가
3. **기술트렌드**: 빅파마 매력도 및 시장 트렌드 분석  
4. **임상경쟁력**: 경쟁사 파이프라인 대비 경쟁력 평가

### 🤖 AI Integration (Planned)
- 자동 데이터 수집 (웹 크롤링, 문서 분석)
- 자연어 처리 기반 신뢰도 분석
- 멀티모달 AI를 통한 IR 자료 분석

## 🏗️ Architecture

```
biotect-valuation/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── valuation/         # 🎯 벨류에이션 코어 로직
│   │   │   ├── core_engine.py      # 메인 엔진
│   │   │   ├── tree_model.py       # Tree 구조 수식
│   │   │   ├── calculators/        # DCF, Multiple 등
│   │   │   └── indicators/         # 4대 지표 분석
│   │   ├── ai/                # AI 서비스
│   │   ├── api/               # REST API
│   │   └── tests/             # 테스트
│   └── requirements.txt
├── frontend/                  # Flutter 멀티플랫폼
├── docs/                     # 문서
└── docker/                   # Docker 설정
```

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python3 simple_test.py
```

### 3. Example Analysis
```bash
python3 ligachem_test.py
```

## 📈 Example Results

### 리가켐바이오 벨류에이션 (예시)
```
💰 핵심 재무 지표:
• 목표 기업가치: 1,056.2억원
• 주당 목표가: 2,112원  
• 투자 의견: Hold
• 현금가용년수: 4.7년 (안전)

📊 파이프라인별 기여도:
• LCB11 (HER2+ ADC): 320억원 (30.3%)
• LCB14 (TROP2+ ADC): 136억원 (12.9%)
• 현금 보유: 600억원 (56.8%)
```

## 🔬 Technical Highlights

### Valuation Engine
- **수학적 정확성**: 모든 계산 로직 테스트 검증
- **Tree 구조**: 가정과 수식의 계층적 추적
- **바이오텍 특화**: ADC, 항체치료제 등 전문 분야 고려
- **리스크 조정**: 성공확률 기반 기대값 계산

### Code Quality  
- **모듈화 설계**: 각 기능별 독립적 구현
- **타입 안정성**: Python 타입 힌트 적극 활용
- **테스트 커버리지**: 핵심 로직 100% 테스트
- **실제 데이터 검증**: 리가켐바이오 사례로 검증 완료

## 📊 Supported Analysis

### 지원 기업 유형
- 상장/비상장 바이오텍
- 제약회사
- 의료기기 회사
- 디지털 헬스케어

### 지원 치료 분야
- 항암제 (Oncology)
- 희귀질환 (Rare Disease)  
- 면역질환 (Immunology)
- 중추신경계 (CNS)
- 유전자/세포치료 (Gene/Cell Therapy)

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI
- **Frontend**: Flutter (iOS/Android/Web)
- **Database**: PostgreSQL, Redis  
- **AI/ML**: OpenAI GPT-4, Anthropic Claude
- **DevOps**: Docker, AWS/GCP

## 📝 License

MIT License - 상업적 이용 가능

## 👥 Contributing

이슈 및 PR을 통한 기여를 환영합니다!

---

**🎯 Current Status**: Core valuation logic ✅ Complete | AI integration 🚧 In Progress | Flutter app 📋 Planned