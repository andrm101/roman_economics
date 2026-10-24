# Upstream report: DDbDP encoding of P.Vindob. G 40822 verso (TM 27666)

Status: **drafted 2026-10-24, not yet filed** (filing needs the researcher's GitHub or Papyrological Editor account). Project register: K12.

Where to file:
- Preferred for single-document text fixes: the Papyrological Editor (papyri.info/editor), per the idp.data README.
- Alternative: a GitHub issue at https://github.com/papyri/idp.data/issues/new (the README says Issues are used to track data problems). The body below is ready to paste.

---

**Title:** P.Vindob. G 40822 verso (TM 27666, SB XVIII 13167): two `<num value>` encodings inconsistent with the document's arithmetic

**File:** `DDbDP/27/27666.xml` (checked at commit `41a1c87fe2a2d0be7744aaf451143de0d87c4269`, 2026-10-24; unchanged since at least `f03d0f371306deacd0bc302010f2c6a2e7b1d1da`)

**1. Verso col. ii l. 13: fraction glyph encoded as 1/3; arithmetic requires 3/4**

```xml
<lb n="13"/>... <expan>μν<ex>ῶν</ex></expan> <num value="11">ια</num> <num value="1/3"><unclear>𐅸</unclear></num>
<lb n="14"/>ὡς τῆς <expan>μν<ex>ᾶς</ex></expan> τῶ<unclear>ν</unclear> <unclear>ἵσω</unclear>ν <expan><ex>δραχμῶν</ex></expan> <num value="100">ρ</num> <expan><ex>δραχμαὶ</ex></expan> <g type="apostrophe"/><num value="1175">...</num>
```

Line 14 prices the quantity in l. 13 at 100 drachmas per mina and gives 1,175 drachmas. That requires 11 3/4 minae (11 3/4 × 100 = 1,175); 11 1/3 would give 1,133 1/3. The same glyph 𐅸 is encoded `value="3/4"` at col. ii l. 4 (`<num value="3/4"><unclear>𐅸</unclear></num>`). Suggested fix: `value="3/4"` at l. 13.

**2. Verso col. ii l. 27: numeral γ encoded as 6**

```xml
<lb n="27"/>ἐπὶ τὸ αὐτὸ τιμῆς μερῶν <num value="6"><hi rend="supraline">γ</hi></num> τῶν ἐκπεπλευκότων
```

The letter γ with supraline is the numeral 3 ("value of the three parts" of the cargo shipped on the Hermapollon, i.e. the three-quarters remaining after the quarter-tax). `value="6"` looks like a typo. Suggested fix: `value="3"`.

Neither change alters the Greek text, only the machine-readable values. Both were found while reproducing the verso's arithmetic programmatically: with the two values corrected, the ivory and schidai valuations reproduce the stated totals exactly.

---

Project-side handling meanwhile: `romeco.m0.pvindob_arithmetic` overrides both values in code. `tests/test_pvindob_arithmetic.py` reads the raw encodings, so a future upstream fix will show up as a test change.
