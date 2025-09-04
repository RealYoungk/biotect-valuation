from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import math

@dataclass
class PipelineAssumptions:
    """파이프라인 가정"""
    name: str
    indication: str
    peak_sales: float  # 피크 매출 (억원)
    peak_sales_year: int  # 피크 매출 연도
    launch_year: int  # 상업화 시작 연도
    patent_expiry: int  # 특허 만료 연도
    success_probability: float  # 성공 확률 (0-1)
    
    # 시장 점유율 가정
    market_share_ramp: Dict[int, float]  # {연도: 점유율}
    
    # 비용 구조
    cogs_rate: float = 0.3  # 매출원가율
    rd_investment: float = 0.0  # 추가 R&D 투자 (억원)
    marketing_rate: float = 0.15  # 마케팅 비율

@dataclass
class CompanyFinancials:
    """회사 재무 정보"""
    current_cash: float  # 현재 현금 (억원)
    annual_opex: float   # 연간 운영비 (억원)
    shares_outstanding: int  # 발행 주식 수
    
    # 할인율 계산 관련
    beta: float = 1.5
    risk_free_rate: float = 0.03
    market_risk_premium: float = 0.06
    
    @property
    def wacc(self) -> float:
        """WACC 계산"""
        cost_of_equity = self.risk_free_rate + self.beta * self.market_risk_premium
        return cost_of_equity  # 단순화 - 부채 고려 X

@dataclass 
class DCFResult:
    """DCF 결과"""
    total_company_value: float  # 총 기업가치 (억원)
    pipeline_value: float       # 파이프라인 가치 (억원)
    cash_value: float          # 현금 가치 (억원)
    equity_value_per_share: float  # 주당 가치 (원)
    
    # 상세 분석
    pipeline_breakdown: Dict[str, float]  # 파이프라인별 가치
    sensitivity_analysis: Dict[str, Dict[str, float]]  # 민감도 분석
    key_assumptions: Dict[str, Any]  # 핵심 가정

class DCFCalculator:
    """DCF 기반 바이오텍 기업가치 계산기"""
    
    def __init__(self, forecast_years: int = 15):
        self.forecast_years = forecast_years
        self.terminal_growth_rate = 0.02  # 영구성장률
    
    def calculate_dcf(
        self,
        pipelines: List[PipelineAssumptions],
        financials: CompanyFinancials,
        scenario: str = "base",  # base, optimistic, pessimistic
        include_sensitivity: bool = True
    ) -> DCFResult:
        """DCF 계산"""
        
        # 1. 각 파이프라인별 가치 계산
        pipeline_values = {}
        total_pipeline_value = 0.0
        
        for pipeline in pipelines:
            pipeline_npv = self._calculate_pipeline_npv(pipeline, financials.wacc)
            risk_adjusted_value = pipeline_npv * pipeline.success_probability
            pipeline_values[pipeline.name] = risk_adjusted_value
            total_pipeline_value += risk_adjusted_value
        
        # 2. 현금 및 기타 자산 가치
        cash_value = financials.current_cash
        
        # 3. 총 기업가치
        total_company_value = total_pipeline_value + cash_value
        
        # 4. 주당 가치
        equity_value_per_share = (total_company_value * 100_000_000) / financials.shares_outstanding  # 억원 -> 원 변환
        
        # 5. 민감도 분석 (순환 참조 방지)
        sensitivity_analysis = {}
        if include_sensitivity:
            sensitivity_analysis = self._perform_sensitivity_analysis(pipelines, financials)
        
        # 6. 핵심 가정 정리
        key_assumptions = self._extract_key_assumptions(pipelines, financials)
        
        return DCFResult(
            total_company_value=round(total_company_value, 1),
            pipeline_value=round(total_pipeline_value, 1),
            cash_value=cash_value,
            equity_value_per_share=round(equity_value_per_share, 0),
            pipeline_breakdown=pipeline_values,
            sensitivity_analysis=sensitivity_analysis,
            key_assumptions=key_assumptions
        )
    
    def _calculate_pipeline_npv(self, pipeline: PipelineAssumptions, discount_rate: float) -> float:
        """개별 파이프라인 NPV 계산"""
        
        cash_flows = {}
        
        # 상업화 이전 비용 (R&D)
        for year in range(2024, pipeline.launch_year):
            cash_flows[year] = -pipeline.rd_investment
        
        # 상업화 이후 현금흐름
        for year in range(pipeline.launch_year, pipeline.patent_expiry + 1):
            revenue = self._calculate_yearly_revenue(pipeline, year)
            
            # 비용 계산
            cogs = revenue * pipeline.cogs_rate
            marketing_cost = revenue * pipeline.marketing_rate
            net_cash_flow = revenue - cogs - marketing_cost
            
            cash_flows[year] = net_cash_flow
        
        # NPV 계산
        npv = 0.0
        base_year = 2024
        
        for year, cash_flow in cash_flows.items():
            years_from_base = year - base_year
            discount_factor = (1 + discount_rate) ** years_from_base
            npv += cash_flow / discount_factor
        
        return npv
    
    def _calculate_yearly_revenue(self, pipeline: PipelineAssumptions, year: int) -> float:
        """연도별 매출 계산"""
        
        if year < pipeline.launch_year or year > pipeline.patent_expiry:
            return 0.0
        
        # 피크 매출까지 선형 성장 가정
        if year <= pipeline.peak_sales_year:
            years_to_peak = pipeline.peak_sales_year - pipeline.launch_year
            if years_to_peak == 0:
                return pipeline.peak_sales
            
            growth_rate = (year - pipeline.launch_year) / years_to_peak
            return pipeline.peak_sales * growth_rate
        else:
            # 피크 이후 감소 (특허 절벽 고려)
            years_after_peak = year - pipeline.peak_sales_year
            decline_rate = 0.05  # 연간 5% 감소
            return pipeline.peak_sales * ((1 - decline_rate) ** years_after_peak)
    
    def _perform_sensitivity_analysis(
        self, 
        pipelines: List[PipelineAssumptions],
        financials: CompanyFinancials
    ) -> Dict[str, Dict[str, float]]:
        """민감도 분석"""
        
        # 순환 참조 방지를 위해 include_sensitivity=False로 base case 계산
        base_case = self.calculate_dcf(pipelines, financials, include_sensitivity=False)
        base_value = base_case.total_company_value
        
        sensitivity_results = {}
        
        # 1. 할인율 민감도
        discount_rate_scenarios = [
            ("할인율 -2%", financials.wacc - 0.02),
            ("할인율 +2%", financials.wacc + 0.02)
        ]
        
        sensitivity_results["할인율"] = {}
        for scenario_name, new_rate in discount_rate_scenarios:
            modified_financials = CompanyFinancials(
                current_cash=financials.current_cash,
                annual_opex=financials.annual_opex,
                shares_outstanding=financials.shares_outstanding,
                beta=new_rate / 0.09 * 1.5,  # 역산으로 베타 조정
                risk_free_rate=financials.risk_free_rate,
                market_risk_premium=financials.market_risk_premium
            )
            
            result = self.calculate_dcf(pipelines, modified_financials, include_sensitivity=False)
            sensitivity_results["할인율"][scenario_name] = result.total_company_value
        
        # 2. 피크 매출 민감도
        sensitivity_results["피크매출"] = {}
        for multiplier, label in [(0.8, "피크매출 -20%"), (1.2, "피크매출 +20%")]:
            modified_pipelines = []
            for pipeline in pipelines:
                modified_pipeline = PipelineAssumptions(
                    name=pipeline.name,
                    indication=pipeline.indication,
                    peak_sales=pipeline.peak_sales * multiplier,
                    peak_sales_year=pipeline.peak_sales_year,
                    launch_year=pipeline.launch_year,
                    patent_expiry=pipeline.patent_expiry,
                    success_probability=pipeline.success_probability,
                    market_share_ramp=pipeline.market_share_ramp,
                    cogs_rate=pipeline.cogs_rate,
                    rd_investment=pipeline.rd_investment,
                    marketing_rate=pipeline.marketing_rate
                )
                modified_pipelines.append(modified_pipeline)
            
            result = self.calculate_dcf(modified_pipelines, financials, include_sensitivity=False)
            sensitivity_results["피크매출"][label] = result.total_company_value
        
        # 3. 성공 확률 민감도
        sensitivity_results["성공확률"] = {}
        for multiplier, label in [(0.8, "성공확률 -20%"), (1.2, "성공확률 +20%")]:
            modified_pipelines = []
            for pipeline in pipelines:
                modified_pipeline = PipelineAssumptions(
                    name=pipeline.name,
                    indication=pipeline.indication,
                    peak_sales=pipeline.peak_sales,
                    peak_sales_year=pipeline.peak_sales_year,
                    launch_year=pipeline.launch_year,
                    patent_expiry=pipeline.patent_expiry,
                    success_probability=min(1.0, pipeline.success_probability * multiplier),
                    market_share_ramp=pipeline.market_share_ramp,
                    cogs_rate=pipeline.cogs_rate,
                    rd_investment=pipeline.rd_investment,
                    marketing_rate=pipeline.marketing_rate
                )
                modified_pipelines.append(modified_pipeline)
            
            result = self.calculate_dcf(modified_pipelines, financials, include_sensitivity=False)
            sensitivity_results["성공확률"][label] = result.total_company_value
        
        return sensitivity_results
    
    def _extract_key_assumptions(
        self,
        pipelines: List[PipelineAssumptions],
        financials: CompanyFinancials
    ) -> Dict[str, Any]:
        """핵심 가정 추출"""
        
        total_peak_sales = sum(p.peak_sales for p in pipelines)
        avg_success_prob = sum(p.success_probability for p in pipelines) / len(pipelines)
        
        return {
            "총_피크매출_추정": f"{total_peak_sales:,.0f}억원",
            "평균_성공확률": f"{avg_success_prob:.1%}",
            "할인율_WACC": f"{financials.wacc:.1%}",
            "파이프라인_개수": len(pipelines),
            "현재_현금": f"{financials.current_cash:,.0f}억원",
            "평가기준일": "2024년",
            "예측기간": f"{self.forecast_years}년"
        }
    
    def create_biotech_dcf_template(
        self, 
        company_name: str,
        main_pipeline_name: str = "주력파이프라인",
        peak_sales_estimate: float = 1000,  # 억원
        current_cash: float = 500,  # 억원
        shares_outstanding: int = 10_000_000
    ) -> tuple[List[PipelineAssumptions], CompanyFinancials]:
        """바이오텍 DCF 템플릿 생성"""
        
        # 기본 파이프라인 가정
        pipeline = PipelineAssumptions(
            name=main_pipeline_name,
            indication="주요적응증",
            peak_sales=peak_sales_estimate,
            peak_sales_year=2030,
            launch_year=2028,
            patent_expiry=2038,
            success_probability=0.35,  # 일반적인 바이오텍 성공확률
            market_share_ramp={
                2028: 0.05,
                2029: 0.15,
                2030: 0.25,
                2031: 0.30
            },
            cogs_rate=0.25,
            rd_investment=50,  # 연간 50억 R&D
            marketing_rate=0.20
        )
        
        # 기본 재무 정보
        financials = CompanyFinancials(
            current_cash=current_cash,
            annual_opex=100,  # 연간 100억 운영비
            shares_outstanding=shares_outstanding,
            beta=1.5,  # 바이오텍 일반적 베타
            risk_free_rate=0.03,
            market_risk_premium=0.06
        )
        
        return [pipeline], financials