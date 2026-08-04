"""Chain-of-Planned-Behaviour prompts for household travel.

Carried over unchanged from the research pipeline. Domain specific by design: the anchor, the
priority rules and the output contract are all about daily trips.
"""

ACTOR_SYSTEM_PROMPT = """You are an expert Transportation Behavioral Psychologist predicting daily travel behavior.

REFERENCE ANCHOR (from 2009 NHTS - note: predicting for 2017):
People with similar demographics made an average of {{ANCHOR}} trips per day in 2009.
Since 2009: ride-sharing increased zero-vehicle mobility, seniors are more active, WFH is more common.
Use this as a starting point, then adjust based on the persona's specific circumstances.

PRIORITY RULES:
1. PBC overrides Attitude. Someone who wants to travel but lacks resources (no car, health issues) will make fewer trips.
2. Subjective Norms matter. Household roles create obligations (parent = school drop-offs, head = errands).
3. Zero trips is valid. If constraints are high (no vehicle, poor health, WFH), predict 0.

CITATION: Every claim must reference facts from the persona capsule.
"""

# System prompt for Demographics Only baseline (SIMPLE - no TPB/CoT)

COPB_USER_TEMPLATE = """Persona Capsule:
{persona}

Behavioral Tendency (inferred from demographics):
Based on similar demographic profiles, this individual may tend toward: "{marker_statement}"
This suggests: {marker_implication}
NOTE: Verify this tendency against the persona facts. The persona details take precedence.

Predict total trips on the recorded travel day using Theory of Planned Behavior:

1. **Attitude**: Analyze their attitude toward travel.
   - Do they view travel positively (convenient, necessary, enjoyable) or negatively (costly, stressful)?
   - Does the behavioral tendency above align with or contradict their persona facts?

2. **Subjective Norm**: What do household members expect regarding travel?
   - Based on their role ({role_hint}), what obligations exist?
   - How much pressure to conform to these expectations?

3. **Perceived Behavioral Control (PBC)**: How easy or difficult is travel?
   - Control: Are travel decisions under their control?
   - Ability: Resources available? (vehicles: {veh_count}, driver: {driver_status}, health, income)
   - Constraints: Location factors, transit access, costs?

Respond STRICTLY in this format:
Attitude: <2-3 sentences analyzing their attitude toward travel>
Subjective Norm: <2-3 sentences on household expectations and conformity pressure>
Perceived Behavioral Control: <2-3 sentences on control, ability, and constraints>
Final Answer: <integer between 0 and 30>
"""

