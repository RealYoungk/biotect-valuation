#!/usr/bin/env python3
"""
범용 회사 리서치 테스트 스크립트
사용법: python3 test_company_research.py [회사명] [웹사이트URL]
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_company_research(company_name: str, company_url: str = None):
    """범용 회사 리서치 테스트"""
    
    print(f"🔍 {company_name} 리서치 테스트 시작")
    print("=" * 60)
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from research.company_research_engine import CompanyResearchEngine
        
        # 리서치 엔진 초기화
        engine = CompanyResearchEngine(openai_api_key=None)
        
        # 웹사이트 URL이 없는 경우 자동 추측
        if not company_url:
            if "리가켐" in company_name:
                company_url = "https://www.ligachem.com"
            elif "씨어스" in company_name:
                company_url = "https://www.ceresteq.com"
            elif "셀트리온" in company_name:
                company_url = "https://www.celltrion.com"
            elif "유한양행" in company_name:
                company_url = "https://www.yuhan.co.kr"
            else:
                company_url = f"https://www.{company_name.lower().replace(' ', '')}.com"
        
        print(f"🌐 대상 웹사이트: {company_url}")
        print()
        
        # 리서치 실행
        print(f"🧬 {company_name} 리서치 수행 중...")
        result = await engine.conduct_full_research(
            company_name=company_name,
            company_url=company_url
        )
        
        print(f"✅ {company_name} 리서치 완료!")
        print()
        
        # === 기본 정보 출력 ===
        print("📊 기본 회사 정보")
        print("-" * 30)
        print(f"  • 회사명: {result.company_name}")
        print(f"  • 웹사이트: {result.website_url}")
        print(f"  • 회사 개요: {result.company_overview}")
        print(f"  • 사업 모델: {result.business_model}")
        print(f"  • 플랫폼 기술: {result.platform_technology}")
        print(f"  • 치료 분야: {', '.join(result.therapeutic_areas) if result.therapeutic_areas else '정보 수집 필요'}")
        print(f"  • 신뢰도 점수: {result.confidence_score:.2f}/1.0")
        print()
        
        # === 파이프라인 정보 ===
        if result.pipeline_assets:
            print("💊 파이프라인 현황")
            print("-" * 30)
            for i, pipeline in enumerate(result.pipeline_assets[:5], 1):
                print(f"  {i}. {pipeline.get('name', 'Unknown')}")
                print(f"     - 적응증: {pipeline.get('indication', 'N/A')}")
                print(f"     - 개발단계: {pipeline.get('phase', 'N/A')}")
                print(f"     - 타겟: {pipeline.get('target', 'N/A')}")
                if pipeline.get('description'):
                    desc = pipeline['description'][:80] + "..." if len(pipeline['description']) > 80 else pipeline['description']
                    print(f"     - 설명: {desc}")
                print()
        else:
            print("💊 파이프라인 현황: 정보 수집 필요")
            print()
        
        # === 경쟁 우위 ===
        if result.competitive_advantages:
            print("🎯 경쟁 우위")
            print("-" * 30)
            for i, advantage in enumerate(result.competitive_advantages[:5], 1):
                print(f"  {i}. {advantage}")
            print()
        
        # === 최근 뉴스 ===
        if result.recent_news:
            print("📰 최근 뉴스")
            print("-" * 30)
            for i, news in enumerate(result.recent_news[:5], 1):
                print(f"  {i}. {news.get('title', 'Unknown title')}")
                print(f"     - 출처: {news.get('source', 'N/A')}")
                print(f"     - 날짜: {news.get('date', 'N/A')}")
                print(f"     - 감정: {news.get('sentiment', 'N/A')}")
                if news.get('summary'):
                    print(f"     - 요약: {news['summary']}")
                print()
        else:
            print("📰 최근 뉴스: 정보 수집 필요")
            print()
        
        # === 투자 분석 ===
        print("💡 투자 분석")
        print("-" * 30)
        
        if result.investment_thesis:
            print("  📈 투자 논리:")
            for i, thesis in enumerate(result.investment_thesis[:5], 1):
                print(f"    {i}. {thesis}")
            print()
        
        if result.key_risks:
            print("  ⚠️ 핵심 리스크:")
            for i, risk in enumerate(result.key_risks[:5], 1):
                print(f"    {i}. {risk}")
            print()
        
        if result.short_term_catalysts:
            print("  🚀 단기 모멘텀:")
            for i, catalyst in enumerate(result.short_term_catalysts[:3], 1):
                print(f"    {i}. {catalyst}")
            print()
        
        print(f"  📊 장기 전망: {result.long_term_outlook}")
        print()
        
        # === 종합 평가 ===
        print("🎯 종합 평가")
        print("-" * 30)
        
        # 데이터 완성도 평가
        completeness_score = 0
        total_fields = 10
        
        if result.company_overview and "정보 수집 필요" not in result.company_overview:
            completeness_score += 1
        if result.platform_technology and "정보 수집 필요" not in result.platform_technology:
            completeness_score += 1
        if result.therapeutic_areas and result.therapeutic_areas != ['정보 수집 필요']:
            completeness_score += 1
        if result.pipeline_assets:
            completeness_score += 2
        if result.competitive_advantages:
            completeness_score += 1
        if result.partnerships:
            completeness_score += 1
        if result.recent_news:
            completeness_score += 1
        if result.investment_thesis:
            completeness_score += 1
        if result.key_risks:
            completeness_score += 1
        
        completeness_percentage = (completeness_score / total_fields) * 100
        
        print(f"  • 데이터 완성도: {completeness_percentage:.1f}% ({completeness_score}/{total_fields})")
        print(f"  • 분석 신뢰도: {result.confidence_score:.2f}/1.0")
        
        if completeness_percentage >= 80:
            print("  ✅ 매우 우수한 리서치 결과")
        elif completeness_percentage >= 60:
            print("  ✅ 양호한 리서치 결과")
        elif completeness_percentage >= 40:
            print("  ⚠️ 보통 수준의 리서치 결과")
        else:
            print("  ❌ 추가 데이터 수집 필요")
        
        return result
        
    except Exception as e:
        print(f"❌ {company_name} 리서치 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='회사 리서치 테스트')
    parser.add_argument('company_name', nargs='?', default='씨어스테크놀로지', help='리서치할 회사명')
    parser.add_argument('--url', help='회사 웹사이트 URL (선택사항)')
    parser.add_argument('--examples', action='store_true', help='사용 예시 보기')
    
    args = parser.parse_args()
    
    if args.examples:
        print("🚀 사용 예시:")
        print("python3 test_company_research.py '리가켐바이오'")
        print("python3 test_company_research.py '씨어스테크놀로지' --url https://www.ceresteq.com")
        print("python3 test_company_research.py '셀트리온'")
        print("python3 test_company_research.py '유한양행'")
        return
    
    # 리서치 실행
    result = asyncio.run(test_company_research(args.company_name, args.url))
    
    if result:
        print("\n" + "=" * 60)
        print(f"✅ {args.company_name} 리서치 테스트 완료!")
        print("💡 OpenAI API 키를 설정하면 더 정확한 분석이 가능합니다.")
    else:
        print("\n" + "=" * 60)
        print(f"❌ {args.company_name} 리서치 테스트 실패")

if __name__ == "__main__":
    main()