from dataclasses import dataclass
from typing import Optional, Dict, Any
import math

@dataclass
class CashRunwayData:
    """현금가용년수 계산을 위한 데이터"""
    current_assets: float  # 유동자산 (원)
    current_liabilities: float  # 유동부채 (원)
    annual_operating_loss: float  # 연간 영업적자 (원, 양수로 입력)
    quarterly_burn_rate: Optional[float] = None  # 분기별 소진율 (선택)
    cash_and_equivalents: Optional[float] = None  # 현금성 자산 (더 정확한 계산용)

@dataclass
class CashRunwayResult:
    """현금가용년수 계산 결과"""
    cash_runway_years: float
    net_working_capital: float  # 순운전자본
    monthly_burn_rate: float  # 월별 소진율
    cash_runway_months: float  # 월 단위 현금가용기간
    status: str  # "안전", "주의", "위험"
    recommendations: list[str]
    calculation_method: str
    confidence_score: float  # 0-1, 계산 신뢰도

class CashRunwayCalculator:
    """현금가용년수 계산기"""
    
    def __init__(self):
        self.safety_threshold = 2.0  # 2년 미만시 주의
        self.danger_threshold = 1.0  # 1년 미만시 위험
    
    def calculate(self, data: CashRunwayData) -> CashRunwayResult:
        """현금가용년수 계산"""
        
        # 1. 기본 계산: (유동자산 - 유동부채) / 연간영업적자
        net_working_capital = data.current_assets - data.current_liabilities
        
        if data.annual_operating_loss <= 0:
            # 영업적자가 없거나 흑자인 경우
            return self._handle_no_loss_scenario(net_working_capital, data)
        
        # 2. 기본 현금가용년수 계산
        cash_runway_years = net_working_capital / data.annual_operating_loss
        
        # 3. 더 정확한 계산이 가능한 경우 (분기별 데이터 있음)
        if data.quarterly_burn_rate:
            quarterly_runway = net_working_capital / data.quarterly_burn_rate
            cash_runway_years_from_quarterly = quarterly_runway / 4
            
            # 두 방법의 평균 사용 (더 보수적으로)
            cash_runway_years = min(cash_runway_years, cash_runway_years_from_quarterly)
        
        # 4. 월별 소진율 계산
        monthly_burn_rate = data.annual_operating_loss / 12
        cash_runway_months = cash_runway_years * 12
        
        # 5. 상태 평가
        status = self._evaluate_status(cash_runway_years)
        
        # 6. 추천사항 생성
        recommendations = self._generate_recommendations(cash_runway_years, data)
        
        # 7. 신뢰도 점수 계산
        confidence_score = self._calculate_confidence(data, cash_runway_years)
        
        return CashRunwayResult(
            cash_runway_years=round(cash_runway_years, 2),
            net_working_capital=net_working_capital,
            monthly_burn_rate=monthly_burn_rate,
            cash_runway_months=round(cash_runway_months, 1),
            status=status,
            recommendations=recommendations,
            calculation_method="기본공식" if not data.quarterly_burn_rate else "분기데이터보정",
            confidence_score=confidence_score
        )
    
    def _handle_no_loss_scenario(self, net_working_capital: float, data: CashRunwayData) -> CashRunwayResult:
        """영업적자가 없는 경우 처리"""
        return CashRunwayResult(
            cash_runway_years=float('inf') if net_working_capital > 0 else 0,
            net_working_capital=net_working_capital,
            monthly_burn_rate=0,
            cash_runway_months=float('inf') if net_working_capital > 0 else 0,
            status="우수" if net_working_capital > 0 else "주의",
            recommendations=["흑자 또는 손익분기점 달성으로 현금소진 우려 없음"] if net_working_capital > 0 else ["순운전자본이 음수입니다"],
            calculation_method="흑자기업",
            confidence_score=0.9
        )
    
    def _evaluate_status(self, cash_runway_years: float) -> str:
        """현금가용년수 기반 상태 평가"""
        if cash_runway_years >= self.safety_threshold:
            return "안전"
        elif cash_runway_years >= self.danger_threshold:
            return "주의"
        else:
            return "위험"
    
    def _generate_recommendations(self, cash_runway_years: float, data: CashRunwayData) -> list[str]:
        """추천사항 생성"""
        recommendations = []
        
        if cash_runway_years < self.danger_threshold:
            recommendations.extend([
                "즉시 자금조달 계획 수립 필요",
                "비용 절감 방안 검토",
                "마일스톤 달성 가속화 필요"
            ])
        elif cash_runway_years < self.safety_threshold:
            recommendations.extend([
                "자금조달 계획 사전 준비 권장",
                "현금 소진율 모니터링 강화"
            ])
        else:
            recommendations.append("현금 상황 양호, 정기적 모니터링 유지")
        
        # 추가 분석 기반 권장사항
        burn_rate_monthly = data.annual_operating_loss / 12
        if burn_rate_monthly > 5_000_000_000:  # 월 50억 이상 소진
            recommendations.append("월별 현금소진율이 높음 - 효율성 검토 필요")
        
        return recommendations
    
    def _calculate_confidence(self, data: CashRunwayData, cash_runway_years: float) -> float:
        """계산 신뢰도 점수"""
        confidence = 0.8  # 기본 신뢰도
        
        # 분기별 데이터가 있으면 신뢰도 증가
        if data.quarterly_burn_rate:
            confidence += 0.1
        
        # 현금성 자산 데이터가 따로 있으면 신뢰도 증가  
        if data.cash_and_equivalents:
            confidence += 0.05
        
        # 극단적 값이면 신뢰도 감소
        if cash_runway_years > 10 or cash_runway_years < 0:
            confidence -= 0.2
        
        return min(1.0, max(0.1, confidence))
    
    def get_benchmark_comparison(self, cash_runway_years: float) -> Dict[str, Any]:
        """업계 벤치마크 비교"""
        benchmarks = {
            "바이오벤처_평균": 2.5,
            "상장바이오_평균": 3.2,
            "글로벌바이오_평균": 4.1
        }
        
        comparison = {}
        for benchmark_name, benchmark_value in benchmarks.items():
            comparison[benchmark_name] = {
                "benchmark": benchmark_value,
                "vs_benchmark": cash_runway_years - benchmark_value,
                "percentile": "상위" if cash_runway_years > benchmark_value else "하위"
            }
        
        return comparison