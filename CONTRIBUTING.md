# Contributing to `travel-decision`

This repository is **one domain**. The method lives in
[`hdsim`](https://github.com/HDSim-AI/hdsim), and the guide for adding a whole new decision is
[there](https://github.com/HDSim-AI/hdsim/blob/main/CONTRIBUTING.md).

**What belongs here** is anything that makes the trips domain better:

| You want to… | What that means here |
|---|---|
| Support another dataset | A loader for NHTS, Puget Sound or another travel survey |
| Improve how a survey row reads | The fact translations in `facts.py` |
| Add a replayable case | A scenario other people can run |
| Add an evaluation | A baseline, an ablation, or a metric |

**What belongs in [`hdsim`](https://github.com/HDSim-AI/hdsim)** is anything that changes persona
construction, the negotiation protocol, the model backends, or the metrics. Those are shared by
every domain, so a change here would silently move the other one too.

## Data

Do not commit survey microdata. Most household surveys carry redistribution terms and PSID requires
registration. Ship a loader and download instructions, plus a small synthetic example so the package
runs before anyone downloads anything.

## Pull requests

- Branch from `main`, one logical change per pull request.
- Include tests. They must pass with no API key and no network.
- If you change persona construction or the negotiation protocol, re-run the evaluation and include
  the numbers. Those changes move published metrics.

## Reproducibility

Record the model and version behind any reported result. Results produced by a language model are
not reproducible without it, and reproducibility is the point of this project.

## Questions and comments

If something is unclear, or you think a design choice is wrong, or you want to talk through a use
case before writing code, send an email to mustafasameen@ufl.edu. We would rather have the
conversation than have you guess, and we are happy to talk through anything in the method.

## Code of conduct

Be decent to each other. Research infrastructure is a long game and the community is small.
