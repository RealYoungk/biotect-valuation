#!/usr/bin/env python3
"""
간단한 벨류에이션 로직 테스트
"""

import sys
import os

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_cash_runway():
    """현금가용년수 계산 테스트"""
    print("1️⃣ 현금가용년수 계산 테스트")
    
    from valuation.indicators.cash_runway import CashRunwayCalculator, CashRunwayData
    
    calculator = CashRunwayCalculator()
    
    # 테스트 데이터: 유동자산 3000억, 유동부채 500억, 연간적자 1000억
    data = CashRunwayData(
        current_assets=300_000_000_000,
        current_liabilities=50_000_000_000,
        annual_operating_loss=100_000_000_000
    )
    
    result = calculator.calculate(data)
    
    print(f"  ✅ 현금가용년수: {result.cash_runway_years}년")
    print(f"  ✅ 순운전자본: {result.net_working_capital:,.0f}원") 
    print(f"  ✅ 상태: {result.status}")
    print(f"  ✅ 월별 소진율: {result.monthly_burn_rate:,.0f}원")
    print()
    
    return result

def test_dcf_calculation():
    """DCF 계산 테스트"""
    print("2️⃣ DCF 계산 테스트")
    
    from valuation.calculators.dcf import DCFCalculator, PipelineAssumptions, CompanyFinancials
    
    calculator = DCFCalculator()
    
    # 파이프라인 가정
    pipeline = PipelineAssumptions(
        name="주력파이프라인",
        indication="항암제", 
        peak_sales=1000,  # 1000억원
        peak_sales_year=2030,
        launch_year=2028,
        patent_expiry=2038,
        success_probability=0.35,
        market_share_ramp={2028: 0.1, 2029: 0.2, 2030: 0.3},
        cogs_rate=0.25,
        rd_investment=50,
        marketing_rate=0.15
    )
    
    # 재무정보
    financials = CompanyFinancials(
        current_cash=200,
        annual_opex=100,
        shares_outstanding=10_000_000,
        beta=1.5,
        risk_free_rate=0.03,
        market_risk_premium=0.06
    )
    
    result = calculator.calculate_dcf([pipeline], financials)
    
    print(f"  ✅ 총 기업가치: {result.total_company_value:,.1f}억원")
    print(f"  ✅ 파이프라인 가치: {result.pipeline_value:,.1f}억원")
    print(f"  ✅ 현금 가치: {result.cash_value:,.1f}억원")
    print(f"  ✅ 주당 가치: {result.equity_value_per_share:,.0f}원")
    print(f"  ✅ WACC: {financials.wacc:.1%}")
    print()
    
    return result

def test_valuation_tree():
    """벨류에이션 트리 테스트"""
    print("3️⃣ 벨류에이션 트리 테스트")
    
    from valuation.tree_model import ValuationTree, ValuationNode, NodeType
    
    tree = ValuationTree("테스트바이오")
    
    # 파이프라인 노드
    pipeline_node = ValuationNode(
        name="파이프라인A",
        node_type=NodeType.FORMULA,
        formula="peak_sales * success_probability",
        assumptions={"peak_sales": 1000, "success_probability": 0.35}
    )
    tree.add_node(tree.root.id, pipeline_node)
    
    # 현금 노드
    cash_node = ValuationNode(
        name="현금자산",
        node_type=NodeType.VALUE,
        value=200
    )
    tree.add_node(tree.root.id, cash_node)
    
    # 계산
    total_value = tree.calculate_total_value()
    structure = tree.get_tree_structure()
    
    print(f"  ✅ 총 계산 값: {total_value:,.1f}")
    print(f"  ✅ 노드 개수: {structure['metadata']['total_nodes']}")
    print(f"  ✅ 자식 노드 개수: {len(structure['tree']['children'])}")
    print()
    
    return tree

def test_full_valuation():
    """전체 벨류에이션 테스트"""
    print("4️⃣ 전체 벨류에이션 엔진 테스트")
    
    from valuation.core_engine import CoreValuationEngine, create_simple_valuation_example
    
    engine = CoreValuationEngine()
    input_data = create_simple_valuation_example()
    
    result = engine.perform_full_valuation(input_data)
    
    print(f"  ✅ 회사명: {result.company_name}")
    print(f"  ✅ 목표 기업가치: {result.target_enterprise_value:,.1f}억원")
    print(f"  ✅ 목표 주가: {result.target_price_per_share:,.0f}원")
    print(f"  ✅ 투자의견: {result.investment_rating}")
    print(f"  ✅ 신뢰도 점수: {result.confidence_score:.2f}")
    
    print("\n  📊 4대 지표 결과:")
    for indicator, score in result.indicator_scores.items():
        if isinstance(score, dict):
            if "cash_runway_years" in score:
                print(f"    • {indicator}: {score['cash_runway_years']}년 ({score['status']})")
            elif "overall_score" in score:
                print(f"    • {indicator}: {score['overall_score']}/10")
            elif "overall_competitiveness" in score:
                print(f"    • {indicator}: {score['overall_competitiveness']}/10")
            elif "overall_trend_score" in score:
                print(f"    • {indicator}: {score['overall_trend_score']}/10")
            elif "note" in score:
                print(f"    • {indicator}: {score.get('overall_score', 'N/A')} (기본값)")
    print()
    
    return result

def main():
    print("🧪 바이오텍 벨류에이션 코어 로직 테스트\n")
    print("=" * 60)
    
    try:
        # 각 테스트 실행
        cash_result = test_cash_runway()
        dcf_result = test_dcf_calculation()
        tree_result = test_valuation_tree()
        full_result = test_full_valuation()
        
        print("=" * 60)
        print("✅ 모든 테스트 성공!")
        print("\n🎯 핵심 결과 요약:")
        print(f"  • 현금가용년수: {cash_result.cash_runway_years}년 ({cash_result.status})")
        print(f"  • DCF 기업가치: {dcf_result.total_company_value:,.1f}억원")
        print(f"  • 주당 목표가: {full_result.target_price_per_share:,.0f}원")
        print(f"  • 투자 의견: {full_result.investment_rating}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()