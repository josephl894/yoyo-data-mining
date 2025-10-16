"""
Pydantic schema for Asian relevance filter output
"""
from pydantic import BaseModel, Field


class AsianRelevanceFilter(BaseModel):
    """
    Schema for LLM-based Asian relevance filtering
    """
    is_asian_relevant: bool = Field(
        description="True if market is highly relevant to Asian audiences, False otherwise"
    )
    confidence: str = Field(
        description="Confidence level: 'high', 'medium', or 'low'"
    )
    reasoning: str = Field(
        description="1-2 sentence explanation for the decision"
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'is_asian_relevant': self.is_asian_relevant,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }
