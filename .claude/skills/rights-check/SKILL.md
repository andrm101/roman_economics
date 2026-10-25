---
name: rights-check
description: Decide whether a source may be acquired, parsed, and its text redistributed, before any download. Use for every candidate source before acquisition.
---

# Rights check

For one candidate source:

1. Find the **publisher's own** terms: licence page, repository LICENSE, terms of use, and robots.txt for the host. Record the URL and the date you read it.
2. Record four separate answers:
   - may we download it;
   - may we text-mine it;
   - may we commit derived snippets;
   - may we redistribute the full text.
3. Rights belong to each layer separately: ancient text, modern edition, translation, apparatus, images. A public-domain ancient text does not make a modern translation free.
4. Anything behind a login, paywall, bot challenge (e.g. Anubis or a CAPTCHA) or robots disallow is **not acquirable by agents**. Record it as `blocked` and stop. Never use mirrors, caches or alternative hosts to get around a block.
5. Write a proposal row to `registers/rights_proposals.csv` with these columns:
   `source_id, host, terms_url, read_on, download, tdm, snippets, redistribute, evidence_quote (<=15 words), proposed_rights_id, uncertain`.
6. If any answer is uncertain, set `uncertain=yes`. The researcher decides; you never write `rights_register.csv`.
