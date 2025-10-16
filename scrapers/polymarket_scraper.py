"""
Polymarket scraper using Gamma Markets API
Fetches markets with proper filtering and sorting
"""
import json
import sys
import os
import requests
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.market_filter import is_asian_relevant, get_matching_keywords
from scrapers.series_handler import prepare_markets_for_evaluation


class PolymarketScraper:
    def __init__(self, gamma_api_url="https://gamma-api.polymarket.com"):
        """Initialize the Polymarket scraper"""
        self.gamma_api_url = gamma_api_url

    def fetch_markets_gamma(self, limit=1000, min_days_future=30, closed=False):
        """
        Fetch markets from Gamma Markets API with filtering

        Args:
            limit: Number of markets to fetch
            min_days_future: Minimum days until market expires
            closed: Whether to include closed markets

        Returns:
            List of market dictionaries
        """
        # Calculate minimum end date
        end_date_min = (datetime.now() + timedelta(days=min_days_future)).strftime('%Y-%m-%d')

        # Build query parameters
        params = {
            'closed': str(closed).lower(),
            'end_date_min': end_date_min,
            'limit': min(limit, 100),  # API likely has max per request
            'order': 'volume',
            'ascending': 'false'
        }

        markets_list = []
        offset = 0

        print(f"Fetching from Gamma API:")
        print(f"  - closed={closed}")
        print(f"  - end_date_min={end_date_min}")
        print(f"  - order=volume (desc)")

        while len(markets_list) < limit:
            try:
                # Add offset for pagination
                params['offset'] = offset

                # Make request
                url = f"{self.gamma_api_url}/markets"
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Handle different response formats
                if isinstance(data, list):
                    markets_data = data
                elif isinstance(data, dict) and 'data' in data:
                    markets_data = data['data']
                else:
                    markets_data = data

                if not markets_data:
                    print(f"No more markets available (fetched {len(markets_list)} total)")
                    break

                # Add markets up to limit
                remaining = limit - len(markets_list)
                markets_list.extend(markets_data[:remaining])

                print(f"  Fetched batch: {len(markets_data)} markets (total: {len(markets_list)})")

                # Check if we have enough
                if len(markets_list) >= limit:
                    break

                # If we got fewer than requested, we've reached the end
                if len(markets_data) < params['limit']:
                    print(f"Reached end of available markets")
                    break

                # Update offset
                offset += len(markets_data)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching from Gamma API: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        print(f"✓ Fetched {len(markets_list)} markets from Gamma API")
        return markets_list

    def is_active_future_market(self, market, min_days_future=30):
        """
        Check if market is active and expires in the future

        Args:
            market: Market dictionary
            min_days_future: Minimum days in the future (default 30)

        Returns:
            Boolean indicating if market meets criteria
        """
        # NOTE: Polymarket API returns active=True for many closed markets
        # So we primarily rely on the end_date check

        # Check end date
        end_date_iso = market.get('end_date_iso')
        if not end_date_iso:
            return False

        try:
            # Parse ISO date
            end_date = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))

            # Calculate cutoff (today + min_days_future)
            cutoff_date = datetime.now(end_date.tzinfo) + timedelta(days=min_days_future)

            # Check if market expires after cutoff
            is_future = end_date >= cutoff_date

            # Additional check: if closed=False, it's more likely to be active
            # But don't exclude if closed=True since API data seems inconsistent
            return is_future

        except Exception as e:
            print(f"Error parsing date for market: {e}")
            return False

    def filter_active_future_markets(self, markets, min_days_future=30):
        """
        Filter for active markets expiring in the future

        Args:
            markets: List of market dictionaries
            min_days_future: Minimum days in the future

        Returns:
            Filtered list of markets
        """
        filtered = [m for m in markets if self.is_active_future_market(m, min_days_future)]
        print(f"Filtered to {len(filtered)} active future markets (from {len(markets)})")
        return filtered

    def filter_asian_markets(self, markets):
        """
        Filter for markets relevant to Asian audience

        Args:
            markets: List of market dictionaries

        Returns:
            Filtered list of markets with Asian relevance
        """
        filtered = []
        for market in markets:
            if is_asian_relevant(market):
                # Add matching keywords to market data
                market['asian_keywords'] = get_matching_keywords(market)
                filtered.append(market)

        print(f"Filtered to {len(filtered)} Asian-relevant markets (from {len(markets)})")
        return filtered

    def sort_by_volume(self, markets):
        """
        Sort markets by volume (descending - highest first)

        Args:
            markets: List of market dictionaries

        Returns:
            Sorted list of markets
        """
        # Handle None volumes by treating as 0
        sorted_markets = sorted(markets, key=lambda x: x.get('volume') or 0, reverse=True)
        print(f"Sorted {len(sorted_markets)} markets by volume")
        return sorted_markets

    def fetch_filtered_markets(self, target=1000, min_days_future=30, handle_series=True):
        """
        Fetch markets with all filters applied using Gamma API:
        1. Fetch from Gamma API (already filtered for active + future + sorted by volume)
        2. Filter for Asian relevance
        3. Group series markets
        4. Return markets optimized for evaluation

        Args:
            target: Target number of unique topics/series
            min_days_future: Minimum days until expiration
            handle_series: Whether to group series markets

        Returns:
            dict: {
                'evaluation_targets': markets to evaluate,
                'all_markets': all markets including series conditions,
                'series_metadata': series grouping info
            }
        """
        print(f"\n{'='*80}")
        print(f"Fetching {target} unique Asian-relevant markets...")
        print(f"{'='*80}\n")

        # Fetch more to account for series expansion and filtering
        # Target 1000 unique topics might expand to 1500-2000 conditions
        initial_fetch = min(target * 6, 6000)

        # Step 1: Fetch from Gamma API (already filtered and sorted)
        print(f"[1/3] Fetching {initial_fetch} markets from Gamma API...")
        print(f"      (Active, expiring ≥{min_days_future} days, sorted by volume)")
        raw_markets = self.fetch_markets_gamma(
            limit=initial_fetch,
            min_days_future=min_days_future,
            closed=False
        )

        if not raw_markets:
            print("No markets fetched from Gamma API!")
            return {'evaluation_targets': [], 'all_markets': [], 'series_metadata': {}}

        # Step 2: Filter for Asian relevance
        print(f"\n[2/3] Filtering for Asian-relevant markets (738 keywords)...")
        asian_markets = self.filter_asian_markets(raw_markets)

        if not asian_markets:
            print("No Asian-relevant markets found!")
            return {'evaluation_targets': [], 'all_markets': [], 'series_metadata': {}}

        # Step 3: Handle series grouping
        if handle_series:
            print(f"\n[3/3] Grouping series markets for efficient evaluation...")
            prepared = prepare_markets_for_evaluation(asian_markets)

            # Limit to target number of evaluation targets
            evaluation_targets = prepared['evaluation_targets'][:target]

            # Filter all_markets to only those we're evaluating or in their series
            eval_ids = {m.get('id') or m.get('conditionId') for m in evaluation_targets}
            eval_slugs = {m.get('event_slug') for m in evaluation_targets if m.get('is_part_of_series')}

            filtered_all = [
                m for m in prepared['all_markets']
                if (m.get('id') or m.get('conditionId')) in eval_ids
                or m.get('event_slug') in eval_slugs
            ]

            result = {
                'evaluation_targets': evaluation_targets,
                'all_markets': filtered_all,
                'series_metadata': prepared['series_metadata']
            }
        else:
            # No series handling - treat all markets independently
            final_markets = asian_markets[:target]
            result = {
                'evaluation_targets': final_markets,
                'all_markets': final_markets,
                'series_metadata': {}
            }

        print(f"\n{'='*80}")
        print(f"✓ Results:")
        print(f"  Evaluation targets: {len(result['evaluation_targets'])}")
        print(f"  Total markets (with series): {len(result['all_markets'])}")
        print(f"{'='*80}\n")

        return result

    def save_to_json(self, markets, filepath):
        """
        Save markets to JSON file

        Args:
            markets: List of market dictionaries
            filepath: Path to save JSON file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(markets, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(markets)} markets to {filepath}")


def main():
    """Test the scraper with Gamma API filtering"""
    scraper = PolymarketScraper()

    # Test with 50 markets
    print("Testing Gamma API scraper with target of 50 Asian markets...")
    markets = scraper.fetch_filtered_markets(target=50, min_days_future=30)

    if markets:
        scraper.save_to_json(markets, 'data/raw/scraped_markets_test.json')

        # Print sample market info
        print("\n" + "="*80)
        print("Sample markets:")
        print("="*80)
        for i, market in enumerate(markets[:3], 1):
            # Handle volume (might be string, float, or None)
            vol = market.get('volume') or 0
            try:
                vol_str = f"${float(vol):,.0f}"
            except:
                vol_str = f"${vol}"

            print(f"\n{i}. {market.get('question', 'N/A')[:70]}")
            print(f"   Volume: {vol_str}")
            print(f"   End Date: {market.get('end_date_iso', market.get('endDate', 'N/A'))}")
            print(f"   Asian Keywords: {', '.join(market.get('asian_keywords', [])[:5])}")
    else:
        print("No markets found!")


if __name__ == "__main__":
    main()
