#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FlowCast engine - pure-Python math core (no UI)."""
import json, copy
SCHEMA_VERSION = 5
DEFAULT_SOURCES = ["Jeff (salary)", "Jess (salary)", "Pension / 403b",
                   "Trust distribution", "Other distribution", "Misc income"]
DEFAULT_TABLE_LABELS = {
    "year": "Year", "age": "Age", "begin": "Begin NW", "home_value": "Home value",
    "income": "Income", "living": "Living exp", "education": "Education",
    "events": "Events", "contribution": "Give Steven", "end": "Proj. NW",
    "original": "Original NW", "diff": "Diff vs orig",
}
_SEED = json.loads(r"""{"SRC":{"2026":{"Jeff (salary)":255426.9,"Jess (salary)":36720.0,"Pension / 403b":30000.0,"Trust distribution":6829,"Other distribution":43920,"Misc income":20026.3},"2027":{"Jeff (salary)":264481.5,"Jess (salary)":37454.4,"Pension / 403b":30000.0,"Trust distribution":7179,"Other distribution":30625.46,"Misc income":20026.3},"2028":{"Jeff (salary)":264481.5,"Jess (salary)":38203.49,"Pension / 403b":30000.0,"Trust distribution":7547,"Other distribution":30825.46,"Misc income":20026.3},"2029":{"Jeff (salary)":264481.5,"Jess (salary)":38967.56,"Pension / 403b":30000.0,"Trust distribution":7934,"Other distribution":31025.46,"Misc income":20026.3},"2030":{"Jeff (salary)":264481.5,"Jess (salary)":39746.91,"Pension / 403b":30000.0,"Trust distribution":8342,"Other distribution":31225.46,"Misc income":20026.3},"2031":{"Jeff (salary)":264481.5,"Jess (salary)":40541.85,"Pension / 403b":30000.0,"Trust distribution":7816,"Other distribution":31425.46,"Misc income":20026.3},"2032":{"Jeff (salary)":264481.5,"Jess (salary)":41352.68,"Pension / 403b":30000.0,"Trust distribution":1518,"Other distribution":31625.46,"Misc income":20026.3},"2033":{"Jeff (salary)":264481.5,"Jess (salary)":42179.74,"Pension / 403b":80000.0,"Trust distribution":0.0,"Other distribution":31825.46,"Misc income":20026.3},"2034":{"Jeff (salary)":265617.3,"Jess (salary)":43023.33,"Pension / 403b":80000.0,"Trust distribution":0.0,"Other distribution":32139.04,"Misc income":20026.3},"2035":{"Jeff (salary)":267748.5,"Jess (salary)":43883.8,"Pension / 403b":80000.0,"Trust distribution":0.0,"Other distribution":32552.16,"Misc income":20026.3},"2036":{"Jeff (salary)":269879.7,"Jess (salary)":44761.48,"Pension / 403b":80000.0,"Trust distribution":0.0,"Other distribution":32965.28,"Misc income":20026.3},"2037":{"Jeff (salary)":272010.9,"Jess (salary)":45656.7,"Pension / 403b":80000.0,"Trust distribution":0.0,"Other distribution":33378.4,"Misc income":20026.3},"2038":{"Jeff (salary)":274142.1,"Jess (salary)":46569.84,"Pension / 403b":130000.0,"Trust distribution":0.0,"Other distribution":33791.52,"Misc income":20026.3},"2039":{"Jeff (salary)":276273.3,"Jess (salary)":0.0,"Pension / 403b":130000.0,"Trust distribution":0.0,"Other distribution":34204.64,"Misc income":20026.3},"2040":{"Jeff (salary)":278404.5,"Jess (salary)":0.0,"Pension / 403b":130000.0,"Trust distribution":0.0,"Other distribution":34617.76,"Misc income":20026.3},"2041":{"Jeff (salary)":280535.7,"Jess (salary)":0.0,"Pension / 403b":130000.0,"Trust distribution":0.0,"Other distribution":35030.88,"Misc income":20026.3},"2042":{"Jeff (salary)":282666.9,"Jess (salary)":0.0,"Pension / 403b":130000.0,"Trust distribution":0.0,"Other distribution":35444.0,"Misc income":20026.3},"2043":{"Jeff (salary)":284798.1,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":35857.12,"Misc income":20026.3},"2044":{"Jeff (salary)":286929.3,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":36270.24,"Misc income":20026.3},"2045":{"Jeff (salary)":289060.5,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":36683.36,"Misc income":20026.3},"2046":{"Jeff (salary)":291191.7,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":37096.48,"Misc income":20026.3},"2047":{"Jeff (salary)":293322.9,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":37509.6,"Misc income":20026.3},"2048":{"Jeff (salary)":295454.1,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":37922.72,"Misc income":20026.3},"2049":{"Jeff (salary)":297585.3,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":38335.84,"Misc income":20026.3},"2050":{"Jeff (salary)":299716.5,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":38748.96,"Misc income":20026.3},"2051":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":350000.0,"Other distribution":6903.9,"Misc income":20026.3},"2052":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2053":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2054":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2055":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2056":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2057":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2058":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2059":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2060":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2061":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2062":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2063":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2064":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2065":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2066":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2067":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2068":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2069":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2070":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2071":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2072":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2073":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2074":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2075":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2076":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2077":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2078":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2079":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2080":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2081":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2082":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2083":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2084":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3},"2085":{"Jeff (salary)":0.0,"Jess (salary)":0.0,"Pension / 403b":180000.0,"Trust distribution":0.0,"Other distribution":6903.9,"Misc income":20026.3}},"LIV":{"2026":260501.24,"2027":268316.28,"2028":276365.77,"2029":284656.74,"2030":293196.45,"2031":301992.34,"2032":311052.11,"2033":320383.67,"2034":329995.18,"2035":339895.04,"2036":350091.89,"2037":360594.65,"2038":371412.49,"2039":382554.86,"2040":394031.51,"2041":405852.45,"2042":418028.03,"2043":430568.87,"2044":443485.93,"2045":456790.51,"2046":470494.23,"2047":484609.05,"2048":499147.32,"2049":514121.74,"2050":529545.4,"2051":481159.76,"2052":495594.55,"2053":510462.39,"2054":525776.26,"2055":541549.55,"2056":557796.03,"2057":574529.91,"2058":591765.81,"2059":609518.78,"2060":627804.35,"2061":646638.48,"2062":666037.63,"2063":686018.76,"2064":706599.33,"2065":727797.3,"2066":749631.22,"2067":772120.16,"2068":795283.77,"2069":819142.28,"2070":843716.55,"2071":869028.04,"2072":895098.88,"2073":921951.85,"2074":949610.41,"2075":978098.72,"2076":1007441.68,"2077":1037664.93,"2078":1068794.88,"2079":1100858.72,"2080":1133884.49,"2081":1167901.02,"2082":1202938.05,"2083":1239026.19,"2084":1276196.98,"2085":1314483.89},"EDU":{"2026":22000,"2027":22000,"2028":25000,"2029":25000,"2030":25000,"2031":32500,"2032":142000,"2033":173000,"2034":241000,"2035":241000,"2036":138000,"2037":206000,"2038":103000,"2039":103000,"2040":103000,"2041":0.0,"2042":0.0,"2043":0.0,"2044":0.0,"2045":0.0,"2046":0.0,"2047":0.0,"2048":0.0,"2049":0.0,"2050":0.0,"2051":0.0,"2052":0.0,"2053":0.0,"2054":0.0,"2055":0.0,"2056":0.0,"2057":0.0,"2058":0.0,"2059":0.0,"2060":0.0,"2061":0.0,"2062":0.0,"2063":0.0,"2064":0.0,"2065":0.0,"2066":0.0,"2067":0.0,"2068":0.0,"2069":0.0,"2070":0.0,"2071":0.0,"2072":0.0,"2073":0.0,"2074":0.0,"2075":0.0,"2076":0.0,"2077":0.0,"2078":0.0,"2079":0.0,"2080":0.0,"2081":0.0,"2082":0.0,"2083":0.0,"2084":0.0,"2085":0.0},"EVENTS":[{"year":2026,"name":"Bar/Bat Mitzvah + camp x2","category":"Bar/Bat Mitzvah","type":"expense","amount":89000.0},{"year":2027,"name":"Summer camp x3","category":"Camp","type":"expense","amount":36000.0},{"year":2028,"name":"Bar/Bat Mitzvah + camp x2","category":"Bar/Bat Mitzvah","type":"expense","amount":124000.0},{"year":2029,"name":"Car + camp x2","category":"Car","type":"expense","amount":57000.0},{"year":2030,"name":"Camp + car","category":"Car","type":"expense","amount":52000.0},{"year":2031,"name":"Bar/Bat Mitzvah","category":"Bar/Bat Mitzvah","type":"expense","amount":100000.0},{"year":2033,"name":"First car - child 2","category":"Car","type":"expense","amount":45000.0},{"year":2034,"name":"Car","category":"Car","type":"expense","amount":40000.0},{"year":2036,"name":"Family sabbatical / big trip","category":"Travel/Sabbatical","type":"expense","amount":70000.0},{"year":2038,"name":"Car - child 3","category":"Car","type":"expense","amount":45000.0},{"year":2040,"name":"Wedding - child 1","category":"Wedding","type":"expense","amount":120000.0},{"year":2041,"name":"European sabbatical","category":"Travel/Sabbatical","type":"expense","amount":90000.0},{"year":2043,"name":"Wedding - child 2","category":"Wedding","type":"expense","amount":120000.0},{"year":2044,"name":"New car","category":"Car","type":"expense","amount":55000.0},{"year":2046,"name":"Wedding - child 3","category":"Wedding","type":"expense","amount":120000.0},{"year":2048,"name":"Vacation home purchase","category":"Home purchase","type":"expense","amount":900000.0},{"year":2052,"name":"New car","category":"Car","type":"expense","amount":60000.0},{"year":2058,"name":"Car","category":"Car","type":"expense","amount":60000.0},{"year":2064,"name":"Milestone anniversary trip","category":"Travel/Sabbatical","type":"expense","amount":80000.0},{"year":2070,"name":"New car","category":"Car","type":"expense","amount":65000.0},{"year":2050,"name":"Inheritance","category":"Inheritance","type":"income","amount":10000000.0}]}""")


def _seed_sources(year):
    s = _SEED["SRC"].get(str(year)) or _SEED["SRC"].get("2085", {})
    return {k: float(s.get(k, 0.0)) for k in DEFAULT_SOURCES}


def _base_settings():
    return {
        "start_year": 2026, "target_year": 2085,
        "current_net_worth": 5_000_000.0, "original_target": 53_735_176.0,
        "growth_rate": 0.045, "inflation_rate": 0.03,
        "legacy_children": 3, "legacy_per_child": 10_000_000.0,
        "legacy_charity": 10_000_000.0, "steven_name": "Steven",
        "jhs_birth_year": 1985,
        "ssi_enabled": False, "ssi_amount": 29657.52,
        "ssi_start_year": 2052, "ssi_grow_with_inflation": True,
        "target_mode": "original", "spend_extra_enabled": False,
    }


def default_model():
    start, target = 2026, 2085
    liv = {int(k): v for k, v in _SEED["LIV"].items()}
    edu = {int(k): v for k, v in _SEED["EDU"].items()}
    years = {}
    home0, infl0 = 1_500_000.0, 0.03
    for i, y in enumerate(range(start, target + 1)):
        years[y] = {
            "begin_override": None,
            "home_value": round(home0 * (1 + infl0) ** i, 2),
            "sources": _seed_sources(y),
            "living": float(liv.get(y, 0.0)),
            "education": float(edu.get(y, 0.0)),
        }
    model = {
        "schema_version": SCHEMA_VERSION, "settings": _base_settings(),
        "source_names": list(DEFAULT_SOURCES),
        "table_labels": dict(DEFAULT_TABLE_LABELS),
        "years": {str(y): years[y] for y in years},
        "events": copy.deepcopy(_SEED["EVENTS"]),
        "original_projection": {}, "plan_name": "My Legacy Plan",
    }
    base = compute_core(model, 0.0)
    model["original_projection"] = {str(r["year"]): round(r["end"], 2) for r in base}
    model["settings"]["original_target"] = round(base[-1]["end"], 2)
    return model


def blank_model(start=2026, target=2085, current_net_worth=1_000_000.0,
                birth_year=1985, sources=None):
    if not sources:
        sources = ["Salary 1", "Salary 2", "Other income"]
    years = {}
    for y in range(start, target + 1):
        years[y] = {"begin_override": None, "home_value": 0.0,
                    "sources": {s: 0.0 for s in sources}, "living": 0.0, "education": 0.0}
    s = _base_settings()
    s.update({"start_year": start, "target_year": target,
              "current_net_worth": float(current_net_worth), "jhs_birth_year": int(birth_year),
              "steven_name": "your advisor", "target_mode": "legacy",
              "legacy_children": 1, "legacy_per_child": 1_000_000.0, "legacy_charity": 0.0})
    labels = dict(DEFAULT_TABLE_LABELS); labels["contribution"] = "To invest"
    model = {"schema_version": SCHEMA_VERSION, "settings": s,
             "source_names": list(sources), "table_labels": labels,
             "years": {str(y): years[y] for y in years},
             "events": [], "original_projection": {}, "plan_name": "New Plan"}
    base = compute_core(model, 0.0)
    model["original_projection"] = {str(r["year"]): round(r["end"], 2) for r in base}
    model["settings"]["original_target"] = round(base[-1]["end"], 2)
    return model


def source_names(model):
    names = model.get("source_names")
    if not names:
        names = list(DEFAULT_SOURCES); model["source_names"] = names
    return names


def table_labels(model):
    lbl = model.get("table_labels")
    if not lbl:
        lbl = dict(DEFAULT_TABLE_LABELS); model["table_labels"] = lbl
    for k, v in DEFAULT_TABLE_LABELS.items():
        lbl.setdefault(k, v)
    return lbl


def migrate_model(m):
    migrated = False
    base = default_model()
    m.setdefault("settings", {}); m.setdefault("years", {})
    m.setdefault("events", []); m.setdefault("plan_name", "My Plan")
    for k, v in base["settings"].items():
        if k not in m["settings"]:
            m["settings"][k] = v; migrated = True
    if "source_names" not in m or not m["source_names"]:
        m["source_names"] = list(DEFAULT_SOURCES); migrated = True
    if "table_labels" not in m or not m["table_labels"]:
        m["table_labels"] = dict(DEFAULT_TABLE_LABELS); migrated = True
    else:
        for k, v in DEFAULT_TABLE_LABELS.items():
            m["table_labels"].setdefault(k, v)
    names = m["source_names"]
    for ystr, yd in m["years"].items():
        if not isinstance(yd, dict):
            continue
        src = yd.get("sources")
        if not isinstance(src, dict):
            yd["sources"] = {nm: 0.0 for nm in names}; migrated = True
        else:
            for nm in names:
                src.setdefault(nm, 0.0)
    if m.get("schema_version") != SCHEMA_VERSION:
        m["schema_version"] = SCHEMA_VERSION; migrated = True
    if not m.get("original_projection"):
        m["original_projection"] = base["original_projection"]; migrated = True
    return m, migrated


def compute_core(model, extra_spend=0.0, use_original=False):
    s = model["settings"]
    start = int(s["start_year"]); target = int(s["target_year"])
    g = float(s["growth_rate"]); infl = float(s["inflation_rate"])
    cnw = float(s["current_net_worth"])
    orig = {int(k): v for k, v in model.get("original_projection", {}).items()}
    ssi_on = bool(s.get("ssi_enabled", False)); ssi_amt = float(s.get("ssi_amount", 0) or 0)
    ssi_from = int(s.get("ssi_start_year", start)); ssi_grow = bool(s.get("ssi_grow_with_inflation", True))
    ev_in, ev_out = {}, {}
    for e in model["events"]:
        y = int(e["year"]); amt = float(e.get("amount", 0) or 0)
        if e.get("type") == "income": ev_in[y] = ev_in.get(y, 0.0) + amt
        else: ev_out[y] = ev_out.get(y, 0.0) + amt
    extra = 0.0 if use_original else float(extra_spend or 0.0)
    rows = []; end_prev = cnw
    for y in range(start, target + 1):
        yd = model["years"].get(str(y), {})
        override = yd.get("begin_override", None)
        if (not use_original) and override not in (None, ""):
            begin = float(override)
        else:
            begin = cnw if y == start else end_prev
        sources = {k: float(v or 0) for k, v in yd.get("sources", {}).items()}
        src_total = sum(sources.values())
        ssi = 0.0
        if ssi_on and y >= ssi_from:
            ssi = ssi_amt * ((1 + infl) ** (y - ssi_from) if ssi_grow else 1.0)
        income = src_total + ssi + ev_in.get(y, 0.0)
        living = float(yd.get("living", 0) or 0); edu = float(yd.get("education", 0) or 0)
        events = ev_out.get(y, 0.0)
        expense = living + edu + events + extra
        contribution = income - expense
        end = (begin + contribution) * (1 + g)
        rf = (1 + infl) ** (y - start)
        rec_income = src_total + ssi
        rec_surplus = rec_income - (living + edu)
        rows.append({
            "year": y, "age": y - int(s["jhs_birth_year"]), "begin": begin,
            "begin_override": (override not in (None, "")) and not use_original,
            "home_value": float(yd.get("home_value", 0) or 0),
            "sources": sources, "ssi": ssi, "income": income,
            "living": living, "education": edu, "events": events,
            "extra_spend": extra, "expense": expense, "contribution": contribution,
            "rec_income": rec_income, "rec_surplus": rec_surplus,
            "end": end, "end_real": end / rf,
            "original": orig.get(y, None),
            "original_real": (orig.get(y) / rf) if orig.get(y) is not None else None,
            "real_factor": rf,
        })
        end_prev = end
    return rows


def _target_value(model, base_rows):
    s = model["settings"]
    if s.get("target_mode", "original") == "legacy":
        return int(s["legacy_children"]) * float(s["legacy_per_child"]) + float(s["legacy_charity"])
    ol = base_rows[-1]["original"]
    return float(ol) if ol is not None else float(s["original_target"])


def sustainable_extra(model, base_rows=None):
    s = model["settings"]
    start = int(s["start_year"]); target = int(s["target_year"]); g = float(s["growth_rate"])
    if base_rows is None:
        base_rows = compute_core(model, 0.0)
    T = _target_value(model, base_rows)
    slack = base_rows[-1]["end"] - T
    periods = target - start + 1
    annuity_full = sum((1 + g) ** e for e in range(1, periods + 1)) if periods > 0 else 1.0
    return slack / annuity_full, T, slack, annuity_full


def compute(model, use_original=False):
    if use_original:
        return compute_core(model, 0.0, True)
    base = compute_core(model, 0.0, False)
    if model["settings"].get("spend_extra_enabled", False):
        le, _T, _slack, _ann = sustainable_extra(model, base)
        return compute_core(model, le, False)
    return base


def dashboard_metrics(model, base_rows, live_rows):
    s = model["settings"]
    start = int(s["start_year"]); target = int(s["target_year"]); g = float(s["growth_rate"])
    base_end = base_rows[-1]["end"]
    orig_line = base_rows[-1]["original"]
    orig_end = float(orig_line) if orig_line is not None else float(s["original_target"])
    legacy = int(s["legacy_children"]) * float(s["legacy_per_child"]) + float(s["legacy_charity"])
    surplus0 = base_rows[0]["income"] - base_rows[0]["expense"]
    this_income = base_rows[0]["income"]; this_expense = base_rows[0]["expense"]
    le, T, slack, annuity_full = sustainable_extra(model, base_rows)
    periods = target - start + 1
    factor_once = (1 + g) ** periods
    cushion_once = slack / factor_once
    required_once = surplus0 - cushion_once
    n = target - start
    annuity = sum((1 + g) ** k for k in range(1, n + 1)) if n > 0 else 1.0
    gap_orig = orig_end - base_end; gap_legacy = legacy - base_end
    return {
        "base_end": base_end, "live_end": live_rows[-1]["end"],
        "orig_end": orig_end, "legacy_goal": legacy,
        "target_mode": s.get("target_mode", "original"), "target_value": T,
        "surplus": surplus0, "this_income": this_income, "this_expense": this_expense,
        "slack": slack, "cushion_once": cushion_once, "required_once": required_once,
        "sustainable_extra": le, "annuity_full": annuity_full,
        "spend_extra_on": bool(s.get("spend_extra_enabled", False)),
        "gap_orig": gap_orig, "gap_legacy": gap_legacy,
        "on_track_original": base_end >= orig_end, "on_track_legacy": base_end >= legacy,
    }


def refreeze_original(model):
    base = compute_core(model, 0.0, use_original=True)
    model["original_projection"] = {str(r["year"]): round(r["end"], 2) for r in base}
    model["settings"]["original_target"] = round(base[-1]["end"], 2)
    return model


def money(x):
    if x is None: return "-"
    try: return "${:,.0f}".format(float(x))
    except Exception: return str(x)
