#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowCast / LegacyPath  -  Streamlit web app (with Google Drive auto-save)
=========================================================================
Runs in any browser (desktop + iPhone). Reuses flowcast_engine.py for math
and drive_store.py for optional Google Drive persistence.

If Google Drive is configured (Streamlit secrets), the app auto-loads your
plan on start and auto-saves after every change. If not, it falls back to
manual Download/Upload of a JSON file. Either way it never crashes.
"""
import json, datetime
import pandas as pd
import altair as alt
import streamlit as st

import flowcast_engine as fc
import drive_store as ds

st.set_page_config(page_title="FlowCast / LegacyPath", page_icon="\U0001F4C8",
                   layout="wide", initial_sidebar_state="expanded")


# --------------------------------------------------------------------------
#  Optional password gate  (set  app_password  in Streamlit secrets)
# --------------------------------------------------------------------------
def check_password():
    try:
        pw = st.secrets.get("app_password", None)
    except Exception:
        pw = None
    if not pw:
        return True
    if st.session_state.get("authed"):
        return True
    st.title("\U0001F512 FlowCast / LegacyPath")
    entered = st.text_input("Enter password", type="password")
    if entered:
        if entered == pw:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


check_password()


# --------------------------------------------------------------------------
#  Model state + Drive auto-save
# --------------------------------------------------------------------------
def _init_model():
    """On first load: try Drive, else seeded default."""
    if ds.is_configured(st):
        loaded, msg = ds.load(st)
        if loaded is not None:
            loaded, _ = fc.migrate_model(loaded)
            st.session_state.model = loaded
            st.session_state.drive_msg = msg
            return
        st.session_state.drive_msg = msg  # e.g. "No saved plan yet"
    st.session_state.model = fc.default_model()


if "model" not in st.session_state:
    _init_model()


def autosave():
    """Auto-save to Drive if configured. Safe no-op otherwise."""
    if ds.is_configured(st):
        ok, msg = ds.save(st, st.session_state.model)
        st.session_state.drive_msg = msg


def set_model(m, save=True):
    m, _ = fc.migrate_model(m)
    st.session_state.model = m
    if save:
        autosave()


model = st.session_state.model
s = model["settings"]
drive_on = ds.is_configured(st)


# ==========================================================================
#  SIDEBAR
# ==========================================================================
with st.sidebar:
    st.markdown("## \U0001F4C8 FlowCast")
    st.caption("Multi-decade net-worth & legacy planner")

    if drive_on:
        st.success("\u2601\uFE0F Google Drive auto-save is ON")
        if st.session_state.get("drive_msg"):
            st.caption(st.session_state["drive_msg"])
    else:
        st.info("\U0001F4BE Manual save (Drive not configured)")

    st.markdown("### Plan")
    new_name = st.text_input("Plan name", value=model.get("plan_name", "My Plan"))
    if new_name != model.get("plan_name"):
        model["plan_name"] = new_name
        autosave()

    with st.expander("Start a different plan"):
        c1, c2 = st.columns(2)
        if c1.button("Load seeded example", use_container_width=True):
            set_model(fc.default_model()); st.rerun()
        if c2.button("Start blank plan", use_container_width=True):
            set_model(fc.blank_model()); st.rerun()
        st.caption("Blank = a clean template you fill with your own numbers.")

    st.divider()
    st.markdown("### Core assumptions")
    changed = False
    v = st.number_input("Current net worth ($)", value=float(s["current_net_worth"]),
                        step=50000.0, format="%.0f")
    if v != s["current_net_worth"]: s["current_net_worth"] = v; changed = True
    cc1, cc2 = st.columns(2)
    sy = int(cc1.number_input("Start year", value=int(s["start_year"]), step=1))
    ty = int(cc2.number_input("Target year", value=int(s["target_year"]), step=1))
    if sy != s["start_year"]: s["start_year"] = sy; changed = True
    if ty != s["target_year"]: s["target_year"] = ty; changed = True
    gr = st.number_input("Growth rate %", value=float(s["growth_rate"]) * 100, step=0.25, format="%.2f")
    ir = st.number_input("Inflation %", value=float(s["inflation_rate"]) * 100, step=0.25, format="%.2f")
    if gr / 100.0 != s["growth_rate"]: s["growth_rate"] = gr / 100.0; changed = True
    if ir / 100.0 != s["inflation_rate"]: s["inflation_rate"] = ir / 100.0; changed = True
    by = int(st.number_input("Birth year (for age display)", value=int(s.get("jhs_birth_year", 1985)), step=1))
    if by != s["jhs_birth_year"]: s["jhs_birth_year"] = by; changed = True

    st.divider()
    st.markdown("### Legacy goal")
    lc1, lc2 = st.columns(2)
    kids = int(lc1.number_input("Kids", value=int(s["legacy_children"]), step=1, min_value=0))
    perk = lc2.number_input("$ / kid", value=float(s["legacy_per_child"]), step=500000.0, format="%.0f")
    char = st.number_input("Charity $", value=float(s["legacy_charity"]), step=500000.0, format="%.0f")
    if kids != s["legacy_children"]: s["legacy_children"] = kids; changed = True
    if perk != s["legacy_per_child"]: s["legacy_per_child"] = perk; changed = True
    if char != s["legacy_charity"]: s["legacy_charity"] = char; changed = True
    st.caption("Legacy goal total: **%s**" % fc.money(kids * perk + char))

    st.divider()
    st.markdown("### Retirement income")
    ssi_e = st.checkbox("Add Social Security", value=bool(s.get("ssi_enabled", False)))
    if ssi_e != s.get("ssi_enabled"): s["ssi_enabled"] = ssi_e; changed = True
    if ssi_e:
        a = st.number_input("Soc. Sec. $/yr", value=float(s["ssi_amount"]), step=1000.0, format="%.0f")
        fy = int(st.number_input("From year", value=int(s["ssi_start_year"]), step=1))
        gw = st.checkbox("Grow w/ inflation", value=bool(s.get("ssi_grow_with_inflation", True)))
        if a != s["ssi_amount"]: s["ssi_amount"] = a; changed = True
        if fy != s["ssi_start_year"]: s["ssi_start_year"] = fy; changed = True
        if gw != s["ssi_grow_with_inflation"]: s["ssi_grow_with_inflation"] = gw; changed = True

    st.divider()
    st.markdown("### Target & policy")
    tmode = st.radio("Stay on track for:", options=["original", "legacy"],
                     format_func=lambda x: "Original projection" if x == "original" else "Legacy goal",
                     index=(0 if s.get("target_mode", "original") == "original" else 1))
    if tmode != s.get("target_mode"): s["target_mode"] = tmode; changed = True
    sx = st.checkbox("\U0001F4B8 Spend the sustainable extra each year (bend to target)",
                     value=bool(s.get("spend_extra_enabled", False)))
    if sx != s.get("spend_extra_enabled"): s["spend_extra_enabled"] = sx; changed = True

    if changed:
        autosave()

    st.divider()
    st.markdown("### Save / Load")
    if drive_on:
        cs1, cs2 = st.columns(2)
        if cs1.button("Save now", use_container_width=True):
            ok, msg = ds.save(st, model); st.session_state.drive_msg = msg
            (st.success if ok else st.error)(msg)
        if cs2.button("Dated backup", use_container_width=True):
            ok, msg = ds.backup(st, model)
            (st.success if ok else st.error)(msg)
    st.download_button("\U0001F4BE Download my plan (JSON)",
                       data=json.dumps(model, indent=2),
                       file_name="flowcast_%s.json" % datetime.date.today(),
                       mime="application/json", use_container_width=True)
    up = st.file_uploader("Load a saved plan", type=["json"])
    if up is not None:
        try:
            set_model(json.load(up)); st.success("Plan loaded."); st.rerun()
        except Exception as exc:
            st.error("Could not read that file: %s" % exc)
    if st.button("Re-freeze 'original' line to current plan", use_container_width=True):
        fc.refreeze_original(model); autosave(); st.rerun()

# ==========================================================================
#  RECOMPUTE
# ==========================================================================
base_rows = fc.compute_core(model, 0.0)
live_rows = fc.compute(model)
m = fc.dashboard_metrics(model, base_rows, live_rows)
names = fc.source_names(model)
labels = fc.table_labels(model)

st.title("\U0001F4C8 %s" % model.get("plan_name", "Legacy Plan"))
tgt_name = "Legacy goal (%s)" % fc.money(m["legacy_goal"]) if m["target_mode"] == "legacy" else "original projection"

tabs = st.tabs(["\U0001F3AF Dashboard", "\U0001F4C9 Projection", "\U0001F4B0 Spend / Invest Plan",
                "\U0001F4C5 Yearly Table", "\U0001F4B5 Income Sources", "\U0001F389 Life Events", "\u2139\uFE0F Help"])

# --------------------------------------------------------------------------
#  DASHBOARD
# --------------------------------------------------------------------------
with tabs[0]:
    req = m["required_once"]; cushion = m["cushion_once"]; surplus = m["surplus"]; sustain = m["sustainable_extra"]
    req_display = max(0.0, req)
    st.subheader("Give %s this year to stay on track for the %s" % (s.get("steven_name", "your advisor"), tgt_name))
    hero1, hero2, hero3 = st.columns(3)
    hero1.metric("Required to invest THIS year", fc.money(req_display),
                 delta=("behind" if req > surplus else "on track"),
                 delta_color=("inverse" if req > surplus else "normal"))
    hero2.metric("Could spend THIS year (one-time)", fc.money(cushion))
    hero3.metric("Extra to spend EVERY year", fc.money(sustain) + " / yr")

    if req <= 0:
        st.success("You're ahead: you don't NEED to invest any surplus to hit this target. "
                   "You could spend up to **%s** extra this year \u2014 or **%s** extra every year \u2014 and still get there."
                   % (fc.money(cushion), fc.money(sustain)))
    elif req <= surplus:
        st.info("Invest at least **%s** of your **%s** surplus; the remaining **%s** is safe to spend this year. "
                "Sustainable level: **%s** extra every year."
                % (fc.money(req), fc.money(surplus), fc.money(cushion), fc.money(sustain)))
    else:
        st.warning("You're behind: even investing your entire **%s** surplus is about **%s** short this year. "
                   "To reach target you'd need to spend **%s** LESS every year."
                   % (fc.money(surplus), fc.money(req - surplus), fc.money(-sustain)))

    st.divider()
    g1, g2, g3 = st.columns(3)
    g1.metric("Yearly excess / deficit", fc.money(surplus))
    g2.metric("This year income", fc.money(m["this_income"]))
    g3.metric("This year spending", fc.money(m["this_expense"]))
    g4, g5, g6 = st.columns(3)
    g4.metric("Projected net worth @ %d" % int(s["target_year"]),
              fc.money(m["live_end"]) + (" (spending extra)" if m["spend_extra_on"] else ""))
    g5.metric("Target you must not miss", fc.money(m["target_value"]))
    go = m["gap_orig"]
    g6.metric("Vs. original target", ("%s behind" % fc.money(go)) if go > 0 else ("%s ahead" % fc.money(-go)))

    st.caption("Each year: end = (begin + income \u2212 spending) \u00d7 (1 + growth). "
               "One-time cushion = slack discounted to today; level extra spreads that slack evenly over every "
               "remaining year. Required to invest = surplus \u2212 one-time cushion.")

# --------------------------------------------------------------------------
#  PROJECTION CHART
# --------------------------------------------------------------------------
with tabs[1]:
    real = st.checkbox("Inflation-adjusted (today's $)", value=False)
    key = "end_real" if real else "end"
    okey = "original_real" if real else "original"
    df = pd.DataFrame({
        "Year": [r["year"] for r in live_rows],
        "Live projection": [r[key] for r in live_rows],
        "Original projection": [r[okey] for r in live_rows],
    })
    dfl = df.melt("Year", var_name="Series", value_name="Net worth")
    goal = m["legacy_goal"]
    base_chart = alt.Chart(dfl).mark_line().encode(
        x=alt.X("Year:Q", axis=alt.Axis(format="d", tickCount=12)),
        y=alt.Y("Net worth:Q", axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Series:N", scale=alt.Scale(
            domain=["Live projection", "Original projection"], range=["#1f6feb", "#8b949e"])),
        tooltip=["Year", "Series", alt.Tooltip("Net worth:Q", format="$,.0f")],
    )
    goal_line = alt.Chart(pd.DataFrame({"y": [goal]})).mark_rule(
        color="#2da44e", strokeDash=[6, 4]).encode(y="y:Q")
    st.altair_chart((base_chart + goal_line).properties(height=460).interactive(), use_container_width=True)
    st.caption("Blue = your live plan \u2022 grey = frozen original \u2022 green dashed = legacy goal (%s)." % fc.money(goal)
               + ("  Live line reflects spending the sustainable extra each year." if m["spend_extra_on"] else ""))

# --------------------------------------------------------------------------
#  SPEND / INVEST PLAN
# --------------------------------------------------------------------------
with tabs[2]:
    level = m["sustainable_extra"]
    dfp = pd.DataFrame({
        "Year": [r["year"] for r in base_rows],
        "Recurring surplus / yr": [r["rec_surplus"] for r in base_rows],
        "Give advisor / yr (after extra)": [r["rec_surplus"] - level for r in base_rows],
    })
    dpl = dfp.melt("Year", var_name="Series", value_name="Amount")
    line = alt.Chart(dpl).mark_line().encode(
        x=alt.X("Year:Q", axis=alt.Axis(format="d", tickCount=12)),
        y=alt.Y("Amount:Q", axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Series:N", scale=alt.Scale(
            domain=["Recurring surplus / yr", "Give advisor / yr (after extra)"],
            range=["#0969da", "#8250df"])),
        tooltip=["Year", "Series", alt.Tooltip("Amount:Q", format="$,.0f")],
    )
    extra_line = alt.Chart(pd.DataFrame({"y": [level]})).mark_rule(
        color="#1a7f37", strokeDash=[6, 4]).encode(y="y:Q")
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#c0c4c9").encode(y="y:Q")
    st.altair_chart((line + extra_line + zero).properties(height=460).interactive(), use_container_width=True)
    st.caption("Blue = recurring surplus each year \u2022 green dashed = level extra you could spend every year "
               "(**%s**/yr) \u2022 purple = what you'd still give your advisor after taking that extra. "
               "One-time events are excluded here for readability." % fc.money(level))

# --------------------------------------------------------------------------
#  YEARLY TABLE
# --------------------------------------------------------------------------
with tabs[3]:
    st.caption("Edit Home value, Living, Education, or a Begin-NW override. Income comes from the "
               "Income Sources tab. Leave Begin override blank to auto-flow. Changes auto-save.")
    rows_for_edit = []
    for r in base_rows:
        yd = model["years"].get(str(r["year"]), {})
        ov = yd.get("begin_override", None)
        rows_for_edit.append({
            "Year": r["year"], "Age": r["age"],
            "Begin override": (float(ov) if ov not in (None, "") else None),
            labels.get("home_value", "Home value"): r["home_value"],
            labels.get("living", "Living exp"): r["living"],
            labels.get("education", "Education"): r["education"],
            labels.get("income", "Income"): r["income"],
            labels.get("contribution", "Give"): r["contribution"],
            labels.get("end", "Proj NW"): r["end"],
            labels.get("original", "Original"): r["original"],
        })
    dfy = pd.DataFrame(rows_for_edit)
    editable_cols = ["Begin override", labels.get("home_value", "Home value"),
                     labels.get("living", "Living exp"), labels.get("education", "Education")]
    colcfg = {}
    for c in dfy.columns:
        if c in editable_cols:
            colcfg[c] = st.column_config.NumberColumn(c, format="$%.0f")
        elif c in ("Year", "Age"):
            colcfg[c] = st.column_config.NumberColumn(c, format="%d", disabled=True)
        else:
            colcfg[c] = st.column_config.NumberColumn(c, format="$%.0f", disabled=True)
    edited = st.data_editor(dfy, column_config=colcfg, hide_index=True,
                            use_container_width=True, height=460, key="yearly_editor")
    if st.button("Apply yearly-table changes", type="primary"):
        for _, row in edited.iterrows():
            y = str(int(row["Year"])); yd = model["years"].setdefault(y, {})
            ov = row["Begin override"]
            yd["begin_override"] = (None if pd.isna(ov) else float(ov))
            yd["home_value"] = float(row[labels.get("home_value", "Home value")] or 0)
            yd["living"] = float(row[labels.get("living", "Living exp")] or 0)
            yd["education"] = float(row[labels.get("education", "Education")] or 0)
        autosave(); st.success("Applied."); st.rerun()

# --------------------------------------------------------------------------
#  INCOME SOURCES
# --------------------------------------------------------------------------
with tabs[4]:
    st.caption("Edit any income source for any year. Rename a column below, or add/remove a source. Auto-saves.")
    data = {"Year": [r["year"] for r in base_rows]}
    for nm in names:
        data[nm] = [model["years"].get(str(r["year"]), {}).get("sources", {}).get(nm, 0.0) for r in base_rows]
    dfi = pd.DataFrame(data)
    cfg = {"Year": st.column_config.NumberColumn("Year", format="%d", disabled=True)}
    for nm in names:
        cfg[nm] = st.column_config.NumberColumn(nm, format="$%.0f")
    edited_i = st.data_editor(dfi, column_config=cfg, hide_index=True,
                              use_container_width=True, height=420, key="income_editor")
    ca, cb = st.columns(2)
    if ca.button("Apply income changes", type="primary"):
        for _, row in edited_i.iterrows():
            y = str(int(row["Year"])); yd = model["years"].setdefault(y, {}); yd.setdefault("sources", {})
            for nm in names:
                yd["sources"][nm] = float(row[nm] or 0)
        autosave(); st.success("Applied."); st.rerun()
    if cb.button("Fill start-year values down to all years"):
        first = model["years"].get(str(int(s["start_year"])), {}).get("sources", {})
        for r in base_rows:
            yd = model["years"].setdefault(str(r["year"]), {}); yd.setdefault("sources", {})
            for nm in names:
                yd["sources"][nm] = float(first.get(nm, 0.0))
        autosave(); st.success("Filled down."); st.rerun()

    st.divider()
    st.markdown("**Rename / add / remove income sources**")
    rc1, rc2, rc3 = st.columns([2, 2, 1])
    old = rc1.selectbox("Rename source", options=names, key="rename_src")
    new = rc2.text_input("New name", value="", key="rename_new")
    if rc3.button("Rename"):
        new = new.strip()
        if new and new not in names:
            i = names.index(old); names[i] = new
            for ystr, yd in model["years"].items():
                src = yd.get("sources", {})
                if old in src: src[new] = src.pop(old)
                src.setdefault(new, 0.0)
            autosave(); st.rerun()
        else:
            st.warning("Enter a unique new name.")
    ac1, ac2 = st.columns(2)
    add_name = ac1.text_input("Add new source", value="", key="add_src")
    if ac1.button("Add source"):
        add_name = add_name.strip()
        if add_name and add_name not in names:
            names.append(add_name)
            for ystr, yd in model["years"].items():
                yd.setdefault("sources", {})[add_name] = 0.0
            autosave(); st.rerun()
    rem = ac2.selectbox("Remove source", options=["(none)"] + names, key="rem_src")
    if ac2.button("Remove source") and rem != "(none)" and len(names) > 1:
        names.remove(rem)
        for ystr, yd in model["years"].items():
            yd.get("sources", {}).pop(rem, None)
        autosave(); st.rerun()

# --------------------------------------------------------------------------
#  LIFE EVENTS
# --------------------------------------------------------------------------
with tabs[5]:
    st.caption("Add, edit, or delete life events (weddings, cars, college, inheritance, unforeseen). "
               "Use the + row to add. Edit then Apply. Auto-saves.")
    evs = sorted(model["events"], key=lambda e: (int(e["year"]), e.get("category", "")))
    if evs:
        dfe = pd.DataFrame([{
            "Year": e["year"], "Category": e.get("category", "Other"),
            "Description": e.get("name", ""), "Type": e.get("type", "expense"),
            "Amount": float(e.get("amount", 0)),
        } for e in evs])
    else:
        dfe = pd.DataFrame({"Year": pd.Series(dtype="int"), "Category": pd.Series(dtype="str"),
                            "Description": pd.Series(dtype="str"), "Type": pd.Series(dtype="str"),
                            "Amount": pd.Series(dtype="float")})
    cfg_e = {
        "Year": st.column_config.NumberColumn("Year", format="%d"),
        "Category": st.column_config.SelectboxColumn("Category", options=[
            "Bar/Bat Mitzvah", "Wedding", "Car", "College", "Home purchase",
            "Travel/Sabbatical", "Inheritance", "Camp", "Medical", "Gift", "Other"]),
        "Description": st.column_config.TextColumn("Description"),
        "Type": st.column_config.SelectboxColumn("Type", options=["expense", "income"]),
        "Amount": st.column_config.NumberColumn("Amount", format="$%.0f"),
    }
    edited_e = st.data_editor(dfe, column_config=cfg_e, num_rows="dynamic",
                              hide_index=True, use_container_width=True, height=460, key="events_editor")
    if st.button("Apply event changes", type="primary"):
        newevs = []
        for _, row in edited_e.iterrows():
            if pd.isna(row.get("Year")) or pd.isna(row.get("Amount")):
                continue
            newevs.append({
                "year": int(row["Year"]), "category": str(row.get("Category") or "Other"),
                "name": str(row.get("Description") or row.get("Category") or "Event"),
                "type": str(row.get("Type") or "expense"), "amount": float(row["Amount"] or 0),
            })
        model["events"] = newevs
        autosave(); st.success("Applied."); st.rerun()

# --------------------------------------------------------------------------
#  HELP
# --------------------------------------------------------------------------
with tabs[6]:
    st.markdown("""
### How FlowCast works
Each year: **end = (begin + income − spending) × (1 + growth)**

- **Income** = income sources + Social Security (if on) + income events (e.g. an inheritance).
- **Spending** = living + education + life events.
- **Yearly excess/deficit** = income − spending.
- **Required to invest this year** = the minimum of that surplus you must invest to stay on track.
- **Could spend this year (one-time)** = a single-year splurge you could take and still hit target.
- **Extra to spend EVERY year** = a level amount you could add to spending every remaining year and still land on target.

**Two ways to start** (sidebar → *Start a different plan*):
- **Seeded example** — a fully worked plan you can explore.
- **Blank plan** — a clean template: set your net worth, years, and income sources, then fill in the tables.

**Saving:**
- If **Google Drive is connected** (cloud badge in the sidebar), the app auto-loads your plan on open and auto-saves after every change. Use *Dated backup* for snapshots.
- Otherwise, use **Download my plan (JSON)** and **Load a saved plan** manually.

**Privacy:** if a password is configured, only you can open the app.
""")
