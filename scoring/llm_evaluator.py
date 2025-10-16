"""
LLM evaluator using LM Studio with Qwen 3 4B
Evaluates markets based on 10 metrics
"""
import json
import time
from datetime import timedelta
from openai import OpenAI
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from models.evaluation_schema import MarketEvaluation
from config.llm_prompts import SYSTEM_PROMPT, create_user_prompt

console = Console()


class LLMEvaluator:
    def __init__(self, base_url="http://172.31.0.1:1234/v1", model_name="qwen3-4b"):
        """
        Initialize the LLM evaluator

        Args:
            base_url: LM Studio API endpoint (Windows host IP for WSL2)
            model_name: Model name (as shown in LM Studio) - Qwen 3 4B
        """
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model_name = model_name

    def evaluate_market(self, market):
        """
        Evaluate a single market using the LLM

        Args:
            market: Dictionary containing market information

        Returns:
            MarketEvaluation object or None if evaluation fails
        """
        try:
            # Create user prompt
            user_prompt = create_user_prompt(market)

            # Call LM Studio (no response_format for compatibility)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT + '\n\nOUTPUT ONLY VALID JSON. No other text.'},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent scoring
                max_tokens=512  # Limit response length for speed
            )

            # Parse response
            content = response.choices[0].message.content
            evaluation_data = json.loads(content)

            # Validate with Pydantic
            evaluation = MarketEvaluation(**evaluation_data)

            return evaluation

        except Exception as e:
            print(f"Error evaluating market '{market.get('question', 'N/A')}': {e}")
            return None

    def evaluate_markets_batch(self, markets):
        """
        Evaluate multiple markets with progress tracking

        Args:
            markets: List of market dictionaries

        Returns:
            List of tuples (market, evaluation)
        """
        results = []
        total = len(markets)
        success_count = 0
        fail_count = 0
        start_time = time.time()

        console.print(Panel.fit(
            f"[bold magenta]LLM Market Evaluation[/bold magenta]\n"
            f"Total markets: {total} | Model: Qwen 3 4B",
            border_style="magenta"
        ))

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[green]✓{task.fields[success]}"),
            TextColumn("[red]✗{task.fields[failed]}"),
            TextColumn("•"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]Evaluating markets...",
                total=total,
                success=0,
                failed=0
            )

            for i, market in enumerate(markets, 1):
                question = market.get('question', 'N/A')[:50]
                progress.update(task, description=f"[cyan]Evaluating: {question}...")

                # Evaluate
                market_start = time.time()
                evaluation = self.evaluate_market(market)
                eval_time = time.time() - market_start

                if evaluation:
                    results.append((market, evaluation))
                    success_count += 1
                else:
                    fail_count += 1

                progress.update(
                    task,
                    advance=1,
                    success=success_count,
                    failed=fail_count
                )

        # Final summary
        total_time = time.time() - start_time
        summary_text = (
            f"[bold green]✓ LLM Evaluation Complete![/bold green]\n\n"
            f"Total Markets: {total}\n"
            f"[green]Successful: {success_count}[/green] ({(success_count/total)*100:.1f}%)\n"
            f"[red]Failed: {fail_count}[/red] ({(fail_count/total)*100:.1f}%)\n\n"
            f"Total Time: {timedelta(seconds=int(total_time))}\n"
            f"Average: {total_time/total:.1f}s per market"
        )

        console.print(Panel(summary_text, border_style="green", title="Evaluation Summary"))

        return results


def main():
    """Test the evaluator"""
    import json

    # Load test markets
    with open('data/raw/scraped_markets_test.json', 'r') as f:
        markets = json.load(f)

    # Test on first market
    evaluator = LLMEvaluator()
    print("Testing LLM evaluator on first market...")

    evaluation = evaluator.evaluate_market(markets[0])

    if evaluation:
        print("\nEvaluation result:")
        print(json.dumps(evaluation.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("Evaluation failed")


if __name__ == "__main__":
    main()
