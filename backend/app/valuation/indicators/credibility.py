from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import re
from datetime import datetime, timedelta

class CredibilityFactor(Enum):
    TRACK_RECORD = "track_record"  # 과거 실적
    MANAGEMENT = "management"      # 경영진
    DISCLOSURE = "disclosure"      # 공시 품질
    CLINICAL_DATA = "clinical_data"  # 임상 데이터
    PARTNERSHIP = "partnership"    # 파트너십
    FINANCIAL_TRANSPARENCY = "financial_transparency"  # 재무 투명성

@dataclass
class TrackRecordData:
    """과거 실적 데이터"""
    milestone_promises: List[Dict[str, Any]]  # 과거 약속한 마일스톤들
    milestone_achievements: List[Dict[str, Any]]  # 실제 달성한 것들
    timeline_deviations: List[Dict[str, Any]]  # 일정 지연 내역
    guidance_accuracy: Optional[float] = None  # 가이던스 정확도 (0-1)

@dataclass
class ManagementData:
    """경영진 데이터"""
    ceo_background: Dict[str, Any]
    key_executives: List[Dict[str, Any]]
    board_composition: Dict[str, Any]
    track_record_score: Optional[float] = None

@dataclass
class DisclosureData:
    """공시 데이터"""
    recent_disclosures: List[Dict[str, Any]]
    disclosure_frequency: int
    disclosure_quality_indicators: Dict[str, float]
    regulatory_compliance: bool = True

@dataclass
class CredibilityResult:
    """신뢰도 분석 결과"""
    overall_score: float  # 0-10 종합 점수
    factor_scores: Dict[CredibilityFactor, float]
    strengths: List[str]
    concerns: List[str]
    detailed_analysis: Dict[str, Any]
    confidence_level: float
    recommendation: str

class CredibilityAnalyzer:
    """신뢰도 분석기"""
    
    def __init__(self):
        self.weights = {
            CredibilityFactor.TRACK_RECORD: 0.30,
            CredibilityFactor.MANAGEMENT: 0.20,
            CredibilityFactor.DISCLOSURE: 0.15,
            CredibilityFactor.CLINICAL_DATA: 0.20,
            CredibilityFactor.PARTNERSHIP: 0.10,
            CredibilityFactor.FINANCIAL_TRANSPARENCY: 0.05
        }
    
    def analyze_credibility(
        self, 
        track_record: TrackRecordData,
        management: ManagementData,
        disclosure: DisclosureData,
        clinical_statements: List[str] = None,
        partnerships: List[Dict] = None
    ) -> CredibilityResult:
        """종합 신뢰도 분석"""
        
        # 각 요소별 점수 계산
        factor_scores = {}
        factor_scores[CredibilityFactor.TRACK_RECORD] = self._analyze_track_record(track_record)
        factor_scores[CredibilityFactor.MANAGEMENT] = self._analyze_management(management)
        factor_scores[CredibilityFactor.DISCLOSURE] = self._analyze_disclosure(disclosure)
        factor_scores[CredibilityFactor.CLINICAL_DATA] = self._analyze_clinical_data(clinical_statements or [])
        factor_scores[CredibilityFactor.PARTNERSHIP] = self._analyze_partnerships(partnerships or [])
        factor_scores[CredibilityFactor.FINANCIAL_TRANSPARENCY] = self._analyze_financial_transparency(disclosure)
        
        # 가중 평균으로 종합 점수 계산
        overall_score = sum(
            score * self.weights[factor] 
            for factor, score in factor_scores.items()
        )
        
        # 강점과 우려사항 도출
        strengths, concerns = self._identify_strengths_and_concerns(factor_scores)
        
        # 상세 분석 결과
        detailed_analysis = self._generate_detailed_analysis(factor_scores, track_record, management)
        
        # 신뢰도 및 추천
        confidence_level = self._calculate_confidence_level(factor_scores)
        recommendation = self._generate_recommendation(overall_score, factor_scores)
        
        return CredibilityResult(
            overall_score=round(overall_score, 1),
            factor_scores=factor_scores,
            strengths=strengths,
            concerns=concerns,
            detailed_analysis=detailed_analysis,
            confidence_level=confidence_level,
            recommendation=recommendation
        )
    
    def _analyze_track_record(self, data: TrackRecordData) -> float:
        """과거 실적 분석"""
        if not data.milestone_promises:
            return 5.0  # 중립 점수
        
        # 마일스톤 달성률 계산
        total_promises = len(data.milestone_promises)
        achievements = len(data.milestone_achievements)
        achievement_rate = achievements / total_promises if total_promises > 0 else 0
        
        # 가이던스 정확도 고려
        guidance_factor = data.guidance_accuracy if data.guidance_accuracy else 0.5
        
        # 일정 지연 페널티
        delay_penalty = min(len(data.timeline_deviations) * 0.5, 2.0)
        
        score = (achievement_rate * 6 + guidance_factor * 4) - delay_penalty
        return max(0, min(10, score))
    
    def _analyze_management(self, data: ManagementData) -> float:
        """경영진 분석"""
        score = 5.0  # 기본 점수
        
        # CEO 백그라운드 점수
        ceo_experience = data.ceo_background.get('biotech_experience_years', 0)
        if ceo_experience >= 10:
            score += 2.0
        elif ceo_experience >= 5:
            score += 1.0
        
        # 성공 경험
        if data.ceo_background.get('previous_success', False):
            score += 1.5
        
        # 핵심 임원진 구성
        key_exec_count = len(data.key_executives)
        if key_exec_count >= 3:
            score += 1.0
        
        # 이사회 구성 (독립성 등)
        independent_ratio = data.board_composition.get('independent_ratio', 0)
        if independent_ratio >= 0.5:
            score += 0.5
        
        return max(0, min(10, score))
    
    def _analyze_disclosure(self, data: DisclosureData) -> float:
        """공시 품질 분석"""
        score = 5.0
        
        # 공시 빈도 (적절성)
        if 4 <= data.disclosure_frequency <= 12:  # 분기별~월별이 적절
            score += 1.0
        
        # 공시 품질 지표들
        quality_indicators = data.disclosure_quality_indicators
        
        # 구체성 점수
        if quality_indicators.get('specificity', 0) > 0.7:
            score += 1.5
        
        # 일관성 점수  
        if quality_indicators.get('consistency', 0) > 0.8:
            score += 1.0
        
        # 적시성 점수
        if quality_indicators.get('timeliness', 0) > 0.8:
            score += 1.0
        
        # 규제 준수
        if data.regulatory_compliance:
            score += 0.5
        else:
            score -= 2.0
        
        return max(0, min(10, score))
    
    def _analyze_clinical_data(self, statements: List[str]) -> float:
        """임상 데이터 일관성 분석"""
        if not statements:
            return 5.0
        
        score = 5.0
        
        # 일관성 키워드 분석 (간단한 버전)
        positive_keywords = ['significant', 'promising', 'positive', 'improved', 'effective']
        negative_keywords = ['discontinued', 'failed', 'negative', 'adverse', 'terminated']
        
        positive_count = sum(
            sum(1 for keyword in positive_keywords if keyword in statement.lower())
            for statement in statements
        )
        
        negative_count = sum(
            sum(1 for keyword in negative_keywords if keyword in statement.lower())
            for statement in statements
        )
        
        # 일관성 점수 계산
        if positive_count > negative_count * 2:
            score += 2.0
        elif negative_count > positive_count:
            score -= 1.5
        
        # 데이터 구체성 검사 (숫자 포함 여부 등)
        specific_data_count = sum(
            1 for statement in statements 
            if re.search(r'\d+\.?\d*%|\d+\.?\d*\s*(?:patients?|subjects?)', statement.lower())
        )
        
        if specific_data_count > len(statements) * 0.7:
            score += 1.5
        
        return max(0, min(10, score))
    
    def _analyze_partnerships(self, partnerships: List[Dict]) -> float:
        """파트너십 분석"""
        if not partnerships:
            return 3.0  # 파트너십 없으면 낮은 점수
        
        score = 5.0
        
        # 대형 파트너십 보너스
        big_pharma_partners = [
            p for p in partnerships 
            if p.get('partner_type') == 'big_pharma'
        ]
        
        score += len(big_pharma_partners) * 2.0
        
        # 최근 파트너십
        recent_partnerships = [
            p for p in partnerships 
            if p.get('year', 2020) >= 2022
        ]
        
        score += len(recent_partnerships) * 0.5
        
        return min(10, score)
    
    def _analyze_financial_transparency(self, disclosure_data: DisclosureData) -> float:
        """재무 투명성 분석"""
        score = 7.0  # 기본적으로 높은 점수 (상장사 기준)
        
        # 공시 품질이 재무 투명성에도 영향
        quality_avg = sum(disclosure_data.disclosure_quality_indicators.values()) / len(disclosure_data.disclosure_quality_indicators)
        score += (quality_avg - 0.5) * 2
        
        return max(0, min(10, score))
    
    def _identify_strengths_and_concerns(self, factor_scores: Dict[CredibilityFactor, float]) -> tuple[List[str], List[str]]:
        """강점과 우려사항 식별"""
        strengths = []
        concerns = []
        
        for factor, score in factor_scores.items():
            if score >= 8.0:
                strengths.append(self._get_strength_message(factor, score))
            elif score <= 4.0:
                concerns.append(self._get_concern_message(factor, score))
        
        return strengths, concerns
    
    def _get_strength_message(self, factor: CredibilityFactor, score: float) -> str:
        """강점 메시지 생성"""
        messages = {
            CredibilityFactor.TRACK_RECORD: "과거 약속 이행률이 우수함",
            CredibilityFactor.MANAGEMENT: "경험이 풍부한 경영진",
            CredibilityFactor.DISCLOSURE: "투명하고 적시성 있는 공시",
            CredibilityFactor.CLINICAL_DATA: "일관되고 신뢰할만한 임상 데이터",
            CredibilityFactor.PARTNERSHIP: "우수한 파트너십 포트폴리오",
            CredibilityFactor.FINANCIAL_TRANSPARENCY: "높은 재무 투명성"
        }
        return messages.get(factor, "우수한 성과")
    
    def _get_concern_message(self, factor: CredibilityFactor, score: float) -> str:
        """우려사항 메시지 생성"""
        messages = {
            CredibilityFactor.TRACK_RECORD: "과거 약속 이행에 문제가 있음",
            CredibilityFactor.MANAGEMENT: "경영진 경험이나 실적이 부족",
            CredibilityFactor.DISCLOSURE: "공시 품질이나 빈도에 문제",
            CredibilityFactor.CLINICAL_DATA: "임상 데이터의 일관성 부족",
            CredibilityFactor.PARTNERSHIP: "의미있는 파트너십 부족",
            CredibilityFactor.FINANCIAL_TRANSPARENCY: "재무 투명성 개선 필요"
        }
        return messages.get(factor, "개선이 필요한 영역")
    
    def _generate_detailed_analysis(self, factor_scores: Dict, track_record: TrackRecordData, management: ManagementData) -> Dict[str, Any]:
        """상세 분석 결과 생성"""
        return {
            "score_breakdown": {factor.value: score for factor, score in factor_scores.items()},
            "key_metrics": {
                "milestone_achievement_rate": len(track_record.milestone_achievements) / max(len(track_record.milestone_promises), 1),
                "management_experience_years": management.ceo_background.get('biotech_experience_years', 0),
                "timeline_delays": len(track_record.timeline_deviations)
            }
        }
    
    def _calculate_confidence_level(self, factor_scores: Dict) -> float:
        """분석 신뢰도 계산"""
        # 점수들의 표준편차가 클수록 신뢰도 감소
        scores = list(factor_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        
        # 표준편차가 클수록 신뢰도 낮음
        confidence = max(0.5, 1.0 - (variance ** 0.5) / 10)
        return round(confidence, 2)
    
    def _generate_recommendation(self, overall_score: float, factor_scores: Dict) -> str:
        """투자 추천 생성"""
        if overall_score >= 8.0:
            return "신뢰도 높음 - 적극적 투자 검토 가능"
        elif overall_score >= 6.0:
            return "보통 수준의 신뢰도 - 신중한 투자 검토 필요"
        elif overall_score >= 4.0:
            return "신뢰도 우려 - 추가 분석 및 모니터링 필요"
        else:
            return "신뢰도 낮음 - 투자 보류 권장"