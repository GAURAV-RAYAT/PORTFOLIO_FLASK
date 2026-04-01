"""
Phase-1 Monitoring Agent runner.

Usage:
  python scripts/run_monitoring_agent.py
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app
from utils.monitoring_agent import run_monitoring_cycle


def main():
    with app.app_context():
        results = run_monitoring_cycle()
        print("Monitoring cycle completed:")
        for item in results:
            print(item)


if __name__ == "__main__":
    main()
