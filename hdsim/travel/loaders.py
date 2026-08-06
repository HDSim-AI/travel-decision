"""Survey loaders.

No survey data ships with this package. NHTS and the Puget Sound household travel survey are both
public, and both have terms attached, so the loaders read files you download yourself.

    NHTS 2017          https://nhts.ornl.gov/downloads
    Puget Sound        https://household-travel-survey-psrc.hub.arcgis.com

For a first run you do not need either. `load_example()` returns a household built into the
package, which is enough to see the pipeline work.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from hdsim.core import Household, Member

from .config import label_for

HOUSEHOLD_KEY = "HOUSEID"
PERSON_KEY = "PERSONID"
TARGET = "CNTTDTR"


def _to_household(household_id: str, rows: list[dict]) -> Household:
    members = []
    for row in sorted(rows, key=lambda r: r.get(PERSON_KEY, 0)):
        members.append(Member(
            person_id=int(row.get(PERSON_KEY, len(members) + 1)),
            record=row,
            label=label_for(row),
        ))
    truth = None
    values = [row.get(TARGET) for row in rows if row.get(TARGET) is not None]
    if values:
        try:
            truth = float(sum(float(v) for v in values))
        except (TypeError, ValueError):
            truth = None
    return Household(household_id=str(household_id), members=members, ground_truth=truth)


def load_csv(path: str | Path, *, household_key: str = HOUSEHOLD_KEY,
             min_members: int = 1, max_households: int | None = None) -> list[Household]:
    """Read a person-level survey CSV and group it into households.

    The household's ground truth is the sum of its members' trip counts, since that is the quantity
    the negotiation produces. Households whose members lack the target keep `ground_truth = None`
    and are still usable for simulation, just not for scoring.
    """
    import pandas as pd

    frame = pd.read_csv(path, low_memory=False)
    if household_key not in frame.columns:
        raise KeyError(
            f"{household_key!r} is not a column in {path}. "
            f"Found: {', '.join(list(frame.columns)[:10])}..."
        )

    households = []
    for household_id, group in frame.groupby(household_key, sort=True):
        rows = group.where(group.notna(), None).to_dict("records")
        if len(rows) < min_members:
            continue
        households.append(_to_household(str(household_id), rows))
        if max_households and len(households) >= max_households:
            break
    return households


def load_nhts(path: str | Path, **kwargs) -> list[Household]:
    """Load an NHTS person file. Needs R_AGE_IMP, R_SEX_IMP, R_RELAT, HHSIZE and the rest."""
    return load_csv(path, **kwargs)


def load_puget(path: str | Path, **kwargs) -> list[Household]:
    """Load a Puget Sound person file that has been mapped onto NHTS column names."""
    return load_csv(path, **kwargs)


def load_jsonl(path: str | Path) -> Iterator[Household]:
    """Read households already in hdsim's own format, one JSON object per line."""
    for line in Path(path).read_text().splitlines():
        if line.strip():
            yield Household.from_dict(json.loads(line))


def load_example() -> Household:
    """A four-person household bundled with the package, for a first run without a download.

    The values are representative rather than real: no survey record is redistributed here.
    """
    rows = [
        {"HOUSEID": "example", "PERSONID": 1, "R_AGE_IMP": 44, "R_SEX_IMP": 1, "R_RELAT": 1,
         "HHSIZE": 4, "NUMADLT": 2, "HHVEHCNT": 2, "DRVRCNT": 2, "HHFAMINC": 6, "HOMEOWN": 1,
         "DRIVER": 1, "WORKER": 1, "WKFTPT": 1, "EDUC": 4, "URBRUR": 1, "LIF_CYC": 5},
        {"HOUSEID": "example", "PERSONID": 2, "R_AGE_IMP": 42, "R_SEX_IMP": 2, "R_RELAT": 2,
         "HHSIZE": 4, "NUMADLT": 2, "HHVEHCNT": 2, "DRVRCNT": 2, "HHFAMINC": 6, "HOMEOWN": 1,
         "DRIVER": 1, "WORKER": 1, "WKFTPT": 2, "EDUC": 4, "URBRUR": 1, "LIF_CYC": 5},
        {"HOUSEID": "example", "PERSONID": 3, "R_AGE_IMP": 15, "R_SEX_IMP": 1, "R_RELAT": 3,
         "HHSIZE": 4, "NUMADLT": 2, "HHVEHCNT": 2, "DRVRCNT": 2, "HHFAMINC": 6, "HOMEOWN": 1,
         "DRIVER": 2, "WORKER": 2, "SCHTYP": 1, "EDUC": 1, "URBRUR": 1, "LIF_CYC": 5},
        {"HOUSEID": "example", "PERSONID": 4, "R_AGE_IMP": 9, "R_SEX_IMP": 2, "R_RELAT": 3,
         "HHSIZE": 4, "NUMADLT": 2, "HHVEHCNT": 2, "DRVRCNT": 2, "HHFAMINC": 6, "HOMEOWN": 1,
         "DRIVER": 2, "WORKER": 2, "SCHTYP": 1, "EDUC": 1, "URBRUR": 1, "LIF_CYC": 5},
    ]
    return _to_household("example", rows)
