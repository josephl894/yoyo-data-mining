"""
Pydantic models for market evaluation
Defines the structure for LLM output
"""
from pydantic import BaseModel, Field


class MarketEvaluation(BaseModel):
    """
    Evaluation metrics for a Polymarket market
    All scores are on a 1-5 scale
    """
    热度传播度: int = Field(
        ge=1, le=5,
        description="话题热度、交易量、媒体关注度 (1=最低, 5=最高)"
    )
    文化契合度: int = Field(
        ge=1, le=5,
        description="与亚洲文化/兴趣的相关性 (1=最低, 5=最高)"
    )
    结果无争议度: int = Field(
        ge=1, le=5,
        description="结果是否清晰无争议 (1=有争议, 5=无争议)"
    )
    话题对抗性: int = Field(
        ge=1, le=5,
        description="竞争性、争议性、激烈程度 (1=最低, 5=最高)"
    )
    事件发生周期: int = Field(
        ge=1, le=5,
        description="持续时间 (1=短期, 5=长期可交易)"
    )
    历史渊源: int = Field(
        ge=1, le=5,
        description="是否有历史背景/传统 (1=无, 5=深厚)"
    )
    模板可标准化: int = Field(
        ge=1, le=5,
        description="可复用性 (1=难以复用, 5=易于标准化)"
    )
    用户流动性: int = Field(
        ge=1, le=5,
        description="预期交易活跃度 (1=最低, 5=最高)"
    )
    结果波动: int = Field(
        ge=1, le=5,
        description="赔率变化潜力 (1=最低, 5=最高)"
    )
    信息获取: int = Field(
        ge=1, le=5,
        description="信息透明度 (1=难以获取, 5=容易获取)"
    )
    reasoning: str = Field(
        description="简短解释评分理由"
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "热度传播度": self.热度传播度,
            "文化契合度": self.文化契合度,
            "结果无争议度": self.结果无争议度,
            "话题对抗性": self.话题对抗性,
            "事件发生周期": self.事件发生周期,
            "历史渊源": self.历史渊源,
            "模板可标准化": self.模板可标准化,
            "用户流动性": self.用户流动性,
            "结果波动": self.结果波动,
            "信息获取": self.信息获取,
            "reasoning": self.reasoning
        }
