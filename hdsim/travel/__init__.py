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

from hdsim.core import (DecisionTask, DomainConfig, Household, Member, build_personas,
                        enrich, negotiate, propose, simulate)

from .config import (NHTS, PUGET, TRIP_COUNT, anchor_for, describe_member, label_for,
                     relate_members)
from .facts import generate_facts_list
from .loaders import load_csv, load_example, load_jsonl, load_nhts, load_puget

__all__ = [
    "__version__",
    # re-exported from hdsim.core so a domain user needs one import
    "Household",
    "Member",
    "DecisionTask",
    "DomainConfig",
    "build_personas",
    "enrich",
    "propose",
    "negotiate",
    "simulate",
    "NHTS",
    "PUGET",
    "TRIP_COUNT",
    "anchor_for",
    "describe_member",
    "label_for",
    "relate_members",
    "generate_facts_list",
    "load_csv",
    "load_nhts",
    "load_puget",
    "load_jsonl",
    "load_example",
]
