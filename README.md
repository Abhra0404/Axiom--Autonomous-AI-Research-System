# Axiom

### Autonomous AI Research System

> **Give Axiom a research question. It investigates the topic, gathers evidence, critiques its findings, and produces a structured research report.**

Axiom is an agentic AI research system designed to autonomously investigate technical and scientific questions.

Instead of simply answering a question from an LLM, Axiom follows a research workflow: it decomposes the problem, searches relevant sources, extracts evidence, evaluates conflicting claims, identifies knowledge gaps, and iterates when more research is required.

---

## How It Works

```text
                    Research Question
                           │
                           ▼
                      ┌─────────┐
                      │ Planner │
                      └────┬────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌─────────┐  ┌─────────┐  ┌───────────┐
         │Research │  │Evidence │  │Experiment │
         │ Agent   │  │  Agent  │  │   Agent   │
         └────┬────┘  └────┬────┘  └─────┬─────┘
              │            │              │
              └────────────┼──────────────┘
                           ▼
                      ┌─────────┐
                      │ Critic  │
                      └────┬────┘
                           │
                    More evidence?
                      /         \
                    Yes          No
                     │            │
                     ▼            ▼
                 Research     Synthesis
                   Again          │
                                  ▼
                            Final Report
```

The **Experiment Agent is optional**. Axiom can perform pure literature research when experiments are unnecessary, or combine existing research with new experiments when empirical evidence is useful.

---

## Core Capabilities

### Research Planning

* Understand the research objective
* Break complex questions into sub-questions
* Generate a research strategy
* Define evidence requirements and stopping criteria

### Autonomous Research

* Search academic papers and technical sources
* Collect relevant evidence
* Track sources and citations
* Compare different approaches and findings

### Evidence Analysis

* Extract claims from sources
* Link claims to supporting evidence
* Identify contradictory results
* Evaluate source and methodology quality
* Track uncertainty and confidence

### Self-Critique

Axiom evaluates its own research:

```text
Research
   ↓
Evidence
   ↓
Critique
   ↓
Knowledge Gap
   ↓
New Research
   ↓
Evidence
   ↓
...
```

This allows the system to continue investigating when the available evidence is insufficient.

### Experimental Research

When appropriate, Axiom can extend literature research into empirical experimentation:

* Find or use relevant datasets
* Design experiments
* Generate Python code
* Execute experiments in isolated environments
* Evaluate results
* Compare models and methodologies
* Feed experimental findings back into the research loop

---

## Example

### Research Question

> **Does Retrieval-Augmented Generation actually reduce hallucinations in LLMs?**

Axiom may investigate:

```text
1. Define hallucination
2. Identify evaluation methods
3. Find relevant research
4. Extract experimental results
5. Compare methodologies
6. Identify contradictory findings
7. Evaluate evidence quality
8. Identify research gaps
9. Perform additional research
10. Synthesize the findings
```

The final output contains:

```text
Research Question
Background
Methodology
Key Evidence
Comparative Analysis
Contradictory Findings
Limitations
Conclusion
Confidence
References
```

---

## Architecture

Axiom is designed as a modular multi-agent system.

```text
axiom/
├── agents/
│   ├── planner/
│   ├── researcher/
│   ├── evidence/
│   ├── experiment/
│   ├── critic/
│   └── synthesis/
│
├── api/
├── execution/
├── evaluation/
├── storage/
├── models/
│
├── experiments/
├── research/
├── reports/
├── tests/
│
├── frontend/
├── docker/
│
├── pyproject.toml
└── README.md
```

Agents communicate through structured schemas rather than unstructured text wherever possible.

---

## Tech Stack

| Layer               | Technology                        |
| ------------------- | --------------------------------- |
| Language            | Python                            |
| API                 | FastAPI                           |
| Agent Orchestration | LangGraph                         |
| LLM                 | OpenAI API                        |
| Validation          | Pydantic                          |
| Database            | PostgreSQL                        |
| Experiment Tracking | MLflow                            |
| ML                  | PyTorch, scikit-learn, XGBoost    |
| Execution           | Docker                            |
| Frontend            | Next.js, TypeScript, Tailwind CSS |

The stack will evolve as the system moves from research prototype to production infrastructure.

---

## Research Artifacts

Every research run should produce reproducible artifacts:

```text
research_run/
├── research_plan.json
├── sources.json
├── claims.json
├── evidence.json
├── critiques.json
├── findings.json
├── experiments/
└── report.md
```

This makes the research process inspectable rather than treating the final answer as a black box.

---

## Design Principles

**Evidence over confidence**
LLM confidence is not evidence. Claims should be grounded in sources or reproducible experiments.

**Reproducibility**
Research plans, sources, experiments, results, and conclusions should be traceable.

**Explicit uncertainty**
Axiom should distinguish between established evidence, supported claims, uncertain findings, contradictions, and speculation.

**Controlled autonomy**
Agents operate within defined tool permissions, execution limits, budgets, and stopping conditions.

**Modularity**
Each agent has a focused responsibility and communicates through structured interfaces.

---

## Vision

Most AI systems are built to **answer questions**.

Axiom is built to **investigate them**.

> **Research. Experiment. Critique. Discover.**

**Status:** 🚧 Active Development
