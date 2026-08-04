# 🚗 travel-decision

Household **trip planning and generation** simulated via persona-enriched multi-agent negotiation (**PEMAND**).

Part of [HDSim](https://github.com/HDSim-AI) | [Live demo](https://yushundong.github.io/pemand_simulation/pemand_official_site.html) | [Paper](https://arxiv.org/abs/2604.10475)

## How it works

```
survey record -> theory-grounded personas -> independent proposals -> moderated negotiation -> household trip count
```

Each household member becomes an agent with attitudes, subjective norms, and perceived
behavioral control derived from real survey data. Members propose independently, with no
anchoring. They then negotiate in structured rounds while a moderator checks every turn
for persona consistency and feasibility.

## Quick start

```bash
pip install -e .
hdsim demo                        # replay a recorded negotiation, no API key needed
```

Simulate the bundled household against a model:

```bash
cp ../hdsim/.env.example .env     # add HDSIM_API_KEY
python examples/run_travel.py
```

```python
from hdsim.travel import NHTS, build_personas, load_example, simulate

household = load_example()
build_personas(household, NHTS)
simulate(household, NHTS)
print(household.consensus_value)
```

Real data: `load_nhts("perpub.csv", min_members=2)`. NHTS 2017 is at
<https://nhts.ornl.gov/downloads>. No survey data ships with this package.

Requires [`hdsim`](https://github.com/HDSim-AI/hdsim), the method core.

## Contributing

Issues and pull requests are welcome, especially new scenarios, survey loaders, agent
skills, and evaluations. See the [organization page](https://github.com/HDSim-AI) for
the project scope.

## License

MIT
