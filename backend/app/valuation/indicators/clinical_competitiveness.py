from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ClinicalPhase(Enum):
    PRECLINICAL = "preclinical"
    PHASE_1 = "phase1"
    PHASE_2 = "phase2" 
    PHASE_3 = "phase3"
    SUBMITTED = "submitted"
    APPROVED = "approved"

class CompetitiveAdvantage(Enum):
    FIRST_IN_CLASS = "first_in_class"
    BEST_IN_CLASS = "best_in_class"
    FAST_FOLLOWER = "fast_follower"
    ME_TOO = "me_too"

@dataclass
class PipelineAsset:
    """파이프라인 자산 정보"""
    name: str
    indication: str
    current_phase: ClinicalPhase
    mechanism_of_action: str
    target: str
    expected_timeline: Dict[str, str]  # {phase: expected_date}
    clinical_data: Dict[str, Any]     # 임상 데이터
    differentiation_factors: List[str]

@dataclass
class CompetitorAsset:
    """경쟁사 파이프라인"""
    competitor_name: str
    asset_name: str
    indication: str
    current_phase: ClinicalPhase
    mechanism_of_action: str
    clinical_performance: Dict[str, float]
    expected_launch: Optional[str] = None
    market_position: str = "unknown"

@dataclass
class ClinicalCompetitivenessResult:
    """임상 경쟁력 분석 결과"""
    overall_competitiveness: float  # 0-10
    asset_competitiveness: Dict[str, Dict[str, Any]]  # 자산별 경쟁력
    competitive_advantages: List[CompetitiveAdvantage]
    key_differentiators: List[str]
    competitive_risks: List[str]
    market_positioning: Dict[str, str]
    success_probability_adjustments: Dict[str, float]
    strategic_recommendations: List[str]

class ClinicalCompetitivenessAnalyzer:
    """임상 경쟁력 분석기"""
    
    def __init__(self):
        # 임상 단계별 기본 성공 확률
        self.base_success_rates = {
            ClinicalPhase.PRECLINICAL: 0.40,
            ClinicalPhase.PHASE_1: 0.60,
            ClinicalPhase.PHASE_2: 0.35,
            ClinicalPhase.PHASE_3: 0.65,
            ClinicalPhase.SUBMITTED: 0.90,
            ClinicalPhase.APPROVED: 1.00
        }
        
        # 경쟁 우위별 성공 확률 조정
        self.competitive_multipliers = {
            CompetitiveAdvantage.FIRST_IN_CLASS: 1.3,
            CompetitiveAdvantage.BEST_IN_CLASS: 1.2,
            CompetitiveAdvantage.FAST_FOLLOWER: 1.1,
            CompetitiveAdvantage.ME_TOO: 0.8
        }
    
    def analyze_clinical_competitiveness(
        self,
        company_pipeline: List[PipelineAsset],
        competitor_landscape: List[CompetitorAsset],
        market_context: Dict[str, Any] = None
    ) -> ClinicalCompetitivenessResult:
        """임상 경쟁력 종합 분석"""
        
        # 1. 자산별 경쟁력 분석
        asset_competitiveness = {}
        overall_scores = []
        
        for asset in company_pipeline:
            asset_analysis = self._analyze_single_asset_competitiveness(
                asset, competitor_landscape, market_context or {}
            )
            asset_competitiveness[asset.name] = asset_analysis
            overall_scores.append(asset_analysis['competitiveness_score'])
        
        # 2. 전체 경쟁력 점수
        overall_competitiveness = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        # 3. 경쟁 우위 식별
        competitive_advantages = self._identify_competitive_advantages(
            company_pipeline, competitor_landscape
        )
        
        # 4. 핵심 차별화 요소
        key_differentiators = self._extract_key_differentiators(company_pipeline)
        
        # 5. 경쟁 리스크 분석
        competitive_risks = self._analyze_competitive_risks(
            company_pipeline, competitor_landscape
        )
        
        # 6. 시장 포지셔닝
        market_positioning = self._determine_market_positioning(
            company_pipeline, competitor_landscape
        )
        
        # 7. 성공 확률 조정
        success_probability_adjustments = self._calculate_success_probability_adjustments(
            company_pipeline, competitive_advantages, competitor_landscape
        )
        
        # 8. 전략적 권장사항
        strategic_recommendations = self._generate_strategic_recommendations(
            asset_competitiveness, competitive_risks, competitive_advantages
        )
        
        return ClinicalCompetitivenessResult(
            overall_competitiveness=round(overall_competitiveness, 1),
            asset_competitiveness=asset_competitiveness,
            competitive_advantages=competitive_advantages,
            key_differentiators=key_differentiators,
            competitive_risks=competitive_risks,
            market_positioning=market_positioning,
            success_probability_adjustments=success_probability_adjustments,
            strategic_recommendations=strategic_recommendations
        )
    
    def _analyze_single_asset_competitiveness(
        self,
        asset: PipelineAsset,
        competitors: List[CompetitorAsset],
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개별 자산의 경쟁력 분석"""
        
        # 같은 적응증 경쟁사 필터링
        relevant_competitors = [
            comp for comp in competitors 
            if comp.indication.lower() == asset.indication.lower()
        ]
        
        base_score = 5.0  # 기본 점수
        
        # 1. 임상 단계 비교 우위
        phase_advantage = self._calculate_phase_advantage(asset, relevant_competitors)
        base_score += phase_advantage
        
        # 2. 임상 데이터 우수성
        clinical_data_score = self._evaluate_clinical_data(asset.clinical_data)
        base_score += clinical_data_score
        
        # 3. 차별화 요소 점수
        differentiation_score = len(asset.differentiation_factors) * 0.5
        base_score += min(differentiation_score, 2.0)
        
        # 4. 메커니즘 차별화
        mechanism_uniqueness = self._evaluate_mechanism_uniqueness(
            asset, relevant_competitors
        )
        base_score += mechanism_uniqueness
        
        # 5. 타이밍 우위
        timing_advantage = self._calculate_timing_advantage(asset, relevant_competitors)
        base_score += timing_advantage
        
        competitiveness_score = min(10.0, max(0.0, base_score))
        
        return {
            'competitiveness_score': competitiveness_score,
            'phase_advantage': phase_advantage,
            'clinical_data_quality': clinical_data_score,
            'differentiation_strength': differentiation_score,
            'mechanism_uniqueness': mechanism_uniqueness,
            'timing_advantage': timing_advantage,
            'relevant_competitors_count': len(relevant_competitors),
            'competitive_threats': [comp.competitor_name for comp in relevant_competitors[:3]]
        }
    
    def _calculate_phase_advantage(
        self, 
        asset: PipelineAsset, 
        competitors: List[CompetitorAsset]
    ) -> float:
        """임상 단계 우위 계산"""
        if not competitors:
            return 1.0  # 경쟁사 없으면 우위
        
        asset_phase_value = self._get_phase_numeric_value(asset.current_phase)
        competitor_phases = [
            self._get_phase_numeric_value(comp.current_phase) 
            for comp in competitors
        ]
        
        avg_competitor_phase = sum(competitor_phases) / len(competitor_phases)
        phase_difference = asset_phase_value - avg_competitor_phase
        
        # 1단계 앞서면 +1점, 1단계 뒤지면 -1점
        return max(-2.0, min(2.0, phase_difference))
    
    def _get_phase_numeric_value(self, phase: ClinicalPhase) -> float:
        """임상 단계 숫자 값"""
        phase_values = {
            ClinicalPhase.PRECLINICAL: 0,
            ClinicalPhase.PHASE_1: 1,
            ClinicalPhase.PHASE_2: 2,
            ClinicalPhase.PHASE_3: 3,
            ClinicalPhase.SUBMITTED: 4,
            ClinicalPhase.APPROVED: 5
        }
        return phase_values.get(phase, 0)
    
    def _evaluate_clinical_data(self, clinical_data: Dict[str, Any]) -> float:
        """임상 데이터 품질 평가"""
        score = 0.0
        
        # 유효성 데이터
        if 'efficacy_endpoint_met' in clinical_data:
            if clinical_data['efficacy_endpoint_met']:
                score += 1.5
            else:
                score -= 0.5
        
        # 안전성 프로파일
        if 'safety_profile' in clinical_data:
            safety_score = clinical_data.get('safety_score', 0.5)  # 0-1 scale
            score += (safety_score - 0.5) * 2  # -1 to +1
        
        # 환자 수
        if 'patient_count' in clinical_data:
            patient_count = clinical_data['patient_count']
            if patient_count >= 100:
                score += 1.0
            elif patient_count >= 50:
                score += 0.5
        
        # 통계적 유의성
        if 'statistical_significance' in clinical_data:
            if clinical_data['statistical_significance']:
                score += 1.0
        
        return min(3.0, max(-1.0, score))
    
    def _evaluate_mechanism_uniqueness(
        self, 
        asset: PipelineAsset, 
        competitors: List[CompetitorAsset]
    ) -> float:
        """메커니즘 고유성 평가"""
        if not competitors:
            return 1.0
        
        similar_mechanisms = [
            comp for comp in competitors
            if comp.mechanism_of_action.lower() == asset.mechanism_of_action.lower()
        ]
        
        if not similar_mechanisms:
            return 2.0  # 고유 메커니즘
        elif len(similar_mechanisms) <= 2:
            return 1.0  # 제한적 경쟁
        else:
            return -0.5  # 치열한 경쟁
    
    def _calculate_timing_advantage(
        self, 
        asset: PipelineAsset, 
        competitors: List[CompetitorAsset]
    ) -> float:
        """타이밍 우위 계산"""
        if not competitors or not asset.expected_timeline:
            return 0.0
        
        # 예상 상업화 시점 비교 (간단한 버전)
        try:
            asset_launch_phase = max(asset.expected_timeline.keys())
            
            competitors_with_timeline = [
                comp for comp in competitors 
                if comp.expected_launch
            ]
            
            if competitors_with_timeline:
                # 첫 번째로 출시 예정이면 우위
                return 1.0 if len(competitors_with_timeline) > 0 else 0.0
            
        except:
            pass
        
        return 0.0
    
    def _identify_competitive_advantages(
        self, 
        company_pipeline: List[PipelineAsset],
        competitors: List[CompetitorAsset]
    ) -> List[CompetitiveAdvantage]:
        """경쟁 우위 식별"""
        advantages = []
        
        for asset in company_pipeline:
            same_indication_competitors = [
                comp for comp in competitors
                if comp.indication.lower() == asset.indication.lower()
            ]
            
            if not same_indication_competitors:
                advantages.append(CompetitiveAdvantage.FIRST_IN_CLASS)
            elif len(asset.differentiation_factors) >= 3:
                advantages.append(CompetitiveAdvantage.BEST_IN_CLASS)
            elif len(asset.differentiation_factors) >= 1:
                advantages.append(CompetitiveAdvantage.FAST_FOLLOWER)
            else:
                advantages.append(CompetitiveAdvantage.ME_TOO)
        
        return list(set(advantages))  # 중복 제거
    
    def _extract_key_differentiators(self, pipeline: List[PipelineAsset]) -> List[str]:
        """핵심 차별화 요소 추출"""
        all_differentiators = []
        for asset in pipeline:
            all_differentiators.extend(asset.differentiation_factors)
        
        # 빈도별 상위 차별화 요소 반환
        from collections import Counter
        differentiator_counts = Counter(all_differentiators)
        return [diff for diff, count in differentiator_counts.most_common(5)]
    
    def _analyze_competitive_risks(
        self, 
        pipeline: List[PipelineAsset],
        competitors: List[CompetitorAsset]
    ) -> List[str]:
        """경쟁 리스크 분석"""
        risks = []
        
        # 각 파이프라인별 리스크 분석
        for asset in pipeline:
            relevant_competitors = [
                comp for comp in competitors
                if comp.indication.lower() == asset.indication.lower()
            ]
            
            # 앞선 경쟁사 존재
            advanced_competitors = [
                comp for comp in relevant_competitors
                if self._get_phase_numeric_value(comp.current_phase) > 
                   self._get_phase_numeric_value(asset.current_phase)
            ]
            
            if advanced_competitors:
                risks.append(f"{asset.indication} 분야에 {len(advanced_competitors)}개 앞선 경쟁사 존재")
            
            # 메이저 제약회사 경쟁
            major_pharma_competitors = [
                comp for comp in relevant_competitors
                if any(major in comp.competitor_name.lower() 
                      for major in ['pfizer', 'roche', 'novartis', 'merck', 'astrazeneca'])
            ]
            
            if major_pharma_competitors:
                risks.append(f"{asset.indication}에서 메이저 제약회사와 경쟁")
        
        return risks
    
    def _determine_market_positioning(
        self, 
        pipeline: List[PipelineAsset],
        competitors: List[CompetitorAsset]
    ) -> Dict[str, str]:
        """시장 포지셔닝 결정"""
        positioning = {}
        
        for asset in pipeline:
            relevant_competitors = [
                comp for comp in competitors
                if comp.indication.lower() == asset.indication.lower()
            ]
            
            if not relevant_competitors:
                positioning[asset.name] = "Pioneer"
            elif len(relevant_competitors) <= 2:
                positioning[asset.name] = "Early Entrant"
            elif len(asset.differentiation_factors) >= 2:
                positioning[asset.name] = "Differentiated Player"
            else:
                positioning[asset.name] = "Fast Follower"
        
        return positioning
    
    def _calculate_success_probability_adjustments(
        self,
        pipeline: List[PipelineAsset],
        competitive_advantages: List[CompetitiveAdvantage],
        competitors: List[CompetitorAsset]
    ) -> Dict[str, float]:
        """성공 확률 조정 계산"""
        adjustments = {}
        
        for asset in pipeline:
            base_probability = self.base_success_rates[asset.current_phase]
            
            # 경쟁 우위에 따른 조정
            advantage_multiplier = 1.0
            for advantage in competitive_advantages:
                advantage_multiplier *= self.competitive_multipliers.get(advantage, 1.0)
            
            # 경쟁 강도에 따른 조정
            relevant_competitors = [
                comp for comp in competitors
                if comp.indication.lower() == asset.indication.lower()
            ]
            
            competition_adjustment = max(0.8, 1.0 - len(relevant_competitors) * 0.05)
            
            adjusted_probability = base_probability * advantage_multiplier * competition_adjustment
            adjustments[asset.name] = min(0.95, max(0.05, adjusted_probability))
        
        return adjustments
    
    def _generate_strategic_recommendations(
        self,
        asset_competitiveness: Dict[str, Dict[str, Any]],
        competitive_risks: List[str],
        competitive_advantages: List[CompetitiveAdvantage]
    ) -> List[str]:
        """전략적 권장사항 생성"""
        recommendations = []
        
        # 경쟁력 높은 자산 집중
        high_competitiveness_assets = [
            name for name, data in asset_competitiveness.items()
            if data['competitiveness_score'] >= 7.0
        ]
        
        if high_competitiveness_assets:
            recommendations.append(f"높은 경쟁력 자산({', '.join(high_competitiveness_assets)})에 리소스 집중")
        
        # 경쟁 우위 활용
        if CompetitiveAdvantage.FIRST_IN_CLASS in competitive_advantages:
            recommendations.append("First-in-class 우위를 활용한 빠른 시장 진입 전략")
        
        if CompetitiveAdvantage.BEST_IN_CLASS in competitive_advantages:
            recommendations.append("Best-in-class 포지셔닝으로 프리미엄 가격 전략")
        
        # 리스크 대응
        if len(competitive_risks) > 3:
            recommendations.append("높은 경쟁 리스크 - 차별화 전략 및 파트너십 고려")
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append("경쟁 환경 지속 모니터링 및 차별화 요소 강화")
        
        return recommendations