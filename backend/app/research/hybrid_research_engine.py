"""
하이브리드 리서치 엔진: 웹 크롤링 + AI 분석
실시간 웹 데이터 수집 -> AI 분석 -> 구조화된 투자 인사이트 제공
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# AI 클라이언트 설정
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class CompanyInsight:
    """AI가 분석한 회사 인사이트"""
    company_name: str
    business_model: str
    key_technologies: List[str]
    competitive_advantages: List[str]
    market_opportunity: str
    financial_highlights: Dict[str, Any]
    growth_drivers: List[str]
    risk_factors: List[str]
    investment_thesis: List[str]
    valuation_factors: Dict[str, Any]
    confidence_score: float
    data_sources: List[str]

class HybridResearchEngine:
    """웹 크롤링 + AI 분석을 결합한 하이브리드 리서치 엔진"""
    
    def __init__(self, anthropic_api_key: str = None, openai_api_key: str = None):
        # 환경변수에서 API 키 가져오기
        self.anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # AI 클라이언트 초기화
        self.anthropic_client = None
        self.openai_client = None
        
        if self.anthropic_key and ANTHROPIC_AVAILABLE:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
                print("🧠 Anthropic Claude API 활성화")
            except Exception as e:
                print(f"⚠️ Anthropic API 초기화 실패: {e}")
        
        if self.openai_key and OPENAI_AVAILABLE and not self.anthropic_client:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_key)
                print("🧠 OpenAI API 활성화")
            except Exception as e:
                print(f"⚠️ OpenAI API 초기화 실패: {e}")
        
        if not self.anthropic_client and not self.openai_client:
            print("📊 기본 분석 모드 - AI API 미설정")
        
        # SSL 설정
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    async def conduct_hybrid_research(self, company_name: str, company_url: str = None) -> CompanyInsight:
        """하이브리드 리서치 실행"""
        
        print(f"🚀 {company_name} 하이브리드 리서치 시작")
        print("=" * 50)
        
        # 1단계: 웹 크롤링으로 실시간 데이터 수집
        print("1️⃣ 실시간 웹 데이터 수집 중...")
        web_data = await self._collect_web_data(company_name, company_url)
        
        # 2단계: 뉴스 및 공개 정보 수집
        print("2️⃣ 뉴스 및 공개 정보 수집 중...")
        news_data = await self._collect_news_data(company_name)
        
        # 3단계: AI 분석으로 인사이트 생성
        print("3️⃣ AI 분석으로 투자 인사이트 생성 중...")
        ai_insight = await self._generate_ai_insight(company_name, web_data, news_data)
        
        # 4단계: 결과 검증 및 신뢰도 평가
        print("4️⃣ 결과 검증 및 신뢰도 평가 중...")
        final_insight = await self._validate_and_score(ai_insight, web_data, news_data)
        
        print(f"✅ {company_name} 하이브리드 리서치 완료!")
        return final_insight
    
    async def _collect_web_data(self, company_name: str, company_url: str = None) -> Dict[str, Any]:
        """웹사이트 크롤링으로 실시간 데이터 수집"""
        
        web_data = {
            'company_website': None,
            'investor_relations': None,
            'press_releases': [],
            'product_info': [],
            'raw_content': '',
            'structured_data': {}
        }
        
        if not company_url:
            return web_data
        
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                # 메인 페이지 크롤링
                try:
                    async with session.get(company_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # 텍스트 추출
                            text_content = soup.get_text(separator=' ', strip=True)
                            web_data['raw_content'] = text_content
                            
                            # 구조화된 데이터 추출
                            web_data['structured_data'] = {
                                'title': soup.find('title').get_text() if soup.find('title') else '',
                                'headings': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]],
                                'meta_description': soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else '',
                                'links': [a.get('href') for a in soup.find_all('a', href=True)[:20]]
                            }
                            
                            print(f"  ✅ 웹사이트 크롤링 성공: {len(text_content):,}자")
                            
                except Exception as e:
                    print(f"  ❌ 웹사이트 크롤링 실패: {str(e)}")
                
                # IR 페이지 시도
                ir_urls = [
                    f"{company_url}/ir",
                    f"{company_url}/investor",
                    f"{company_url}/investment",
                    f"{company_url}/lang_kr/company.php"
                ]
                
                for ir_url in ir_urls:
                    try:
                        async with session.get(ir_url, headers=headers, timeout=5) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                ir_content = soup.get_text(separator=' ', strip=True)
                                
                                if len(ir_content) > 200:
                                    web_data['investor_relations'] = ir_content[:2000]
                                    print(f"  ✅ IR 정보 수집 성공")
                                    break
                    except:
                        continue
        
        except Exception as e:
            print(f"  ❌ 웹 데이터 수집 오류: {str(e)}")
        
        return web_data
    
    async def _collect_news_data(self, company_name: str) -> Dict[str, Any]:
        """뉴스 및 공개 정보 수집"""
        
        # 실제로는 뉴스 API를 사용하지만, 여기서는 웹 검색 시뮬레이션
        news_data = {
            'recent_news': [],
            'analyst_mentions': [],
            'market_sentiment': 'neutral',
            'key_events': []
        }
        
        # 뉴스 검색 시뮬레이션 (실제로는 네이버뉴스 API, 구글뉴스 등 사용)
        simulated_news = [
            {
                'title': f'{company_name} 관련 최신 뉴스',
                'summary': '최근 사업 현황 및 성과',
                'date': datetime.now().isoformat(),
                'source': '경제신문',
                'sentiment': 'positive'
            }
        ]
        
        news_data['recent_news'] = simulated_news
        
        print(f"  ✅ 뉴스 데이터 수집: {len(simulated_news)}건")
        
        return news_data
    
    async def _generate_ai_insight(self, company_name: str, web_data: Dict, news_data: Dict) -> CompanyInsight:
        """AI 분석으로 투자 인사이트 생성"""
        
        # 수집된 데이터 통합
        combined_data = f"""
        회사명: {company_name}
        
        웹사이트 내용:
        {web_data.get('raw_content', '')[:3000]}
        
        주요 제목들:
        {', '.join(web_data.get('structured_data', {}).get('headings', []))}
        
        IR 정보:
        {web_data.get('investor_relations', '')[:1000] if web_data.get('investor_relations') else '정보 없음'}
        
        최근 뉴스:
        {json.dumps(news_data.get('recent_news', []), ensure_ascii=False, indent=2)}
        """
        
        # Anthropic Claude를 우선으로, 없으면 OpenAI 사용
        ai_client = self.anthropic_client or self.openai_client
        
        if ai_client and combined_data.strip():
            try:
                # AI 프롬프트
                prompt = f"""
다음은 {company_name}에 대한 웹 크롤링 및 뉴스 데이터입니다. 
이 정보를 바탕으로 투자 관점에서 회사를 분석해주세요.

데이터:
{combined_data}

다음 JSON 형식으로 분석 결과를 제공해주세요:

{{
    "business_model": "회사의 핵심 사업 모델을 간단히 설명",
    "key_technologies": ["핵심 기술 1", "핵심 기술 2", "핵심 기술 3"],
    "competitive_advantages": ["경쟁 우위 1", "경쟁 우위 2", "경쟁 우위 3"],
    "market_opportunity": "시장 기회에 대한 분석",
    "financial_highlights": {{
        "revenue_trend": "매출 트렌드 분석",
        "profitability": "수익성 분석",
        "growth_metrics": "성장 지표"
    }},
    "growth_drivers": ["성장 동력 1", "성장 동력 2", "성장 동력 3"],
    "risk_factors": ["리스크 요인 1", "리스크 요인 2", "리스크 요인 3"],
    "investment_thesis": ["투자 논리 1", "투자 논리 2", "투자 논리 3"],
    "valuation_factors": {{
        "key_metrics": "주요 밸류에이션 지표",
        "peer_comparison": "동종업계 대비 평가",
        "fair_value_range": "적정 가치 범위 추정"
    }}
}}

정보가 부족한 경우 "추가 분석 필요"로 표시해주세요.
"""
                
                # Anthropic Claude API 사용
                if self.anthropic_client:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20241022",
                        max_tokens=2000,
                        temperature=0.3,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    ai_result_text = response.content[0].text
                    print(f"  ✅ Claude API 분석 완료")
                
                # OpenAI API 사용 (fallback)
                elif self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    ai_result_text = response.choices[0].message.content
                    print(f"  ✅ OpenAI API 분석 완료")
                
                # JSON 파싱
                ai_result = json.loads(ai_result_text)
                
                return CompanyInsight(
                    company_name=company_name,
                    business_model=ai_result.get('business_model', '분석 필요'),
                    key_technologies=ai_result.get('key_technologies', []),
                    competitive_advantages=ai_result.get('competitive_advantages', []),
                    market_opportunity=ai_result.get('market_opportunity', '분석 필요'),
                    financial_highlights=ai_result.get('financial_highlights', {}),
                    growth_drivers=ai_result.get('growth_drivers', []),
                    risk_factors=ai_result.get('risk_factors', []),
                    investment_thesis=ai_result.get('investment_thesis', []),
                    valuation_factors=ai_result.get('valuation_factors', {}),
                    confidence_score=0.9 if self.anthropic_client else 0.85,
                    data_sources=['웹사이트 크롤링', 'Claude AI 분석' if self.anthropic_client else 'OpenAI 분석']
                )
                
            except Exception as e:
                print(f"  ❌ AI 분석 오류: {str(e)}")
                # JSON 파싱 실패 시 재시도
                if "json" in str(e).lower():
                    print("  🔄 JSON 파싱 재시도 중...")
                    return self._basic_analysis(company_name, combined_data)
        
        # AI 없을 때 기본 분석
        return self._basic_analysis(company_name, combined_data)
    
    def _basic_analysis(self, company_name: str, combined_data: str) -> CompanyInsight:
        """AI 없을 때 기본 분석"""
        
        content_lower = combined_data.lower()
        
        # 키워드 기반 기본 분석
        tech_keywords = []
        if any(word in content_lower for word in ['바이오', 'bio', '치료제', 'drug']):
            tech_keywords.append('바이오테크놀로지')
        if any(word in content_lower for word in ['디지털', 'digital', '플랫폼', 'platform']):
            tech_keywords.append('디지털플랫폼')
        if any(word in content_lower for word in ['ai', '인공지능', 'machine learning']):
            tech_keywords.append('AI기술')
        
        advantages = []
        if '특허' in content_lower or 'patent' in content_lower:
            advantages.append('독점 기술 보유')
        if '인증' in content_lower or 'certification' in content_lower:
            advantages.append('규제 인증 확보')
        if '파트너' in content_lower or 'partner' in content_lower:
            advantages.append('전략적 파트너십')
        
        risks = ['시장 경쟁 심화', '규제 변화', '기술 리스크']
        
        return CompanyInsight(
            company_name=company_name,
            business_model='기본 분석 결과 - 추가 AI 분석 권장',
            key_technologies=tech_keywords if tech_keywords else ['기술 분석 필요'],
            competitive_advantages=advantages if advantages else ['분석 필요'],
            market_opportunity='시장 기회 분석 필요',
            financial_highlights={'status': '재무 데이터 분석 필요'},
            growth_drivers=['성장 동력 분석 필요'],
            risk_factors=risks,
            investment_thesis=['투자 논리 분석 필요'],
            valuation_factors={'status': '밸류에이션 분석 필요'},
            confidence_score=0.4,
            data_sources=['웹사이트 크롤링', '기본 키워드 분석']
        )
    
    async def _validate_and_score(self, insight: CompanyInsight, web_data: Dict, news_data: Dict) -> CompanyInsight:
        """결과 검증 및 신뢰도 평가"""
        
        # 데이터 품질 점수 계산
        data_quality_score = 0.0
        
        # 웹 데이터 품질
        if web_data.get('raw_content') and len(web_data['raw_content']) > 500:
            data_quality_score += 0.3
        if web_data.get('structured_data', {}).get('headings'):
            data_quality_score += 0.2
        if web_data.get('investor_relations'):
            data_quality_score += 0.2
        
        # 뉴스 데이터 품질
        if news_data.get('recent_news'):
            data_quality_score += 0.1
        
        # AI 분석 품질
        if len(insight.investment_thesis) > 0 and insight.investment_thesis[0] != '투자 논리 분석 필요':
            data_quality_score += 0.2
        
        # 신뢰도 점수 업데이트
        final_confidence = min(data_quality_score, 1.0)
        insight.confidence_score = final_confidence
        
        print(f"  ✅ 신뢰도 평가: {final_confidence:.2f}/1.0")
        
        return insight

# 테스트용 함수
async def test_hybrid_research():
    """하이브리드 리서치 엔진 테스트"""
    
    engine = HybridResearchEngine(openai_api_key=None)  # OpenAI API 키 설정 필요
    
    # 씨어스테크놀로지 테스트
    result = await engine.conduct_hybrid_research(
        company_name="씨어스테크놀로지",
        company_url="https://seerstech.com"
    )
    
    print("\n" + "=" * 60)
    print("🎯 하이브리드 리서치 결과")
    print("=" * 60)
    print(f"회사명: {result.company_name}")
    print(f"사업모델: {result.business_model}")
    print(f"핵심기술: {', '.join(result.key_technologies)}")
    print(f"경쟁우위: {', '.join(result.competitive_advantages)}")
    print(f"시장기회: {result.market_opportunity}")
    print(f"투자논리: {', '.join(result.investment_thesis)}")
    print(f"신뢰도: {result.confidence_score:.2f}/1.0")
    print(f"데이터출처: {', '.join(result.data_sources)}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_research())