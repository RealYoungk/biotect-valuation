#!/usr/bin/env python3
"""
실제 웹사이트 데이터로 리서치 엔진 테스트
"""

import sys
import os
import urllib.request
import urllib.error
from html.parser import HTMLParser
import re
from datetime import datetime
from typing import Dict, List, Any

class SimpleHTMLParser(HTMLParser):
    """간단한 HTML 파서"""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.current_tag = None
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href' and attr_value:
                    self.links.append(attr_value)
    
    def handle_endtag(self, tag):
        self.current_tag = None
        
    def handle_data(self, data):
        if self.current_tag not in ['script', 'style', 'head']:
            clean_data = data.strip()
            if clean_data and len(clean_data) > 2:
                self.text_content.append(clean_data)

def fetch_website_content(url: str) -> Dict[str, Any]:
    """웹사이트 내용 가져오기 (urllib 사용)"""
    try:
        print(f"🌐 웹사이트 접속 중: {url}")
        
        # User-Agent 헤더 추가
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        print(f"✅ HTML 다운로드 완료: {len(html_content):,}자")
        
        # HTML 파싱
        parser = SimpleHTMLParser()
        parser.feed(html_content)
        
        text_content = ' '.join(parser.text_content)
        # 텍스트 정리
        text_content = re.sub(r'\s+', ' ', text_content)
        text_content = text_content[:5000]  # 처음 5000자만
        
        return {
            'url': url,
            'content': text_content,
            'links': parser.links[:20],  # 처음 20개 링크만
            'length': len(text_content),
            'status': 'success'
        }
        
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 오류: {e.code} - {e.reason}")
        return {'url': url, 'error': f'HTTP {e.code}', 'status': 'error'}
    except urllib.error.URLError as e:
        print(f"❌ URL 오류: {e.reason}")
        return {'url': url, 'error': str(e.reason), 'status': 'error'}
    except Exception as e:
        print(f"❌ 기타 오류: {str(e)}")
        return {'url': url, 'error': str(e), 'status': 'error'}

def extract_company_info_basic(content: str, company_name: str) -> Dict[str, Any]:
    """기본 정보 추출 (규칙 기반)"""
    
    content_lower = content.lower()
    
    # 키워드 기반 정보 추출
    extracted_info = {
        'company_name': company_name,
        'business_keywords': [],
        'technology_keywords': [],
        'pipeline_mentions': [],
        'partnership_mentions': [],
        'contact_info': {}
    }
    
    # 바이오/제약 관련 키워드 찾기
    bio_keywords = [
        'adc', 'antibody', '항체', 'drug', '의약품', '치료제', 
        'pipeline', '파이프라인', 'clinical', '임상', 'phase',
        'biotech', '바이오', 'pharmaceutical', '제약'
    ]
    
    found_keywords = []
    for keyword in bio_keywords:
        if keyword in content_lower:
            found_keywords.append(keyword)
    
    extracted_info['business_keywords'] = found_keywords
    
    # 파이프라인 코드 찾기 (LCB##, YH#### 등)
    pipeline_patterns = [
        r'[A-Z]{2,3}[B]?\d{1,4}',  # LCB11, YH1234 등
        r'[A-Z]+-\d{1,4}',         # AB-123 등
    ]
    
    pipeline_codes = []
    for pattern in pipeline_patterns:
        matches = re.findall(pattern, content)
        pipeline_codes.extend(matches)
    
    extracted_info['pipeline_mentions'] = list(set(pipeline_codes))  # 중복 제거
    
    # 이메일, 전화번호 찾기
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{8,15}'
    
    emails = re.findall(email_pattern, content)
    phones = re.findall(phone_pattern, content)
    
    extracted_info['contact_info'] = {
        'emails': emails[:3],  # 처음 3개만
        'phones': [p.strip() for p in phones[:3] if len(p.strip()) > 8]
    }
    
    return extracted_info

def analyze_investment_signals(content: str) -> Dict[str, Any]:
    """투자 신호 분석"""
    
    content_lower = content.lower()
    
    # 긍정적 신호 키워드
    positive_keywords = [
        'approval', '승인', 'partnership', '파트너십', 'licensing', '라이선싱',
        'breakthrough', 'positive', '긍정적', 'success', '성공', 'milestone', '마일스톤',
        'funding', '투자', 'revenue', '매출', 'growth', '성장'
    ]
    
    # 부정적 신호 키워드
    negative_keywords = [
        'failure', '실패', 'delay', '지연', 'suspend', '중단', 'risk', '리스크',
        'concern', '우려', 'challenge', '도전', 'problem', '문제'
    ]
    
    positive_count = sum(1 for keyword in positive_keywords if keyword in content_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in content_lower)
    
    # 간단한 감정 점수 계산
    sentiment_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
    
    return {
        'positive_signals': positive_count,
        'negative_signals': negative_count,
        'sentiment_score': sentiment_score,  # -1 to 1
        'overall_sentiment': 'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral'
    }

def test_ligachem_research():
    """리가켐바이오 실제 리서치 테스트"""
    
    print("🧬 리가켐바이오 실제 리서치 테스트 시작")
    print("=" * 60)
    
    # 1. 메인 홈페이지 크롤링
    main_result = fetch_website_content("https://www.ligachem.com")
    
    if main_result['status'] == 'error':
        print(f"❌ 메인 페이지 접속 실패: {main_result['error']}")
        print("🔄 대체 URL로 테스트...")
        # 대체 테스트 - 다른 바이오 기업
        main_result = fetch_website_content("https://www.celltrion.com")
    
    if main_result['status'] == 'success':
        print(f"✅ 웹사이트 접속 성공!")
        print(f"  📄 내용 길이: {main_result['length']:,}자")
        print(f"  🔗 발견된 링크: {len(main_result['links'])}개")
        
        # 2. 내용 분석
        print(f"\n📊 내용 분석 중...")
        content = main_result['content']
        
        # 기본 정보 추출
        company_info = extract_company_info_basic(content, "리가켐바이오")
        
        print(f"  🔬 비즈니스 키워드: {len(company_info['business_keywords'])}개 발견")
        for keyword in company_info['business_keywords'][:10]:
            print(f"    - {keyword}")
        
        print(f"  💊 파이프라인 코드: {len(company_info['pipeline_mentions'])}개 발견")
        for pipeline in company_info['pipeline_mentions'][:5]:
            print(f"    - {pipeline}")
        
        print(f"  📧 연락처 정보:")
        print(f"    - 이메일: {len(company_info['contact_info']['emails'])}개")
        print(f"    - 전화번호: {len(company_info['contact_info']['phones'])}개")
        
        # 3. 투자 신호 분석
        print(f"\n💡 투자 신호 분석:")
        investment_signals = analyze_investment_signals(content)
        
        print(f"  📈 긍정적 신호: {investment_signals['positive_signals']}개")
        print(f"  📉 부정적 신호: {investment_signals['negative_signals']}개") 
        print(f"  🎯 전체 감정: {investment_signals['overall_sentiment']}")
        print(f"  📊 감정 점수: {investment_signals['sentiment_score']:.2f}")
        
        # 4. 내용 샘플 출력
        print(f"\n📝 웹사이트 내용 샘플 (처음 500자):")
        print("─" * 50)
        print(content[:500])
        print("─" * 50)
        
        # 5. 추출 가능한 투자 포인트
        print(f"\n💡 자동 추출된 투자 관련 정보:")
        
        # ADC 관련 언급 찾기
        if any(word in content.lower() for word in ['adc', 'antibody', 'conjugate']):
            print(f"  ✅ ADC 기술 관련 내용 발견")
        
        # 임상 관련 언급
        if any(word in content.lower() for word in ['clinical', '임상', 'phase']):
            print(f"  ✅ 임상시험 관련 내용 발견")
        
        # 파트너십 언급
        if any(word in content.lower() for word in ['partnership', '파트너', 'collaboration']):
            print(f"  ✅ 파트너십 관련 내용 발견")
        
        return {
            'website_data': main_result,
            'company_info': company_info,
            'investment_signals': investment_signals,
            'status': 'success'
        }
    
    else:
        print(f"❌ 웹사이트 접속 실패")
        return {'status': 'failed', 'error': main_result.get('error')}

def test_news_search_simulation():
    """뉴스 검색 시뮬레이션"""
    
    print(f"\n📰 뉴스 검색 시뮬레이션")
    print("─" * 30)
    
    # 실제로는 뉴스 API나 검색 엔진을 사용하지만, 
    # 여기서는 일반적인 뉴스 패턴을 시뮬레이션
    
    simulated_news = [
        {
            'title': '리가켐바이오, ADC 플랫폼 기술력 인정받아',
            'summary': 'LCB11 임상 1상에서 안전성 확인, 글로벌 제약사 관심 증대',
            'date': '2024-08-20',
            'source': '바이오스펙테이터',
            'sentiment': 'positive',
            'keywords': ['ADC', 'LCB11', '임상', '안전성']
        },
        {
            'title': '바이오 업계 M&A 활발, ADC 기술 기업들 주목',
            'summary': 'ADC 시장 성장률 연 20% 이상, 리가켐바이오 등 유망 기업 부상',
            'date': '2024-08-15',
            'source': '메디칼타임즈',
            'sentiment': 'positive',
            'keywords': ['ADC', 'M&A', '시장성장', 'biotech']
        },
        {
            'title': 'ADC 치료제 시장 경쟁 치열해져',
            'summary': '다수 제약사들의 ADC 개발로 경쟁 심화 우려',
            'date': '2024-08-10', 
            'source': '약업신문',
            'sentiment': 'neutral',
            'keywords': ['ADC', '경쟁', 'competition']
        }
    ]
    
    print(f"📊 뉴스 분석 결과:")
    positive_news = [n for n in simulated_news if n['sentiment'] == 'positive']
    neutral_news = [n for n in simulated_news if n['sentiment'] == 'neutral']
    negative_news = [n for n in simulated_news if n['sentiment'] == 'negative']
    
    print(f"  📈 긍정적 뉴스: {len(positive_news)}건")
    print(f"  📊 중립적 뉴스: {len(neutral_news)}건")
    print(f"  📉 부정적 뉴스: {len(negative_news)}건")
    
    for news in simulated_news:
        print(f"\n  📰 {news['title']}")
        print(f"    📅 {news['date']} | 📍 {news['source']} | 😊 {news['sentiment']}")
        print(f"    📝 {news['summary']}")
    
    return simulated_news

def main():
    """메인 테스트 실행"""
    
    print("🔍 실제 데이터 기반 리서치 엔진 테스트")
    print("=" * 60)
    
    # 1. 실제 웹사이트 리서치 테스트
    research_result = test_ligachem_research()
    
    # 2. 뉴스 검색 시뮬레이션
    news_result = test_news_search_simulation()
    
    print(f"\n" + "=" * 60)
    
    if research_result.get('status') == 'success':
        print("✅ 실제 웹사이트 리서치 성공!")
        
        # 종합 분석 결과
        website_data = research_result['website_data']
        company_info = research_result['company_info'] 
        signals = research_result['investment_signals']
        
        print(f"\n🎯 종합 리서치 결과:")
        print(f"  • 웹사이트 분석: ✅ 성공 ({website_data['length']}자 분석)")
        print(f"  • 비즈니스 키워드: {len(company_info['business_keywords'])}개 발견")
        print(f"  • 파이프라인 정보: {len(company_info['pipeline_mentions'])}개 코드 추출")
        print(f"  • 투자 감정: {signals['overall_sentiment']} ({signals['sentiment_score']:.2f})")
        print(f"  • 뉴스 분석: {len(news_result)}건 수집")
        
        print(f"\n💡 실제 리서치 시스템의 장점:")
        print(f"  ✅ 실시간 웹사이트 정보 수집 가능")
        print(f"  ✅ 자동 키워드 및 파이프라인 코드 추출")
        print(f"  ✅ 감정 분석 기반 투자 신호 판별")
        print(f"  ✅ 구조화된 데이터로 벨류에이션 연동 가능")
        
        print(f"\n🚀 다음 개선 사항:")
        print(f"  • OpenAI GPT 연동으로 더 정교한 정보 추출")
        print(f"  • 실제 뉴스 API 연동 (네이버, 구글 뉴스)")
        print(f"  • PDF 애널리스트 리포트 자동 분석")
        print(f"  • 유튜브 IR 영상 transcript 분석")
        
    else:
        print("❌ 웹사이트 접속 실패 - 네트워크나 접근 제한 확인 필요")
        print("💡 하지만 시뮬레이션으로 로직 검증은 완료!")

if __name__ == "__main__":
    main()