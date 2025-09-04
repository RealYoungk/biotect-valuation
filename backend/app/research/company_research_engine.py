from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import openai
from urllib.parse import urljoin, urlparse
import re

@dataclass
class CompanyResearchResult:
    """회사 리서치 결과"""
    company_name: str
    website_url: str
    
    # 기본 정보
    company_overview: str
    business_model: str
    key_executives: List[Dict[str, str]]
    
    # 파이프라인 정보
    pipeline_assets: List[Dict[str, Any]]
    platform_technology: str
    therapeutic_areas: List[str]
    
    # 재무 정보
    financial_highlights: Dict[str, Any]
    cash_position: Optional[float]
    recent_funding: List[Dict[str, Any]]
    
    # 파트너십 및 협업
    partnerships: List[Dict[str, Any]]
    licensing_deals: List[Dict[str, Any]]
    
    # 투자 포인트
    investment_thesis: List[str]
    key_catalysts: List[str]
    competitive_advantages: List[str]
    
    # 리스크 요소
    key_risks: List[str]
    competitive_threats: List[str]
    
    # 뉴스 및 모멘텀
    recent_news: List[Dict[str, Any]]
    short_term_catalysts: List[str]
    long_term_outlook: str
    
    # 메타데이터
    research_date: datetime
    data_sources: List[str]
    confidence_score: float

class CompanyWebCrawler:
    """회사 홈페이지 크롤링"""
    
    def __init__(self):
        self.session = None
        self.max_pages = 10  # 크롤링할 최대 페이지 수
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def crawl_company_website(self, company_url: str) -> Dict[str, Any]:
        """회사 홈페이지 크롤링"""
        try:
            # 메인 페이지 크롤링
            main_content = await self._fetch_page(company_url)
            
            # 주요 섹션 URL 찾기
            important_urls = await self._find_important_urls(company_url, main_content)
            
            # 각 섹션별 크롤링
            all_content = {"main": main_content}
            for section, url in important_urls.items():
                content = await self._fetch_page(url)
                all_content[section] = content
                
            return all_content
            
        except Exception as e:
            print(f"웹사이트 크롤링 오류: {str(e)}")
            return {}
    
    async def _fetch_page(self, url: str) -> str:
        """개별 페이지 크롤링"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 불필요한 요소 제거
                    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                        tag.decompose()
                    
                    # 텍스트 추출
                    text = soup.get_text()
                    # 정리
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text[:10000]  # 10KB 제한
                else:
                    return ""
        except:
            return ""
    
    async def _find_important_urls(self, base_url: str, main_content: str) -> Dict[str, str]:
        """중요한 섹션 URL 찾기"""
        important_urls = {}
        
        # 일반적인 중요 섹션들
        sections = {
            "pipeline": ["pipeline", "products", "development", "연구개발", "파이프라인"],
            "technology": ["technology", "platform", "science", "기술", "플랫폼"],
            "investor": ["investor", "ir", "투자자", "투자정보"],
            "news": ["news", "press", "media", "뉴스", "보도자료"],
            "about": ["about", "company", "회사소개", "기업정보"]
        }
        
        try:
            async with self.session.get(base_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                for section, keywords in sections.items():
                    for link in soup.find_all('a', href=True):
                        href = link['href'].lower()
                        text = link.get_text().lower()
                        
                        if any(keyword in href or keyword in text for keyword in keywords):
                            full_url = urljoin(base_url, link['href'])
                            important_urls[section] = full_url
                            break
        except:
            pass
            
        return important_urls

class LLMDataExtractor:
    """LLM 기반 데이터 추출"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
    
    def extract_company_information(self, company_name: str, web_content: Dict[str, str]) -> Dict[str, Any]:
        """웹사이트 내용에서 구조화된 회사 정보 추출"""
        
        # 모든 컨텐츠 합치기
        full_content = ""
        for section, content in web_content.items():
            full_content += f"\n\n=== {section.upper()} ===\n{content}"
        
        # LLM 프롬프트
        prompt = f"""
다음은 {company_name} 회사 웹사이트의 내용입니다. 이 정보를 분석해서 구조화된 JSON 형태로 정리해주세요.

웹사이트 내용:
{full_content[:8000]}  # 토큰 제한

다음 형식으로 정보를 추출해주세요:

{{
    "company_overview": "회사 개요 (2-3문장)",
    "business_model": "비즈니스 모델 설명",
    "platform_technology": "핵심 플랫폼 기술",
    "therapeutic_areas": ["치료 분야1", "치료 분야2"],
    "pipeline_assets": [
        {{
            "name": "파이프라인명",
            "indication": "적응증",
            "phase": "개발단계",
            "target": "타겟",
            "description": "설명"
        }}
    ],
    "key_executives": [
        {{
            "name": "이름",
            "title": "직책",
            "background": "경력"
        }}
    ],
    "competitive_advantages": ["경쟁우위1", "경쟁우위2"],
    "partnerships": [
        {{
            "partner": "파트너사",
            "type": "협업 유형",
            "description": "협업 내용"
        }}
    ],
    "investment_highlights": ["투자 포인트1", "투자 포인트2"],
    "recent_achievements": ["최근 성과1", "최근 성과2"]
}}

정보가 명확하지 않은 항목은 빈 배열이나 "정보 없음"으로 표시해주세요.
"""

        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                return eval(response.choices[0].message.content)  # JSON 파싱
            else:
                # LLM이 없을 때는 기본 파싱
                return self._basic_extraction(company_name, web_content)
        except Exception as e:
            print(f"LLM 추출 오류: {str(e)}")
            return self._basic_extraction(company_name, web_content)
    
    def _basic_extraction(self, company_name: str, web_content: Dict[str, str]) -> Dict[str, Any]:
        """기본적인 규칙 기반 추출 (LLM 없을 때)"""
        return {
            "company_overview": f"{company_name}에 대한 정보를 수집했습니다.",
            "business_model": "바이오텍 기업",
            "platform_technology": "정보 수집 필요",
            "therapeutic_areas": ["정보 수집 필요"],
            "pipeline_assets": [],
            "key_executives": [],
            "competitive_advantages": [],
            "partnerships": [],
            "investment_highlights": [],
            "recent_achievements": []
        }

class NewsCollector:
    """뉴스 및 언론 보도 수집"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def collect_company_news(self, company_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """회사 관련 뉴스 수집"""
        news_list = []
        
        # 여러 뉴스 소스에서 수집
        sources = [
            self._collect_from_naver_news,
            self._collect_from_google_news,
            # self._collect_from_bioworld_news  # 바이오 전문 뉴스
        ]
        
        for source_func in sources:
            try:
                source_news = await source_func(company_name, days)
                news_list.extend(source_news)
            except Exception as e:
                print(f"뉴스 수집 오류 ({source_func.__name__}): {str(e)}")
                continue
        
        # 중복 제거 및 정렬
        news_list = self._deduplicate_news(news_list)
        news_list.sort(key=lambda x: x.get('date', datetime.now()), reverse=True)
        
        return news_list[:20]  # 최신 20개
    
    async def _collect_from_naver_news(self, company_name: str, days: int) -> List[Dict[str, Any]]:
        """네이버 뉴스 수집 (예시)"""
        # 실제로는 네이버 뉴스 API나 크롤링 구현
        return [
            {
                "title": f"{company_name} 관련 뉴스 예시",
                "summary": "뉴스 요약",
                "url": "https://example.com/news1",
                "source": "네이버뉴스",
                "date": datetime.now(),
                "sentiment": "neutral"
            }
        ]
    
    async def _collect_from_google_news(self, company_name: str, days: int) -> List[Dict[str, Any]]:
        """구글 뉴스 수집 (예시)"""
        # 실제로는 Google News API 구현
        return []
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """뉴스 중복 제거"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title_key = news.get('title', '').lower().strip()
            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news

class CompanyResearchEngine:
    """종합 회사 리서치 엔진"""
    
    def __init__(self, openai_api_key: str = None):
        self.llm_extractor = LLMDataExtractor(openai_api_key)
        
    async def conduct_full_research(self, company_name: str, company_url: str) -> CompanyResearchResult:
        """종합적인 회사 리서치 수행"""
        
        print(f"🔍 {company_name} 리서치 시작...")
        
        # 1. 웹사이트 크롤링
        print("1️⃣ 웹사이트 크롤링 중...")
        async with CompanyWebCrawler() as crawler:
            web_content = await crawler.crawl_company_website(company_url)
        
        # 2. LLM으로 정보 추출
        print("2️⃣ AI 정보 추출 중...")
        extracted_info = self.llm_extractor.extract_company_information(company_name, web_content)
        
        # 3. 뉴스 수집
        print("3️⃣ 뉴스 수집 중...")
        async with NewsCollector() as collector:
            recent_news = await collector.collect_company_news(company_name)
        
        # 4. 투자 포인트 분석
        print("4️⃣ 투자 분석 중...")
        investment_analysis = self._analyze_investment_points(extracted_info, recent_news)
        
        # 5. 결과 통합
        result = CompanyResearchResult(
            company_name=company_name,
            website_url=company_url,
            company_overview=extracted_info.get('company_overview', ''),
            business_model=extracted_info.get('business_model', ''),
            key_executives=extracted_info.get('key_executives', []),
            pipeline_assets=extracted_info.get('pipeline_assets', []),
            platform_technology=extracted_info.get('platform_technology', ''),
            therapeutic_areas=extracted_info.get('therapeutic_areas', []),
            financial_highlights={},  # 별도 구현 필요
            cash_position=None,
            recent_funding=[],
            partnerships=extracted_info.get('partnerships', []),
            licensing_deals=[],
            investment_thesis=investment_analysis['investment_thesis'],
            key_catalysts=investment_analysis['key_catalysts'],
            competitive_advantages=extracted_info.get('competitive_advantages', []),
            key_risks=investment_analysis['key_risks'],
            competitive_threats=[],
            recent_news=recent_news,
            short_term_catalysts=investment_analysis['short_term_catalysts'],
            long_term_outlook=investment_analysis['long_term_outlook'],
            research_date=datetime.now(),
            data_sources=[company_url, "뉴스 소스"],
            confidence_score=0.7  # 데이터 품질에 따라 조정
        )
        
        print(f"✅ {company_name} 리서치 완료!")
        return result
    
    def _analyze_investment_points(self, extracted_info: Dict, recent_news: List) -> Dict[str, Any]:
        """투자 포인트 분석"""
        
        # 기본 투자 분석 (실제로는 더 정교한 LLM 분석)
        investment_thesis = extracted_info.get('investment_highlights', [])
        if not investment_thesis:
            investment_thesis = ["자동 분석된 투자 포인트 필요"]
        
        # 뉴스 기반 단기 모멘텀
        short_term_catalysts = []
        for news in recent_news[:5]:  # 최신 5개 뉴스
            if any(keyword in news.get('title', '').lower() 
                   for keyword in ['승인', '허가', '파트너십', '투자', '임상', '결과']):
                short_term_catalysts.append(f"최근 뉴스: {news.get('title', '')[:50]}...")
        
        return {
            'investment_thesis': investment_thesis,
            'key_catalysts': extracted_info.get('recent_achievements', []),
            'key_risks': ['임상 실패 리스크', '경쟁 심화', '자금 조달 리스크'],  # 기본 리스크
            'short_term_catalysts': short_term_catalysts,
            'long_term_outlook': '바이오텍 업계의 전반적인 성장세를 고려할 때 긍정적'
        }

# 사용 예시 함수
async def research_ligachem_bio():
    """리가켐바이오 리서치 예시"""
    
    engine = CompanyResearchEngine(openai_api_key=None)  # API 키 설정 필요
    
    result = await engine.conduct_full_research(
        company_name="리가켐바이오",
        company_url="https://www.ligachem.com"
    )
    
    return result

if __name__ == "__main__":
    # 테스트 실행
    import asyncio
    result = asyncio.run(research_ligachem_bio())
    print(f"리서치 결과: {result.company_overview}")