import pytest
import sys
import os

# 테스트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valuation.core_engine import CoreValuationEngine, create_simple_valuation_example
from valuation.calculators.dcf import DCFCalculator, PipelineAssumptions, CompanyFinancials
from valuation.indicators.cash_runway import CashRunwayCalculator, CashRunwayData
from valuation.tree_model import ValuationTree, ValuationNode, NodeType

class TestValuationCore:
    """벨류에이션 코어 로직 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.engine = CoreValuationEngine()
    
    def test_cash_runway_calculation(self):
        """현금가용년수 계산 테스트"""
        calculator = CashRunwayCalculator()
        
        # 테스트 데이터
        data = CashRunwayData(
            current_assets=300_000_000_000,  # 3000억원
            current_liabilities=50_000_000_000,   # 500억원  
            annual_operating_loss=100_000_000_000  # 1000억원 적자
        )
        
        result = calculator.calculate(data)
        
        # 검증
        assert result.cash_runway_years > 0
        assert result.net_working_capital == 250_000_000_000  # 2500억원
        assert result.cash_runway_years == 2.5  # (3000-500)/1000 = 2.5년
        assert result.status in ["안전", "주의", "위험"]
        
        print(f"✅ 현금가용년수: {result.cash_runway_years}년")
        print(f"✅ 상태: {result.status}")
        print(f"✅ 순운전자본: {result.net_working_capital:,.0f}원")
    
    def test_dcf_calculation(self):
        """DCF 계산 테스트"""
        calculator = DCFCalculator()
        
        # 파이프라인 가정
        pipeline = PipelineAssumptions(
            name="테스트파이프라인",
            indication="항암제",
            peak_sales=1000,  # 1000억원 피크매출
            peak_sales_year=2030,
            launch_year=2028,
            patent_expiry=2038,
            success_probability=0.4,  # 40% 성공확률
            market_share_ramp={2028: 0.1, 2029: 0.2, 2030: 0.3},
            cogs_rate=0.25,
            rd_investment=50,  # 50억원 R&D
            marketing_rate=0.15
        )
        
        # 회사 재무정보
        financials = CompanyFinancials(
            current_cash=200,  # 200억원 현금
            annual_opex=100,   # 100억원 연간 운영비
            shares_outstanding=10_000_000,  # 1천만주
            beta=1.5,
            risk_free_rate=0.03,
            market_risk_premium=0.06
        )
        
        result = calculator.calculate_dcf([pipeline], financials)
        
        # 검증
        assert result.total_company_value > 0
        assert result.pipeline_value >= 0
        assert result.cash_value == 200
        assert result.equity_value_per_share > 0
        assert len(result.pipeline_breakdown) == 1
        
        print(f"✅ 총 기업가치: {result.total_company_value:,.1f}억원")
        print(f"✅ 파이프라인 가치: {result.pipeline_value:,.1f}억원") 
        print(f"✅ 주당 가치: {result.equity_value_per_share:,.0f}원")
        print(f"✅ WACC: {financials.wacc:.1%}")
    
    def test_valuation_tree(self):
        """벨류에이션 트리 구조 테스트"""
        tree = ValuationTree("테스트바이오")
        
        # 파이프라인 노드 추가
        pipeline_node = ValuationNode(
            name="주력파이프라인",
            node_type=NodeType.FORMULA,
            formula="peak_sales * success_probability",
            assumptions={"peak_sales": 1000, "success_probability": 0.4}
        )
        tree.add_node(tree.root.id, pipeline_node)
        
        # 현금 노드 추가
        cash_node = ValuationNode(
            name="현금자산", 
            node_type=NodeType.VALUE,
            value=200
        )
        tree.add_node(tree.root.id, cash_node)
        
        # 계산 및 검증
        total_value = tree.calculate_total_value()
        tree_structure = tree.get_tree_structure()
        
        assert total_value > 0
        assert tree_structure["total_value"] == total_value
        assert len(tree_structure["tree"]["children"]) == 2
        
        print(f"✅ 트리 계산 결과: {total_value:,.0f}")
        print(f"✅ 노드 개수: {tree_structure['metadata']['total_nodes']}")
    
    def test_full_valuation_engine(self):
        """전체 벨류에이션 엔진 테스트"""
        # 샘플 데이터 생성
        input_data = create_simple_valuation_example()
        
        # 벨류에이션 실행
        result = self.engine.perform_full_valuation(input_data)
        
        # 검증
        assert result.company_name == "예시바이오텍"
        assert result.target_enterprise_value > 0
        assert result.target_price_per_share > 0
        assert result.investment_rating in ["Buy", "Hold", "Sell"]
        assert result.confidence_score >= 0 and result.confidence_score <= 1
        assert len(result.indicator_scores) == 4  # 4대 지표
        
        print(f"✅ 회사명: {result.company_name}")
        print(f"✅ 목표 기업가치: {result.target_enterprise_value:,.1f}억원")
        print(f"✅ 목표 주가: {result.target_price_per_share:,.0f}원")
        print(f"✅ 투자의견: {result.investment_rating}")
        print(f"✅ 신뢰도: {result.confidence_score:.2f}")
        
        # 4대 지표 결과 출력
        print("\n📊 4대 지표 분석 결과:")
        for indicator, score in result.indicator_scores.items():
            if isinstance(score, dict):
                if "cash_runway_years" in score:
                    print(f"  • {indicator}: {score['cash_runway_years']}년 ({score['status']})")
                elif "overall_score" in score:
                    print(f"  • {indicator}: {score['overall_score']}/10")
                elif "overall_competitiveness" in score:
                    print(f"  • {indicator}: {score['overall_competitiveness']}/10")
                elif "overall_trend_score" in score:
                    print(f"  • {indicator}: {score['overall_trend_score']}/10")
                else:
                    print(f"  • {indicator}: {score}")
    
    def test_sensitivity_analysis(self):
        """민감도 분석 테스트"""
        calculator = DCFCalculator()
        pipelines, financials = calculator.create_biotech_dcf_template(
            "민감도테스트", 
            peak_sales_estimate=1000,
            current_cash=300
        )
        
        result = calculator.calculate_dcf(pipelines, financials)
        
        # 민감도 분석 결과 검증
        assert "할인율" in result.sensitivity_analysis
        assert "피크매출" in result.sensitivity_analysis
        assert "성공확률" in result.sensitivity_analysis
        
        print("\n📈 민감도 분석 결과:")
        for factor, scenarios in result.sensitivity_analysis.items():
            print(f"  {factor}:")
            for scenario, value in scenarios.items():
                print(f"    - {scenario}: {value:,.1f}억원")

def run_manual_test():
    """수동 테스트 실행"""
    print("🧪 벨류에이션 코어 로직 테스트 시작\n")
    
    test_instance = TestValuationCore()
    test_instance.setup_method()
    
    try:
        print("1️⃣ 현금가용년수 계산 테스트")
        test_instance.test_cash_runway_calculation()
        print()
        
        print("2️⃣ DCF 계산 테스트") 
        test_instance.test_dcf_calculation()
        print()
        
        print("3️⃣ 벨류에이션 트리 테스트")
        test_instance.test_valuation_tree()
        print()
        
        print("4️⃣ 전체 엔진 테스트")
        test_instance.test_full_valuation_engine()
        print()
        
        print("5️⃣ 민감도 분석 테스트")
        test_instance.test_sensitivity_analysis()
        
        print("\n✅ 모든 테스트 통과!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_manual_test()