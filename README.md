# A/B Testing System for Prompt Optimization

An automated evaluation system to compare two different prompt strategies using statistical analysis and performance metrics.

## Overview

This system tests 10 diverse user queries against two different system prompts (A vs B) to determine which performs better for different query types.

## Project Structure

```
d:\Downloads\ASSIGN\
├── data/
│   └── evaluation_queries.csv    # 10 test queries with metadata
├── src/
│   ├── system_prompts.py        # Two prompt strategies
│   └── ab_test_runner.py        # Automated evaluation
├── notebooks/
│   └── analysis.ipynb          # Statistical analysis & visualizations
├── results/
│   └── results.csv             # Evaluation results (generated)
├── main.py                     # Simple entry point - runs evaluation
├── requirements.txt            # Dependencies
└── README.md                  # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start
```bash
# Run the evaluation directly
python main.py
```

### Manual Usage
```bash
# Run A/B test evaluation manually
cd src
python ab_test_runner.py

# View results in Jupyter notebook
cd notebooks
jupyter notebook analysis.ipynb
```

## What main.py does

The `main.py` file is a simple entry point that:
1. Runs the A/B test evaluation automatically
2. Displays results or error messages
3. No menus or extra options - just executes the evaluation

## Evaluation Metrics

- **Quality Score**: Manual rating (1-5 scale)
- **Latency**: Response time in milliseconds
- **Statistical Significance**: T-test comparisons
- **Category Performance**: Breakdown by query type

## Key Findings

Results show statistical significance in performance differences between prompts, with each excelling in predicted areas. See `analysis.ipynb` for detailed findings.

## File Descriptions

### evaluation_queries.csv
10 diverse queries (5 favoring each prompt type) with categories and expected difficulty levels.

### system_prompts.py
Implementation of both prompt strategies with clear documentation of differences.

### ab_test_runner.py
Automated system that runs all queries against both prompts and measures performance.

### analysis.ipynb
Jupyter notebook with:
- Statistical comparisons (t-tests)
- Visualizations (box plots, scatter plots)
- Performance recommendations
- Category-wise analysis

### results.csv
Complete evaluation results including:
- Query text and metadata
- Prompt version (A/B)
- Response quality scores
- Latency measurements
- Timestamps
- Timestamps
- Response quality scores
- Latency measurements
- Timestamps
