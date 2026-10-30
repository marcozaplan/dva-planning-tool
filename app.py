import json
import re
from copy import deepcopy
from datetime import date
from html import escape

import pandas as pd
import streamlit as st

from brief import ROLES, build_pdf

st.set_page_config(page_title="DVa · Data Visualisation Planning", page_icon="🎨")

STEPS = ["Project", "Purpose & Audience", "Data & Key Fact", "Story & Content",
         "Design & Distribution", "Brief"]
FORMATS = ["Infographic", "Single chart", "Social media card", "Report figure",
           "Interactive / web", "Dashboard", "Poster", "Slide"]
LITERACY = ["General public", "Informed public", "Policy makers", "Technical experts"]
CHARTS = ["Bar", "Line", "Map", "Pictogram / icons", "Big number", "Table", "Scatter",
          "Pie / donut", "Treemap", "Flow / Sankey", "Timeline", "Illustration"]
CHANNELS = ["Facebook", "Instagram", "X / Twitter", "LinkedIn", "TikTok", "Website / blog",
            "Report / publication", "Print", "Presentation", "Email / newsletter", "Messaging apps"]
DATA_COLUMNS = ["Dataset", "Source", "Period", "Notes"]

DEFAULTS = {
    "project": "", "organisation": "", "contact": "", "deadline": None, "format": "Infographic",
    "objective": "",
    "data": [],
    "audience": "", "literacy": "Informed public", "languages": "English",
    "fact": "",
    "story": "", "takeaway": "",
    "elements": "", "charts": [],
    "title": "", "subtitle": "", "orientation": "Portrait", "layout": "",
    "heading_font": "Open Sans", "body_font": "Open Sans",
    "colors": ["#00A6E6", "#2B3A42", "#F0877A", "#F7F7F5", "#FFC845"],
    "channels": [], "dimensions": "", "distribution": "",
}

REQUIRED = {"objective": "Purpose", "data": "Data", "audience": "Audience", "fact": "Key fact",
            "story": "Story", "elements": "Content", "title": "Title", "channels": "Distribution"}

HINTS = {
    1: ["What should change after people see this: a decision, a conversation, a share?",
        "Be specific about who it's for. \"Municipal budget officers\" beats \"the public\".",
        "How much time will they give it: three seconds on a feed, or ten minutes in a report?"],
    2: ["Where does each number come from, and can you cite it? Is it the latest release?",
        "If your reader remembers only one number, which one, and why does it matter to them?",
        "Make the fact relatable: per person, per day, or next to something familiar."],
    3: ["Write the story as a sentence someone would repeat to a friend.",
        "List elements in the order a reader should see them, and cut anything that doesn't serve the story.",
        "Flag numbers the designer must not round or change."],
    4: ["Use one accent colour to highlight what matters; let the rest recede.",
        "The title should state the finding, not the topic.",
        "Every channel has its own size and attention span — list the specs you already know."],
}

if "brief" not in st.session_state:
    st.session_state.brief = deepcopy(DEFAULTS)
    st.session_state.nav = STEPS[0]
    st.session_state.loaded = None
b = st.session_state.brief


def go(i):
    st.session_state.nav = STEPS[i]


def put(name, widget, label, **kw):
    b[name] = widget(label, key=f"w_{name}", **kw)


def filled(v):
    return bool(v.strip()) if isinstance(v, str) else bool(v)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "dva"


def load(file):
    saved = json.load(file)
    for k in DEFAULTS:
        if k in saved:
            b[k] = saved[k]
    if isinstance(b["deadline"], str):
        b["deadline"] = date.fromisoformat(b["deadline"])
    for k in [k for k in st.session_state if str(k).startswith("w_")]:
        del st.session_state[k]
    st.session_state.nav = STEPS[0]


def ask(n, q):
    st.caption(f"STEP {n} OF 4")
    st.header(q)
    with st.expander("Things to think about"):
        st.markdown("\n".join(f"- {h}" for h in HINTS[n]))


def preview():
    h, bd = b["heading_font"].strip() or "sans-serif", b["body_font"].strip() or "sans-serif"
    families = "&".join("family=" + f.replace(" ", "+") for f in {h, bd})
    c = b["colors"]
    strip = "".join(f'<div style="flex:1;height:10px;background:{x}"></div>' for x in c)
    title = escape(b["title"]) or "Your title states the finding"
    subtitle = escape(b["subtitle"]) or "A subtitle adds the context: where, when, who."
    fact = escape(b["fact"][:90]) or "42%"
    st.markdown(f"""<style>@import url('https://fonts.googleapis.com/css2?{families}&display=swap');</style>
<div style="background:{c[3]};color:{c[1]};border-radius:10px;overflow:hidden;border:1px solid rgba(0,0,0,.1)">
<div style="display:flex">{strip}</div>
<div style="padding:1.2rem 1.4rem">
<div style="font-family:'{escape(h)}',sans-serif;font-size:1.6rem;font-weight:700;line-height:1.2">{title}</div>
<div style="font-family:'{escape(bd)}',sans-serif;margin-top:.4rem">{subtitle}</div>
<div style="font-family:'{escape(h)}',sans-serif;font-size:2rem;font-weight:700;color:{c[0]};margin-top:.8rem;line-height:1.2">{fact}</div>
<div style="font-family:'{escape(bd)}',sans-serif;margin-top:.6rem;padding:.3rem .6rem;display:inline-block;background:{c[4]};border-left:4px solid {c[2]}">Highlight and accent</div>
</div></div>""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## DVa")
    st.caption("Data visualisation planning, since 2016")
    nav_slot = st.empty()
    status = st.container()
    st.divider()
    upload = st.file_uploader("Resume a saved brief", type="json")
    if upload and upload.file_id != st.session_state.loaded:
        st.session_state.loaded = upload.file_id
        load(upload)
    with nav_slot:
        st.radio("Steps", STEPS, key="nav", label_visibility="collapsed",
                 on_change=lambda: go(STEPS.index(st.session_state.nav)))

step = STEPS.index(st.session_state.nav)

if step == 0:
    st.title("DVa")
    st.markdown(
        "**A data visualisation planning tool.** DVa started as a pen-and-paper form at the "
        "Southeast Asia Open Data Innovation Week in November 2016. It walks you through a few "
        "questions so that what you hand your designer is a clear brief, not a spreadsheet and a hope."
    )
    st.markdown("Less than an hour and two cups of coffee. Start with the basics.")
    put("project", st.text_input, "Project name", value=b["project"])
    a, c = st.columns(2)
    with a:
        put("organisation", st.text_input, "Organisation", value=b["organisation"])
        put("format", st.selectbox, "What are you making?", options=FORMATS,
            index=FORMATS.index(b["format"]))
    with c:
        put("contact", st.text_input, "Contact person", value=b["contact"])
        put("deadline", st.date_input, "Deadline", value=b["deadline"])

elif step == 1:
    ask(1, "Why are we making this, and who is it for?")
    put("objective", st.text_area, "Objective", value=b["objective"], height=130,
        placeholder="e.g. Push the provincial board to publish mining revenue shares before the budget hearing.")
    st.divider()
    put("audience", st.text_area, "Target audience", value=b["audience"], height=100)
    a, c = st.columns(2)
    with a:
        put("literacy", st.selectbox, "How comfortable are they with data?", options=LITERACY,
            index=LITERACY.index(b["literacy"]))
    with c:
        put("languages", st.text_input, "Languages", value=b["languages"])

elif step == 2:
    ask(2, "What data do we have, and what's the one fact that matters?")
    edited = st.data_editor(
        pd.DataFrame(b["data"], columns=DATA_COLUMNS), key="w_data", num_rows="dynamic", hide_index=True,
        column_config={c: st.column_config.TextColumn(c) for c in DATA_COLUMNS},
    )
    b["data"] = [r for r in edited.fillna("").to_dict("records") if any(str(v).strip() for v in r.values())]
    st.caption("One row per dataset. Add a link in Source so the designer can check figures.")
    st.divider()
    put("fact", st.text_area, "The one fact readers should remember", value=b["fact"], height=100,
        placeholder="e.g. 3 in 5 mining towns received less than half of the revenue share.")

elif step == 3:
    ask(3, "What's the story, and what should we show?")
    put("story", st.text_area, "The story", value=b["story"], height=140)
    put("takeaway", st.text_input, "After seeing it, readers should…", value=b["takeaway"])
    st.divider()
    put("elements", st.text_area, "Elements to show, in reading order", value=b["elements"], height=140,
        placeholder="1. Headline number\n2. Map of provinces by share received\n3. Trend since 2015")
    put("charts", st.multiselect, "Chart types you have in mind", options=CHARTS, default=b["charts"])

elif step == 4:
    ask(4, "What should it look like, and how will it reach people?")
    put("title", st.text_input, "Title", value=b["title"])
    put("subtitle", st.text_input, "Heading / subtitle", value=b["subtitle"])
    put("orientation", st.radio, "Orientation", options=["Portrait", "Landscape", "Square", "Long scroll"],
        index=["Portrait", "Landscape", "Square", "Long scroll"].index(b["orientation"]), horizontal=True)
    put("layout", st.text_area, "Layout notes", value=b["layout"], height=90,
        placeholder="Big number top left, map as hero, sources in footer.")
    a, c = st.columns(2)
    with a:
        put("heading_font", st.text_input, "Heading font", value=b["heading_font"],
            help="Any Google Fonts name previews below.")
    with c:
        put("body_font", st.text_input, "Body font", value=b["body_font"])
    st.markdown("**Colour scheme**")
    for i, col in enumerate(st.columns(5)):
        b["colors"][i] = col.color_picker(ROLES[i], b["colors"][i], key=f"w_color{i}")
    st.markdown("**Preview**")
    preview()
    st.divider()
    put("channels", st.multiselect, "Channels", options=CHANNELS, default=b["channels"])
    put("dimensions", st.text_input, "Sizes and file specs", value=b["dimensions"],
        placeholder="1080×1350 PNG for Instagram, A3 PDF for print")
    put("distribution", st.text_area, "Distribution plan", value=b["distribution"], height=100)

else:
    st.title(b["project"] or "Your brief")
    missing = [v for k, v in REQUIRED.items() if not filled(b[k])]
    if missing:
        st.warning("Still blank: " + ", ".join(missing) + ". You can download now, but expect questions from your designer.")
    else:
        st.success("Every core section is filled in. Ready for your designer.")
    if filled(b["title"]):
        st.subheader(b["title"])
    if filled(b["story"]):
        st.write(b["story"])
    st.download_button("Download PDF brief", build_pdf(b), type="primary",
                       file_name=f"{slug(b['project'])}-brief.pdf", mime="application/pdf")

st.divider()
left, _, right = st.columns([1, 2, 1])
if step > 0:
    left.button("← Back", on_click=go, args=(step - 1,))
if step < len(STEPS) - 1:
    right.button("Next →", on_click=go, args=(step + 1,), type="primary")

with status:
    done = sum(filled(b[k]) for k in REQUIRED)
    st.progress(done / len(REQUIRED), text=f"{done} of {len(REQUIRED)} core answers")
    st.download_button("Save progress", json.dumps(b, default=str, indent=2),
                       file_name=f"{slug(b['project'])}-dva.json", mime="application/json")
