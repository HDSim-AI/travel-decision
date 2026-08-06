"""Travel domain tests. No API key, no network, no survey download."""

from hdsim.travel import NHTS, anchor_for, generate_facts_list, load_example


def test_example_household_has_four_members():
    household = load_example()
    assert len(household) == 4
    assert household.household_id == "example"


def test_members_get_readable_labels():
    labels = [m.label for m in load_example()]
    assert labels == ["Head", "Wife", "Son", "Daughter"]


def test_facts_compose_age_and_sex():
    facts = generate_facts_list({"R_AGE_IMP": 44, "R_SEX_IMP": 1})
    assert facts[0] == "I am a 44-year-old man."
    facts = generate_facts_list({"R_AGE_IMP": 9, "R_SEX_IMP": 2})
    assert facts[0] == "I am a 9-year-old girl."


def test_missing_value_codes_render_nothing():
    """NHTS negative codes are unknowns, not facts."""
    assert generate_facts_list({"HOMEOWN": -9, "DRIVER": -1, "WORKER": -8}) == []


def test_roster_relates_members_without_guessing():
    household = load_example()
    household.build_roster(NHTS.describe_member, NHTS.relate_members)
    head = household.member(1).roster
    assert "my spouse or partner" in head
    assert head.count("my child") == 2
    # the son sees a parent and a sibling, and is not described to himself
    son = household.member(3).roster
    assert "my parent" in son and "my sibling" in son


def test_persona_may_not_state_the_outcome():
    assert NHTS.leaks_outcome("I usually make four trips a day") is not None
    assert NHTS.leaks_outcome("I drive to work and back") is None


def test_anchor_reproduces_the_published_lookup():
    """Workers anchor at 4.29, non-workers at 3.40. These are the values behind the paper."""
    assert anchor_for({"WORKER": 1}) == 4.29
    assert anchor_for({"WORKER": 2}) == 3.40
    assert anchor_for({"WORKER": 1, "WRK_HOME": 1}) == 4.29
    assert anchor_for({}) == 3.40           # unknown worker status falls to non-worker


def test_household_ground_truth_is_the_member_sum():
    from hdsim.travel.loaders import _to_household
    rows = [{"PERSONID": 1, "CNTTDTR": 4}, {"PERSONID": 2, "CNTTDTR": 3}]
    assert _to_household("h", rows).ground_truth == 7


def test_uses_the_travel_copb_prompt_not_another_domains():
    """Each domain carries its own prompt. Running the wrong one is a silent wrong answer."""
    assert "Transportation Behavioral Psychologist" in NHTS.copb_system
    assert "{{ANCHOR}}" in NHTS.copb_system
    assert "residential mobility" not in NHTS.copb_system.lower()


def test_every_documented_import_resolves():
    """The README and the examples are executable claims. `hdsim` is a namespace package with
    nothing at top level, so `from hdsim import x` reads fine and fails at runtime."""
    import importlib
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parent.parent
    sources = [root / "README.md", *sorted((root / "examples").glob("*.py"))]
    checked = 0
    for path in sources:
        if not path.is_file():
            continue
        for module, names in re.findall(r"^from (hdsim[\w.]*) import ([^\n#]+)",
                                        path.read_text(), re.MULTILINE):
            mod = importlib.import_module(module)
            for name in (n.strip() for n in names.split(",")):
                assert hasattr(mod, name), f"{path.name}: {module} has no {name!r}"
                checked += 1
    assert checked, "no documented imports found to check"
