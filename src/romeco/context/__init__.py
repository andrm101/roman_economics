"""Context layer: legions, cities, roads, prices/inflation.

Builds small, derived, provenance-labelled tables in data/derived/context/
from pinned raw datasets (config/datasets.yaml) and curated anchors
(data/curated/context/). Everything here is *context*: it constrains or
conditions the pilot models, it is not itself a test of RQ1.

Derived outputs inherit the strictest licence of their inputs (AWMC: ODbL,
share-alike) -- see data/derived/context/README.md.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import yaml

from romeco.ingest.fetch import raw_path

ROOT = Path(__file__).resolve().parents[3]
CUR = ROOT / "data" / "curated" / "context"
OUT = ROOT / "data" / "derived" / "context"

EGYPT_BBOX = (24.0, 20.0, 37.5, 32.0)          # lon_min, lat_min, lon_max, lat_max
EASTERN_DESERT_BBOX = (32.6, 22.0, 36.2, 28.6)  # Nile valley edge to Red Sea coast
WINDOWS = {"W1": (-30, 90), "W2": (100, 200)}   # D002


def _windows() -> dict:
    cfg = yaml.safe_load((ROOT / "config" / "project.yaml").read_text(encoding="utf-8"))
    return cfg.get("windows", WINDOWS)


def haversine_km(lon1, lat1, lon2, lat2) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def line_km(coords) -> float:
    return sum(haversine_km(*coords[i][:2], *coords[i + 1][:2]) for i in range(len(coords) - 1))


def _in_bbox(lon, lat, bbox) -> bool:
    return bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]


def _overlaps(a_from, a_to, b_from, b_to) -> bool | None:
    if pd.isna(a_from) or pd.isna(a_to):
        return None
    return a_from <= b_to and b_from <= a_to


# ---------------------------------------------------------------------------
# Pleiades helpers
# ---------------------------------------------------------------------------
def pleiades_places() -> pd.DataFrame:
    pl = pd.read_csv(raw_path("pleiades", "data/gis/places.csv"),
                     usecols=["id", "title", "uri", "representative_latitude", "representative_longitude",
                              "location_precision"], low_memory=False)
    pt = pd.read_csv(raw_path("pleiades", "data/gis/places_place_types.csv"))
    types = pt.groupby("place_id").place_type.apply(lambda s: ";".join(sorted(set(s))))
    pl["place_types"] = pl.id.map(types).fillna("")
    lp = pd.read_csv(raw_path("pleiades", "data/gis/location_points.csv"),
                     usecols=["place_id", "year_after_which", "year_before_which"], low_memory=False)
    span = lp.groupby("place_id").agg(year_from=("year_after_which", "min"), year_to=("year_before_which", "max"))
    return pl.merge(span, left_on="id", right_index=True, how="left")


def build_gazetteer(pl: pd.DataFrame) -> pd.DataFrame:
    cw = pd.read_csv(CUR / "place_crosswalk.csv")
    g = cw.merge(pl, left_on="pleiades_id", right_on="id", how="left")
    g["resolved"] = g["title"].notna()
    cols = ["name", "pleiades_id", "role", "match_status", "title", "uri", "representative_longitude",
            "representative_latitude", "place_types", "year_from", "year_to", "resolved", "note"]
    return g[cols]


def build_eastern_desert_military(pl: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mil_types = ("fort", "fort-2", "fortlet", "station", "military-installation-or-camp-temporary", "military-base")
    is_mil = pl.place_types.apply(lambda s: any(t in s.split(";") for t in mil_types))
    inside = pl.apply(lambda r: _in_bbox(r.representative_longitude, r.representative_latitude, EASTERN_DESERT_BBOX)
                      if pd.notna(r.representative_longitude) else False, axis=1)
    ed = pl[is_mil & inside].copy()
    for w, (a, b) in _windows().items():
        ed[f"active_{w}"] = ed.apply(lambda r: _overlaps(r.year_from, r.year_to, a, b), axis=1)
    rows = []
    for w in _windows():
        col = ed[f"active_{w}"]
        rows.append(dict(window=w, active=int((col == True).sum()), inactive=int((col == False).sum()),  # noqa: E712
                         undated=int(col.isna().sum()), total=len(ed)))
    return ed, pd.DataFrame(rows)


def build_settlements(pl: pd.DataFrame) -> pd.DataFrame:
    is_set = pl.place_types.apply(lambda s: any(t in s.split(";") for t in ("settlement", "urban", "polis")))
    inside = pl.apply(lambda r: _in_bbox(r.representative_longitude, r.representative_latitude, EGYPT_BBOX)
                      if pd.notna(r.representative_longitude) else False, axis=1)
    eg = pl[is_set & inside].copy()
    rows = []
    for w, (a, b) in _windows().items():
        act = eg.apply(lambda r: _overlaps(r.year_from, r.year_to, a, b), axis=1)
        rows.append(dict(window=w, settlements_active=int((act == True).sum()),  # noqa: E712
                         undated=int(act.isna().sum()), total_in_bbox=len(eg)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Roads
# ---------------------------------------------------------------------------
def _geom_lines(g):
    return [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]


def build_awmc_roads() -> pd.DataFrame:
    fc = json.loads(raw_path("awmc", "Cultural-Data/roads/roads.geojson").read_text(encoding="utf-8"))
    rows = []
    for f in fc["features"]:
        lines = _geom_lines(f["geometry"])
        pts = [p for ln in lines for p in ln]
        region = ("eastern_desert" if any(_in_bbox(p[0], p[1], EASTERN_DESERT_BBOX) for p in pts)
                  else "egypt_other" if any(_in_bbox(p[0], p[1], EGYPT_BBOX) for p in pts) else "rest")
        p = f["properties"]
        rows.append(dict(name=p.get("Name"), major=p.get("Major_or_M"), known=p.get("Known_or_a"),
                         source=p.get("Source"), region=region, km=sum(line_km(ln) for ln in lines)))
    df = pd.DataFrame(rows)
    return df.groupby(["region", "major", "known"], dropna=False).agg(segments=("km", "size"), km=("km", "sum")).reset_index()


def build_orbis_pilot_edges(gaz: pd.DataFrame) -> pd.DataFrame:
    # Select by geography, never by label: ORBIS 'Nicopolis' is the Epirote city (identity trap).
    sites = pd.read_csv(raw_path("orbis_v2", "sites.csv"))
    name = dict(zip(sites.id, sites.label))
    in_eg = {r.id for r in sites.itertuples() if _in_bbox(r.x, r.y, EGYPT_BBOX)}
    fc = json.loads(raw_path("orbis_v2", "new_routes.geojson").read_text(encoding="utf-8"))
    rows = []
    for f in fc["features"]:
        p = f["properties"]
        a, b = name.get(p["sid"]), name.get(p["tid"])
        if p["sid"] in in_eg and p["tid"] in in_eg:
            km = sum(line_km(ln) for ln in _geom_lines(f["geometry"]))
            rows.append(dict(from_site=a, to_site=b, route_type=p["t"], field_e=p["e"], field_s=p["s"],
                             field_m=p["m"], geometry_km=round(km, 1),
                             record_origin="model_output (ORBIS v2; field semantics undocumented)"))
    df = pd.DataFrame(rows).sort_values(["from_site", "to_site"])
    ed = {r.label for r in sites.itertuples() if _in_bbox(r.x, r.y, EASTERN_DESERT_BBOX)}
    df["eastern_desert"] = df.from_site.isin(ed) | df.to_site.isin(ed)
    df["km_per_field_s"] = (df.geometry_km / df.field_s).round(2)
    return df


# ---------------------------------------------------------------------------
# Cities: AWMC urban footprints (area), Hanson pending
# ---------------------------------------------------------------------------
def _ring_area_km2(ring) -> float:
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    kx, ky = 111.320 * math.cos(lat0), 110.574
    xy = [(p[0] * kx, p[1] * ky) for p in ring]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2


def build_urban_areas() -> pd.DataFrame:
    fc = json.loads(raw_path("awmc", "Cultural-Data/urban_areas/urban_areas.geojson").read_text(encoding="utf-8"))
    rows = []
    for f in fc["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        area = sum(_ring_area_km2(poly[0]) - sum(_ring_area_km2(h) for h in poly[1:]) for poly in polys)
        p = f["properties"]
        rows.append(dict(title=p.get("title"), pleiadesid=p.get("pleiadesid"), timeperiod=p.get("timeperiod"),
                         area_ha=round(area * 100, 1), source="AWMC urban_areas (Barrington-derived)"))
    return pd.DataFrame(rows).sort_values("area_ha", ascending=False)


# ---------------------------------------------------------------------------
# Legions: provisional disposition joined to Pleiades
# ---------------------------------------------------------------------------
def build_legions(pl: pd.DataFrame) -> pd.DataFrame:
    leg = pd.read_csv(CUR / "legions_c150_provisional.csv")
    cw = pd.read_csv(CUR / "place_crosswalk.csv")
    cw = cw[cw.role.str.contains("legion_base")][["name", "pleiades_id"]]
    m = leg.merge(cw, left_on="base", right_on="name", how="left").drop(columns="name")
    m = m.merge(pl[["id", "title", "representative_longitude", "representative_latitude", "place_types"]],
                left_on="pleiades_id", right_on="id", how="left").drop(columns="id")
    return m


# ---------------------------------------------------------------------------
# Prices: deflator scenarios between evidence windows
# ---------------------------------------------------------------------------
def build_deflators() -> pd.DataFrame:
    a = pd.read_csv(CUR / "price_level_anchors.csv").set_index("anchor_id")
    w1 = a.loc["PL-EG-WHEAT-W1"]
    w3 = a.loc["PL-EG-WHEAT-W3"]
    rows = [
        dict(scenario="pre_break_central", regime="70s-160s", wheat_dr_per_artaba=w1.value_central,
             index_vs_pre_break=1.0, applies_to="W1 and Hermapollon if dated before the break"),
        dict(scenario="pre_break_low", regime="70s-160s", wheat_dr_per_artaba=w1.value_low,
             index_vs_pre_break=w1.value_low / w1.value_central, applies_to="seasonal/inter-annual band"),
        dict(scenario="pre_break_high", regime="70s-160s", wheat_dr_per_artaba=w1.value_high,
             index_vs_pre_break=w1.value_high / w1.value_central, applies_to="seasonal/inter-annual band"),
        dict(scenario="post_break_central", regime="190s-250s", wheat_dr_per_artaba=w3.value_central,
             index_vs_pre_break=w3.value_central / w1.value_central,
             applies_to="Hermapollon only if dated after the break (HGV range 126-175 makes this unlikely)"),
    ]
    return pd.DataFrame(rows)


def hermapollon_post_break_share(break_from: int = 160, break_to: int = 199,
                                 doc_from: int = 126, doc_to: int = 175) -> dict:
    """Share of the document's date range that could lie after the price break.

    Treats both ranges as uniform (an explicit assumption): returns the
    probability that a uniformly drawn document date exceeds a uniformly
    drawn break date.
    """
    n, hits = 0, 0
    for d in range(doc_from, doc_to + 1):
        for b in range(break_from, break_to + 1):
            n += 1
            hits += d > b
    return dict(p_after_break=hits / n, assumption="uniform document date and uniform break date (integer years)")


def build_all(verbose: bool = False) -> dict[str, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    pl = pleiades_places()
    outputs = {}

    def save(df: pd.DataFrame, name: str):
        path = OUT / f"{name}.csv"
        df.to_csv(path, index=False)
        outputs[name] = path
        if verbose:
            print(f"{name:32s} rows={len(df):5d}")

    gaz = build_gazetteer(pl)
    save(gaz, "pilot_gazetteer")
    ed, ed_sum = build_eastern_desert_military(pl)
    save(ed[["id", "title", "place_types", "representative_longitude", "representative_latitude", "year_from",
             "year_to"] + [c for c in ed.columns if c.startswith("active_")]], "eastern_desert_military")
    save(ed_sum, "eastern_desert_military_summary")
    save(build_settlements(pl), "egypt_settlements_summary")
    save(build_awmc_roads(), "awmc_roads_summary")
    save(build_orbis_pilot_edges(gaz), "orbis_pilot_edges")
    save(build_urban_areas(), "awmc_urban_areas")
    save(build_legions(pl), "legions_c150_joined")
    save(build_deflators(), "egypt_price_deflators")
    regime = hermapollon_post_break_share()
    (OUT / "hermapollon_price_regime.json").write_text(json.dumps(regime, indent=2))

    orbis = outputs and pd.read_csv(OUT / "orbis_pilot_edges.csv")
    cb = orbis[(orbis.from_site == "Berenice") & (orbis.to_site == "Coptos")].iloc[0]
    ed_w2 = ed_sum.set_index("window").loc["W2"]
    roads = pd.read_csv(OUT / "awmc_roads_summary.csv")
    ed_km = roads[roads.region == "eastern_desert"].km.sum()
    derived = pd.DataFrame([
        dict(assertion_id="CTX-PLEIADES-ED-MIL-W2", quantity_concept="military_installations_active_W2_eastern_desert",
             value_low=int(ed_w2.active), value_high=int(ed_w2.active + ed_w2.undated), unit="places",
             claim_text="Pleiades fort/station places in the Eastern Desert bbox whose dated locations overlap 100-200 CE (upper = + undated)",
             source="SRC-PLEIADES-DATASETS"),
        dict(assertion_id="CTX-AWMC-ED-ROAD-KM", quantity_concept="road_length_eastern_desert_bbox",
             value_low=round(ed_km), value_high=round(ed_km), unit="km",
             claim_text="Sum of AWMC (Barrington-derived) road segment lengths touching the Eastern Desert bbox; undated",
             source="SRC-AWMC-GEODATA"),
        dict(assertion_id="CTX-ORBIS-COPTOS-BERENIKE", quantity_concept="route_length_coptos_berenike",
             value_low=float(cb.geometry_km), value_high=float(cb.geometry_km), unit="km",
             claim_text=(f"ORBIS v2 edge geometry. field_s={cb.field_s} = km/30 on every road edge (tested), so its "
                        "closeness to Pliny's 12 days is a speed assumption, not evidence"),
             source="SRC-ORBIS-V2"),
        dict(assertion_id="CTX-HERMAPOLLON-POSTBREAK-P", quantity_concept="p_hermapollon_after_price_break",
             value_low=regime["p_after_break"], value_high=regime["p_after_break"], unit="probability",
             claim_text=regime["assumption"], source="SRC-HGV-TM27666; SRC-RATHBONE-2009"),
    ])
    save(derived, "context_assertions")
    return outputs
