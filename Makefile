.PHONY: help clean clean-all run test install

# Default target
help:
	@echo "Polymarket Data Mining Pipeline"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run              - Clean cache and run pipeline (default: 1000 markets)"
	@echo "  make run SCRAPE=10000 - Run pipeline with custom number of markets"
	@echo "  make run-fresh        - Clean all cache and run fresh pipeline"
	@echo "  make clean            - Remove cached filter/processed files"
	@echo "  make clean-all        - Remove ALL cached files (including scraped)"
	@echo "  make test             - Run with 100 markets (quick test)"
	@echo "  make install          - Install Python dependencies"
	@echo "  make help             - Show this help message"

# Clean cached filter and processed files (keeps raw scraped data)
clean:
	@echo "Cleaning cached filter and processed files..."
	@rm -f data/raw/filtered_markets_*.json
	@rm -f data/processed/evaluated_markets_*.json
	@rm -f data/processed/evaluated_markets_*.csv
	@echo "✓ Cache cleaned!"

# Clean ALL cached files including raw scraped data
clean-all:
	@echo "Cleaning ALL cached files..."
	@rm -f data/raw/scraped_markets_*.json
	@rm -f data/raw/filtered_markets_*.json
	@rm -f data/processed/evaluated_markets_*.json
	@rm -f data/processed/evaluated_markets_*.csv
	@echo "✓ All cache cleaned!"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	@pip3 install --user requests ollama pydantic pandas rich openai
	@echo "✓ Dependencies installed!"

# Run pipeline (clean first)
# Usage: make run SCRAPE=10000 (default: 1000)
run: clean
	@echo "Starting pipeline..."
	@if [ -n "$(SCRAPE)" ]; then \
		sed -i "s/NUM_MARKETS = [0-9]*/NUM_MARKETS = $(SCRAPE)/" main.py; \
		echo "Set NUM_MARKETS to $(SCRAPE)"; \
	fi
	@python3 main.py

# Run full clean + pipeline
# Usage: make run-fresh SCRAPE=10000 (default: 1000)
run-fresh: clean-all
	@echo "Starting fresh pipeline (no cache)..."
	@if [ -n "$(SCRAPE)" ]; then \
		sed -i "s/NUM_MARKETS = [0-9]*/NUM_MARKETS = $(SCRAPE)/" main.py; \
		echo "Set NUM_MARKETS to $(SCRAPE)"; \
	fi
	@python3 main.py

# Quick test with 100 markets
test: clean
	@echo "Running quick test (100 markets)..."
	@sed -i 's/NUM_MARKETS = [0-9]*/NUM_MARKETS = 100/' main.py
	@python3 main.py
	@sed -i 's/NUM_MARKETS = 100/NUM_MARKETS = 1000/' main.py
	@echo "✓ Test complete! (Reset to 1000 markets)"
