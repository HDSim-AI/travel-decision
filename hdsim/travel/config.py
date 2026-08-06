"""The travel domain.

What a household is deciding, how its survey record reads in English, and what a typical household
like it does. Everything else comes from `hdsim`.
"""

from __future__ import annotations

import json
from pathlib import Path

from hdsim.core import DecisionTask, DomainConfig

from .copb import ACTOR_SYSTEM_PROMPT, COPB_USER_TEMPLATE
from .facts import generate_facts_list

# Behavioural tendencies offered to the persona as a leaning, not a constraint. Carried over from
# the research pipeline so the wording is the wording the published results used.
MARKERS = json.loads((Path(__file__).parent / "attitudinal_markers.json").read_text())

# --- what is being decided ------------------------------------------------------------------------

TRIP_COUNT = DecisionTask(
    name="trip_count",
    domain="household travel",
    context="the recorded travel day",
    target_description=(
        "the total number of one-way trips every member of the household will make"
    ),
    unit="trips",
    final_label="FINAL_VALUE",
    value_type=int,
    value_range=(0, 30),
)

# --- empirical anchors ------------------------------------------------------------------------------
# Mean trips per person, computed from NHTS 2009 (308,901 person records).
#
# These are the values used to produce the published results, and they are reproduced here exactly
# so this package returns what the paper reports. Two properties are worth knowing before relying
# on them. They come from 2009 and are applied to later travel years, and the lookup below reaches
# only three of the thirteen entries. Both are noted rather than fixed, because changing an anchor
# changes every persona built with it, and no evaluation of a replacement has been run.
ANCHORS = {
    "worker_commuter": 4.29,
    "worker_wfh": 4.29,
    "worker": 4.29,
    "non_worker": 3.40,
    "urban": 3.86,
    "rural": 3.58,
    "zero_vehicle": 2.30,
    "has_vehicle": 3.83,
    "senior": 3.36,
    "non_senior": 3.94,
    "worker_urban": 4.40,
    "worker_rural": 4.06,
    "global_mean": 3.78,
}


def _int(record: dict, key: str) -> int | None:
    value = record.get(key)
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return None
    return None if number < 0 else number


def anchor_for(record: dict) -> float:
    """The expected trip count for someone with this profile.

    Reproduces the published lookup: worker status first, then whether that worker is at home.
    The anchor is a starting expectation for the persona to reason against, not a threshold and
    not a prediction.
    """
    is_worker = _int(record, "WORKER") == 1
    is_wfh = is_worker and _int(record, "WRK_HOME") == 1
    if is_worker:
        return ANCHORS["worker_wfh"] if is_wfh else ANCHORS["worker_commuter"]
    return ANCHORS["non_worker"]


# --- how members are described to each other ---------------------------------------------------------

_RELATION = {
    1: "the head of the household",
    2: "the head of the household's spouse or partner",
    3: "a child of the household head",
    4: "a parent of the household head",
    5: "a sibling of the household head",
    6: "a relative of the household head",
    7: "a non-relative living in the household",
}


def label_for(record: dict) -> str:
    """A short speaker name for transcripts, so a discussion reads "Mother" not "Member 2"."""
    relation = _int(record, "R_RELAT")
    male = _int(record, "R_SEX_IMP") == 1
    age = _int(record, "R_AGE_IMP")
    if relation == 1:
        return "Head"
    if relation == 2:
        return "Husband" if male else "Wife"
    if relation == 3:
        if age is not None and age >= 18:
            return "Adult son" if male else "Adult daughter"
        return "Son" if male else "Daughter"
    if relation == 4:
        return "Father" if male else "Mother"
    if relation == 5:
        return "Brother" if male else "Sister"
    return "Relative" if relation == 6 else "Housemate"


def describe_member(member) -> str:
    """One line about a person, for their housemates to read."""
    record = member.record
    age = _int(record, "R_AGE_IMP")
    male = _int(record, "R_SEX_IMP") == 1
    if age is None:
        who = "an adult"
    elif age < 18:
        who = f"a {age}-year-old " + ("boy" if male else "girl")
    else:
        who = f"a {age}-year-old " + ("man" if male else "woman")

    notes = []
    if _int(record, "WORKER") == 1:
        notes.append("works full time" if _int(record, "WKFTPT") == 1 else "works")
    elif _int(record, "WORKER") == 2:
        notes.append("does not work")
    if _int(record, "SCHTYP") is not None:
        notes.append("in school")
    driver = _int(record, "DRIVER")
    if driver == 1:
        notes.append("a licensed driver")
    elif driver == 2:
        notes.append("not a licensed driver")
    if _int(record, "MEDCOND") == 1:
        notes.append("has a medical condition affecting travel")
    return who + (", " + ", ".join(notes) if notes else "")


def relate_members(me, other) -> str:
    """How `other` relates to `me`.

    R_RELAT records each person's relation to the household reference person, not to each other, so
    member-to-member relations are derived. Where the record does not determine one, say something
    weaker and true rather than guess: a roster that invents a relationship causes exactly the
    confusion it exists to prevent.
    """
    a, b = _int(me.record, "R_RELAT"), _int(other.record, "R_RELAT")
    pairs = {
        (1, 2): "my spouse or partner", (2, 1): "my spouse or partner",
        (1, 3): "my child", (3, 1): "my parent",
        (1, 4): "my parent", (4, 1): "my child",
        (1, 5): "my sibling", (5, 1): "my sibling",
        (3, 3): "my sibling",
        (3, 4): "my grandparent", (4, 3): "my grandchild",
    }
    known = pairs.get((a, b))
    if known:
        return known
    age = _int(other.record, "R_AGE_IMP")
    return ("another child in my household" if age is not None and age < 18
            else "another adult in my household")


_ROLE_HINT = {1: "head of household", 2: "spouse/partner", 3: "child",
              4: "parent", 5: "sibling", 6: "other relative", 7: "non-relative"}


def copb_fields(record: dict) -> dict:
    """Values the Chain-of-Planned-Behaviour template needs, as the research code derived them."""
    driver = _int(record, "DRIVER")
    return {
        "role_hint": _ROLE_HINT.get(_int(record, "R_RELAT"), "household member"),
        "veh_count": record.get("HHVEHCNT", "unknown"),
        "driver_status": "yes" if driver == 1 else ("no" if driver == 2 else "unknown"),
    }


# --- the domain -------------------------------------------------------------------------------------

NHTS = DomainConfig(
    name="nhts",
    task=TRIP_COUNT,
    facts_fn=generate_facts_list,
    anchors=ANCHORS,
    anchor_for=anchor_for,
    copb_system=ACTOR_SYSTEM_PROMPT,
    copb_user=COPB_USER_TEMPLATE,
    markers=MARKERS,
    copb_fields=copb_fields,
    # Persona text is written before the household decides, so it must not state a trip count.
    # This is the published pattern set and nothing more. An earlier version also banned
    # "travel day", which rejected every real NHTS persona: TRAVDAY renders as "The day I
    # recorded my travel was a Monday", which is survey context, not the outcome.
    banned_patterns=[r"\btrips?\b"],
    describe_member=describe_member,
    relate_members=relate_members,
)

# Puget Sound uses the same decision and the same rendering; only the loader differs.
PUGET = DomainConfig(
    name="puget",
    task=TRIP_COUNT,
    facts_fn=generate_facts_list,
    anchors=ANCHORS,
    anchor_for=anchor_for,
    copb_system=ACTOR_SYSTEM_PROMPT,
    copb_user=COPB_USER_TEMPLATE,
    markers=MARKERS,
    copb_fields=copb_fields,
    banned_patterns=[r"\btrips?\b"],
    describe_member=describe_member,
    relate_members=relate_members,
)
