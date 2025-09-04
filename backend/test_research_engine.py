#!/usr/bin/env python3
"""
회사 리서치 엔진 테스트
"""

import sys
import os
import asyncio

# 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_company_research():
    """회사 리서치 엔진 테스트"""
    print("🔍 회사 리서치 엔진 테스트 시작\n")
    
    from research.company_research_engine import CompanyResearchEngine
    
    # 리서치 엔진 초기화 (OpenAI API 키 없이 테스트)
    engine = CompanyResearchEngine(openai_api_key=None)
    
    # 리가켐바이오 리서치 테스트
    try:
        print("🧬 리가켐바이오 리서치 수행 중...")
        
        result = await engine.conduct_full_research(
            company_name="리가켐바이오",
            company_url="https://www.ligachem.com"
        )
        
        print(f"✅ 리서치 완료!")
        print(f"\n📊 리서치 결과 요약:")
        print(f"  • 회사명: {result.company_name}")
        print(f"  • 웹사이트: {result.website_url}")
        print(f"  • 회사 개요: {result.company_overview}")
        print(f"  • 플랫폼 기술: {result.platform_technology}")
        print(f"  • 치료 분야: {', '.join(result.therapeutic_areas) if result.therapeutic_areas else '정보 수집 필요'}")
        print(f"  • 파이프라인 수: {len(result.pipeline_assets)}개")
        print(f"  • 파트너십 수: {len(result.partnerships)}개") 
        print(f"  • 최근 뉴스: {len(result.recent_news)}건")
        print(f"  • 신뢰도 점수: {result.confidence_score:.2f}/1.0")
        
        if result.pipeline_assets:
            print(f"\n💊 파이프라인 정보:")
            for i, pipeline in enumerate(result.pipeline_assets[:3], 1):
                print(f"  {i}. {pipeline.get('name', 'Unknown')}")
                print(f"     - 적응증: {pipeline.get('indication', 'Unknown')}")
                print(f"     - 개발단계: {pipeline.get('phase', 'Unknown')}")
                print(f"     - 설명: {pipeline.get('description', 'N/A')[:100]}...")
        
        if result.competitive_advantages:
            print(f"\n🎯 경쟁 우위:")
            for i, advantage in enumerate(result.competitive_advantages[:3], 1):
                print(f"  {i}. {advantage}")
        
        if result.recent_news:
            print(f"\n📰 최근 뉴스:")
            for i, news in enumerate(result.recent_news[:3], 1):
                print(f"  {i}. {news.get('title', 'Unknown title')}")
                print(f"     - 출처: {news.get('source', 'Unknown')}")
                print(f"     - 날짜: {news.get('date', 'Unknown')}")
        
        print(f"\n💡 투자 분석:")
        print(f"  • 투자 논리: {len(result.investment_thesis)}개 포인트")
        print(f"  • 핵심 리스크: {len(result.key_risks)}개 항목")
        print(f"  • 단기 모멘텀: {len(result.short_term_catalysts)}개 요인")
        print(f"  • 장기 전망: {result.long_term_outlook}")
        
        return result
        
    except Exception as e:
        print(f"❌ 리서치 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_document_analyzer():
    """문서 분석기 테스트"""
    print("\n📄 문서 분석기 테스트 시작")
    
    from research.document_analyzer import DocumentAnalysisEngine
    
    try:
        engine = DocumentAnalysisEngine(openai_api_key=None)
        
        # 샘플 텍스트로 테스트 (실제 PDF URL이 없으므로)
        sample_text = """
        리가켐바이오 투자의견 리포트
        
        목표주가: 15,000원
        투자의견: BUY
        
        투자 포인트:
        1. 독자적 ADC 플랫폼 기술 보유
        2. 다양한 타겟에 적용 가능한 링커 기술
        3. 빅파마와의 파트너십 가능성 높음
        
        주요 리스크:
        1. 임상 3상 진입 시점 불확실성
        2. ADC 시장 경쟁 심화
        3. 제조 복잡성에 따른 비용 증가
        
        매출 예측:
        2025년: 0억원 (개발 단계)
        2026년: 50억원 (라이선싱 수익)
        2027년: 200억원 (상업화 시작)
        """
        
        # 기본 분석 테스트
        from research.document_analyzer import AnalystReportAnalyzer
        analyzer = AnalystReportAnalyzer()
        
        result = await analyzer.analyze_analyst_report(sample_text, "리가켐바이오")
        
        print(f"📊 애널리스트 리포트 분석 결과:")
        print(f"  • 리포트 제목: {result.report_title}")
        print(f"  • 목표주가: {result.target_price}원" if result.target_price else "  • 목표주가: 정보 없음")
        print(f"  • 투자의견: {result.recommendation}")
        print(f"  • 밸류에이션 방법: {result.valuation_method}")
        print(f"  • 투자 논리 수: {len(result.investment_thesis)}개")
        print(f"  • 리스크 요인: {len(result.risk_factors)}개")
        print(f"  • 신뢰도: {result.confidence_score:.2f}/1.0")
        
        if result.investment_thesis:
            print(f"  💡 투자 논리:")
            for i, thesis in enumerate(result.investment_thesis[:3], 1):
                print(f"    {i}. {thesis}")
        
        return result
        
    except Exception as e:
        print(f"❌ 문서 분석 테스트 실패: {str(e)}")
        return None

async def main():
    """메인 테스트 실행"""
    print("🧪 AI 기반 회사 리서치 시스템 테스트")
    print("=" * 60)
    
    # 회사 리서치 테스트
    research_result = await test_company_research()
    
    # 문서 분석 테스트  
    document_result = await test_document_analyzer()
    
    print("\n" + "=" * 60)
    if research_result and document_result:
        print("✅ 모든 리서치 모듈 테스트 성공!")
        print("\n🎯 다음 단계:")
        print("  1. OpenAI API 키 설정으로 정확도 향상")
        print("  2. 실제 PDF 문서 URL로 테스트")
        print("  3. 뉴스 API 연동으로 실시간 정보 수집")
        print("  4. 유튜브 IR 영상 분석 추가")
        print("  5. 벨류에이션 엔진과 통합")
    else:
        print("❌ 일부 테스트 실패 - 디버깅 필요")

if __name__ == "__main__":
    asyncio.run(main())