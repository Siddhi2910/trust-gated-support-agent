#!/usr/bin/env python3
"""CLI wrapper for TrustGatedPipeline.
Reads JSON payload from stdin: {"text": "...", "conversation_id": null, "tweet_id": null}
Writes JSON response to stdout.
"""

import sys
import os
import json

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.trust.pipeline import TrustGatedPipeline

def main():
    try:
        input_data = json.load(sys.stdin)
        text = input_data.get("text", "")
        cid = input_data.get("conversation_id")
        tid = input_data.get("tweet_id")

        pipeline = TrustGatedPipeline()
        result = pipeline.process(query_text=text, conversation_id=cid, tweet_id=tid)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
