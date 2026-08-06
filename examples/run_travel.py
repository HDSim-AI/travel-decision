"""Simulate the bundled example household.

    pip install -e .
    python examples/run_travel.py        # needs HDSIM_API_KEY
"""

from hdsim.travel import NHTS, build_personas, load_example, simulate

household = load_example()
print(f"Household {household.household_id}: {[m.label for m in household]}")

build_personas(household, NHTS)
for member in household:
    print(f"\n{member.label}\n  {member.capsule}")

simulate(household, NHTS)

print("\nOpening positions")
for member in household:
    print(f"  {member.label:<10} {member.proposal_value}")
print(f"  sum before discussion: {household.proposal_sum}")

print("\nDiscussion")
for turn in household.transcript:
    print(f"  [{turn['round']}] {turn['speaker']}: {turn['text']}")

print(f"\nAgreed: {household.consensus_value} trips")
