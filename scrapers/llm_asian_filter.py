"""
LLM-based Asian relevance filter using LM Studio with Qwen 3 4B
Filters markets based on strict Asian audience relevance criteria
"""
import json
import re
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
    def __init__(self, base_url="http://172.31.0.1:1234/v1", model_name="qwen3-4b", batch_size=10):
        """
        Initialize the LLM Asian relevance filter

        Args:
            base_url: LM Studio API endpoint (Windows host IP for WSL2)
            model_name: Model name (as shown in LM Studio) - Qwen 3 4B
            batch_size: Number of markets to filter per batch (default: 10)
        """
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model_name = model_name
        self.batch_size = batch_size

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

    def filter_markets_batch_single_call(self, markets_batch):
        """
        Filter multiple markets in a single API call

        Args:
            markets_batch: List of market dictionaries (up to batch_size)

        Returns:
            List of AsianRelevanceFilter objects or None if filtering fails
        """
        try:
            # Create batch prompt
            batch_prompt = "Evaluate the following markets for Asian relevance.\n\n"
            for i, market in enumerate(markets_batch, 1):
                question = market.get('question', 'N/A').replace('"', "'").replace('\n', ' ')[:200]
                description = market.get('description', 'N/A').replace('"', "'").replace('\n', ' ')[:300]
                tags = ', '.join(market.get('tags', [])[:3])

                batch_prompt += f"**Market {i}:**\n"
                batch_prompt += f"Question: {question}\n"
                batch_prompt += f"Description: {description}...\n"
                batch_prompt += f"Tags: {tags}\n\n"

            batch_prompt += f"\nOutput a JSON array with {len(markets_batch)} objects, one for each market in order."
            batch_prompt += '\nFormat: [{"is_asian_relevant": bool, "confidence": "high/medium/low", "reasoning": "..."}, ...]'
            batch_prompt += '\nIMPORTANT: Keep ALL text on single lines. No line breaks in reasoning field. Use compact JSON format.'

            # Call LM Studio with streaming
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': FILTER_SYSTEM_PROMPT + '\n\nOUTPUT ONLY VALID JSON ARRAY. No other text.'},
                    {'role': 'user', 'content': batch_prompt}
                ],
                temperature=0.1,
                max_tokens=len(markets_batch) * 100,  # ~100 tokens per result
                stream=True
            )

            # Stream and collect response with rich progress
            content = ""
            token_count = 0
            start_stream = time.time()

            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("[yellow]{task.fields[tokens]:>6,} tokens"),
                TextColumn("•"),
                TextColumn("[green]{task.fields[tps]:>4.0f} t/s"),
                TimeElapsedColumn(),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Streaming batch ({len(markets_batch)} markets)...",
                    total=len(markets_batch) * 100,  # Estimate: ~100 tokens per result
                    tokens=0,
                    tps=0
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                        token_count += 1

                        # Update progress
                        elapsed = time.time() - start_stream
                        tps = token_count / elapsed if elapsed > 0 else 0
                        progress.update(
                            task,
                            completed=min(token_count, len(markets_batch) * 100),
                            tokens=token_count,
                            tps=tps
                        )

            # Final stats
            total_time = time.time() - start_stream
            avg_tps = token_count / total_time if total_time > 0 else 0
            console.print(f"    [green]✓[/green] Streamed {token_count:,} tokens in {total_time:.1f}s ([green]{avg_tps:.0f} t/s[/green])")

            content = content.strip()

            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            # Try to find JSON array if there's extra text
            if not content.startswith('['):
                start_idx = content.find('[')
                if start_idx != -1:
                    content = content[start_idx:]

            if not content.endswith(']'):
                end_idx = content.rfind(']')
                if end_idx != -1:
                    content = content[:end_idx + 1]

            # Try parsing as-is first
            try:
                filter_data_list = json.loads(content)
            except json.JSONDecodeError:
                # Fix common issues: replace newlines within string values
                # This is a heuristic fix for LLM output with embedded newlines
                fixed_content = re.sub(r'"\s*\n\s*', ' ', content)
                filter_data_list = json.loads(fixed_content)

            # Validate each result
            results = []
            for filter_data in filter_data_list:
                filter_result = AsianRelevanceFilter(**filter_data)
                results.append(filter_result)

            return results

        except json.JSONDecodeError as e:
            console.print(f"[red]JSON parsing error in batch: {e}[/red]")
            console.print(f"[yellow]Response preview: {content[:500]}...[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error batch filtering {len(markets_batch)} markets: {e}[/red]")
            return None

    def filter_markets_batch(self, markets):
        """
        Filter multiple markets with batching and progress tracking

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
            f"Total markets: {total} | Batch size: {self.batch_size}",
            border_style="cyan"
        ))

        # Process in batches
        for batch_start in range(0, total, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total)
            batch = markets[batch_start:batch_end]
            batch_num = (batch_start // self.batch_size) + 1
            total_batches = (total + self.batch_size - 1) // self.batch_size

            # Progress
            elapsed = time.time() - start_time
            avg_time_per_batch = elapsed / batch_num if batch_num > 0 else 0
            remaining_batches = total_batches - batch_num
            eta_seconds = remaining_batches * avg_time_per_batch
            eta = timedelta(seconds=int(eta_seconds))

            console.print(f"\n[bold cyan]Batch {batch_num}/{total_batches}[/bold cyan] | "
                          f"Markets {batch_start+1}-{batch_end} | "
                          f"[green]✓{accepted_count}[/green] "
                          f"[red]✗{rejected_count}[/red] "
                          f"[yellow]⚠{fail_count}[/yellow] | "
                          f"ETA: {eta}")

            # Filter batch
            batch_results = self.filter_markets_batch_single_call(batch)

            if batch_results and len(batch_results) == len(batch):
                # Success - process results
                for market, filter_result in zip(batch, batch_results):
                    results.append((market, filter_result))

                    if filter_result.is_asian_relevant:
                        accepted_count += 1
                    else:
                        rejected_count += 1

                batch_accepted = sum(1 for _, r in zip(batch, batch_results) if r.is_asian_relevant)
                console.print(f"    [green]✓[/green] Batch complete | "
                              f"Accepted: [green]{batch_accepted}[/green]/{len(batch)}")

            else:
                # Batch failed - fallback to individual filtering
                console.print(f"    [yellow]⚠[/yellow] Batch failed, falling back to individual filtering...")
                for market in batch:
                    filter_result = self.filter_market(market, show_progress=False)
                    if filter_result:
                        results.append((market, filter_result))
                        if filter_result.is_asian_relevant:
                            accepted_count += 1
                        else:
                            rejected_count += 1
                    else:
                        fail_count += 1

        # Final summary
        total_time = time.time() - start_time
        speedup = (total * 1.7 / total_time) if total_time > 0 else 0  # 1.7s = individual time

        summary_text = (
            f"[bold green]✓ LLM Asian Filter Complete![/bold green]\n\n"
            f"Total Markets: {total}\n"
            f"[green]Accepted: {accepted_count}[/green] ({(accepted_count/total)*100:.1f}%)\n"
            f"[red]Rejected: {rejected_count}[/red] ({(rejected_count/total)*100:.1f}%)\n"
            f"[yellow]Failed: {fail_count}[/yellow] ({(fail_count/total)*100:.1f}%)\n\n"
            f"Total Time: {timedelta(seconds=int(total_time))}\n"
            f"Average: {total_time/total:.2f}s per market\n"
            f"[cyan]Speedup from batching: ~{speedup:.1f}x[/cyan]"
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
