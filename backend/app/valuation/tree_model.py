from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

class NodeType(Enum):
    ROOT = "root"
    FORMULA = "formula" 
    ASSUMPTION = "assumption"
    VALUE = "value"

@dataclass
class ValuationNode:
    """벨류에이션 Tree 구조의 노드"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    node_type: NodeType = NodeType.VALUE
    value: Optional[float] = None
    formula: Optional[str] = None
    assumptions: Dict[str, Any] = field(default_factory=dict)
    children: List['ValuationNode'] = field(default_factory=list)
    parent_id: Optional[str] = None
    description: str = ""
    source: str = ""
    confidence_level: float = 1.0  # 0-1 신뢰도
    
    def add_child(self, child: 'ValuationNode'):
        """자식 노드 추가"""
        child.parent_id = self.id
        self.children.append(child)
        return child
    
    def calculate(self) -> float:
        """노드 값 계산"""
        if self.node_type == NodeType.VALUE and self.value is not None:
            return self.value
        
        if self.node_type == NodeType.ASSUMPTION and self.value is not None:
            return self.value
        
        if self.node_type == NodeType.FORMULA and self.formula:
            return self._execute_formula()
        
        if self.node_type == NodeType.ROOT:
            return sum(child.calculate() for child in self.children)
        
        return 0.0
    
    def _execute_formula(self) -> float:
        """수식 실행"""
        if not self.formula:
            return 0.0
        
        # 자식 노드들의 값을 변수로 사용
        variables = {}
        for i, child in enumerate(self.children):
            variables[f'child_{i}'] = child.calculate()
            variables[child.name.lower().replace(' ', '_')] = child.calculate()
        
        # assumptions도 변수로 추가
        variables.update(self.assumptions)
        
        try:
            # 안전한 수식 실행
            allowed_names = {
                "__builtins__": {},
                "abs": abs, "round": round, "min": min, "max": max,
                "pow": pow, "sum": sum, "len": len,
                **variables
            }
            return eval(self.formula, {"__builtins__": {}}, allowed_names)
        except Exception as e:
            print(f"Formula execution error: {e}")
            return 0.0
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "value": self.value,
            "formula": self.formula,
            "assumptions": self.assumptions,
            "children": [child.to_dict() for child in self.children],
            "parent_id": self.parent_id,
            "description": self.description,
            "source": self.source,
            "confidence_level": self.confidence_level,
            "calculated_value": self.calculate()
        }

class ValuationTree:
    """벨류에이션 Tree 관리 클래스"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.root = ValuationNode(
            name=f"{company_name} 기업가치",
            node_type=NodeType.ROOT,
            description=f"{company_name}의 총 기업가치"
        )
        self.nodes: Dict[str, ValuationNode] = {self.root.id: self.root}
    
    def add_node(self, parent_id: str, node: ValuationNode) -> ValuationNode:
        """노드 추가"""
        parent = self.nodes.get(parent_id)
        if not parent:
            raise ValueError(f"Parent node not found: {parent_id}")
        
        parent.add_child(node)
        self.nodes[node.id] = node
        return node
    
    def get_node(self, node_id: str) -> Optional[ValuationNode]:
        """노드 조회"""
        return self.nodes.get(node_id)
    
    def calculate_total_value(self) -> float:
        """총 기업가치 계산"""
        return self.root.calculate()
    
    def get_tree_structure(self) -> Dict:
        """전체 트리 구조 반환"""
        return {
            "company_name": self.company_name,
            "total_value": self.calculate_total_value(),
            "tree": self.root.to_dict(),
            "metadata": {
                "total_nodes": len(self.nodes),
                "calculation_date": None  # 실제로는 현재 날짜
            }
        }
    
    def validate_tree(self) -> List[str]:
        """트리 구조 검증"""
        errors = []
        
        for node_id, node in self.nodes.items():
            # 수식 노드는 자식이 있어야 함
            if node.node_type == NodeType.FORMULA and not node.children:
                errors.append(f"Formula node '{node.name}' has no children")
            
            # 가정 노드는 값이 있어야 함  
            if node.node_type == NodeType.ASSUMPTION and node.value is None:
                errors.append(f"Assumption node '{node.name}' has no value")
                
            # 순환 참조 검사 (간단한 버전)
            if node.parent_id == node.id:
                errors.append(f"Node '{node.name}' has circular reference")
        
        return errors

def create_biotech_valuation_template(company_name: str) -> ValuationTree:
    """바이오텍 기업 벨류에이션 템플릿 생성"""
    tree = ValuationTree(company_name)
    
    # 1. 파이프라인 가치
    pipeline_node = ValuationNode(
        name="파이프라인 총 가치",
        node_type=NodeType.FORMULA,
        formula="sum([child.calculate() for child in self.children])",
        description="모든 파이프라인의 NPV 합계"
    )
    tree.add_node(tree.root.id, pipeline_node)
    
    # 2. 현금 및 기타 자산
    cash_node = ValuationNode(
        name="현금 및 기타 자산",
        node_type=NodeType.ASSUMPTION,
        value=0.0,
        description="현재 보유 현금과 기타 자산의 가치"
    )
    tree.add_node(tree.root.id, cash_node)
    
    return tree