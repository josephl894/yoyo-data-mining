"""
Series market handler for Polymarket
Groups related markets (e.g., "Bitcoin hits $X by 2025?") together
"""


def get_event_slug(market):
    """Get event slug that identifies series group"""
    events = market.get('events', [])
    if events and len(events) > 0:
        return events[0].get('slug')
    return None


def get_parent_event_title(market):
    """Get parent event title for series"""
    events = market.get('events', [])
    if events and len(events) > 0:
        return events[0].get('title')
    return None


def group_markets_by_series(markets):
    """
    Group markets into series

    Args:
        markets: List of market dictionaries

    Returns:
        dict: {
            'series': {event_slug: [markets]},
            'standalone': [markets]
        }
    """
    series_groups = {}
    standalone = []

    for market in markets:
        event_slug = get_event_slug(market)

        if event_slug:
            if event_slug not in series_groups:
                series_groups[event_slug] = []
            series_groups[event_slug].append(market)
        else:
            standalone.append(market)

    # Separate actual series (2+ markets) from single markets with events
    actual_series = {}
    for slug, group_markets in series_groups.items():
        if len(group_markets) > 1:
            actual_series[slug] = group_markets
        else:
            standalone.extend(group_markets)

    return {
        'series': actual_series,
        'standalone': standalone
    }


def get_series_representative(series_markets):
    """
    Get best representative market from a series for evaluation

    Args:
        series_markets: List of markets in same series

    Returns:
        Market dictionary (highest volume one)
    """
    if not series_markets:
        return None

    # Sort by volume, return highest
    sorted_markets = sorted(
        series_markets,
        key=lambda x: float(x.get('volume') or 0),
        reverse=True
    )

    return sorted_markets[0]


def calculate_series_metadata(series_markets):
    """
    Calculate aggregate metadata for a series

    Args:
        series_markets: List of markets in same series

    Returns:
        dict with series metadata
    """
    if not series_markets:
        return {}

    # Sum volumes
    total_volume = sum(float(m.get('volume') or 0) for m in series_markets)

    # Get common data
    parent_title = get_parent_event_title(series_markets[0])
    event_slug = get_event_slug(series_markets[0])

    # Get all questions
    conditions = [m.get('question') for m in series_markets]

    return {
        'event_slug': event_slug,
        'parent_title': parent_title,
        'condition_count': len(series_markets),
        'total_volume': total_volume,
        'conditions': conditions,
        'markets': series_markets
    }


def prepare_markets_for_evaluation(markets):
    """
    Prepare markets for efficient evaluation
    - Group series together
    - Select representatives for series
    - Keep all standalone markets

    Args:
        markets: List of market dictionaries

    Returns:
        dict: {
            'evaluation_targets': [markets to evaluate],
            'series_metadata': {event_slug: metadata},
            'all_markets': [all original markets with metadata added]
        }
    """
    grouped = group_markets_by_series(markets)

    evaluation_targets = []
    series_metadata = {}

    # Process series
    for event_slug, series_markets in grouped['series'].items():
        # Get representative for evaluation
        rep = get_series_representative(series_markets)
        if rep:
            # Mark as series representative
            rep['is_series_representative'] = True
            rep['series_condition_count'] = len(series_markets)
            evaluation_targets.append(rep)

            # Store metadata
            series_metadata[event_slug] = calculate_series_metadata(series_markets)

            # Mark all markets in series
            for m in series_markets:
                m['is_part_of_series'] = True
                m['event_slug'] = event_slug
                m['parent_event_title'] = get_parent_event_title(m)

    # Add standalone markets
    for m in grouped['standalone']:
        m['is_part_of_series'] = False
        evaluation_targets.append(m)

    # Collect all markets with metadata
    all_markets = []
    for series_markets in grouped['series'].values():
        all_markets.extend(series_markets)
    all_markets.extend(grouped['standalone'])

    print(f"\nSeries Analysis:")
    print(f"  Series groups: {len(grouped['series'])}")
    print(f"  Total conditions in series: {sum(len(m) for m in grouped['series'].values())}")
    print(f"  Standalone markets: {len(grouped['standalone'])}")
    print(f"  Total markets: {len(all_markets)}")
    print(f"  Evaluation targets: {len(evaluation_targets)} "
          f"({(1 - len(evaluation_targets)/len(all_markets))*100:.0f}% reduction)")

    return {
        'evaluation_targets': evaluation_targets,
        'series_metadata': series_metadata,
        'all_markets': all_markets
    }


def apply_evaluation_to_series(all_markets, evaluated_markets, series_metadata):
    """
    Apply evaluation scores from representatives to all markets in series

    Args:
        all_markets: All markets (including series conditions)
        evaluated_markets: List of (market, evaluation) tuples
        series_metadata: Series metadata dict

    Returns:
        List of (market, evaluation) tuples for ALL markets
    """
    # Create lookup: market id -> evaluation
    eval_lookup = {}
    for market, evaluation in evaluated_markets:
        market_id = market.get('id') or market.get('conditionId')
        eval_lookup[market_id] = evaluation

    # Apply to all markets
    results = []

    for market in all_markets:
        market_id = market.get('id') or market.get('conditionId')

        if market_id in eval_lookup:
            # Direct evaluation
            results.append((market, eval_lookup[market_id]))
        elif market.get('is_part_of_series'):
            # Find series representative's evaluation
            event_slug = market.get('event_slug')
            if event_slug in series_metadata:
                series_markets = series_metadata[event_slug]['markets']
                rep = get_series_representative(series_markets)
                rep_id = rep.get('id') or rep.get('conditionId')

                if rep_id in eval_lookup:
                    # Use representative's evaluation
                    results.append((market, eval_lookup[rep_id]))

    return results
