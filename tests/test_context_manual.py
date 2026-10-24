"""Tests for researcher-supplied datasets (romeco.context.manual).

Pure-function tests always run; data-dependent tests skip when the manual files are absent
(they are git-ignored and supplied by the researcher; checksums in config/datasets.lock.yaml).
"""

import math
import struct

import numpy as np
import pytest
import yaml

from romeco.context import manual as m

ROOT = m.ROOT


def test_mercator_inverse_round_trip():
    # forward ellipsoidal Mercator (EPSG:3395) for a point near Coptos
    lon, lat = 32.81, 26.0
    phi = math.radians(lat)
    es = m._E * math.sin(phi)
    y = m._A * math.log(math.tan(math.pi / 4 + phi / 2) * ((1 - es) / (1 + es)) ** (m._E / 2))
    x = m._A * math.radians(lon)
    lo, la = m.mercator3395_to_lonlat(x, y)
    assert abs(lo - lon) < 1e-9 and abs(la - lat) < 1e-9


def test_wkb_linestring_parse():
    pts = [(1.0, 2.0), (3.0, 4.0)]
    wkb = struct.pack("<BII", 1, 2, len(pts)) + b"".join(struct.pack("<dd", *p) for p in pts)
    # GeoPackage header: 'GP', version, flags (little-endian, no envelope), srs_id
    blob = b"GP" + bytes([0, 0b00000001]) + struct.pack("<i", 3395) + wkb
    lines = m.gpkg_lines(blob)
    assert len(lines) == 1 and len(lines[0]) == 2


def test_haversine_scale():
    # one degree of latitude ~ 111.2 km
    assert abs(m._hav(32.0, 25.0, 32.0, 26.0) - 111.2) < 0.5


def test_break_scan_recovers_synthetic_step():
    # synthetic software test (not evidence): a clean doubling at tau=165
    rng = np.random.default_rng(1)
    years = np.arange(80, 260, 5, dtype=float)
    lp = np.log(9) + np.log(2) * (years > 165) + rng.normal(0, 0.02, len(years))
    s = m.break_scan(years, lp, range(140, 221))
    best = s.loc[s.sse.idxmin()]
    assert 165 <= best.tau < 170
    assert abs(best.ratio - 2) < 0.05


def test_lock_registers_manual_checksums():
    lock = yaml.safe_load(open(ROOT / "config" / "datasets.lock.yaml"))
    for key, name in [("itinere", "itinere"), ("hanson_cities", "hanson_cities"), ("harper_prices", "harper_prices")]:
        files = lock[key]["files"]
        assert m.EXPECTED_SHA256[name] in {f["sha256"] for f in files.values()}


needs = lambda name: pytest.mark.skipif(not m.available(name), reason=f"{name} not supplied")


@needs("harper_prices")
def test_harper_checksum_and_break():
    m.verify("harper_prices")
    r = m.harper_break_analysis(seed=20261024, n_boot=200)
    assert r["median_70_169"] == 9.0 and r["median_190_259"] == 16.0
    assert 1.6 < r["best_ratio"] < 2.6
    # identification limit: tau is tied over the data gap; the scan cannot separate 160..187
    s = m.harper_wheat_1_3c()
    y = s[s.Year_value.between(1, 275) & s.price_dr_art.notna()].Year_value
    assert not ((y > 160) & (y <= 187)).any()


@needs("itinere")
def test_itinere_coptos_berenike_route():
    m.verify("itinere")
    g = m.itinere_graph((32.6, 23.8, 35.6, 26.3))
    r = m.route_km(g, (32.814, 25.998), (35.475, 23.911))
    assert r["connected"]
    assert 395 < r["km"] < 415  # c. 402-408 km; longer than Pliny's ~380


@needs("hanson_cities")
def test_hanson_checksum_and_aegyptus_count():
    m.verify("hanson_cities")
    summary, _ = m.hanson_city_summary({"W2": (100, 200)})
    row = summary[(summary.province == "Aegyptus") & (summary.window == "W2")].iloc[0]
    assert row.cities == 47 and row.with_area == 20
