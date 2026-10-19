# Triage: study what matters, park the rest

An AI study planner. A student tells it how many hours are left before an exam. Triage shows which topics to study first, where to find them in the study material, and which to park for later.

**Live demo:** https://triage-gold-theta.vercel.app/

## The problem
Students with limited time face a huge syllabus and no idea where to start. Coaching academies sell "guess papers" and "important questions" for a fee, and many students cannot afford them. Triage gives every student an evidence-based version of that advice.

## What it does
1. Analyses past exam papers and tags every question by topic.
2. Scores each topic: how likely it is to appear (recent papers count more) and how many marks it earns per hour of study.
3. Sorts topics into **Lock It In**, **Handle With Care** and **Park It**, each with a confidence % and a one-line reason.
4. Builds a focused plan for the hours the student has, with built-in breaks. Low-value topics are *parked*, never deleted.
5. Points to the matching chapter and exercise in the study material, e.g. "Study Unit 2 · Exercise 2.3".
6. Flags topics that are no longer in the current study material, and shows brand-new topics separately as "New this year".

Triage is built to work for exam subjects in general. This demo runs on **sample data** to show the full experience.

## How the AI works
| Step | Method |
|---|---|
| Read papers | A vision model tags each question to a topic list |
| Predict | Recency-weighted probability with an uncertainty range |
| Plan | Knapsack optimiser: most expected marks within the student's hours |
| Prove | Backtest: train on earlier papers, test on the latest |

### Backtest on the sample data (marks out of 75)
| Study hours | Triage plan | Most-frequent-first | Random |
|---|---|---|---|
| 6 | 18.0 | 13.5 | 9.2 |
| 10 | 28.0 | 18.5 | 16.3 |
| 15 | 39.5 | 26.5 | 25.3 |

Assumption: studying a topic earns all its marks, capped where the exam lets students skip parts.

## Responsible AI
- Predictions are patterns, not promises. Confidence is shown on every topic.
- Topics with no past-paper evidence are never given an invented probability.
- Plans include breaks, and parked topics are shown calmly (grey, not red) to reduce panic and burnout.
- Uploaded papers will be processed per session and never change the shared data.

## Repository layout
```
/backend    Python (FastAPI): scoring model, planner, study-material mapping, API
```
The web app was built with v0 by Vercel and is deployed at the live demo link above.

## Run the backend locally
```
cd backend
pip install -r requirements.txt
mkdir data
python seed.py
python pipeline.py
python test_flow.py
python -m uvicorn api:app --reload
```

## What's next
- **Online paper upload** is coming soon: students will add their own past papers and get a plan from them.
- More subjects and exam boards.
- Personalised plans based on each student's weak areas.
- A pilot with a school or study group to measure score improvement.

## AI tools used
Claude (coding assistant, and help preparing the sample dataset), v0 by Vercel (interface design).

## Team
Detail-Oriented: Rameen Fatima, Ilsa
