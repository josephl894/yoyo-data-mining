"""
LLM-based Asian relevance filter using LM Studio with Qwen 3 4B
Filters markets based on strict Asian audience relevance criteria
"""
import json
import time
from datetime import timedelta
from openai import OpenAI
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.console import Console
from rich.panel import Panel
from models.filter_schema import AsianRelevanceFilter
from config.filter_prompts import FILTER_SYSTEM_PROMPT, create_filter_prompt

console = Console()


class LLMAsianFilter:
    def __init__(self, base_url="http://172.31.0.1:1234/v1", model_name="qwen3-4b"):
        """
        Initialize the LLM Asian relevance filter

        Args:
            base_url: LM Studio API endpoint (Windows host IP for WSL2)
            model_name: Model name (as shown in LM Studio) - Qwen 3 4B
        """
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model_name = model_name

    def filter_market(self, market, show_progress=True):
        """
        Filter a single market using the LLM with streaming

        Args:
            market: Dictionary containing market information
            show_progress: Show streaming progress with t/s

        Returns:
            AsianRelevanceFilter object or None if filtering fails
        """
        try:
            # Create user prompt
            user_prompt = create_filter_prompt(market)

            # Call LM Studio with streaming
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': FILTER_SYSTEM_PROMPT + '\n\nOUTPUT ONLY VALID JSON. No other text.'},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.1,  # Very low temperature for consistent filtering
                max_tokens=256,  # Short response for binary filter
                stream=True
            )

            # Stream and collect response
            content = ""
            token_count = 0
            start_stream = time.time()

            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[yellow]{task.fields[tokens]:>4} tokens"),
                    TextColumn("•"),
                    TextColumn("[green]{task.fields[tps]:>5.0f} t/s"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("", tokens=0, tps=0)

                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content += chunk.choices[0].delta.content
                            token_count += 1

                            # Update progress
                            elapsed = time.time() - start_stream
                            tps = token_count / elapsed if elapsed > 0 else 0
                            progress.update(task, tokens=token_count, tps=tps)
            else:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content

            # Handle markdown code blocks
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            # Parse JSON
            filter_data = json.loads(content)

            # Validate with Pydantic
            filter_result = AsianRelevanceFilter(**filter_data)

            return filter_result

        except Exception as e:
            print(f"Error filtering market '{market.get('question', 'N/A')[:50]}...': {e}")
            return None

    def filter_markets_batch(self, markets):
        """
        Filter multiple markets individually with progress tracking

        Args:
            markets: List of market dictionaries

        Returns:
            List of tuples (market, filter_result) for successfully filtered markets
        """
        results = []
        total = len(markets)
        accepted_count = 0
        rejected_count = 0
        fail_count = 0
        start_time = time.time()

        console.print(Panel.fit(
            f"[bold cyan]LLM Asian Relevance Filter[/bold cyan]\n"
            f"Total markets: {total} | Processing individually",
            border_style="cyan"
        ))

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[green]✓{task.fields[accepted]}"),
            TextColumn("[red]✗{task.fields[rejected]}"),
            TextColumn("[yellow]⚠{task.fields[failed]}"),
            TextColumn("•"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                "[cyan]Filtering markets...",
                total=total,
                accepted=0,
                rejected=0,
                failed=0
            )

            for i, market in enumerate(markets, 1):
                question = market.get('question', 'N/A')[:50]
                progress.update(task, description=f"[cyan]Filtering: {question}...")

                # Filter individual market
                filter_result = self.filter_market(market)

                if filter_result:
                    results.append((market, filter_result))
                    if filter_result.is_asian_relevant:
                        accepted_count += 1
                    else:
                        rejected_count += 1
                else:
                    fail_count += 1

                progress.update(
                    task,
                    advance=1,
                    accepted=accepted_count,
                    rejected=rejected_count,
                    failed=fail_count
                )

        # Final summary
        total_time = time.time() - start_time

        summary_text = (
            f"[bold green]✓ LLM Asian Filter Complete![/bold green]\n\n"
            f"Total Markets: {total}\n"
            f"[green]Accepted: {accepted_count}[/green] ({(accepted_count/total)*100:.1f}%)\n"
            f"[red]Rejected: {rejected_count}[/red] ({(rejected_count/total)*100:.1f}%)\n"
            f"[yellow]Failed: {fail_count}[/yellow] ({(fail_count/total)*100:.1f}%)\n\n"
            f"Total Time: {timedelta(seconds=int(total_time))}\n"
            f"Average: {total_time/total:.2f}s per market"
        )

        console.print(Panel(summary_text, border_style="green", title="Summary"))

        return results

    def get_accepted_markets(self, filter_results):
        """
        Extract only accepted markets from filter results

        Args:
            filter_results: List of tuples (market, filter_result)

        Returns:
            List of tuples (market, filter_result) for accepted markets only
        """
        accepted = [
            (market, result) for market, result in filter_results
            if result.is_asian_relevant
        ]

        console.print(f"[cyan]Extracted {len(accepted)} accepted markets from {len(filter_results)} total[/cyan]")
        return accepted


def main():
    """Test the filter"""
    import json
    from scrapers.polymarket_scraper import PolymarketScraper

    # Scrape test markets
    print("Fetching 20 test markets...")
    scraper = PolymarketScraper()
    result = scraper.fetch_filtered_markets(target=20, min_days_future=30, handle_series=False)

    # Use evaluation_targets (which is just markets if handle_series=False)
    markets = result['evaluation_targets']

    # Test filter
    filter_obj = LLMAsianFilter()
    print(f"\nTesting LLM Asian filter on {len(markets)} markets...\n")

    filter_results = filter_obj.filter_markets_batch(markets)

    # Show accepted markets
    accepted = filter_obj.get_accepted_markets(filter_results)

    print("\n" + "="*80)
    print("ACCEPTED MARKETS:")
    print("="*80)
    for i, (market, result) in enumerate(accepted, 1):
        print(f"\n{i}. {market.get('question')}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Reasoning: {result.reasoning}")


if __name__ == "__main__":
    main()
