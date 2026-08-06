"""NHTS 2017 survey fields to first-person facts.

Ported unchanged from the pipeline that produced the published results, so personas built here
read identically to the ones in arXiv:2604.10475. The composition is deliberate and worth keeping
intact:

  - age and sex combine into "a 44-year-old man", and into boy/girl below 18
  - relationship code and sex combine into "the wife of the household head"
  - household size and adult count reconcile against the lifecycle code, preferring exact counts
    over vague codebook phrases like "two or more adults"
  - negative codes (-1 appropriate skip, -7 refused, -8 don't know, -9 not ascertained) render as
    nothing at all, because an unknown is not a fact about a person

None of that survives a per-column rewrite, which is why this file is carried over rather than
reimplemented against `DomainConfig.translations`.
"""

try:  # pandas is optional here; loaders need it, fact building does not
    import pandas as pd
except ImportError:  # pragma: no cover
    class _PandasShim:
        @staticmethod
        def notna(value):
            # NaN is the only value unequal to itself, which is the whole test here
            return value is not None and value == value  # noqa: PLR0124

        @staticmethod
        def isna(value):
            return not _PandasShim.notna(value)

    pd = _PandasShim()

# Columns used for persona generation (Strict parity with External ML variable list)
# Last updated: Added LPACT, HTHTNRNT, PLACE; reorganized for better flow
KEY_COLUMNS_FOR_PERSONA = [
    # --- Core demographics ---
    'R_AGE_IMP',
    'R_SEX_IMP',
    'HHSIZE',
    'NUMADLT',
    'LIF_CYC',
    'HHVEHCNT',
    'HHFAMINC',
    'HOMEOWN',
    'DRIVER',
    'WORKER',
    'EDUC',
    'OCCAT',
    'MEDCOND',
    'GT1JBLWK',
    'PHYACT',
    'LPACT',
    
    # --- Built environment ---
    'URBRUR',
    'MSASIZE',
    'RAIL',
    'HTPPOPDN',
    'HTEEMPDN',
    'HTRESDN',
    'HTHTNRNT',
    'GASPRICE',
    
    # --- Technology use ---
    'PC',
    'SPHONE',
    
    # --- Proxies ---
    'R_RACE',
    'R_HISP',
    'SCHTYP',
    'BORNINUS',
    'USEPUBTR',
    
    # --- Structural ---
    'R_RELAT',        # For role assignment (prevents hallucinations)
    'TRAVDAY',
    'CNTTDTR',        # Target variable (not used in narrative)
    
    # --- Worker details ---
    'WKFTPT',         # Full/part-time (detail for workers)
    # 'MSACAT',       # Redundant with MSASIZE + RAIL
    # 'TAB',          # Not in ML features
    'RIDESHARE',
    'DRVRCNT',
    # 'HBPPOPDN',     # Redundant with HTPPOPDN
]

# Translation map for raw codes to human-readable text
# Handles negative codes (-1, -7, -8, -9) by mapping to None
TRANSLATION_MAP = {
    'R_SEX_IMP': {
        1: 'male',
        2: 'female',
        -1: None, -7: None, -8: None, -9: None
    },
    'HOMEOWN': {
        1: 'own our home',
        2: 'rent our home',
        3: 'have other living arrangements',
        -1: None, -7: None, -8: None, -9: None
    },
    'DRIVER': {
        1: 'I am a licensed driver',
        2: 'I am not a licensed driver',
        -1: None, -7: None, -8: None, -9: None
    },
    'WORKER': {
        1: 'I am a worker',
        2: 'I am not a worker',
        -1: None, -7: None, -8: None, -9: None
    },
    'URBRUR': {
        1: 'I live in an urban area',
        2: 'I live in a rural area',
        -1: None, -7: None, -8: None, -9: None
    },
    'HHFAMINC': {
        1: 'less than $10,000',
        2: '$10,000 to $14,999',
        3: '$15,000 to $24,999',
        4: '$25,000 to $34,999',
        5: '$35,000 to $49,999',
        6: '$50,000 to $74,999',
        7: '$75,000 to $99,999',
        8: '$100,000 to $124,999',
        9: '$125,000 to $149,999',
        10: '$150,000 to $199,999',
        11: '$200,000 or more',
        -1: None, -7: None, -8: None, -9: None
    },
    'EDUC': {
        # SAS: 01-05 only (no separate associate's code)
        1: 'less than a high school diploma',
        2: 'a high school diploma or GED',
        3: 'some college or an associate\'s degree',
        4: "a bachelor's degree",
        5: 'a graduate or professional degree',
        -1: None, -7: None, -8: None, -9: None
    },
    'OCCAT': { 
        1: 'I work in Sales or Service',
        2: 'I work in Clerical or Administration',
        3: 'I work in Manual Labor or Manufacturing',
        4: 'I am a Professional, Manager, or Technical worker',
        97: 'I have another type of occupation',
        -1: None, -7: None, -8: None, -9: None
    },
    'MEDCOND': {
        1: 'I have a medical condition',
        2: 'I do not have a medical condition',
        -1: None, -7: None, -8: None, -9: None
    },
    'MSASIZE': {
        # SAS: MSA population size categories
        1: 'an MSA of less than 250,000',
        2: 'an MSA of 250,000 to 499,999',
        3: 'an MSA of 500,000 to 999,999',
        4: 'an MSA of 1 to 3 million',
        5: 'an MSA of 3 million or more',
        6: 'not in an MSA',
        -1: None, -7: None, -8: None, -9: None
    },
    'MSACAT': {
        1: 'an MSA of 1 million or more with rail',
        2: 'an MSA of 1 million or more without rail',
        3: 'an MSA of less than 1 million',
        4: 'not in an MSA',
        -1: None, -7: None, -8: None, -9: None
    },
    # LIF_CYC: Household lifecycle from SAS proc_format.sas
    # FACTUAL descriptions only - no assumptions about relationships
    'LIF_CYC': {
        1: 'one adult, no children',              # SAS: one adult, no children
        2: 'two or more adults, no children',     # SAS: 2+ adults, no children
        3: 'one adult with young children (0-5)', # SAS: one adult, youngest child 0-5
        4: 'two or more adults with young children (0-5)',  # SAS: 2+ adults, youngest child 0-5
        5: 'one adult with school-age children (6-15)',     # SAS: one adult, youngest child 6-15
        6: 'two or more adults with school-age children (6-15)', # SAS: 2+ adults, youngest child 6-15
        7: 'one adult with older children (16-21)',         # SAS: one adult, youngest child 16-21
        8: 'two or more adults with older children (16-21)', # SAS: 2+ adults, youngest child 16-21
        9: 'one adult, retired, no children',     # SAS: one adult, retired, no children
        10: 'two or more adults, retired, no children', # SAS: 2+ adults, retired, no children
        -1: None, -7: None, -8: None, -9: None
    },
    'RAIL': {
        1: 'has heavy rail',
        2: 'does not have heavy rail',
        -1: None, -7: None, -8: None, -9: None
    },
    'PHYACT': {
        # SAS Codebook: 1=Rare/Never, 2=Light/Mod, 3=Vigorous
        1: 'I rarely or never engage in physical activity',
        2: 'I engage in some light or moderate physical activities',
        3: 'I engage in some vigorous physical activities',
        -1: None, -7: None, -8: None, -9: None
    },
    'GT1JBLWK': {
        1: 'I have more than one job',
        2: 'I have only one job',
        -1: None, -7: None, -8: None, -9: None
    },
    'WKFTPT': {
        1: 'I work full-time',
        2: 'I work part-time',
        -1: None, -7: None, -8: None, -9: None
    },
    'TRAVDAY': {
        1: 'The travel day recorded was a Sunday',
        2: 'The travel day recorded was a Monday',
        3: 'The travel day recorded was a Tuesday',
        4: 'The travel day recorded was a Wednesday',
        5: 'The travel day recorded was a Thursday',
        6: 'The travel day recorded was a Friday',
        7: 'The travel day recorded was a Saturday',
        -1: None, -7: None, -8: None, -9: None
    },
    # Mapping for Relationship
    'R_RELAT': {
        1: 'Self',
        2: 'Spouse/Partner',
        3: 'Child',
        4: 'Parent',
        5: 'Brother/Sister', # Added back missing 5
        6: 'Other relative',
        7: 'Non-relative',
        -1: None, -7: None, -8: None, -9: None
    },
    # --- Race/Ethnicity from SAS proc_format.sas ---
    'R_RACE': {
        1: 'White',
        2: 'Black or African American',
        3: 'Asian',
        4: 'American Indian or Alaska Native',
        5: 'Native Hawaiian or other Pacific Islander',
        6: 'multiple races',       # SAS: Multiple responses selected
        97: 'another race',        # SAS: Some other race
        -1: None, -7: None, -8: None
    },
    'R_HISP': {
         1: 'of Hispanic or Latino origin',
         2: 'not of Hispanic or Latino origin',
         -1: None, -7: None, -8: None
    },
    'BORNINUS': {
        1: 'born in the United States',
        2: 'born outside the United States',
         -1: None, -7: None, -8: None
    },
    'SCHTYP': {
        1: 'a public or private school', # SAS: 01="Public or private school"
        2: 'home school',
        3: None, # SAS: 03="Not in school"
        -1: None, -7: None, -8: None, -9: None
    },
    'USEPUBTR': {
        1: 'use public transit',
        2: 'do not use public transit', 
        -1: None, -7: None, -8: None, -9: None
    },
    'PC': {
        1: 'use a computer daily',
        2: 'use a computer a few times a week',
        3: 'use a computer a few times a month',
        4: 'use a computer a few times a year',
        5: 'never use a computer',
        -7: None, -8: None, -9: None
    },
    'SPHONE': {
        1: 'use a smartphone daily',
        2: 'use a smartphone a few times a week',
        3: 'use a smartphone a few times a month',
        4: 'use a smartphone a few times a year',
        5: 'never use a smartphone',
        -7: None, -8: None, -9: None
    },
}

def _translate_value(column_name, value):
    """Translate one coded value into English.

    Returns None when the code is missing, negative or absent from the map. NHTS uses negative
    codes for non-responses, and a non-response is not a fact about a person.
    """
    if value is None or pd.isna(value):
        return None
        
    try:
        # Cast to int to handle potential floats from pandas (e.g., 1.0)
        value_int = int(value)
        return TRANSLATION_MAP.get(column_name, {}).get(value_int)
    except (ValueError, TypeError):
        return None

def _identity_facts(row):
    """Age, sex, race, origin and education.

    Also returns the values later sections need, so they are read from the record once."""
    facts = []
    age = int(row['R_AGE_IMP']) if pd.notna(row.get('R_AGE_IMP')) else None
    relat_code = row.get('R_RELAT')
    try:
        relat_code = int(relat_code) if pd.notna(relat_code) else None
    except (ValueError, TypeError):
        relat_code = None
    
    sex_raw = _translate_value('R_SEX_IMP', row.get('R_SEX_IMP'))
    sex_text = None
    if sex_raw:
        if age is not None and age < 18:
            sex_text = 'boy' if sex_raw == 'male' else 'girl'
        else:
            sex_text = 'man' if sex_raw == 'male' else 'woman'
    
    if age is not None and sex_text:
        facts.append(f"I am a {age}-year-old {sex_text}.")
    elif age is not None:
        facts.append(f"I am {age} years old.")
    
    # Race, ethnicity, nativity
    race_text = _translate_value('R_RACE', row.get('R_RACE'))
    if race_text:
        facts.append(f"My race is {race_text}.")
    
    hisp_raw = row.get('R_HISP')
    try:
        if hisp_raw is not None and int(hisp_raw) == 1:
            facts.append("I am of Hispanic or Latino origin.")
    except (ValueError, TypeError):
        pass
    
    born_text = _translate_value('BORNINUS', row.get('BORNINUS'))
    if born_text:
        facts.append(f"I was {born_text}.")
    
    # Education (fits with identity)
    educ_text = _translate_value('EDUC', row.get('EDUC'))
    if educ_text:
        facts.append(f"I have {educ_text}.")
    return facts, {"age": age, "relat_code": relat_code,
                   "sex_raw": sex_raw, "sex_text": sex_text}

def _household_facts(row, ctx):
    """Role in the household, its composition, income, home and vehicles."""
    relat_code, sex_raw = ctx['relat_code'], ctx['sex_raw']
    facts = []
    # Role in household (gender-aware for clarity)
    relat_raw = _translate_value('R_RELAT', relat_code)
    is_male = (sex_raw == 'male')
    
    if relat_raw:
        # Gender-aware role mapping for clearer relationships
        if relat_raw == 'Self':
            facts.append("I am the head of my household.")
        elif relat_raw == 'Spouse/Partner':
            if is_male:
                facts.append("I am the husband of the household head.")
            else:
                facts.append("I am the wife of the household head.")
        elif relat_raw == 'Child':
            # NOTE: "Child" is relationship-to-head (can include adult children, e.g., age 19+)
            if is_male:
                facts.append("I am the son of the household head.")
            else:
                facts.append("I am the daughter of the household head.")
        elif relat_raw == 'Parent':
            if is_male:
                facts.append("I am the father of the household head.")
            else:
                facts.append("I am the mother of the household head.")
        elif relat_raw == 'Brother/Sister':
            if is_male:
                facts.append("I am the brother of the household head.")
            else:
                facts.append("I am the sister of the household head.")
        elif relat_raw == 'Other relative':
            facts.append("I am a relative in this household.")
        elif relat_raw == 'Non-relative':
            facts.append("I am a non-relative in this household.")
    
    # Household composition
    lif_cyc_code = row.get('LIF_CYC')
    try:
        lif_cyc_code = int(lif_cyc_code) if pd.notna(lif_cyc_code) else None
    except (ValueError, TypeError):
        lif_cyc_code = None
    
    # IMPORTANT: LIF_CYC is defined from the household head's perspective; apply only to head/spouse.
    if lif_cyc_code and relat_code in (1, 2):
        # Prefer exact household counts when available (avoids vague phrases like "two or more adults")
        # while preserving the lifecycle meaning (youngest child age band / retired).
        hhsz = None
        num_adults = None
        try:
            hhsz = int(row["HHSIZE"]) if pd.notna(row.get("HHSIZE")) else None
        except (ValueError, TypeError, KeyError):
            hhsz = None
        try:
            num_adults = int(row["NUMADLT"]) if pd.notna(row.get("NUMADLT")) else None
        except (ValueError, TypeError, KeyError):
            num_adults = None

        retired_flag = lif_cyc_code in (9, 10)
        youngest_band = None
        if lif_cyc_code in (3, 4):
            youngest_band = "0-5"
        elif lif_cyc_code in (5, 6):
            youngest_band = "6-15"
        elif lif_cyc_code in (7, 8):
            youngest_band = "16-21"

        if hhsz is not None and num_adults is not None and hhsz >= 0 and num_adults >= 0 and num_adults <= hhsz:
            num_children = hhsz - num_adults
            adult_phrase = f"{num_adults} adult{'s' if num_adults != 1 else ''}"
            parts = [adult_phrase]

            if num_children > 0:
                child_phrase = f"{num_children} child{'ren' if num_children != 1 else ''}"
                parts.append(child_phrase)

            extra = []
            if num_children == 0:
                extra.append("no children")
            if retired_flag:
                extra.append("retired")
            if youngest_band and num_children > 0:
                extra.append(f"youngest child aged {youngest_band}")

            if extra:
                facts.append(f"My household consists of {', '.join(parts)}, {', '.join(extra)}.")
            else:
                facts.append(f"My household consists of {', '.join(parts)}.")
        else:
            # Fallback to codebook label
            lif_cyc_text = _translate_value('LIF_CYC', lif_cyc_code)
            if lif_cyc_text:
                facts.append(f"My household consists of {lif_cyc_text}.")
    
    # Household size
    if 'HHSIZE' in row and pd.notna(row['HHSIZE']):
        size = int(row['HHSIZE'])
        num_adults = int(row['NUMADLT']) if 'NUMADLT' in row and pd.notna(row['NUMADLT']) else None
        
        if size == 1:
            facts.append("I live alone.")
        elif num_adults is not None and num_adults < size:
            num_children = size - num_adults
            facts.append(f"There are {size} people in my household: {num_adults} adult{'s' if num_adults != 1 else ''} and {num_children} child{'ren' if num_children != 1 else ''}.")
        else:
            facts.append(f"There are {size} people in my household.")
    
    # Income and homeownership
    income_text = _translate_value('HHFAMINC', row.get('HHFAMINC'))
    if income_text:
        facts.append(f"My household income is {income_text}.")
    
    home_text = _translate_value('HOMEOWN', row.get('HOMEOWN'))
    if home_text:
        facts.append(f"We {home_text}.")
    
    # Vehicles
    if 'HHVEHCNT' in row and pd.notna(row['HHVEHCNT']):
        vehicles = int(row['HHVEHCNT'])
        if vehicles == 0:
            facts.append("My household does not own any vehicles.")
        else:
            facts.append(f"My household owns {vehicles} vehicle{'s' if vehicles != 1 else ''}.")

    # Drivers in HH
    if 'DRVRCNT' in row and pd.notna(row['DRVRCNT']):
        try:
            d_cnt = int(row['DRVRCNT'])
            if d_cnt >= 0:
                facts.append(f"There {'are' if d_cnt != 1 else 'is'} {d_cnt} licensed driver{'s' if d_cnt != 1 else ''} in my household.")
        except (ValueError, TypeError):
            pass
    return facts

def _location_facts(row):
    """Where the household lives: urbanity, metropolitan area, density, costs."""
    facts = []
    # Combine urban/rural, MSA size, and rail into fewer sentences to reduce "I live" repetition
    urb_text = _translate_value('URBRUR', row.get('URBRUR'))
    if urb_text:
        facts.append(f"{urb_text}.")
    
    # Combine MSA size and rail availability into one fact to reduce "I live" repetition
    msa_text = _translate_value('MSASIZE', row.get('MSASIZE'))
    rail_text = _translate_value('RAIL', row.get('RAIL'))
    msa_code = row.get('MSASIZE')
    try:
        msa_code = int(msa_code) if pd.notna(msa_code) else None
    except (ValueError, TypeError):
        msa_code = None
    
    # Special case: not in an MSA (code 6) - don't combine with rail
    if msa_code == 6:
        facts.append("I do not live in a metropolitan area.")
    elif msa_text and rail_text:
        # In an MSA: combine population and rail
        msa_pop = msa_text.replace('an MSA of ', '')
        facts.append(f"My metropolitan area has a population of {msa_pop} and {rail_text}.")
    elif msa_text:
        msa_pop = msa_text.replace('an MSA of ', '')
        facts.append(f"My metropolitan area has a population of {msa_pop}.")
    elif rail_text:
        facts.append(f"My area {rail_text}.")

    # Densities (combine into one fact for flow, but keep labels explicit to avoid odd paraphrases)
    density_parts = []
    for dens_col, dens_name in [('HTPPOPDN', 'population density'), ('HTEEMPDN', 'employment density'), ('HTRESDN', 'residential density')]:
        if dens_col in row and pd.notna(row[dens_col]):
            try:
                val = float(row[dens_col])
                if val >= 0:
                    density_parts.append(f"{dens_name}: {val:.0f}")
            except (ValueError, TypeError):
                pass
    if density_parts:
        facts.append(f"My area's density (per sq mi) is {', '.join(density_parts)}.")
    
    # Housing + Transportation affordability (HTHTNRNT)
    if 'HTHTNRNT' in row and pd.notna(row['HTHTNRNT']):
        try:
            ht_val = int(row['HTHTNRNT'])
            if ht_val >= 0:
                # HTHTNRNT is percentage ranges: 0=0-4%, 5=5-14%, 20=15-24%, etc.
                ht_ranges = {0: '0-4%', 5: '5-14%', 20: '15-24%', 30: '25-34%', 
                            40: '35-44%', 50: '45-54%', 60: '55-64%', 70: '65-74%', 
                            80: '75-84%', 90: '85% or more'}
                if ht_val in ht_ranges:
                    facts.append(f"Housing and transportation costs are {ht_ranges[ht_val]} of income in my area.")
        except (ValueError, TypeError):
            pass
    
    # Gas price
    if 'GASPRICE' in row and pd.notna(row['GASPRICE']):
        try:
            val = float(row['GASPRICE'])
            if val > 0:
                price_dollars = val / 100.0
                facts.append(f"Gas costs about ${price_dollars:.2f} per gallon in my area.")
        except (ValueError, TypeError):
            pass
    return facts

def _work_facts(row, ctx):
    """Employment, job details and student status."""
    age = ctx['age']
    facts = []
    is_adult = (age is None) or (age >= 18)
    worker_text = _translate_value('WORKER', row.get('WORKER'))
    if worker_text and is_adult:
        facts.append(f"{worker_text}.")
    
    # Work details (only if worker)
    if worker_text and is_adult and 'I am a worker' in worker_text:
        wkftpt_text = _translate_value('WKFTPT', row.get('WKFTPT'))
        if wkftpt_text:
            facts.append(f"{wkftpt_text}.")
        
        gt1jblwk_text = _translate_value('GT1JBLWK', row.get('GT1JBLWK'))
        if gt1jblwk_text:
            facts.append(f"{gt1jblwk_text}.")
        
        occu_text = _translate_value('OCCAT', row.get('OCCAT'))
        if occu_text:
            facts.append(f"{occu_text}.")
    
    # Student status
    sch_code = row.get('SCHTYP')
    if sch_code:
        try:
            sch_val = int(sch_code)
            if sch_val in [1, 2]:
                sch_desc = TRANSLATION_MAP['SCHTYP'].get(sch_val)
                if sch_desc:
                    facts.append(f"I am a student attending {sch_desc}.")
        except (ValueError, TypeError):
            pass
    return facts

def _health_facts(row):
    """Medical conditions and physical activity."""
    facts = []
    medcond_text = _translate_value('MEDCOND', row.get('MEDCOND'))
    if medcond_text:
        facts.append(f"{medcond_text}.")
    
    phyact_text = _translate_value('PHYACT', row.get('PHYACT'))
    if phyact_text:
        facts.append(f"{phyact_text}.")
    
    # Light physical activity days (LPACT)
    if 'LPACT' in row and pd.notna(row['LPACT']):
        try:
            lpact_val = int(row['LPACT'])
            if lpact_val >= 0:
                day_word = "day" if lpact_val == 1 else "days"
                facts.append(f"I do light physical activity about {lpact_val} {day_word} per month.")
        except (ValueError, TypeError):
            pass
    return facts

def _mobility_facts(row):
    """Licence, transit use, rideshare and devices."""
    facts = []
    driver_text = _translate_value('DRIVER', row.get('DRIVER'))
    if driver_text:
        facts.append(f"{driver_text}.")
    
    # Transit usage
    pt_text = _translate_value('USEPUBTR', row.get('USEPUBTR'))
    if pt_text:
        facts.append(f"I {pt_text}.")
    
    # Tech usage
    tech_facts = []
    # Rideshare usage
    if 'RIDESHARE' in row and pd.notna(row['RIDESHARE']):
        try:
            rs_val = int(row['RIDESHARE'])
            if rs_val > 0:
                times_word = "time" if rs_val == 1 else "times"
                tech_facts.append(f"used rideshare apps {rs_val} {times_word} in the past month")
            else:
                tech_facts.append("did not use rideshare apps in the past month")
        except (ValueError, TypeError):
            pass

    for tech_col in ['PC', 'SPHONE']:
        val = _translate_value(tech_col, row.get(tech_col))
        if val:
            tech_facts.append(val)
    if tech_facts:
        facts.append(f"I {' and '.join(tech_facts)}.")
    return facts

def _survey_context_facts(row):
    """Which day of the week the record covers."""
    facts = []
    travday_text = _translate_value('TRAVDAY', row.get('TRAVDAY'))
    if travday_text:
        facts.append(f"{travday_text}.")
    return facts

def generate_facts_list(row):
    """A survey record as an ordered list of first-person facts.

    Order follows how a person would introduce themselves: who they are, who they live with, where
    that is, what they do, their health, how they get around, and finally which day was recorded.
    """
    facts, ctx = _identity_facts(row)
    facts += _household_facts(row, ctx)
    facts += _location_facts(row)
    facts += _work_facts(row, ctx)
    facts += _health_facts(row)
    facts += _mobility_facts(row)
    facts += _survey_context_facts(row)
    return facts
