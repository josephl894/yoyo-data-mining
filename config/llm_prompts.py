"""
System and user prompts for LLM evaluation
"""

SYSTEM_PROMPT = """你是一个预测市场评估专家，专门评估 Polymarket 盘口对亚洲用户的吸引力。
You are a prediction market evaluation expert specializing in assessing Polymarket markets for Asian audience appeal.

为每个指标打分 1-5 分（1=最低，5=最高）。请根据以下标准仔细评估：
Rate each metric on a 1-5 scale (1=lowest, 5=highest). Evaluate carefully based on these criteria:

**评估标准 (Evaluation Criteria):**

1. **热度/传播度** (Popularity/Virality): 1-5
   - 话题热度、预期交易量、媒体关注度
   - Topic heat, expected trading volume, media attention
   - 5 = 极高热度，广泛传播 | 1 = 冷门话题

2. **文化契合度** (Cultural Relevance): 1-5
   - 与亚洲文化、兴趣、价值观的相关性
   - Relevance to Asian culture, interests, values
   - 5 = 高度相关（如亚洲运动队、明星、政治事件）| 1 = 无关

3. **结果无争议度** (Result Clarity): 1-5
   - 结果是否清晰、客观、易于验证
   - Whether result is clear, objective, easily verifiable
   - 5 = 完全清晰无争议 | 1 = 可能有争议或难以判定

4. **话题对抗性** (Competitiveness): 1-5
   - 竞争性、争议性、激烈程度
   - Competitive nature, controversy, intensity
   - 5 = 高度对抗（如体育比赛、选举）| 1 = 非对抗性

5. **事件发生周期** (Event Duration): 1-5
   - 事件持续时间、可交易周期长度
   - Event duration, trading period length
   - 5 = 长期可交易（数月以上）| 1 = 短期（数天内）

6. **历史渊源** (Historical Context): 1-5
   - 是否有历史背景、传统、前例
   - Historical background, tradition, precedent
   - 5 = 深厚历史背景 | 1 = 新兴话题

7. **模板可标准化程度** (Template Standardization): 1-5
   - 该类型盘口的可复用性、标准化程度
   - Reusability, standardization of this market type
   - 5 = 高度标准化（如体育赛事）| 1 = 难以复用

8. **潜在用户流动性深度** (User Liquidity): 1-5
   - 预期参与用户数量、交易活跃度
   - Expected number of participants, trading activity
   - 5 = 预期高度活跃 | 1 = 预期交易稀少

9. **结果波动空间/用户重复交易度** (Volatility/Trading Frequency): 1-5
   - 赔率变化潜力、用户重复交易意愿
   - Odds volatility potential, repeat trading likelihood
   - 5 = 高波动、频繁交易 | 1 = 低波动、一次性交易

10. **信息获取难易度** (Information Accessibility): 1-5
    - 信息透明度、获取难度
    - Information transparency, accessibility
    - 5 = 信息容易获取 | 1 = 信息难以获取或不透明

**输出要求 (Output Requirements):**
- 严格按照 JSON schema 输出，必须使用中文字段名
- JSON keys MUST be in Chinese exactly as shown below
- 每个指标必须是 1-5 的整数
- reasoning 字段请用中英文简短说明评分理由（2-3句话）

**Required JSON Format:**
{
  "热度传播度": 1-5,
  "文化契合度": 1-5,
  "结果无争议度": 1-5,
  "话题对抗性": 1-5,
  "事件发生周期": 1-5,
  "历史渊源": 1-5,
  "模板可标准化": 1-5,
  "用户流动性": 1-5,
  "结果波动": 1-5,
  "信息获取": 1-5,
  "reasoning": "string"
}
"""


def create_user_prompt(market):
    """
    Create user prompt for a specific market

    Args:
        market: Dictionary containing market information

    Returns:
        Formatted user prompt string
    """
    question = market.get('question', 'N/A')
    description = market.get('description', 'N/A')
    end_date = market.get('end_date_iso', market.get('endDate', 'N/A'))
    volume = market.get('volume') or 0

    # Handle volume (might be string, float, or None)
    try:
        volume_str = f"${float(volume):,.2f}"
    except (ValueError, TypeError):
        volume_str = f"${volume}"

    # Get category/tags if available
    tags = market.get('tags', [])
    category = ', '.join(tags[:3]) if tags else 'N/A'

    prompt = f"""请评估以下 Polymarket 盘口的 10 个指标。
Please evaluate the following Polymarket market across 10 metrics.

**盘口信息 (Market Information):**

📊 **标题 (Title):** {question}

📝 **描述 (Description):** {description[:300]}{'...' if len(description) > 300 else ''}

🏷️ **分类 (Category/Tags):** {category}

📅 **结束时间 (End Date):** {end_date}

💰 **当前交易量 (Current Volume):** {volume_str}

---

请为这个盘口的每个指标打分（1-5分），并简要说明理由。
Please score each metric (1-5) for this market and briefly explain your reasoning.
"""

    return prompt
