"""
Market scorer - calculates final weighted scores
Combines market data with LLM evaluation
"""
import json
import pandas as pd
from config.scoring_weights import calculate_weighted_score


class MarketScorer:
    def __init__(self):
        """Initialize the market scorer"""
        pass

    def score_evaluated_markets(self, evaluated_markets):
        """
        Calculate weighted scores for evaluated markets

        Args:
            evaluated_markets: List of tuples (market, evaluation)

        Returns:
            List of dictionaries with market info + scores
        """
        scored_markets = []

        for market, evaluation in evaluated_markets:
            # Get evaluation scores as dict
            eval_dict = evaluation.to_dict()

            # Extract scores (without reasoning)
            scores = {k: v for k, v in eval_dict.items() if k != 'reasoning'}

            # Calculate weighted score
            final_score = calculate_weighted_score(scores)

            # Combine market info with evaluation
            scored_market = {
                'question': market.get('question', 'N/A'),
                'description': market.get('description', 'N/A')[:200] + '...',
                'end_date': market.get('end_date_iso', market.get('endDate', 'N/A')),
                'volume': market.get('volume', 0),
                'tags': market.get('tags', []),
                **scores,  # All individual scores
                'reasoning': eval_dict['reasoning'],
                'final_score': round(final_score, 2)
            }

            # Add series metadata if available
            if market.get('is_part_of_series'):
                scored_market['is_part_of_series'] = True
                scored_market['event_slug'] = market.get('event_slug')
                scored_market['parent_event_title'] = market.get('parent_event_title')
            else:
                scored_market['is_part_of_series'] = False

            if market.get('is_series_representative'):
                scored_market['is_series_representative'] = True
                scored_market['series_condition_count'] = market.get('series_condition_count')

            scored_markets.append(scored_market)

        # Sort by final score (descending)
        scored_markets.sort(key=lambda x: x['final_score'], reverse=True)

        return scored_markets

    def save_to_json(self, scored_markets, filepath):
        """
        Save scored markets to JSON

        Args:
            scored_markets: List of scored market dictionaries
            filepath: Path to save JSON file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(scored_markets, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(scored_markets)} scored markets to {filepath}")

    def save_to_csv(self, scored_markets, filepath):
        """
        Save scored markets to CSV

        Args:
            scored_markets: List of scored market dictionaries
            filepath: Path to save CSV file
        """
        df = pd.DataFrame(scored_markets)

        # Reorder columns for better readability
        column_order = [
            'final_score',
            'question',
            'volume',
            'end_date',
            'is_part_of_series',
            'is_series_representative',
            'series_condition_count',
            'event_slug',
            'parent_event_title',
            '热度传播度',
            '文化契合度',
            '结果无争议度',
            '话题对抗性',
            '事件发生周期',
            '历史渊源',
            '模板可标准化',
            '用户流动性',
            '结果波动',
            '信息获取',
            'reasoning',
            'description',
            'tags'
        ]

        # Only include columns that exist
        column_order = [col for col in column_order if col in df.columns]

        df = df[column_order]
        df.to_csv(filepath, index=False, encoding='utf-8-sig')  # BOM for Excel
        print(f"Saved {len(scored_markets)} scored markets to {filepath}")


def main():
    """Test the scorer"""
    from scoring.llm_evaluator import LLMEvaluator

    # Load test markets
    with open('data/raw/scraped_markets_test.json', 'r') as f:
        markets = json.load(f)

    # Evaluate markets
    evaluator = LLMEvaluator()
    evaluated = evaluator.evaluate_markets_batch(markets[:2])  # Test on 2 markets

    # Score markets
    scorer = MarketScorer()
    scored = scorer.score_evaluated_markets(evaluated)

    # Print results
    print("\n=== Scored Markets ===")
    for market in scored:
        print(f"\n{market['question'][:60]}...")
        print(f"Final Score: {market['final_score']}")
        print(f"Reasoning: {market['reasoning'][:100]}...")

    # Save results
    scorer.save_to_json(scored, 'data/processed/evaluated_markets_test.json')
    scorer.save_to_csv(scored, 'data/processed/evaluated_markets_test.csv')


if __name__ == "__main__":
    main()
