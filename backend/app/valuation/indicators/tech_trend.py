from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta

class TechCategory(Enum):
    ONCOLOGY = "oncology"
    RARE_DISEASE = "rare_disease"
    CNS = "central_nervous_system"
    IMMUNOLOGY = "immunology"
    METABOLIC = "metabolic"
    INFECTIOUS_DISEASE = "infectious_disease"
    GENE_THERAPY = "gene_therapy"
    CELL_THERAPY = "cell_therapy"
    DIGITAL_THERAPEUTICS = "digital_therapeutics"

class TrendStatus(Enum):
    HOT = "hot"          # 매우 주목받는 분야
    RISING = "rising"    # 상승 중인 분야
    STABLE = "stable"    # 안정적 분야
    DECLINING = "declining"  # 하락 중인 분야

@dataclass
class CompanyTechnology:
    """회사의 기술 정보"""
    platform_technology: str
    therapeutic_areas: List[TechCategory]
    pipeline_stages: Dict[str, str]  # {pipeline_name: stage}
    differentiation_factors: List[str]
    patent_portfolio: Optional[Dict[str, Any]] = None

@dataclass
class MarketTrendData:
    """시장 트렌드 데이터"""
    category_trends: Dict[TechCategory, Dict[str, Any]]
    recent_deals: List[Dict[str, Any]]  # 최근 M&A, 라이선싱 딜
    big_pharma_focus_areas: List[str]
    venture_investment_trends: Dict[str, float]
    regulatory_environment: Dict[str, Any]

@dataclass
class TechTrendResult:
    """기술 트렌드 분석 결과"""
    overall_trend_score: float  # 0-10
    category_alignment_scores: Dict[TechCategory, float]
    big_pharma_attractiveness: float  # 빅파마 매력도
    market_timing_score: float
    competitive_positioning: str
    key_opportunities: List[str]
    potential_risks: List[str]
    trend_analysis: Dict[str, Any]
    recommendation: str

class TechTrendAnalyzer:
    """기술 트렌드 분석기"""
    
    def __init__(self):
        # 각 기술 카테고리별 현재 트렌드 가중치
        self.category_weights = {
            TechCategory.ONCOLOGY: 1.0,
            TechCategory.RARE_DISEASE: 0.9,
            TechCategory.CNS: 0.8,
            TechCategory.IMMUNOLOGY: 0.9,
            TechCategory.GENE_THERAPY: 1.0,
            TechCategory.CELL_THERAPY: 0.9,
            TechCategory.METABOLIC: 0.7,
            TechCategory.INFECTIOUS_DISEASE: 0.6,
            TechCategory.DIGITAL_THERAPEUTICS: 0.8
        }
        
        # 빅파마 선호도 매트릭스
        self.big_pharma_preferences = {
            TechCategory.ONCOLOGY: 0.95,
            TechCategory.RARE_DISEASE: 0.85,
            TechCategory.IMMUNOLOGY: 0.90,
            TechCategory.CNS: 0.75,
            TechCategory.GENE_THERAPY: 0.80,
            TechCategory.CELL_THERAPY: 0.75,
            TechCategory.METABOLIC: 0.70,
            TechCategory.INFECTIOUS_DISEASE: 0.60,
            TechCategory.DIGITAL_THERAPEUTICS: 0.50
        }
    
    def analyze_tech_trend(
        self, 
        company_tech: CompanyTechnology,
        market_data: MarketTrendData
    ) -> TechTrendResult:
        """기술 트렌드 종합 분석"""
        
        # 1. 카테고리별 정렬 점수 계산
        category_scores = self._analyze_category_alignment(
            company_tech.therapeutic_areas, 
            market_data.category_trends
        )
        
        # 2. 빅파마 매력도 계산
        big_pharma_score = self._calculate_big_pharma_attractiveness(
            company_tech, 
            market_data.recent_deals
        )
        
        # 3. 시장 타이밍 점수
        timing_score = self._analyze_market_timing(
            company_tech, 
            market_data
        )
        
        # 4. 종합 트렌드 점수
        overall_score = self._calculate_overall_trend_score(
            category_scores, 
            big_pharma_score, 
            timing_score
        )
        
        # 5. 경쟁 포지셔닝 분석
        competitive_positioning = self._analyze_competitive_positioning(
            company_tech, 
            market_data
        )
        
        # 6. 기회와 리스크 식별
        opportunities, risks = self._identify_opportunities_and_risks(
            company_tech, 
            market_data, 
            category_scores
        )
        
        # 7. 상세 분석 결과
        trend_analysis = self._generate_trend_analysis(
            company_tech, 
            market_data, 
            category_scores
        )
        
        # 8. 추천사항
        recommendation = self._generate_recommendation(overall_score, big_pharma_score)
        
        return TechTrendResult(
            overall_trend_score=round(overall_score, 1),
            category_alignment_scores=category_scores,
            big_pharma_attractiveness=round(big_pharma_score, 1),
            market_timing_score=round(timing_score, 1),
            competitive_positioning=competitive_positioning,
            key_opportunities=opportunities,
            potential_risks=risks,
            trend_analysis=trend_analysis,
            recommendation=recommendation
        )
    
    def _analyze_category_alignment(
        self, 
        company_areas: List[TechCategory], 
        trend_data: Dict[TechCategory, Dict[str, Any]]
    ) -> Dict[TechCategory, float]:
        """카테고리별 트렌드 정렬도 분석"""
        scores = {}
        
        for category in company_areas:
            base_score = self.category_weights.get(category, 0.5) * 10
            
            # 트렌드 데이터 기반 조정
            if category in trend_data:
                trend_info = trend_data[category]
                
                # 투자 증가율 반영
                investment_growth = trend_info.get('investment_growth_rate', 0)
                base_score += investment_growth * 2
                
                # M&A 활동 반영
                ma_activity = trend_info.get('ma_activity_score', 0.5)
                base_score += ma_activity * 1.5
                
                # 규제 환경 반영
                regulatory_support = trend_info.get('regulatory_support', 0.5)
                base_score += regulatory_support * 1.0
            
            scores[category] = min(10.0, max(0.0, base_score))
        
        return scores
    
    def _calculate_big_pharma_attractiveness(
        self, 
        company_tech: CompanyTechnology, 
        recent_deals: List[Dict[str, Any]]
    ) -> float:
        """빅파마 매력도 계산"""
        base_score = 0.0
        
        # 카테고리별 빅파마 선호도
        for category in company_tech.therapeutic_areas:
            preference = self.big_pharma_preferences.get(category, 0.5)
            base_score += preference * 10
        
        if company_tech.therapeutic_areas:
            base_score /= len(company_tech.therapeutic_areas)
        
        # 최근 딜 트렌드 반영
        relevant_deals = [
            deal for deal in recent_deals
            if any(area.value in deal.get('therapeutic_area', '').lower() 
                  for area in company_tech.therapeutic_areas)
        ]
        
        if relevant_deals:
            avg_deal_premium = sum(deal.get('premium_multiple', 1.0) for deal in relevant_deals) / len(relevant_deals)
            base_score += min(2.0, (avg_deal_premium - 1.0) * 2)
        
        # 플랫폼 기술 보너스
        platform_bonus = self._calculate_platform_technology_bonus(company_tech.platform_technology)
        base_score += platform_bonus
        
        # 파이프라인 단계 보너스 (후기 단계일수록 매력적)
        stage_bonus = self._calculate_pipeline_stage_bonus(company_tech.pipeline_stages)
        base_score += stage_bonus
        
        return min(10.0, max(0.0, base_score))
    
    def _calculate_platform_technology_bonus(self, platform_tech: str) -> float:
        """플랫폼 기술 보너스 계산"""
        high_value_platforms = [
            'antibody-drug conjugate', 'adc', 'car-t', 'gene editing',
            'crispr', 'mrna', 'protein degradation', 'protac'
        ]
        
        platform_lower = platform_tech.lower()
        if any(tech in platform_lower for tech in high_value_platforms):
            return 1.5
        elif 'antibody' in platform_lower or 'biologics' in platform_lower:
            return 1.0
        elif 'small molecule' in platform_lower:
            return 0.5
        else:
            return 0.0
    
    def _calculate_pipeline_stage_bonus(self, pipeline_stages: Dict[str, str]) -> float:
        """파이프라인 단계별 보너스"""
        stage_values = {
            'preclinical': 0.2,
            'phase1': 0.5,
            'phase2': 1.0,
            'phase3': 1.5,
            'submitted': 2.0,
            'approved': 2.5
        }
        
        total_bonus = 0.0
        for pipeline, stage in pipeline_stages.items():
            stage_lower = stage.lower()
            for stage_key, bonus in stage_values.items():
                if stage_key in stage_lower:
                    total_bonus += bonus
                    break
        
        return min(2.0, total_bonus)
    
    def _analyze_market_timing(
        self, 
        company_tech: CompanyTechnology, 
        market_data: MarketTrendData
    ) -> float:
        """시장 타이밍 분석"""
        timing_score = 5.0  # 기본 점수
        
        # 벤처 투자 트렌드 분석
        for category in company_tech.therapeutic_areas:
            if category.value in market_data.venture_investment_trends:
                investment_trend = market_data.venture_investment_trends[category.value]
                timing_score += (investment_trend - 1.0) * 2  # 1.0이 평균
        
        # 규제 환경 분석
        regulatory_env = market_data.regulatory_environment
        if regulatory_env.get('fast_track_opportunities', False):
            timing_score += 1.0
        if regulatory_env.get('breakthrough_designation_potential', False):
            timing_score += 1.5
        
        return min(10.0, max(0.0, timing_score))
    
    def _calculate_overall_trend_score(
        self, 
        category_scores: Dict[TechCategory, float], 
        big_pharma_score: float, 
        timing_score: float
    ) -> float:
        """종합 트렌드 점수 계산"""
        # 카테고리 점수 평균
        avg_category_score = sum(category_scores.values()) / len(category_scores) if category_scores else 5.0
        
        # 가중 평균
        weights = {
            'category': 0.4,
            'big_pharma': 0.4,
            'timing': 0.2
        }
        
        overall_score = (
            avg_category_score * weights['category'] +
            big_pharma_score * weights['big_pharma'] +
            timing_score * weights['timing']
        )
        
        return overall_score
    
    def _analyze_competitive_positioning(
        self, 
        company_tech: CompanyTechnology, 
        market_data: MarketTrendData
    ) -> str:
        """경쟁 포지셔닝 분석"""
        
        # 차별화 요소 개수로 간단한 포지셔닝 분석
        differentiation_count = len(company_tech.differentiation_factors)
        
        if differentiation_count >= 3:
            return "Strong Differentiation"
        elif differentiation_count >= 2:
            return "Moderate Differentiation"
        else:
            return "Limited Differentiation"
    
    def _identify_opportunities_and_risks(
        self, 
        company_tech: CompanyTechnology, 
        market_data: MarketTrendData,
        category_scores: Dict[TechCategory, float]
    ) -> tuple[List[str], List[str]]:
        """기회와 리스크 식별"""
        
        opportunities = []
        risks = []
        
        # 높은 점수 카테고리는 기회
        for category, score in category_scores.items():
            if score >= 8.0:
                opportunities.append(f"{category.value} 분야의 높은 시장 관심도")
            elif score <= 4.0:
                risks.append(f"{category.value} 분야의 시장 관심도 저조")
        
        # 빅파마 선호 분야 체크
        high_preference_areas = [
            category for category in company_tech.therapeutic_areas
            if self.big_pharma_preferences.get(category, 0) >= 0.8
        ]
        
        if high_preference_areas:
            opportunities.append("빅파마 높은 관심 분야")
        
        # 플랫폼 기술 관련
        if 'gene' in company_tech.platform_technology.lower():
            opportunities.append("차세대 유전자 치료 기술 보유")
            risks.append("규제 및 제조 복잡성")
        
        return opportunities, risks
    
    def _generate_trend_analysis(
        self, 
        company_tech: CompanyTechnology, 
        market_data: MarketTrendData,
        category_scores: Dict[TechCategory, float]
    ) -> Dict[str, Any]:
        """상세 트렌드 분석 결과"""
        
        return {
            "primary_therapeutic_area": company_tech.therapeutic_areas[0].value if company_tech.therapeutic_areas else "unknown",
            "platform_technology": company_tech.platform_technology,
            "pipeline_maturity": self._assess_pipeline_maturity(company_tech.pipeline_stages),
            "category_trend_summary": {
                category.value: score for category, score in category_scores.items()
            },
            "key_differentiators": company_tech.differentiation_factors
        }
    
    def _assess_pipeline_maturity(self, pipeline_stages: Dict[str, str]) -> str:
        """파이프라인 성숙도 평가"""
        stages = list(pipeline_stages.values())
        
        if any('phase3' in stage.lower() or 'submitted' in stage.lower() for stage in stages):
            return "Late-stage"
        elif any('phase2' in stage.lower() for stage in stages):
            return "Mid-stage"
        elif any('phase1' in stage.lower() for stage in stages):
            return "Early-stage"
        else:
            return "Preclinical"
    
    def _generate_recommendation(self, overall_score: float, big_pharma_score: float) -> str:
        """투자 추천 생성"""
        
        if overall_score >= 8.0 and big_pharma_score >= 8.0:
            return "매우 유망한 기술 트렌드 - 적극적 투자 검토"
        elif overall_score >= 6.5:
            return "양호한 기술 트렌드 - 긍정적 투자 검토"
        elif overall_score >= 5.0:
            return "보통 수준의 기술 트렌드 - 신중한 검토 필요"
        else:
            return "기술 트렌드 불리 - 추가 분석 후 결정"