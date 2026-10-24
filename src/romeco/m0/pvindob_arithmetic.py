"""The papyrus's own arithmetic (P.Vindob. G 40822 verso), reproduced exactly.

Inputs are the numerals of the DDbDP EpiDoc text (TM 27666; edition Tyche 26,
2011, as encoded by papyri.info), read line by line in session 2. Each
function names the lines it uses. Two DDbDP encodings are overridden where
the document's own arithmetic forces a different value; both are logged in
registers/contradiction_register.md (K12):

* col. ii l. 13: fraction glyph encoded value="1/3"; arithmetic (l. 14,
  11 3/4 minae x 100 dr = 1,175 dr) requires 3/4 (same glyph as l. 4).
* col. ii l. 27: numeral gamma encoded value="6"; the letter is 3 ("three
  parts").

Conventions visible in the text and used here:

* quantities in the quarter-tax weights: 1 talent = 95 litrai (col. ii l. 7);
* litrai truncated to whole units (7,478 from 7,478.08; 1,214 from 1,214.42);
* re-expressed in the merchants' talent and truncated to whole minae;
* the merchants' talent itself is lost in the lacuna at col. ii l. 9.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction as F

TETARTE_TALENT_LITRAI = F(95)          # col. ii l. 7
MINAE_PER_TALENT = 60
DRACHMAE_PER_MONEY_TALENT = 6000


def tm(talents: int, minae) -> F:
    """Weight in talents from (talents, minae)."""
    return F(talents) + F(minae) / MINAE_PER_TALENT


def split_tm(t: F) -> tuple[int, F]:
    whole = math.floor(t)
    return whole, (t - whole) * MINAE_PER_TALENT


def truncate_to_minae(t: F) -> F:
    whole, minae = split_tm(t)
    return F(whole) + F(math.floor(minae), MINAE_PER_TALENT)


@dataclass(frozen=True)
class ItemValuation:
    commodity: str
    whole_t: F                 # col. i: full quantity before the tetarte
    quarter_t: F               # col. i: exact quarter
    taken_by_fisc_t: F         # col. i: quarter + surcharge actually removed
    listed_three_quarters_t: F # col. ii: nominal remainder
    surcharge_minae: F         # col. ii: 'pleio hyper tes tetartologias'
    valued_t: F                # col. ii: remainder after surcharge, tetarte weights
    litrai: int                # col. ii: truncated
    merchant_t: F              # col. ii: truncated to whole minae
    price_dr_per_mina: F
    value_main_dr: F
    value_surcharge_dr: F

    @property
    def value_total_dr(self) -> F:
        return self.value_main_dr + self.value_surcharge_dr


def value_item(commodity: str, whole_t: F, price_dr_per_mina: F,
               surcharge_minae: F, merchant_talent_litrai: F = F(195, 2)) -> ItemValuation:
    quarter = whole_t / 4
    listed = whole_t - quarter
    valued = listed - surcharge_minae / MINAE_PER_TALENT
    litrai = math.floor(valued * TETARTE_TALENT_LITRAI)
    merchant = truncate_to_minae(F(litrai) / merchant_talent_litrai)
    main = merchant * MINAE_PER_TALENT * price_dr_per_mina
    sur = surcharge_minae * price_dr_per_mina
    return ItemValuation(commodity, whole_t, quarter, quarter + surcharge_minae / MINAE_PER_TALENT,
                         listed, surcharge_minae, valued, litrai, merchant, price_dr_per_mina, main, sur)


def ivory() -> ItemValuation:
    # col. i l. 5: 167 tusks, 105 T 13 min; col. ii ll. 4-15; price 100 dr/mina (l. 10, l. 14)
    return value_item("ivory_sound", tm(105, 13), F(100), F(47, 4))


def schidai() -> ItemValuation:
    # col. i l. 10: 17 T 33 min; col. ii ll. 16-25; price 70 dr/mina (l. 20, l. 24)
    return value_item("schidai", tm(17, 33), F(70), F(91, 4))


def nard() -> dict:
    # col. i l. 4 (quarter: 20 boxes, context supplied); col. ii ll. 1-3: 60 boxes at 4,500 dr
    boxes_three_quarters = 60
    return dict(commodity="gangetic_nard", whole_boxes=boxes_three_quarters * 4 // 3,
                quarter_boxes=boxes_three_quarters // 3, value_dr=F(boxes_three_quarters * 4500))


# What the papyrus states, for comparison (DDbDP numerals, money in drachmas).
STATED = {
    "ivory_litrai": 7478,                                  # col. ii l. 7
    "ivory_merchant_t": tm(76, 41),                        # col. ii l. 10
    "ivory_value_main_dr": F(76 * 6000 + 4100),            # col. ii l. 10
    "ivory_value_surcharge_dr": F(1175),                   # col. ii l. 14
    "ivory_value_total_dr": F(76 * 6000 + 5275),           # col. ii l. 15
    "ivory_fisc_taken_t": tm(26, 30),                      # col. i l. 6
    "ivory_quarter_t": tm(26, F(73, 4)),                   # col. i l. 9 (26 T 18 1/4)
    "ivory_listed_t": tm(78, F(219, 4)),                   # col. ii l. 4 (78 T 54 3/4)
    "ivory_valued_t": tm(78, 43),                          # col. ii l. 5
    "schidai_litrai": 1214,                                # col. ii l. 19
    "schidai_merchant_t": tm(12, 27),                      # col. ii l. 20
    "schidai_value_main_dr": F(8 * 6000 + 4290),           # col. ii l. 21
    "schidai_value_surcharge_dr": F(1592) + F(1, 2),       # col. ii l. 24 (3 obols)
    "schidai_value_total_dr": F(8 * 6000 + 5882) + F(1, 2),# col. ii l. 25
    "schidai_fisc_taken_t": tm(4, 46),                     # col. i l. 11
    "schidai_quarter_t": tm(4, F(93, 4)),                  # col. i l. 13 (4 T 23 1/4)
    "schidai_listed_t": tm(13, F(39, 4)),                  # col. ii l. 16 (13 T 9 3/4)
    "schidai_valued_t": tm(12, 47),                        # col. ii l. 17 (47 partly supplied)
    "ivory_and_schidai_total_dr": F(85 * 6000 + 5157) + F(1, 2),  # col. ii l. 26 (supplied by editor)
    "nard_value_dr": F(45 * 6000),                         # col. ii l. 3
    "pepper_value_part_dr": F(771 * 6000 + 4632),          # col. i ll. 25-26
    "grand_total_dr": F(1151 * 6000 + 5852),               # col. ii l. 29
}


def merchant_talent_interval() -> tuple[F, F]:
    """Litrai per merchants' talent consistent with BOTH truncations in the text.

    Returns (lower_exclusive, upper_inclusive). The talent itself is lost in the
    lacuna of col. ii l. 9; this is identification from the document's rounding.
    """
    lo, hi = F(0), F(10**9)
    for litrai, stated in ((STATED["ivory_litrai"], STATED["ivory_merchant_t"]),
                           (STATED["schidai_litrai"], STATED["schidai_merchant_t"])):
        upper_t = stated + F(1, MINAE_PER_TALENT)
        lo = max(lo, F(litrai) / upper_t)     # litrai/x < stated + 1 mina
        hi = min(hi, F(litrai) / stated)      # litrai/x >= stated
    return lo, hi


# ---------------------------------------------------------------------------
# Pepper: the value is preserved, the price (and so the mass) is disputed.
# ---------------------------------------------------------------------------
PEPPER_PRICE_SCENARIOS = {
    # dr per mina; source: De Romanis 2014 (ISAW Papers 8), introduction and n. 38 (machine summary)
    "DeRomanis_6": F(6),
    "Morelli_24": F(24),
}


def pepper_valued_merchant_talents(price_dr_per_mina: F, value_dr: F | None = None) -> F:
    value_dr = STATED["pepper_value_part_dr"] if value_dr is None else value_dr
    return value_dr / (price_dr_per_mina * MINAE_PER_TALENT)


def merchant_talents_to_kg(t: F, merchant_talent_litrai: F = F(195, 2), kg_per_litra: F = F(3228, 10000)) -> F:
    return t * merchant_talent_litrai * kg_per_litra
