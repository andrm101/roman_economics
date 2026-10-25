---
name: register-source
description: Add a newly discovered work, edition, chapter or dataset to the registers with honest metadata. Use when discovery finds a source not yet in source_register.csv.
---

# Register a source

1. Check for duplicates first. Search `registers/source_register.csv`, `registers/corpus/discovery_candidates.csv` and `registers/expansion_source_candidates.csv` by persistent identifier (DOI, ISBN), then by title + author + year. Distinct editions, translations and chapters are **separate** records linked by relations, never merged.
2. Copy metadata only from an authoritative record you actually saw: publisher page, library catalogue, Crossref, or the work itself. Record where in `notes`.
3. `access_status` for a newly discovered source is `cited_only` or `metadata_only`. Never `inspected_*`. Only a human upgrades it, after a parse manifest entry exists.
4. Log the search that found it in `registers/search_log.csv`: query, service, date, hits, decision.
5. If you are not certain of any field, leave it empty and say so in `notes`. An empty field is better than a guessed one.
