"""
SFL System Network Analyser: Streamlit interface.

Run from the project root:

    streamlit run app/streamlit_app.py
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

from src.analyser import analyse_text, NETWORKS
from src.model import SelectionExpression
from src.renderer import render_combined, render_network
from src.segmenter import nlp


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SFL System Network Analyser",
    page_icon="◧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title { font-size: 2.1rem; font-weight: 700; color: #1f4e79;
                  margin-bottom: 0.1rem; }
    .subtitle   { font-size: 1rem; color: #5b6b7c; margin-bottom: 1.4rem; }
    .clause-box { background: #f5f8fb; border-left: 4px solid #1f4e79;
                  padding: 0.7rem 1rem; border-radius: 0 6px 6px 0;
                  margin: 0.4rem 0 0.8rem 0; }
    .embedded   { border-left-color: #9aa5b1; }
    .evidence   { color: #5b6b7c; font-size: 0.86rem; }
    .lowconf    { color: #b45309; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


ANALYSIS_KEYS = {
    "TRANSITIVITY": "transitivity",
    "THEME": "theme",
    "MOOD": "mood",
}

EXAMPLES = {
    "Simple declarative": "The lion caught the tourist.",
    "Marked Theme": "On Saturday the family left the city.",
    "Multiple Theme": "But surely Mary knows the answer.",
    "Mental process": "Mary saw the bird and immediately understood the problem.",
    "Clause complex": "The lion caught the tourist because it was hungry.",
    "Projection": "She said that he had left, but nobody believed her.",
    "Relative clauses": "The man who left early was tired. John, who left early, was tired.",
    "Short paragraph": (
        "The committee approved the proposal last week. However, several "
        "members raised concerns about the budget. They argued that the "
        "estimates were unrealistic. On Monday the chair will present a "
        "revised plan."
    ),
}


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def analyse_by_sentence(text):
    """Split into sentences, analyse each one separately."""
    doc = nlp(text)
    out = []
    for sent in doc.sents:
        s = sent.text.strip()
        if s:
            out.append({"sentence": s, "result": analyse_text(s)})
    return out


def selection_from(clause, network_key):
    """Rebuild a SelectionExpression from an analysed clause block."""
    if network_key == "mood":
        if clause["mood"] is None:
            return None
        data = clause["mood"]["selection"]
    else:
        data = clause[network_key]["selection"]

    return SelectionExpression(
        rank=data["rank"],
        features=set(data["features"]),
        sub_selections=[
            SelectionExpression(rank=s["rank"], features=set(s["features"]))
            for s in data["sub_selections"]
        ],
    )


def chosen_terms(network, features):
    """system name -> the term chosen in it."""
    out = {}
    for system in network.systems:
        for term in system.terms:
            if term.id in features:
                out[system.name] = term.name
    return out


def all_clauses(sentences, include_embedded=True):
    """Flatten to (sentence_index, sentence_text, clause_block)."""
    rows = []
    for i, block in enumerate(sentences, start=1):
        for clause in block["result"]["clauses"]:
            if not include_embedded and clause["status"] == "embedded":
                continue
            rows.append((i, block["sentence"], clause))
    return rows


def feature_set(clause, network_key):
    """All features for one clause and network, sub-selections included."""
    if network_key == "mood":
        if clause["mood"] is None:
            return set()
        data = clause["mood"]["selection"]
    else:
        data = clause[network_key]["selection"]
    features = set(data["features"])
    for sub in data["sub_selections"]:
        features |= set(sub["features"])
    return features


def show_svg(svg):
    st.markdown(
        f'<div style="overflow-x:auto; background:#fff; border:1px solid #e3e9ef; '
        f'border-radius:8px; padding:6px;">{svg}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Analysis settings")

    chosen_networks = st.multiselect(
        "Networks to analyse",
        options=list(ANALYSIS_KEYS.keys()),
        default=["TRANSITIVITY", "THEME", "MOOD"],
        help="Which metafunctions to analyse and display.",
    )

    st.markdown("---")
    st.markdown("**Systems to tabulate**")
    st.caption("Narrows the frequency tables. Diagrams always show all entered systems.")

    system_filter = {}
    for label in chosen_networks:
        key = ANALYSIS_KEYS[label]
        network = NETWORKS[key]
        names = [s.name for s in network.systems]
        system_filter[key] = st.multiselect(
            label, options=names, default=names, key=f"sys_{key}",
        )

    st.markdown("---")
    include_embedded = st.checkbox(
        "Include embedded clauses", value=True,
        help="Embedded clauses are constituents of a group, not clauses in a complex.",
    )
    only_entered = st.checkbox(
        "Diagrams: entered systems only", value=True,
        help="Off shows the whole network with unentered branches greyed.",
    )
    show_evidence = st.checkbox("Show evidence for each choice", value=True)
    confidence_flag = st.slider(
        "Flag choices below this confidence", 0.0, 1.0, 0.5, 0.05,
    )


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

st.markdown('<p class="main-title">SFL System Network Analyser</p>',
            unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Analyses English text for TRANSITIVITY, THEME and MOOD, '
    'and draws the system networks with the selected path highlighted.</p>',
    unsafe_allow_html=True,
)

col_input, col_examples = st.columns([3, 1])

with col_examples:
    st.markdown("**Examples**")
    picked = st.selectbox("Load an example", ["—"] + list(EXAMPLES.keys()),
                          label_visibility="collapsed")
    if picked != "—":
        st.session_state["text"] = EXAMPLES[picked]

with col_input:
    text = st.text_area(
        "Text to analyse",
        value=st.session_state.get("text", EXAMPLES["Clause complex"]),
        height=150,
        key="text",
    )
    run = st.button("Analyse", type="primary", use_container_width=True)


if not chosen_networks:
    st.warning("Select at least one network in the sidebar.")
    st.stop()

if not (run or text.strip()):
    st.stop()

with st.spinner("Analysing…"):
    sentences = analyse_by_sentence(text)

if not sentences:
    st.warning("No sentences found.")
    st.stop()

rows = all_clauses(sentences, include_embedded)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

tab_numbers, tab_clauses, tab_diagrams = st.tabs(
    ["Numeric results", "Clause by clause", "System networks"]
)


# --- Tab 1: numbers --------------------------------------------------------

with tab_numbers:
    total_clauses = len(rows)
    ranking = sum(1 for _, _, c in rows if c["status"] == "ranking")
    embedded = total_clauses - ranking
    nexuses = sum(len(b["result"]["nexuses"]) for b in sentences)
    confidences = [c["confidence"] for _, _, c in rows]
    all_valid = all(
        b["result"]["summary"]["all_selections_valid"] for b in sentences
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Sentences", len(sentences))
    m2.metric("Clauses", total_clauses)
    m3.metric("Ranking / embedded", f"{ranking} / {embedded}")
    m4.metric("Clause nexuses", nexuses)
    m5.metric("Mean confidence",
              f"{sum(confidences)/len(confidences):.2f}" if confidences else "—")

    if not all_valid:
        st.error("Some selections failed validation — see 'Clause by clause'.")

    st.markdown("---")

    for label in chosen_networks:
        key = ANALYSIS_KEYS[label]
        network = NETWORKS[key]
        wanted = set(system_filter.get(key, []))

        st.markdown(f"#### {label}")

        # count the term chosen in each system, across all clauses
        per_system = {}
        for _, _, clause in rows:
            features = feature_set(clause, key)
            if not features:
                continue
            for system_name, term_name in chosen_terms(network, features).items():
                if system_name not in wanted:
                    continue
                per_system.setdefault(system_name, Counter())[term_name] += 1

        if not per_system:
            st.caption("No systems entered for this network.")
            continue

        cols = st.columns(min(2, len(per_system)))
        for i, (system_name, counts) in enumerate(sorted(per_system.items())):
            with cols[i % len(cols)]:
                total = sum(counts.values())
                df = pd.DataFrame(
                    {
                        "choice": list(counts.keys()),
                        "n": list(counts.values()),
                        "%": [round(v * 100 / total, 1) for v in counts.values()],
                    }
                ).sort_values("n", ascending=False).set_index("choice")

                st.markdown(f"**{system_name}**")
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df["n"], height=180)

        st.markdown("")

    # participants and circumstances
    if "TRANSITIVITY" in chosen_networks:
        st.markdown("#### Participant roles and circumstances")
        roles = Counter()
        circs = Counter()
        for _, _, clause in rows:
            for p in clause["transitivity"]["participants"]:
                roles[p["role"]] += 1
            for c in clause["transitivity"]["circumstances"]:
                circs[c["feature"]] += 1

        c1, c2 = st.columns(2)
        with c1:
            if roles:
                st.markdown("**Participants**")
                st.dataframe(
                    pd.DataFrame({"role": list(roles), "n": list(roles.values())})
                    .sort_values("n", ascending=False).set_index("role"),
                    use_container_width=True,
                )
            else:
                st.caption("No participants found.")
        with c2:
            if circs:
                st.markdown("**Circumstances**")
                st.dataframe(
                    pd.DataFrame({"type": list(circs), "n": list(circs.values())})
                    .sort_values("n", ascending=False).set_index("type"),
                    use_container_width=True,
                )
            else:
                st.caption("No circumstances found.")

    # one row per clause
    st.markdown("#### Choices by clause")
    table_rows = []
    for sent_i, sent_text, clause in rows:
        row = {
            "S": sent_i,
            "clause": clause["clause_id"],
            "text": clause["text"],
            "status": clause["status"],
        }
        for label in chosen_networks:
            key = ANALYSIS_KEYS[label]
            features = feature_set(clause, key)
            if not features:
                continue
            wanted = set(system_filter.get(key, []))
            for system_name, term_name in chosen_terms(
                NETWORKS[key], features
            ).items():
                if system_name in wanted:
                    row[system_name] = term_name
        row["conf"] = round(clause["confidence"], 2)
        table_rows.append(row)

    df_all = pd.DataFrame(table_rows).fillna("")
    st.dataframe(df_all, use_container_width=True, hide_index=True)
    st.download_button(
        "Download this table (CSV)",
        df_all.to_csv(index=False).encode("utf-8"),
        file_name="sfl_analysis.csv",
        mime="text/csv",
    )


# --- Tab 2: clause by clause -----------------------------------------------

with tab_clauses:
    for block in sentences:
        result = block["result"]
        st.markdown(f"### {block['sentence']}")

        summary = result["summary"]
        st.caption(
            f"{summary['clause_count']} clause(s) · "
            f"{summary['ranking_clauses']} ranking, "
            f"{summary['embedded_clauses']} embedded · "
            f"{summary['nexus_count']} nexus(es)"
        )

        for clause in result["clauses"]:
            if not include_embedded and clause["status"] == "embedded":
                continue

            css = "clause-box embedded" if clause["status"] == "embedded" else "clause-box"
            st.markdown(
                f'<div class="{css}"><b>{clause["clause_id"]}</b> · '
                f'{clause["status"]} · {"finite" if clause["finite"] else "non-finite"}'
                f'<br>{clause["text"]}</div>',
                unsafe_allow_html=True,
            )
            if clause["status_reason"]:
                st.caption(f"status: {clause['status_reason']}")

            cols = st.columns(len(chosen_networks))

            for i, label in enumerate(chosen_networks):
                key = ANALYSIS_KEYS[label]
                with cols[i]:
                    st.markdown(f"**{label}**")

                    if key == "mood":
                        if clause["mood"] is None:
                            st.caption("non-finite — no mood")
                            continue
                        st.write(", ".join(clause["mood"]["features"]))
                        if show_evidence:
                            st.markdown(
                                f'<span class="evidence">{clause["mood"]["reason"]}'
                                f'</span>', unsafe_allow_html=True)
                        continue

                    block_data = clause[key]

                    if key == "theme":
                        st.markdown(
                            f"**Theme:** {block_data['theme_text']}  \n"
                            f"**Rheme:** {block_data['rheme_text']}"
                        )
                        if block_data["is_multiple"]:
                            st.caption("multiple Theme")

                    if key == "transitivity":
                        st.markdown(f"**Process:** {block_data['process']}")
                        for p in block_data["participants"]:
                            st.markdown(f"- {p['role']}: {p['text']}")
                        for c in block_data["circumstances"]:
                            st.markdown(f"- {c['feature'].title()}: {c['text']}")

                    features = chosen_terms(
                        NETWORKS[key], feature_set(clause, key)
                    )
                    if features:
                        st.dataframe(
                            pd.DataFrame(
                                {"system": list(features),
                                 "choice": list(features.values())}
                            ).set_index("system"),
                            use_container_width=True,
                        )

                    conf = block_data["confidence"]
                    if conf < confidence_flag:
                        st.markdown(
                            f'<span class="lowconf">low confidence: {conf:.2f}</span>',
                            unsafe_allow_html=True)

                    if show_evidence:
                        for e in block_data["evidence"]:
                            st.markdown(f'<span class="evidence">• {e}</span>',
                                        unsafe_allow_html=True)

                    if not block_data["selection"]["valid"]:
                        for err in block_data["selection"]["errors"]:
                            st.error(f"{err['rule']}: {err['message']}")

        if result["nexuses"]:
            st.markdown("**Clause relations**")
            for n in result["nexuses"]:
                st.markdown(
                    f"- `{n['notation']['primary']}` … "
                    f"`{n['notation']['secondary']}`  "
                    f"({n['primary_clause_id']} → {n['secondary_clause_id']}) — "
                    f"{', '.join(n['selection']['features'])}"
                )
                if show_evidence and n["reason"]:
                    st.caption(n["reason"])

        st.markdown("---")


# --- Tab 3: diagrams -------------------------------------------------------

with tab_diagrams:
    st.caption(
        "Square bracket = a choice. Brace = simultaneous systems. "
        "Bold blue = selected; grey = the alternatives not taken."
    )

    for sent_i, sent_text, clause in rows:
        sections = []
        for label in chosen_networks:
            key = ANALYSIS_KEYS[label]
            selection = selection_from(clause, key)
            if selection is None:
                continue
            sections.append((label, NETWORKS[key], selection))

        if not sections:
            continue

        st.markdown(f"#### {clause['clause_id']} — {clause['text']}")
        st.caption(f"sentence {sent_i} · {clause['status']}")

        svg = render_combined(sections, title=clause["text"],
                              only_entered=only_entered)
        show_svg(svg)

        st.download_button(
            "Download SVG",
            svg,
            file_name=f"{clause['clause_id']}_networks.svg",
            mime="image/svg+xml",
            key=f"dl_{sent_i}_{clause['clause_id']}",
        )
        st.markdown("---")