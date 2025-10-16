# Polymarket Market Evaluation Pipeline

This project scrapes Polymarket markets and evaluates them using a local LLM (Qwen 2.5 7B) based on 10 metrics optimized for Asian audience appeal.

## Features

- **Scrapes Polymarket markets** using official `py-clob-client`
- **LLM-based evaluation** with Ollama (Qwen 2.5 7B) - completely FREE
- **10 metric scoring system** from 盘口 Matrix.xlsx
- **Structured output** with Pydantic validation
- **Weighted final scores** for ranking markets
- **CSV + JSON exports** for analysis

## Project Structure

```
yoyo-data-mining/
├── config/
│   ├── api_config.py          # Polymarket endpoints
│   ├── scoring_weights.py     # 10 metrics weights
│   └── llm_prompts.py         # System/user prompts
├── scrapers/
│   └── polymarket_scraper.py  # Market scraper
├── scoring/
│   ├── llm_evaluator.py       # Ollama integration
│   └── market_scorer.py       # Weighted scoring
├── models/
│   └── evaluation_schema.py   # Pydantic models
├── data/
│   ├── raw/                   # Scraped markets
│   └── processed/             # Evaluated markets
├── main.py                    # Main pipeline
├── requirements.txt
└── 盘口 Matrix.xlsx           # Metrics reference
```

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 3. Download Qwen 2.5 7B Model (~4GB)

```bash
ollama pull qwen2.5:7b-instruct
```

## Usage

### Run Full Pipeline (20 test markets)

```bash
python3 main.py
```

This will:
1. Load existing scraped markets (or scrape 20 new ones)
2. Evaluate each market with Qwen 2.5 7B (~10s per market)
3. Calculate weighted scores
4. Export to JSON + CSV

### Run Individual Components

**Scrape markets only:**
```bash
python3 scrapers/polymarket_scraper.py
```

**Test LLM evaluation:**
```bash
python3 scoring/llm_evaluator.py
```

**Test scoring:**
```bash
python3 scoring/market_scorer.py
```

## Evaluation Metrics

Each market is scored 1-5 on 10 metrics (based on 盘口 Matrix.xlsx):

| Metric | Weight | Description |
|--------|--------|-------------|
| 热度/传播度 | 15% | Popularity, virality, trading volume |
| 文化契合度 | 10% | Cultural relevance to Asian audience |
| 结果无争议度 | 10% | Result clarity, objectivity |
| 话题对抗性 | 15% | Competitiveness, controversy |
| 事件发生周期 | 5% | Event duration |
| 历史渊源 | 10% | Historical context |
| 模板可标准化 | 5% | Template reusability |
| 用户流动性 | 10% | Expected trading activity |
| 结果波动 | 15% | Volatility, repeat trading potential |
| 信息获取 | 5% | Information accessibility |

**Final Score** = Σ (metric_score × weight)

## Output Files

- `data/raw/scraped_markets_test.json` - Raw scraped markets
- `data/processed/evaluated_markets_test.json` - Full evaluations with scores
- `data/processed/evaluated_markets_test.csv` - Summary table (Excel-friendly)

## Hardware Requirements

- **GPU**: 4070 Super (12GB VRAM) - perfect for Qwen 2.5 7B
- **RAM**: 32GB (recommended)
- **Inference Speed**: ~2-5 tokens/sec on 4070 Super

## Notes

- The pipeline uses **local LLM** (no API costs)
- Markets are saved before evaluation (can re-run evaluation without re-scraping)
- Evaluation prompts are in Chinese + English for better Asian market assessment
- Temperature set to 0.3 for consistent scoring

## Future Enhancements

- Add Asian-relevance filtering (keywords: China, Japan, Korea, cricket, etc.)
- Scale to 1000 markets
- Add parallel processing for faster evaluation
- Implement dashboard for visualization
