#!/usr/bin/env python
"""
Direct capture for verification evidence. No shell pipes.
Usage examples:
  DATA_FOLDER=~/data TARGET_BASE_URL=https://theinternetparty.us \
    pipenv run python scripts/capture_scenario.py --scenario phase2_mixed \
    --n-voters 200 --n-readers 10 --out "$SCRATCH/scale-200-mixed.log"

Exits 1 on any error; writes full JSON to --out.
"""
import argparse
import json
import os
import sys

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', required=True, choices=['full_cycle', 'phase2_mixed', 's_gov_full'])
    parser.add_argument('--base-url', default=os.environ.get('TARGET_BASE_URL', 'https://theinternetparty.us'))
    parser.add_argument('--n-voters', type=int, default=200)
    parser.add_argument('--n-readers', type=int, default=10)
    parser.add_argument('--reader-rounds', type=int, default=1)
    parser.add_argument('--concurrency', type=int, default=10)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cleanup', action='store_true', default=True)
    args = parser.parse_args()

    from npc import scenarios as sc

    base_url = args.base_url
    try:
        if args.scenario == 'phase2_mixed':
            m = sc.run_phase2_mixed(
                base_url=base_url,
                n_voters=args.n_voters,
                n_readers=args.n_readers,
                reader_rounds=args.reader_rounds,
                concurrency=args.concurrency,
                promote=True,
                cleanup=args.cleanup
            )
        elif args.scenario == 's_gov_full':
            m = sc.run_s_gov_full(
                base_url=base_url,
                n_voters=args.n_voters,
                concurrency=args.concurrency,
                promote=True,
                cleanup=args.cleanup
            )
        else:
            m = sc.run_full_cycle(
                base_url=base_url,
                n_voters=args.n_voters,
                concurrency=args.concurrency,
                promote=True,
                cleanup=args.cleanup
            )
        os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(m, f, indent=2, default=str)
        print(f"Written {args.out} ({os.path.getsize(args.out)} bytes)")
        # Basic sanity for 200 mixed
        if args.scenario == 'phase2_mixed' and args.n_voters >= 100:
            if m.get('votes_ok') != args.n_voters or not m.get('tallies_match_expected'):
                print("WARNING: metrics may not meet expectations", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Write partial error info if possible
        try:
            with open(args.out, 'w') as f:
                json.dump({"error": str(e)}, f)
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    main()
