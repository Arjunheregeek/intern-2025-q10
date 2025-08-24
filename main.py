"""
Main entry point for A/B Testing System for Prompt Optimization
"""

import os
import sys
import subprocess

def run_evaluation():
    """Run the A/B test evaluation"""
    try:
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        runner_path = os.path.join(src_path, 'ab_test_runner.py')
        
        if os.path.exists(runner_path):
            result = subprocess.run([sys.executable, runner_path], 
                                  cwd=src_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Evaluation completed successfully!")
                print(result.stdout)
            else:
                print("Evaluation failed:")
                print(result.stderr)
        else:
            print(f"File not found: {runner_path}")
            
    except Exception as e:
        print(f"Error running evaluation: {e}")

if __name__ == "__main__":
    print("A/B Testing System for Prompt Optimization")
    print("=" * 50)
    run_evaluation()
