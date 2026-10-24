"""The papyrus's own arithmetic must reproduce every stated intermediate figure."""

from fractions import Fraction as F
from pathlib import Path

import pytest

from romeco.ingest.epidoc import line, read_lines, sha256
from romeco.m0 import pvindob_arithmetic as P

ROOT = Path(__file__).resolve().parents[1]
EPIDOC = ROOT / "data" / "raw" / "idp_data" / "f03d0f371306deacd0bc302010f2c6a2e7b1d1da" / "DDbDP" / "27" / "27666.xml"
EPIDOC_SHA256 = "39d38d5e371d62a16003f89d97770918b784bc5f107ce6e90527574159e0d9ad"


@pytest.mark.parametrize("fn,prefix", [(P.ivory, "ivory"), (P.schidai, "schidai")])
def test_item_procedure_reproduces_every_stated_figure(fn, prefix):
    it, S = fn(), P.STATED
    assert it.quarter_t == S[f"{prefix}_quarter_t"]
    assert it.taken_by_fisc_t == S[f"{prefix}_fisc_taken_t"]
    assert it.listed_three_quarters_t == S[f"{prefix}_listed_t"]
    assert it.valued_t == S[f"{prefix}_valued_t"]
    assert it.litrai == S[f"{prefix}_litrai"]
    assert it.merchant_t == S[f"{prefix}_merchant_t"]
    assert it.value_main_dr == S[f"{prefix}_value_main_dr"]
    assert it.value_surcharge_dr == S[f"{prefix}_value_surcharge_dr"]
    assert it.value_total_dr == S[f"{prefix}_value_total_dr"]


def test_ivory_plus_schidai_matches_editorial_supplement_l26():
    assert P.ivory().value_total_dr + P.schidai().value_total_dr == P.STATED["ivory_and_schidai_total_dr"]


def test_nard_quarter_and_value():
    n = P.nard()
    assert (n["whole_boxes"], n["quarter_boxes"], n["value_dr"]) == (80, 20, P.STATED["nard_value_dr"])


def test_merchant_talent_identified_by_rounding():
    lo, hi = P.merchant_talent_interval()
    assert lo < F(195, 2) <= hi               # 97.5 litrai is consistent
    assert float(hi - lo) < 0.02              # and the interval is narrow


def test_pepper_mass_ratio_is_exactly_the_price_ratio():
    a = P.pepper_valued_merchant_talents(P.PEPPER_PRICE_SCENARIOS["DeRomanis_6"])
    b = P.pepper_valued_merchant_talents(P.PEPPER_PRICE_SCENARIOS["Morelli_24"])
    assert a / b == 4


def test_morelli_price_reproduces_ddbdp_line_col_i_l21():
    t = P.pepper_valued_merchant_talents(P.PEPPER_PRICE_SCENARIOS["Morelli_24"])
    assert P.truncate_to_minae(t) == P.tm(3215, 43)


@pytest.mark.skipif(not EPIDOC.exists(), reason="raw EpiDoc snapshot not present (git-ignored)")
class TestAgainstEpiDoc:
    def test_snapshot_checksum(self):
        assert sha256(EPIDOC) == EPIDOC_SHA256

    def test_stated_numerals_present_in_text(self):
        L = read_lines(EPIDOC)
        vals = lambda tp, col, n: [nm.value for nm in line(L, tp, col, n).numerals]
        assert vals("v", "ii", "29") == ["1151", "5852"]
        assert vals("v", "ii", "7")[-1] == "7478"
        assert vals("v", "ii", "19") == ["1214"]
        assert vals("v", "i", "25") == ["771"] and vals("v", "i", "26") == ["4632"]
        assert "3215" in vals("v", "i", "21")

    def test_known_encoding_issues_still_present(self):
        # K12: if these fail, DDbDP has been corrected; update the register.
        L = read_lines(EPIDOC)
        assert line(L, "v", "ii", "27").numerals[0].value == "6"
        assert "1/3" in [nm.value for nm in line(L, "v", "ii", "13").numerals]
