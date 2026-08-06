"""Household travel decisions.

Adds the travel domain to `hdsim`: how a household travel survey record reads in English, what a
typical household of that kind does, and how the members are introduced to each other.

    from hdsim import build_personas, simulate
    from hdsim.travel import NHTS, load_example

    household = load_example()
    build_personas(household, NHTS)
    simulate(household, NHTS)
    print(household.consensus_value)

Real data:

    from hdsim.travel import load_nhts
    households = load_nhts("perpub.csv", min_members=2, max_households=100)

NHTS 2017 is at https://nhts.ornl.gov/downloads. No survey data ships with this package.
"""

from __future__ import annotations

__version__ = "0.1.0.dev0"

from hdsim.core import (
                        DecisionTask,
                        DomainConfig,
                        Household,
                        Member,
                        build_personas,
                        enrich,
                        negotiate,
                        propose,
                        simulate,
)

from .config import NHTS, PUGET, TRIP_COUNT, anchor_for, describe_member, label_for, relate_members
from .facts import generate_facts_list
from .loaders import load_csv, load_example, load_jsonl, load_nhts, load_puget

# Household, Member, DecisionTask, DomainConfig and the pipeline functions are re-exported from
# hdsim.core, so a domain user needs one import rather than two.
__all__ = [
    "NHTS",
    "PUGET",
    "TRIP_COUNT",
    "DecisionTask",
    "DomainConfig",
    "Household",
    "Member",
    "__version__",
    "anchor_for",
    "build_personas",
    "describe_member",
    "enrich",
    "generate_facts_list",
    "label_for",
    "load_csv",
    "load_example",
    "load_jsonl",
    "load_nhts",
    "load_puget",
    "negotiate",
    "propose",
    "relate_members",
    "simulate",
]
