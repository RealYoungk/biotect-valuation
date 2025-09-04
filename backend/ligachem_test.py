#!/usr/bin/env python3
"""
리가켐바이오 실제 데이터를 활용한 벨류에이션 검증
"""

import sys
import os

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_ligachem_data():
    """리가켐바이오 실제 데이터 기반 입력 생성"""
    
    from valuation.core_engine import CompanyInput, ValuationInput
    from valuation.calculators.dcf import PipelineAssumptions, CompanyFinancials
    from valuation.indicators.cash_runway import CashRunwayData
    from valuation.indicators.tech_trend import CompanyTechnology, TechCategory
    
    # 리가켐바이오 기본 정보 (2023년 기준 추정)
    company = CompanyInput(
        name="리가켐바이오",
        sector="바이오텍",
        listing_status="상장",
        current_assets=800_000_000_000,   # 약 800억원 (추정)
        current_liabilities=100_000_000_000,  # 약 100억원
        annual_operating_loss=150_000_000_000,  # 약 150억원 영업적자
        current_cash=600_000_000_000,     # 약 600억원 현금
        shares_outstanding=50_000_000,    # 5천만주 (추정)
        pipelines=[
            {
                "name": "LCB11",
                "indication": "고형암(HER2+)",
                "phase": "phase1",
                "moa": "ADC (Anti-HER2)",
                "target": "HER2",
                "differentiators": [
                    "독자적 ADC 플랫폼", 
                    "고효능 페이로드", 
                    "개선된 내약성",
                    "차세대 링커 기술"
                ]
            },
            {
                "name": "LCB14", 
                "indication": "고형암(TROP2+)",
                "phase": "phase1",
                "moa": "ADC (Anti-TROP2)",
                "target": "TROP2",
                "differentiators": [
                    "TROP2 타겟팅", 
                    "플랫폼 기술 적용",
                    "바이어 관심 높음"
                ]
            },
            {
                "name": "LCB71",
                "indication": "혈액암",
                "phase": "preclinical",
                "moa": "ADC",
                "target": "CD19",
                "differentiators": ["혈액암 특화", "CD19 타겟팅"]
            }
        ],
        description="독자적 ADC 플랫폼 기술을 보유한 항체치료제 개발 바이오텍"
    )
    
    # DCF 가정 (리가켐바이오 파이프라인 기반)
    dcf_assumptions = [
        # LCB11 (주력 파이프라인)
        PipelineAssumptions(
            name="LCB11",
            indication="HER2+ 고형암",
            peak_sales=2500,  # 2500억원 (ADC 성공시 블록버스터 가능)
            peak_sales_year=2032,
            launch_year=2030,
            patent_expiry=2040,
            success_probability=0.25,  # Phase1이므로 25%
            market_share_ramp={2030: 0.05, 2031: 0.15, 2032: 0.25, 2033: 0.20},
            cogs_rate=0.30,  # ADC는 제조비용이 높음
            rd_investment=100,  # 연간 100억 추가 R&D
            marketing_rate=0.25  # ADC는 마케팅 비용 높음
        ),
        # LCB14 (두 번째 파이프라인)
        PipelineAssumptions(
            name="LCB14",
            indication="TROP2+ 고형암",
            peak_sales=1800,  # 1800억원
            peak_sales_year=2033,
            launch_year=2031,
            patent_expiry=2041,
            success_probability=0.20,  # Phase1, 후발주자
            market_share_ramp={2031: 0.03, 2032: 0.10, 2033: 0.18, 2034: 0.15},
            cogs_rate=0.30,
            rd_investment=80,
            marketing_rate=0.25
        )
    ]
    
    # 재무 정보
    financials = CompanyFinancials(
        current_cash=600,  # 600억원
        annual_opex=200,   # 연간 200억원 운영비 (R&D 포함)
        shares_outstanding=50_000_000,  # 5천만주
        beta=2.0,  # 바이오텍 높은 베타
        risk_free_rate=0.035,  # 3.5% (한국 국고채)
        market_risk_premium=0.065  # 6.5% 시장 위험 프리미엄
    )
    
    # 현금가용년수 데이터
    cash_runway_data = CashRunwayData(
        current_assets=800_000_000_000,
        current_liabilities=100_000_000_000,
        annual_operating_loss=150_000_000_000,
        cash_and_equivalents=600_000_000_000
    )
    
    # 기술 트렌드 데이터
    company_tech = CompanyTechnology(
        platform_technology="ADC (Antibody-Drug Conjugate)",
        therapeutic_areas=[TechCategory.ONCOLOGY],
        pipeline_stages={
            "LCB11": "Phase 1",
            "LCB14": "Phase 1", 
            "LCB71": "Preclinical"
        },
        differentiation_factors=[
            "독자적 ADC 플랫폼",
            "차세대 링커 기술",
            "다양한 타겟 적용 가능",
            "제조 노하우"
        ]
    )
    
    return ValuationInput(
        company=company,
        dcf_assumptions=dcf_assumptions,
        financials=financials,
        cash_runway_data=cash_runway_data,
        company_tech=company_tech
    )

def analyze_ligachem():
    """리가켐바이오 분석 수행"""
    
    from valuation.core_engine import CoreValuationEngine
    
    print("🧬 리가켐바이오 벨류에이션 분석")
    print("=" * 60)
    
    # 데이터 준비
    input_data = create_ligachem_data()
    
    # 벨류에이션 엔진
    engine = CoreValuationEngine()
    result = engine.perform_full_valuation(input_data)
    
    # 결과 출력
    print(f"📊 {result.company_name} 벨류에이션 결과\n")
    
    print("💰 핵심 재무 지표:")
    print(f"  • 목표 기업가치: {result.target_enterprise_value:,.1f}억원")
    print(f"  • 주당 목표가: {result.target_price_per_share:,.0f}원")
    print(f"  • 투자 의견: {result.investment_rating}")
    print(f"  • 분석 신뢰도: {result.confidence_score:.2f}/1.0")
    
    print("\n🔬 4대 평가지표 결과:")
    for indicator, data in result.indicator_scores.items():
        if isinstance(data, dict):
            if "cash_runway_years" in data:
                print(f"  • {indicator}: {data['cash_runway_years']}년 ({data['status']})")
                if len(data.get('recommendations', [])) > 0:
                    print(f"    추천: {data['recommendations'][0]}")
            elif hasattr(data, 'overall_score'):
                print(f"  • {indicator}: {data.overall_score}/10")
            elif 'overall_score' in data:
                print(f"  • {indicator}: {data['overall_score']}/10")
            elif 'note' in data:
                print(f"  • {indicator}: 기본값 적용 ({data['note']})")
    
    print(f"\n💡 DCF 상세 분석:")
    if result.dcf_result:
        dcf = result.dcf_result
        print(f"  • 파이프라인 가치: {dcf.pipeline_value:,.1f}억원")
        print(f"  • 현금 가치: {dcf.cash_value:,.1f}억원")
        print(f"  • WACC: {input_data.financials.wacc:.1%}")
        
        print(f"\n  📈 파이프라인별 기여도:")
        for pipeline, value in dcf.pipeline_breakdown.items():
            contribution = (value / dcf.total_company_value) * 100 if dcf.total_company_value > 0 else 0
            print(f"    - {pipeline}: {value:,.1f}억원 ({contribution:.1f}%)")
        
        print(f"\n  🔑 핵심 가정:")
        for key, value in dcf.key_assumptions.items():
            print(f"    - {key}: {value}")
    
    print(f"\n🎯 투자 포인트:")
    for point in result.key_investment_points or []:
        print(f"  • {point}")
    
    print(f"\n⚠️ 주요 리스크:")
    for risk in result.key_risks or []:
        print(f"  • {risk}")
    
    # ADC 특화 분석
    print(f"\n🧪 ADC 플랫폼 특화 분석:")
    analyze_adc_specifics(input_data, result)
    
    return result

def analyze_adc_specifics(input_data, result):
    """ADC 특화 분석"""
    
    print(f"  • ADC 시장 트렌드: 연평균 15-20% 성장")
    print(f"  • 빅파마 관심도: 매우 높음 (최근 대형 M&A 빈발)")
    print(f"  • 기술 차별화: 독자 플랫폼 보유로 경쟁력 확보")
    print(f"  • 파이프라인 다양성: HER2, TROP2, CD19 등 다중 타겟")
    
    # 간단한 벤치마킹
    adc_comparables = {
        "Daiichi Sankyo": "엔허투 성공으로 ADC 선두",
        "AbbVie/ImmunoGen": "TROP2 ADC 경쟁",
        "시애틀제네틱스": "ADC 전문기업"
    }
    
    print(f"\n  📊 경쟁사 벤치마킹:")
    for company, note in adc_comparables.items():
        print(f"    - {company}: {note}")
    
    # 리스크 요소
    adc_risks = [
        "ADC 제조의 복잡성과 높은 비용",
        "안전성 이슈 (독성 관리의 중요성)",
        "경쟁 심화 (다수 기업의 ADC 개발)",
        "규제 허들 (복잡한 승인 과정)"
    ]
    
    print(f"\n  ⚡ ADC 특화 리스크:")
    for risk in adc_risks:
        print(f"    - {risk}")

def main():
    try:
        result = analyze_ligachem()
        
        print("\n" + "=" * 60)
        print("✅ 리가켐바이오 분석 완료")
        print(f"💎 최종 의견: 목표가 {result.target_price_per_share:,.0f}원, {result.investment_rating}")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()