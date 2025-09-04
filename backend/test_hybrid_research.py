#!/usr/bin/env python3
"""
하이브리드 리서치 엔진 테스트 (웹 크롤링 + AI 분석)
사용법: python3 test_hybrid_research.py [회사명] --url [웹사이트URL] --openai-key [API키]
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_hybrid_research(company_name: str, company_url: str = None, anthropic_key: str = None, openai_key: str = None):
    """하이브리드 리서치 테스트"""
    
    print(f"🚀 {company_name} 하이브리드 리서치 테스트")
    print("=" * 60)
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if anthropic_key:
        print("🧠 AI 분석 모드: Anthropic Claude API 사용")
    elif openai_key:
        print("🧠 AI 분석 모드: OpenAI API 사용")  
    else:
        print("📊 기본 분석 모드: 키워드 기반 분석")
    
    print(f"🌐 대상 웹사이트: {company_url or '자동 추정'}")
    print()
    
    try:
        from research.hybrid_research_engine import HybridResearchEngine
        
        # 하이브리드 엔진 초기화  
        engine = HybridResearchEngine(anthropic_api_key=anthropic_key, openai_api_key=openai_key)
        
        # URL 자동 추정
        if not company_url:
            url_mapping = {
                '씨어스테크놀로지': 'https://seerstech.com',
                '리가켐바이오': 'https://www.ligachem.com',
                '셀트리온': 'https://www.celltrion.com',
                '삼성바이오로직스': 'https://www.samsungbiologics.com',
                '유한양행': 'https://www.yuhan.co.kr'
            }
            company_url = url_mapping.get(company_name, f"https://www.{company_name.lower()}.com")
        
        # 하이브리드 리서치 실행
        result = await engine.conduct_hybrid_research(company_name, company_url)
        
        # === 결과 출력 ===
        print()
        print("📋 회사 기본 정보")
        print("-" * 40)
        print(f"• 회사명: {result.company_name}")
        print(f"• 사업모델: {result.business_model}")
        print(f"• 시장기회: {result.market_opportunity}")
        print()
        
        if result.key_technologies:
            print("🔬 핵심 기술")
            print("-" * 40)
            for i, tech in enumerate(result.key_technologies, 1):
                print(f"  {i}. {tech}")
            print()
        
        if result.competitive_advantages:
            print("🏆 경쟁 우위")
            print("-" * 40)
            for i, advantage in enumerate(result.competitive_advantages, 1):
                print(f"  {i}. {advantage}")
            print()
        
        if result.growth_drivers:
            print("📈 성장 동력")
            print("-" * 40)
            for i, driver in enumerate(result.growth_drivers, 1):
                print(f"  {i}. {driver}")
            print()
        
        if result.investment_thesis:
            print("💡 투자 논리")
            print("-" * 40)
            for i, thesis in enumerate(result.investment_thesis, 1):
                print(f"  {i}. {thesis}")
            print()
        
        if result.risk_factors:
            print("⚠️ 리스크 요인")
            print("-" * 40)
            for i, risk in enumerate(result.risk_factors, 1):
                print(f"  {i}. {risk}")
            print()
        
        # 재무 하이라이트
        if result.financial_highlights:
            print("💰 재무 하이라이트")
            print("-" * 40)
            for key, value in result.financial_highlights.items():
                print(f"  • {key}: {value}")
            print()
        
        # 밸류에이션 요인
        if result.valuation_factors:
            print("📊 밸류에이션 요인")
            print("-" * 40)
            for key, value in result.valuation_factors.items():
                print(f"  • {key}: {value}")
            print()
        
        # 종합 평가
        print("🎯 종합 평가")
        print("-" * 40)
        print(f"• 데이터 신뢰도: {result.confidence_score:.2f}/1.0")
        print(f"• 분석 방법: {', '.join(result.data_sources)}")
        
        if result.confidence_score >= 0.8:
            rating = "A+ (매우 우수)"
        elif result.confidence_score >= 0.7:
            rating = "A (우수)"
        elif result.confidence_score >= 0.5:
            rating = "B (보통)"
        else:
            rating = "C (부족)"
        
        print(f"• 분석 등급: {rating}")
        
        # AI vs 기본 분석 비교
        print()
        print("🔍 분석 품질 개선 제안")
        print("-" * 40)
        if not anthropic_key and not openai_key:
            print("💡 AI API 키를 설정하면:")
            print("  ✅ 더 정교한 사업모델 분석")
            print("  ✅ 구체적인 투자 논리 도출")
            print("  ✅ 정량적 밸류에이션 인사이트")
            print("  ✅ 리스크 요인 상세 분석")
            print()
            print("🚀 권장 설정:")
            print("  1. .env 파일에 ANTHROPIC_API_KEY 설정 (Claude 권장)")
            print("  2. 또는 OPENAI_API_KEY 설정 (GPT 대안)")
        else:
            print("✅ AI 기반 고도화된 분석 완료")
            print("📈 밸류에이션 엔진과 연동 준비 완료")
        
        return result
        
    except Exception as e:
        print(f"❌ 하이브리드 리서치 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='하이브리드 리서치 엔진 테스트')
    parser.add_argument('company_name', nargs='?', default='씨어스테크놀로지', help='분석할 회사명')
    parser.add_argument('--url', help='회사 웹사이트 URL')
    parser.add_argument('--anthropic-key', help='Anthropic API 키 (선택사항)')
    parser.add_argument('--openai-key', help='OpenAI API 키 (선택사항)')
    parser.add_argument('--examples', action='store_true', help='사용 예시 보기')
    
    args = parser.parse_args()
    
    if args.examples:
        print("🚀 사용 예시:")
        print()
        print("# 기본 분석 (키워드 기반)")
        print("python3 test_hybrid_research.py '씨어스테크놀로지'")
        print()
        print("# URL 지정")
        print("python3 test_hybrid_research.py '씨어스테크놀로지' --url https://seerstech.com")
        print()
        print("# AI 분석 (Anthropic Claude API 키 권장)")
        print("python3 test_hybrid_research.py '리가켐바이오' --anthropic-key sk-ant-xxx")
        print()
        print("# 또는 OpenAI API 키 사용")
        print("python3 test_hybrid_research.py '리가켐바이오' --openai-key sk-xxx")
        print()
        print("# 환경변수로 API 키 설정 (권장)")
        print("echo 'ANTHROPIC_API_KEY=sk-ant-xxx' >> .env")
        print("python3 test_hybrid_research.py '리가켐바이오'")
        print()
        print("# 다른 회사들")
        print("python3 test_hybrid_research.py '셀트리온'")
        print("python3 test_hybrid_research.py '삼성바이오로직스'")
        print("python3 test_hybrid_research.py '유한양행'")
        return
    
    # 하이브리드 리서치 실행
    result = asyncio.run(test_hybrid_research(args.company_name, args.url, args.anthropic_key, args.openai_key))
    
    print("\n" + "=" * 60)
    if result:
        if result.confidence_score >= 0.7:
            print(f"✅ {args.company_name} 하이브리드 리서치 성공!")
        else:
            print(f"⚠️ {args.company_name} 리서치 완료 - 추가 데이터 수집 권장")
        
        print()
        print("🔗 다음 단계:")
        if not args.anthropic_key and not args.openai_key:
            print("  1. .env 파일에 ANTHROPIC_API_KEY 설정으로 AI 분석 활성화")
        print("  2. 밸류에이션 엔진과 연동")
        print("  3. 실시간 뉴스 API 연결") 
        print("  4. PDF 애널리스트 리포트 자동 분석")
    else:
        print(f"❌ {args.company_name} 하이브리드 리서치 실패")

if __name__ == "__main__":
    main()