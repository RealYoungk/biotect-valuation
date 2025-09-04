from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .tree_model import ValuationTree, ValuationNode, NodeType
from .calculators.dcf import DCFCalculator, PipelineAssumptions, CompanyFinancials
from .indicators.cash_runway import CashRunwayCalculator, CashRunwayData
from .indicators.credibility import CredibilityAnalyzer, TrackRecordData, ManagementData, DisclosureData
from .indicators.tech_trend import TechTrendAnalyzer, CompanyTechnology, MarketTrendData
from .indicators.clinical_competitiveness import ClinicalCompetitivenessAnalyzer, PipelineAsset, CompetitorAsset

@dataclass
class CompanyInput:
    """회사 기본 정보"""
    name: str
    sector: str = "바이오텍"
    listing_status: str = "상장"  # 상장, 비상장
    
    # 재무 정보
    current_assets: float = 0
    current_liabilities: float = 0  
    annual_operating_loss: float = 0
    current_cash: float = 0
    shares_outstanding: int = 10_000_000
    
    # 파이프라인 정보
    pipelines: List[Dict[str, Any]] = None
    
    # 기타
    description: str = ""

@dataclass
class ValuationInput:
    """벨류에이션 입력 데이터"""
    company: CompanyInput
    
    # DCF 관련
    dcf_assumptions: Optional[List[PipelineAssumptions]] = None
    financials: Optional[CompanyFinancials] = None
    
    # 4대 지표 관련
    cash_runway_data: Optional[CashRunwayData] = None
    track_record: Optional[TrackRecordData] = None
    management: Optional[ManagementData] = None
    disclosure: Optional[DisclosureData] = None
    company_tech: Optional[CompanyTechnology] = None
    market_data: Optional[MarketTrendData] = None
    competitor_data: Optional[List[CompetitorAsset]] = None

@dataclass
class ValuationOutput:
    """벨류에이션 결과"""
    company_name: str
    valuation_date: str
    
    # 핵심 결과
    target_enterprise_value: float  # 목표 기업가치 (억원)
    target_price_per_share: float   # 목표 주가 (원)
    current_price: Optional[float] = None  # 현재 주가 (원)
    upside_potential: Optional[float] = None  # 상승여력 (%)
    
    # 상세 분석
    dcf_result: Any = None
    indicator_scores: Dict[str, Any] = None
    
    # 벨류에이션 트리
    valuation_tree: Dict[str, Any] = None
    
    # 투자 의견
    investment_rating: str = ""  # Buy, Hold, Sell
    key_investment_points: List[str] = None
    key_risks: List[str] = None
    
    # 메타데이터
    confidence_score: float = 0.0
    methodology_used: List[str] = None

class CoreValuationEngine:
    """코어 벨류에이션 엔진"""
    
    def __init__(self):
        self.dcf_calculator = DCFCalculator()
        self.cash_runway_calculator = CashRunwayCalculator()
        self.credibility_analyzer = CredibilityAnalyzer()
        self.tech_trend_analyzer = TechTrendAnalyzer()
        self.clinical_analyzer = ClinicalCompetitivenessAnalyzer()
    
    def perform_full_valuation(self, input_data: ValuationInput) -> ValuationOutput:
        """전체 벨류에이션 수행"""
        
        company = input_data.company
        
        # 1. 4대 평가지표 분석
        indicator_scores = self._analyze_four_indicators(input_data)
        
        # 2. DCF 벨류에이션
        dcf_result = self._perform_dcf_valuation(input_data)
        
        # 3. 벨류에이션 트리 구성
        valuation_tree = self._build_valuation_tree(company, dcf_result, indicator_scores)
        
        # 4. 목표주가 계산
        target_price = dcf_result.equity_value_per_share if dcf_result else 0
        
        # 5. 투자 의견 생성
        investment_rating, key_points, key_risks = self._generate_investment_opinion(
            indicator_scores, dcf_result, target_price
        )
        
        # 6. 신뢰도 점수 계산
        confidence_score = self._calculate_overall_confidence(indicator_scores, dcf_result)
        
        return ValuationOutput(
            company_name=company.name,
            valuation_date="2024-09-04",  # 실제로는 현재 날짜
            target_enterprise_value=dcf_result.total_company_value if dcf_result else 0,
            target_price_per_share=target_price,
            upside_potential=None,  # 현재주가 필요
            dcf_result=dcf_result,
            indicator_scores=indicator_scores,
            valuation_tree=valuation_tree,
            investment_rating=investment_rating,
            key_investment_points=key_points,
            key_risks=key_risks,
            confidence_score=confidence_score,
            methodology_used=["DCF", "4대지표분석", "Tree구조"]
        )
    
    def _analyze_four_indicators(self, input_data: ValuationInput) -> Dict[str, Any]:
        """4대 평가지표 분석"""
        results = {}
        
        # 1. 현금가용년수
        if input_data.cash_runway_data:
            results["현금가용년수"] = self.cash_runway_calculator.calculate(input_data.cash_runway_data)
        else:
            # 기본 데이터로 계산
            cash_data = CashRunwayData(
                current_assets=input_data.company.current_assets,
                current_liabilities=input_data.company.current_liabilities,
                annual_operating_loss=input_data.company.annual_operating_loss
            )
            results["현금가용년수"] = self.cash_runway_calculator.calculate(cash_data)
        
        # 2. 신뢰도 분석
        if all([input_data.track_record, input_data.management, input_data.disclosure]):
            results["신뢰도"] = self.credibility_analyzer.analyze_credibility(
                input_data.track_record,
                input_data.management, 
                input_data.disclosure
            )
        else:
            results["신뢰도"] = {"overall_score": 5.0, "note": "데이터 부족으로 기본 점수 적용"}
        
        # 3. 기술트렌드
        if input_data.company_tech and input_data.market_data:
            results["기술트렌드"] = self.tech_trend_analyzer.analyze_tech_trend(
                input_data.company_tech,
                input_data.market_data
            )
        else:
            results["기술트렌드"] = {"overall_trend_score": 5.0, "note": "데이터 부족으로 기본 점수 적용"}
        
        # 4. 임상경쟁력
        if input_data.company.pipelines and input_data.competitor_data:
            # 회사 파이프라인을 PipelineAsset으로 변환
            company_pipeline = self._convert_to_pipeline_assets(input_data.company.pipelines)
            results["임상경쟁력"] = self.clinical_analyzer.analyze_clinical_competitiveness(
                company_pipeline,
                input_data.competitor_data
            )
        else:
            results["임상경쟁력"] = {"overall_competitiveness": 5.0, "note": "데이터 부족으로 기본 점수 적용"}
        
        return results
    
    def _perform_dcf_valuation(self, input_data: ValuationInput) -> Any:
        """DCF 벨류에이션 수행"""
        
        if input_data.dcf_assumptions and input_data.financials:
            return self.dcf_calculator.calculate_dcf(
                input_data.dcf_assumptions,
                input_data.financials
            )
        else:
            # 기본 템플릿 사용
            pipelines, financials = self.dcf_calculator.create_biotech_dcf_template(
                input_data.company.name,
                current_cash=input_data.company.current_cash,
                shares_outstanding=input_data.company.shares_outstanding
            )
            return self.dcf_calculator.calculate_dcf(pipelines, financials)
    
    def _build_valuation_tree(self, company: CompanyInput, dcf_result: Any, indicators: Dict) -> Dict:
        """벨류에이션 트리 구성"""
        
        tree = ValuationTree(company.name)
        
        # DCF 결과를 트리에 반영
        if dcf_result:
            # 파이프라인 가치 노드
            pipeline_node = ValuationNode(
                name="파이프라인 가치",
                node_type=NodeType.VALUE,
                value=dcf_result.pipeline_value,
                description=f"DCF 기반 파이프라인 가치"
            )
            tree.add_node(tree.root.id, pipeline_node)
            
            # 현금 가치 노드
            cash_node = ValuationNode(
                name="현금 및 기타 자산",
                node_type=NodeType.VALUE,
                value=dcf_result.cash_value,
                description="보유 현금 및 기타 자산"
            )
            tree.add_node(tree.root.id, cash_node)
        
        # 4대 지표 신뢰도 조정 (향후 구현)
        
        return tree.get_tree_structure()
    
    def _convert_to_pipeline_assets(self, pipeline_data: List[Dict]) -> List[PipelineAsset]:
        """파이프라인 데이터를 PipelineAsset으로 변환"""
        from .indicators.clinical_competitiveness import PipelineAsset, ClinicalPhase
        
        assets = []
        for data in pipeline_data:
            # 간단한 변환 로직
            phase_mapping = {
                "preclinical": ClinicalPhase.PRECLINICAL,
                "phase1": ClinicalPhase.PHASE_1,
                "phase2": ClinicalPhase.PHASE_2,
                "phase3": ClinicalPhase.PHASE_3,
            }
            
            phase = phase_mapping.get(data.get("phase", "preclinical").lower(), ClinicalPhase.PRECLINICAL)
            
            asset = PipelineAsset(
                name=data.get("name", "Unknown"),
                indication=data.get("indication", ""),
                current_phase=phase,
                mechanism_of_action=data.get("moa", ""),
                target=data.get("target", ""),
                expected_timeline=data.get("timeline", {}),
                clinical_data=data.get("clinical_data", {}),
                differentiation_factors=data.get("differentiators", [])
            )
            assets.append(asset)
        
        return assets
    
    def _generate_investment_opinion(
        self, 
        indicators: Dict, 
        dcf_result: Any, 
        target_price: float
    ) -> tuple[str, List[str], List[str]]:
        """투자 의견 생성"""
        
        # 간단한 점수 기반 로직
        total_score = 0
        max_score = 0
        
        # 4대 지표 점수 합산
        for indicator, result in indicators.items():
            if isinstance(result, dict):
                if "overall_score" in result:
                    total_score += result["overall_score"]
                    max_score += 10
                elif "overall_competitiveness" in result:
                    total_score += result["overall_competitiveness"]
                    max_score += 10
                elif "overall_trend_score" in result:
                    total_score += result["overall_trend_score"]
                    max_score += 10
        
        # 점수에 따른 투자 의견
        if max_score > 0:
            score_ratio = total_score / max_score
            if score_ratio >= 0.7:
                rating = "Buy"
            elif score_ratio >= 0.5:
                rating = "Hold"  
            else:
                rating = "Sell"
        else:
            rating = "Hold"
        
        # 투자 포인트 및 리스크 (간단한 버전)
        key_points = [
            f"목표주가: {target_price:,.0f}원",
            f"4대지표 종합점수: {total_score:.1f}/{max_score}",
        ]
        
        key_risks = [
            "임상시험 실패 리스크",
            "경쟁 환경 변화",
            "규제 리스크"
        ]
        
        return rating, key_points, key_risks
    
    def _calculate_overall_confidence(self, indicators: Dict, dcf_result: Any) -> float:
        """전체 신뢰도 점수 계산"""
        
        confidence_factors = []
        
        # DCF 결과 신뢰도
        if dcf_result:
            confidence_factors.append(0.8)  # 기본 DCF 신뢰도
        
        # 지표별 신뢰도
        for indicator, result in indicators.items():
            if isinstance(result, dict) and "confidence_level" in result:
                confidence_factors.append(result["confidence_level"])
        
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5  # 기본값

def create_simple_valuation_example() -> ValuationInput:
    """간단한 벨류에이션 예제 데이터"""
    
    company = CompanyInput(
        name="예시바이오텍",
        current_assets=300,  # 300억원
        current_liabilities=50,  # 50억원
        annual_operating_loss=100,  # 100억원 적자
        current_cash=200,  # 200억원 현금
        shares_outstanding=10_000_000,  # 1천만주
        pipelines=[
            {
                "name": "파이프라인A",
                "indication": "항암제",
                "phase": "phase2",
                "moa": "PD-1 inhibitor",
                "differentiators": ["높은 효능", "낮은 부작용"]
            }
        ]
    )
    
    return ValuationInput(company=company)