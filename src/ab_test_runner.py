"""
A/B Test Runner for Prompt Optimization
Automatically evaluates queries against two prompt strategies.
"""

import pandas as pd
import time
import csv
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List
from system_prompts import SystemPrompts


@dataclass
class EvaluationResult:
    query: str
    prompt_version: str  # "A" or "B"
    response: str
    score: int  # 1-5 manual quality rating
    latency_ms: float
    timestamp: datetime
    category: str
    expected_difficulty: str
    favors_prompt: str


class ABTestRunner:

    def __init__(self):
        self.results: List[EvaluationResult] = []
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "results"
        )

        # Create directories if they don't exist
        os.makedirs(self.results_dir, exist_ok=True)

    def simulate_llm_call(
        self, system_prompt: str, user_query: str
    ) -> tuple[str, float]:
        """Simulate LLM API call with response patterns and latency."""
        if "concise" in system_prompt.lower():
            response = self._generate_concise_response(user_query)
            simulated_latency = 0.2 + (hash(user_query) % 600) / 1000
        else:
            response = self._generate_detailed_response(user_query)
            simulated_latency = 0.8 + (hash(user_query) % 700) / 1000

        time.sleep(0.01)
        latency_ms = simulated_latency * 1000
        return response, latency_ms

    def _generate_concise_response(self, query: str) -> str:
        """Generate simulated concise responses"""
        responses = {
            "capital of France": "Paris.",
            "machine learning": "Machine learning is AI that learns from data to make predictions.",
            "Python for loop": "for i in range(10): print(i)",
            "benefits of exercise": "1. Improves health 2. Boosts mood 3. Increases energy",
            "New York time zone": "Eastern Time (ET).",
        }

        for key, response in responses.items():
            if key in query.lower():
                return response
        return "Brief, direct answer to your question."

    def _generate_detailed_response(self, query: str) -> str:
        """Generate simulated detailed responses"""
        responses = {
            "quantum computing": "Quantum computing harnesses quantum mechanical phenomena like superposition and entanglement to process information exponentially faster than classical computers for certain problems.",
            "time traveler": "Dr. Sarah Chen activated her temporal device but materialized in 1885 instead of 2025. The device was damaged, and she must rebuild it using 19th-century materials while avoiding paradoxes.",
            "remote work": "Remote work offers flexibility and eliminates commuting but presents challenges like isolation and communication difficulties. Success requires discipline and clear boundaries.",
        }

        for key, response in responses.items():
            if key in query.lower():
                return response
        return "This is a comprehensive, detailed response that thoroughly addresses your question with context and examples."

    def run_evaluation(self) -> None:
        """Run complete A/B test evaluation"""
        print("Starting A/B Test Evaluation...")
        print("=" * 50)

        # Load queries
        queries_path = os.path.join(self.data_dir, "evaluation_queries.csv")
        queries_df = pd.read_csv(queries_path)

        for _, row in queries_df.iterrows():
            query = row["query"]
            print(f"\nTesting: {query[:50]}...")

            for version in ["A", "B"]:
                system_prompt = SystemPrompts.get_prompt(version)
                response, latency_ms = self.simulate_llm_call(system_prompt, query)
                score = self._simulate_quality_score(
                    query, version, row["favors_prompt"]
                )

                result = EvaluationResult(
                    query=query,
                    prompt_version=version,
                    response=response,
                    score=score,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(),
                    category=row["category"],
                    expected_difficulty=row["expected_difficulty"],
                    favors_prompt=row["favors_prompt"],
                )
                self.results.append(result)

                print(f"  Prompt {version}: {score}/5 quality, {latency_ms:.1f}ms")

        self.save_results()
        print(f"\nEvaluation complete! Results saved to results/results.csv")

    def _simulate_quality_score(self, query: str, version: str, favors: str) -> int:
        """Simulate quality scoring"""
        base_score = 3
        if version == favors:
            base_score += 1
        else:
            base_score -= 0.5

        import random

        base_score += random.uniform(-0.3, 0.3)
        return max(1, min(5, round(base_score)))

    def save_results(self) -> None:
        """Save results to CSV file"""
        results_path = os.path.join(self.results_dir, "results.csv")
        with open(results_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "query",
                    "prompt_version",
                    "response",
                    "score",
                    "latency_ms",
                    "timestamp",
                    "category",
                    "expected_difficulty",
                    "favors_prompt",
                ]
            )

            for result in self.results:
                writer.writerow(
                    [
                        result.query,
                        result.prompt_version,
                        result.response,
                        result.score,
                        result.latency_ms,
                        result.timestamp.isoformat(),
                        result.category,
                        result.expected_difficulty,
                        result.favors_prompt,
                    ]
                )


if __name__ == "__main__":
    runner = ABTestRunner()
    runner.run_evaluation()
