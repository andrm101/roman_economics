---
name: review-packet
description: Prepare human review packets for extraction candidates, ordered by impact. Use when candidates must be checked before they can become claims.
---

# Review packets

1. Select candidates in this priority order:
   - those that `rx:possiblyBearsOn` a claim feeding a parameter (CQ10);
   - then those bearing on an ancient document in `data/curated/semantic/document_keys.csv`;
   - then the rest.
2. For each, run `PYTHONPATH=src python3 -c "from romeco.agents.review import make_packet; make_packet('<ext_id>')"`.
3. Open the rendered page image yourself. Note any visible mismatch with the extracted value (OCR digit, overline, footnote bleed) in `review_queue/<ext_id>/notes.md`. Do not "correct" the candidate.
4. Write `review_queue/INDEX.md` as a table: ext_id, source, page, value, why it matters, mismatch noted.
5. You never write `registers/review_decisions.csv` and never mark anything `human_reviewed`.
