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

## Status

🚧 **Initial code release in progress.** Until it lands, the
[live demo](https://yushundong.github.io/pemand_simulation/pemand_official_site.html)
replays three precomputed travel scenarios in the browser with no setup required.

Planned quick start:

```bash
pip install -e .
hdsim-travel demo   # replay a real household negotiation in your terminal
```

## Contributing

Issues and pull requests are welcome, especially new scenarios, survey loaders, agent
skills, and evaluations. See the [organization page](https://github.com/HDSim-AI) for
the project scope.

## License

MIT
