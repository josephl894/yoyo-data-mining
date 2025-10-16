#!/usr/bin/env python3
"""
Main orchestration script for Polymarket scraping and evaluation
Runs the full pipeline: scrape → evaluate → score → export
"""
import json
import sys
from scrapers.polymarket_scraper import PolymarketScraper
from scrapers.llm_asian_filter import LLMAsianFilter
from scrapers.series_handler import apply_evaluation_to_series
from scoring.llm_evaluator import LLMEvaluator
from scoring.market_scorer import MarketScorer


def main():
    """
    Main pipeline execution
    """
    print("=" * 80)
    print("Polymarket Market Evaluation Pipeline")
    print("=" * 80)

    # Configuration
    NUM_MARKETS = 10000  # Number of raw markets to scrape initially (before filtering)
    MIN_DAYS_FUTURE = 30  # Markets must expire ≥30 days from now
    RAW_DATA_PATH = f'data/raw/scraped_markets_{NUM_MARKETS}.json'
    FILTERED_DATA_PATH = f'data/raw/filtered_markets_{NUM_MARKETS}.json'
    PROCESSED_JSON_PATH = f'data/processed/evaluated_markets_{NUM_MARKETS}.json'
    PROCESSED_CSV_PATH = f'data/processed/evaluated_markets_{NUM_MARKETS}.csv'

    # Step 1: Check if markets are already scraped
    print("\n[Step 1] Checking for existing market data...")
    try:
        with open(RAW_DATA_PATH, 'r') as f:
            data = json.load(f)
        # Handle both old format (list) and new format (dict)
        if isinstance(data, dict):
            evaluation_targets = data.get('evaluation_targets', [])
            all_markets = data.get('all_markets', [])
            series_metadata = data.get('series_metadata', {})
        else:
            # Old format - treat as evaluation targets
            evaluation_targets = data
            all_markets = data
            series_metadata = {}
        print(f"✓ Loaded {len(evaluation_targets)} evaluation targets from {RAW_DATA_PATH}")
        print(f"  Total markets (with series): {len(all_markets)}")
    except FileNotFoundError:
        print(f"No existing data found.")
        print(f"Scraping {NUM_MARKETS} markets from Gamma API:")
        print(f"  - Active & expiring ≥{MIN_DAYS_FUTURE} days from now")
        print(f"  - Sorted by volume (most popular first)")
        print(f"  - Series markets grouped for efficient filtering")
        print()

        # Scrape markets WITHOUT keyword filter (we'll use LLM filter instead)
        scraper = PolymarketScraper()

        # Fetch raw markets using just Gamma API filtering
        print(f"Fetching {NUM_MARKETS} high-volume markets...")
        raw_markets = scraper.fetch_markets_gamma(
            limit=NUM_MARKETS,
            min_days_future=MIN_DAYS_FUTURE,
            closed=False
        )

        # Group into series
        print(f"\nGrouping markets into series...")
        from scrapers.series_handler import prepare_markets_for_evaluation
        result = prepare_markets_for_evaluation(raw_markets)

        evaluation_targets = result['evaluation_targets']
        all_markets = result['all_markets']
        series_metadata = result['series_metadata']

        # Keyword pre-filter (permissive - catches any Asian mention)
        print(f"\nApplying keyword pre-filter (738 Asian keywords)...")
        from scrapers.market_filter import is_asian_relevant, get_matching_keywords

        keyword_filtered_targets = []
        for market in evaluation_targets:
            if is_asian_relevant(market):
                # Add matching keywords for debugging
                market['asian_keywords'] = get_matching_keywords(market)
                keyword_filtered_targets.append(market)

        print(f"✓ Keyword filter: {len(evaluation_targets)} → {len(keyword_filtered_targets)} candidates")
        print(f"  ({(len(keyword_filtered_targets)/len(evaluation_targets)*100):.1f}% pass rate)")

        # Update evaluation_targets to keyword-filtered set
        evaluation_targets = keyword_filtered_targets

        # Save raw data with series info (before LLM filtering)
        scraper.save_to_json(result, RAW_DATA_PATH)
        print(f"✓ Scraped and saved to {RAW_DATA_PATH}")
        print(f"  Evaluation targets after keyword filter: {len(evaluation_targets)}")
        print(f"  Total markets (with series): {len(all_markets)}")

    if not evaluation_targets:
        print("✗ No markets to evaluate. Exiting.")
        sys.exit(1)

    # Step 2: LLM Asian Relevance Filter
    print(f"\n{'='*80}")
    print("[Step 2] Filtering for Asian Relevance with LLM")
    print(f"{'='*80}")

    # Check if already filtered
    try:
        with open(FILTERED_DATA_PATH, 'r') as f:
            filtered_data = json.load(f)
        evaluation_targets = filtered_data.get('evaluation_targets', [])
        all_markets = filtered_data.get('all_markets', [])
        series_metadata = filtered_data.get('series_metadata', {})
        print(f"✓ Loaded {len(evaluation_targets)} filtered markets from {FILTERED_DATA_PATH}")
        print(f"  Total markets (with series): {len(all_markets)}")
    except FileNotFoundError:
        print(f"  Filtering {len(evaluation_targets)} representatives (series + standalone)...")
        print(f"  Using strict Asian relevance criteria")
        print()

        # Run LLM filter on representatives
        asian_filter = LLMAsianFilter()
        filter_results = asian_filter.filter_markets_batch(evaluation_targets)

        # Get accepted markets
        accepted_filter_results = asian_filter.get_accepted_markets(filter_results)

        # Step 2b: Drop rejected series entirely
        print(f"\n{'='*80}")
        print("Dropping rejected series and filtering all markets...")
        print(f"{'='*80}")

        # Build sets of accepted IDs and event slugs
        accepted_ids = set()
        accepted_event_slugs = set()

        for market, filter_result in accepted_filter_results:
            market_id = market.get('id') or market.get('conditionId')
            accepted_ids.add(market_id)

            # If series representative, mark whole series as accepted
            if market.get('is_series_representative'):
                event_slug = market.get('event_slug')
                if event_slug:
                    accepted_event_slugs.add(event_slug)

        # Filter all_markets - keep only accepted standalone or accepted series
        filtered_all_markets = []
        for market in all_markets:
            market_id = market.get('id') or market.get('conditionId')

            # Keep if: standalone accepted OR part of accepted series
            if market_id in accepted_ids:
                filtered_all_markets.append(market)
            elif market.get('is_part_of_series'):
                event_slug = market.get('event_slug')
                if event_slug in accepted_event_slugs:
                    filtered_all_markets.append(market)

        # Update evaluation targets to only accepted markets
        evaluation_targets = [market for market, _ in accepted_filter_results]

        # Filter series metadata
        series_metadata = {
            slug: meta for slug, meta in series_metadata.items()
            if slug in accepted_event_slugs
        }

        # Update variables
        all_markets = filtered_all_markets

        print(f"✓ Filtered down to {len(evaluation_targets)} Asian-relevant evaluation targets")
        print(f"  Total markets (with accepted series): {len(all_markets)}")
        if series_metadata:
            dropped_series = len(result['series_metadata']) - len(series_metadata)
            print(f"  Dropped {dropped_series} rejected series")

        # Save filtered data
        filtered_result = {
            'evaluation_targets': evaluation_targets,
            'all_markets': all_markets,
            'series_metadata': series_metadata
        }
        scraper = PolymarketScraper()
        scraper.save_to_json(filtered_result, FILTERED_DATA_PATH)

    if not evaluation_targets:
        print("✗ No Asian-relevant markets found after filtering. Exiting.")
        sys.exit(1)

    # Step 3: Evaluate markets with LLM
    print(f"\n{'='*80}")
    print("[Step 3] Evaluating markets with LLM (Qwen 2.5 7B)")
    print(f"{'='*80}")
    print(f"  Evaluation targets: {len(evaluation_targets)} (representatives + standalone)")
    print(f"  Total markets (with series): {len(all_markets)}")
    if series_metadata:
        reduction = (1 - len(evaluation_targets) / len(all_markets)) * 100
        print(f"  Efficiency gain: {reduction:.0f}% fewer LLM calls due to series grouping")
    print(f"  Model: Qwen 2.5 7B Instruct")
    print(f"  Estimated time: ~{len(evaluation_targets) * 8 // 60} minutes")
    print()

    evaluator = LLMEvaluator()
    evaluated_targets = evaluator.evaluate_markets_batch(evaluation_targets)

    if not evaluated_targets:
        print("\n✗ No markets were successfully evaluated. Exiting.")
        sys.exit(1)

    # Apply evaluations to all markets (including series members)
    if series_metadata:
        print(f"\n{'='*80}")
        print("Applying evaluations to series markets...")
        print(f"{'='*80}")
        evaluated_markets = apply_evaluation_to_series(all_markets, evaluated_targets, series_metadata)
        print(f"✓ Applied {len(evaluated_targets)} evaluations to {len(evaluated_markets)} total markets")
    else:
        evaluated_markets = evaluated_targets

    # Step 4: Calculate weighted scores
    print(f"\n{'='*80}")
    print("[Step 4] Calculating weighted scores")
    print(f"{'='*80}")

    scorer = MarketScorer()
    scored_markets = scorer.score_evaluated_markets(evaluated_markets)

    print(f"✓ Scored {len(scored_markets)} markets\n")

    # Step 5: Save results
    print(f"{'='*80}")
    print("[Step 5] Saving results")
    print(f"{'='*80}")

    scorer.save_to_json(scored_markets, PROCESSED_JSON_PATH)
    scorer.save_to_csv(scored_markets, PROCESSED_CSV_PATH)

    print(f"✓ Results saved successfully\n")

    # Step 6: Display summary
    print("=" * 80)
    print("🎉 PIPELINE COMPLETE - Top 10 Markets by Score")
    print("=" * 80)

    for i, market in enumerate(scored_markets[:10], 1):
        # Handle volume display
        vol = market.get('volume') or 0
        try:
            vol_str = f"${float(vol):,.0f}"
        except:
            vol_str = f"${vol}"

        print(f"\n{i}. [{market['final_score']}] {market['question'][:70]}")
        print(f"   Volume: {vol_str} | End: {market['end_date']}")
        print(f"   热度:{market['热度传播度']} 文化:{market['文化契合度']} 争议:{market['结果无争议度']} "
              f"对抗:{market['话题对抗性']} 波动:{market['结果波动']}")
        print(f"   📝 {market['reasoning'][:80]}...")

    print("\n" + "=" * 80)
    print("📁 Output Files:")
    print(f"  • JSON: {PROCESSED_JSON_PATH}")
    print(f"  • CSV:  {PROCESSED_CSV_PATH}")
    print(f"\n📊 Summary:")
    print(f"  • Total markets (with series): {len(all_markets)}")
    print(f"  • Evaluation targets: {len(evaluation_targets)}")
    if series_metadata:
        print(f"  • Series groups: {len(series_metadata)}")
        total_series_conditions = sum(m['condition_count'] for m in series_metadata.values())
        print(f"  • Conditions in series: {total_series_conditions}")
    print(f"  • Successfully scored: {len(scored_markets)}")
    print(f"  • Success rate: {(len(scored_markets)/len(all_markets))*100:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
