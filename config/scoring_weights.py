"""
Scoring weights from the Excel metrics matrix
These weights are used to calculate the final weighted score
"""

# Weights for each metric (must sum to 1.0)
# Based on the Excel file: 盘口 Matrix.xlsx
METRIC_WEIGHTS = {
    '热度传播度': 0.15,        # Popularity/Virality
    '文化契合度': 0.10,        # Cultural Relevance
    '结果无争议度': 0.10,      # Result Clarity
    '话题对抗性': 0.15,        # Competitiveness
    '事件发生周期': 0.05,      # Event Duration
    '历史渊源': 0.10,          # Historical Context
    '模板可标准化': 0.05,      # Template Standardization
    '用户流动性': 0.10,        # User Liquidity
    '结果波动': 0.15,          # Volatility/Trading Frequency
    '信息获取': 0.05,          # Information Accessibility
}

# Note: 作死度 (risk factor) is ignored as per user request

# Verify weights sum to 1.0
assert abs(sum(METRIC_WEIGHTS.values()) - 1.0) < 0.001, "Weights must sum to 1.0"


def calculate_weighted_score(scores):
    """
    Calculate weighted final score

    Args:
        scores: Dictionary with metric names as keys and scores (1-5) as values

    Returns:
        Weighted score (1.0 - 5.0)
    """
    weighted_sum = 0.0

    for metric, weight in METRIC_WEIGHTS.items():
        if metric in scores:
            weighted_sum += scores[metric] * weight
        else:
            print(f"Warning: Missing score for metric '{metric}'")

    return weighted_sum
