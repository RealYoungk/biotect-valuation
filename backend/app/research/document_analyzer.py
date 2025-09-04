from dataclasses import dataclass
from typing import Dict, List, Any, Optional, BinaryIO
import asyncio
import aiohttp
import PyPDF2
import openai
from datetime import datetime
import re
import io

@dataclass
class AnalystReportData:
    """애널리스트 리포트 분석 결과"""
    report_title: str
    analyst_firm: str
    analyst_name: str
    publish_date: datetime
    target_price: Optional[float]
    recommendation: str  # Buy, Hold, Sell
    
    # 핵심 내용
    investment_thesis: List[str]
    key_assumptions: Dict[str, Any]
    valuation_method: str
    risk_factors: List[str]
    
    # 재무 예측
    revenue_forecast: Dict[int, float]  # {년도: 매출}
    pipeline_valuation: Dict[str, float]  # {파이프라인: 가치}
    
    # 메타데이터
    confidence_score: float
    extracted_text: str

@dataclass
class IRDocumentData:
    """IR 문서 분석 결과"""
    document_type: str  # "IR presentation", "Annual report", etc
    company_name: str
    document_date: datetime
    
    # 사업 현황
    business_updates: List[str]
    pipeline_progress: List[Dict[str, Any]]
    financial_highlights: Dict[str, Any]
    
    # 전략 및 계획
    strategic_priorities: List[str]
    upcoming_catalysts: List[str]
    guidance_updates: Dict[str, Any]
    
    # 리스크 및 기회
    opportunities: List[str]
    challenges: List[str]
    
    confidence_score: float

class PDFDocumentProcessor:
    """PDF 문서 처리기"""
    
    def __init__(self):
        self.max_text_length = 50000  # 최대 텍스트 길이
    
    def extract_text_from_pdf(self, pdf_file: BinaryIO) -> str:
        """PDF에서 텍스트 추출"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            
            for page_num in range(min(len(pdf_reader.pages), 50)):  # 최대 50페이지
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            # 텍스트 정리
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return text_content[:self.max_text_length]
        
        except Exception as e:
            print(f"PDF 텍스트 추출 오류: {str(e)}")
            return ""
    
    async def extract_text_from_url(self, pdf_url: str) -> str:
        """URL에서 PDF 다운로드 후 텍스트 추출"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        pdf_content = await response.read()
                        pdf_file = io.BytesIO(pdf_content)
                        return self.extract_text_from_pdf(pdf_file)
            return ""
        except Exception as e:
            print(f"PDF URL 처리 오류: {str(e)}")
            return ""

class AnalystReportAnalyzer:
    """애널리스트 리포트 분석기"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.pdf_processor = PDFDocumentProcessor()
    
    async def analyze_analyst_report(self, pdf_content: str, company_name: str) -> AnalystReportData:
        """애널리스트 리포트 분석"""
        
        if not pdf_content.strip():
            return self._create_empty_report(company_name)
        
        # LLM 분석 프롬프트
        prompt = f"""
다음은 {company_name}에 대한 애널리스트 리포트 내용입니다. 이 리포트를 분석해서 구조화된 정보를 추출해주세요.

리포트 내용:
{pdf_content[:6000]}

다음 형식으로 정보를 추출해주세요:

{{
    "report_title": "리포트 제목",
    "analyst_firm": "분석기관명",
    "analyst_name": "애널리스트 이름",
    "target_price": 목표주가_숫자_또는_null,
    "recommendation": "Buy/Hold/Sell 중 하나",
    "investment_thesis": [
        "투자 논리 1",
        "투자 논리 2",
        "투자 논리 3"
    ],
    "key_assumptions": {{
        "피크매출_추정": "금액 또는 설명",
        "성공확률": "확률 또는 설명",
        "상업화_시점": "년도 또는 설명"
    }},
    "valuation_method": "사용된 밸류에이션 방법 (DCF, Multiple 등)",
    "risk_factors": [
        "주요 리스크 1",
        "주요 리스크 2",
        "주요 리스크 3"
    ],
    "revenue_forecast": {{
        "2025": 매출예상_또는_0,
        "2026": 매출예상_또는_0,
        "2027": 매출예상_또는_0
    }},
    "pipeline_valuation": {{
        "파이프라인1": 가치추정_또는_0,
        "파이프라인2": 가치추정_또는_0
    }}
}}

숫자는 숫자형으로, 정보가 없는 경우 null이나 0으로 표시해주세요.
"""
        
        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                extracted_data = eval(response.choices[0].message.content)
                
                return AnalystReportData(
                    report_title=extracted_data.get('report_title', 'Unknown Report'),
                    analyst_firm=extracted_data.get('analyst_firm', 'Unknown Firm'),
                    analyst_name=extracted_data.get('analyst_name', 'Unknown Analyst'),
                    publish_date=datetime.now(),  # 실제로는 문서에서 추출
                    target_price=extracted_data.get('target_price'),
                    recommendation=extracted_data.get('recommendation', 'Hold'),
                    investment_thesis=extracted_data.get('investment_thesis', []),
                    key_assumptions=extracted_data.get('key_assumptions', {}),
                    valuation_method=extracted_data.get('valuation_method', 'Unknown'),
                    risk_factors=extracted_data.get('risk_factors', []),
                    revenue_forecast=extracted_data.get('revenue_forecast', {}),
                    pipeline_valuation=extracted_data.get('pipeline_valuation', {}),
                    confidence_score=0.8,
                    extracted_text=pdf_content[:1000]
                )
            else:
                return self._basic_analysis(pdf_content, company_name)
                
        except Exception as e:
            print(f"애널리스트 리포트 분석 오류: {str(e)}")
            return self._create_empty_report(company_name)
    
    def _basic_analysis(self, pdf_content: str, company_name: str) -> AnalystReportData:
        """기본 규칙 기반 분석 (LLM 없을 때)"""
        
        # 간단한 키워드 매칭
        target_price_match = re.search(r'목표주?가[:\s]*([0-9,]+)', pdf_content)
        target_price = None
        if target_price_match:
            target_price = float(target_price_match.group(1).replace(',', ''))
        
        # 추천 등급 찾기
        recommendation = "Hold"
        if any(word in pdf_content.lower() for word in ['buy', '매수', '적극매수']):
            recommendation = "Buy"
        elif any(word in pdf_content.lower() for word in ['sell', '매도']):
            recommendation = "Sell"
        
        return AnalystReportData(
            report_title=f"{company_name} 분석 리포트",
            analyst_firm="Unknown",
            analyst_name="Unknown",
            publish_date=datetime.now(),
            target_price=target_price,
            recommendation=recommendation,
            investment_thesis=["기본 분석 필요"],
            key_assumptions={},
            valuation_method="Unknown",
            risk_factors=["상세 분석 필요"],
            revenue_forecast={},
            pipeline_valuation={},
            confidence_score=0.3,
            extracted_text=pdf_content[:1000]
        )
    
    def _create_empty_report(self, company_name: str) -> AnalystReportData:
        """빈 리포트 생성"""
        return AnalystReportData(
            report_title=f"{company_name} - 분석 필요",
            analyst_firm="Unknown",
            analyst_name="Unknown", 
            publish_date=datetime.now(),
            target_price=None,
            recommendation="Hold",
            investment_thesis=[],
            key_assumptions={},
            valuation_method="Unknown",
            risk_factors=[],
            revenue_forecast={},
            pipeline_valuation={},
            confidence_score=0.0,
            extracted_text=""
        )

class IRDocumentAnalyzer:
    """IR 문서 분석기"""
    
    def __init__(self, openai_api_key: str = None):
        self.client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.pdf_processor = PDFDocumentProcessor()
    
    async def analyze_ir_document(self, pdf_content: str, company_name: str, doc_type: str = "IR Document") -> IRDocumentData:
        """IR 문서 분석"""
        
        if not pdf_content.strip():
            return self._create_empty_ir_doc(company_name, doc_type)
        
        prompt = f"""
다음은 {company_name}의 {doc_type} 내용입니다. IR 관점에서 핵심 정보를 추출해주세요.

문서 내용:
{pdf_content[:6000]}

다음 형식으로 정보를 추출해주세요:

{{
    "business_updates": [
        "주요 사업 업데이트 1",
        "주요 사업 업데이트 2"
    ],
    "pipeline_progress": [
        {{
            "name": "파이프라인명",
            "phase": "개발단계",
            "progress": "진행상황",
            "timeline": "예상 일정"
        }}
    ],
    "financial_highlights": {{
        "revenue": "매출 정보",
        "cash_position": "현금 보유",
        "funding": "자금 조달 현황"
    }},
    "strategic_priorities": [
        "전략 우선순위 1",
        "전략 우선순위 2"
    ],
    "upcoming_catalysts": [
        "예정된 중요 이벤트 1",
        "예정된 중요 이벤트 2"
    ],
    "guidance_updates": {{
        "revenue_guidance": "매출 가이던스",
        "milestone_guidance": "마일스톤 가이던스"
    }},
    "opportunities": [
        "성장 기회 1",
        "성장 기회 2"
    ],
    "challenges": [
        "도전과제 1", 
        "도전과제 2"
    ]
}}
"""
        
        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                extracted_data = eval(response.choices[0].message.content)
                
                return IRDocumentData(
                    document_type=doc_type,
                    company_name=company_name,
                    document_date=datetime.now(),
                    business_updates=extracted_data.get('business_updates', []),
                    pipeline_progress=extracted_data.get('pipeline_progress', []),
                    financial_highlights=extracted_data.get('financial_highlights', {}),
                    strategic_priorities=extracted_data.get('strategic_priorities', []),
                    upcoming_catalysts=extracted_data.get('upcoming_catalysts', []),
                    guidance_updates=extracted_data.get('guidance_updates', {}),
                    opportunities=extracted_data.get('opportunities', []),
                    challenges=extracted_data.get('challenges', []),
                    confidence_score=0.8
                )
            else:
                return self._basic_ir_analysis(pdf_content, company_name, doc_type)
                
        except Exception as e:
            print(f"IR 문서 분석 오류: {str(e)}")
            return self._create_empty_ir_doc(company_name, doc_type)
    
    def _basic_ir_analysis(self, pdf_content: str, company_name: str, doc_type: str) -> IRDocumentData:
        """기본 IR 분석"""
        return IRDocumentData(
            document_type=doc_type,
            company_name=company_name,
            document_date=datetime.now(),
            business_updates=["기본 분석 필요"],
            pipeline_progress=[],
            financial_highlights={},
            strategic_priorities=["상세 분석 필요"],
            upcoming_catalysts=["분석 필요"],
            guidance_updates={},
            opportunities=["기회 분석 필요"],
            challenges=["리스크 분석 필요"],
            confidence_score=0.3
        )
    
    def _create_empty_ir_doc(self, company_name: str, doc_type: str) -> IRDocumentData:
        """빈 IR 문서 생성"""
        return IRDocumentData(
            document_type=doc_type,
            company_name=company_name,
            document_date=datetime.now(),
            business_updates=[],
            pipeline_progress=[],
            financial_highlights={},
            strategic_priorities=[],
            upcoming_catalysts=[],
            guidance_updates={},
            opportunities=[],
            challenges=[],
            confidence_score=0.0
        )

class DocumentAnalysisEngine:
    """문서 분석 통합 엔진"""
    
    def __init__(self, openai_api_key: str = None):
        self.analyst_analyzer = AnalystReportAnalyzer(openai_api_key)
        self.ir_analyzer = IRDocumentAnalyzer(openai_api_key)
        self.pdf_processor = PDFDocumentProcessor()
    
    async def analyze_document_from_url(self, pdf_url: str, company_name: str, doc_type: str = "Unknown") -> Dict[str, Any]:
        """URL에서 문서 분석"""
        
        print(f"📄 문서 분석 시작: {pdf_url}")
        
        # PDF 텍스트 추출
        pdf_content = await self.pdf_processor.extract_text_from_url(pdf_url)
        
        if not pdf_content:
            return {"error": "PDF 텍스트 추출 실패"}
        
        # 문서 유형에 따라 분석
        if "analyst" in doc_type.lower() or "research" in doc_type.lower():
            result = await self.analyst_analyzer.analyze_analyst_report(pdf_content, company_name)
            return {"type": "analyst_report", "data": result}
        else:
            result = await self.ir_analyzer.analyze_ir_document(pdf_content, company_name, doc_type)
            return {"type": "ir_document", "data": result}

# 사용 예시
async def analyze_ligachem_documents():
    """리가켐바이오 문서 분석 예시"""
    
    engine = DocumentAnalysisEngine(openai_api_key=None)  # API 키 설정 필요
    
    # 예시 문서 URL들 (실제 URL로 교체 필요)
    documents = [
        ("https://example.com/ligachem_analyst_report.pdf", "리가켐바이오", "analyst_report"),
        ("https://example.com/ligachem_ir_presentation.pdf", "리가켐바이오", "ir_presentation")
    ]
    
    results = []
    for url, company, doc_type in documents:
        try:
            result = await engine.analyze_document_from_url(url, company, doc_type)
            results.append(result)
        except Exception as e:
            print(f"문서 분석 오류 ({url}): {str(e)}")
    
    return results

if __name__ == "__main__":
    # 테스트 실행
    results = asyncio.run(analyze_ligachem_documents())
    print(f"문서 분석 결과: {len(results)}개 문서 처리")