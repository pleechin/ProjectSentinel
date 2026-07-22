from datetime import datetime
import pandas as pd
import streamlit as st

from modules.dashboard import build_dashboard_snapshot, dashboard_table, filter_dashboard_results
from modules.journal import read_journal, save_planned_opportunities
from modules.industry_analysis import get_industry_leadership
from modules.learning import generate_learning_report
from modules.market_context import get_market_context
from modules.scanner import scan_watchlist
from modules.sector_analysis import get_sector_rotation

st.set_page_config(page_title="Project Sentinel", page_icon="🛡️", layout="wide")


def _run_scan() -> None:
    with st.status("Running Project Sentinel scan...", expanded=True) as status:
        st.write("Analysing broad-market trend and volatility...")
        market = get_market_context()
        st.write("Ranking US market sectors...")
        sectors = get_sector_rotation()
        st.write("Ranking industry and thematic ETFs...")
        industries = get_industry_leadership()
        st.write("Scanning stocks and ETFs...")
        results = scan_watchlist(market, sectors=sectors, industries=industries)
        st.write("Updating planned-opportunity journal...")
        journal_result = save_planned_opportunities(results)
        st.write("Refreshing learning report...")
        learning_result = generate_learning_report()
        st.session_state.update({
            "sentinel_market": market,
            "sentinel_results": results,
            "sentinel_sectors": sectors,
            "sentinel_industries": industries,
            "sentinel_journal_result": journal_result,
            "sentinel_learning_result": learning_result,
            "sentinel_last_scan": datetime.now(),
        })
        status.update(label="Sentinel scan completed", state="complete")


def _decision_icon(decision: str) -> str:
    return {"CANDIDATE": "🟢", "WATCH": "🟡", "WAIT": "⚪"}.get(str(decision).upper(), "⚪")


def _market_icon(status: str) -> str:
    return {"BULLISH": "🟢", "NEUTRAL": "🟡", "DEFENSIVE": "🔴", "HEALTHY": "🟢", "CAUTION": "🟡", "UNHEALTHY": "🔴"}.get(str(status).upper(), "⚪")


def _render_overview(snapshot: dict) -> None:
    market, portfolio, journal = snapshot["market"], snapshot["portfolio"], snapshot["journal"]
    columns = st.columns(6)
    columns[0].metric("Market", f"{_market_icon(market['status'])} {market['status']}", f"{market['score']:.0f}/100")
    columns[1].metric("All assets", portfolio["assets_scanned"])
    columns[2].metric("Stocks", portfolio["stocks_scanned"])
    columns[3].metric("ETFs", portfolio["etfs_scanned"])
    columns[4].metric("Candidates", portfolio["candidates"])
    columns[5].metric("Journal plans", journal["total_rows"])


def _render_market(snapshot: dict) -> None:
    market = snapshot["market"]
    st.subheader("Market Intelligence")
    permission = "New long setups permitted" if market["permission"] else "Preserve capital"
    confidence = market.get("confidence", "UNKNOWN")
    st.info(
        f"Market status: **{market['status']}** · Score: **{market['score']:.0f}/100** "
        f"· Confidence: **{confidence}** · {permission}"
    )
    indexes = pd.DataFrame(market["indexes"])
    if not indexes.empty:
        cols = [c for c in ["Symbol", "Close", "EMA20", "EMA50", "EMA200", "Score", "Reasons"] if c in indexes.columns]
        st.dataframe(indexes[cols], use_container_width=True, hide_index=True)



def _render_sectors(snapshot: dict) -> None:
    sectors = snapshot.get("sectors", {})
    st.subheader("Sector Rotation")
    if sectors.get("status") != "READY":
        st.warning(sectors.get("message", "Sector ranking is unavailable."))
        return

    leaders = sectors.get("leaders", [])
    if leaders:
        columns = st.columns(min(3, len(leaders)))
        for column, item in zip(columns, leaders):
            with column:
                st.metric(
                    f"#{item['Rank']} {item['Sector']}",
                    item["Symbol"],
                    f"{item['Sector Score']}/100",
                )
                st.caption(item["Status"])

    rankings = pd.DataFrame(sectors.get("rankings", []))
    if not rankings.empty:
        display_columns = [
            "Rank", "Sector", "Symbol", "Status", "Sector Score",
            "1M Return %", "3M Return %", "1M Relative %",
            "3M Relative %", "Reasons",
        ]
        st.dataframe(
            rankings[[column for column in display_columns if column in rankings.columns]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sector Score": st.column_config.ProgressColumn(
                    "Score", min_value=0, max_value=100, format="%d"
                ),
                "1M Return %": st.column_config.NumberColumn(format="%.2f%%"),
                "3M Return %": st.column_config.NumberColumn(format="%.2f%%"),
                "1M Relative %": st.column_config.NumberColumn(format="%.2f%%"),
                "3M Relative %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )


def _render_industries(snapshot: dict) -> None:
    industries = snapshot.get("industries", {})
    st.subheader("Industry Intelligence")
    if industries.get("status") != "READY":
        st.warning(industries.get("message", "Industry ranking is unavailable."))
        return

    leaders = industries.get("leaders", [])
    if leaders:
        columns = st.columns(min(3, len(leaders)))
        for column, item in zip(columns, leaders):
            with column:
                st.metric(
                    f"#{item['Rank']} {item['Industry']}",
                    item["Symbol"],
                    f"{item['Industry Score']}/100",
                )
                st.caption(item["Status"])

    rankings = pd.DataFrame(industries.get("rankings", []))
    if not rankings.empty:
        display_columns = [
            "Rank", "Industry", "Symbol", "Status", "Industry Score",
            "1M Return %", "3M Return %", "1M Relative %",
            "3M Relative %", "Reasons",
        ]
        st.dataframe(
            rankings[[column for column in display_columns if column in rankings.columns]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Industry Score": st.column_config.ProgressColumn(
                    "Score", min_value=0, max_value=100, format="%d"
                ),
                "1M Return %": st.column_config.NumberColumn(format="%.2f%%"),
                "3M Return %": st.column_config.NumberColumn(format="%.2f%%"),
                "1M Relative %": st.column_config.NumberColumn(format="%.2f%%"),
                "3M Relative %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )


def _opportunity_card(title: str, item: dict | None) -> None:
    st.markdown(f"#### {title}")
    if item is None:
        st.info("No result is available in this category.")
        return
    st.metric("Symbol", item["symbol"])
    st.caption(f"{item.get('category', '')} · {_decision_icon(item['decision'])} {item['decision']}")
    left, right = st.columns(2)
    left.metric("Score", f"{item['score']}/100")
    right.metric("R:R", f"{item['reward_risk']:.2f}R")
    st.write(item.get("headline") or item.get("recommendation") or "Sentinel review available.")


def _render_leaders(snapshot: dict) -> None:
    st.subheader("Best Vehicles Today")
    left, right = st.columns(2)
    with left:
        _opportunity_card("Top ETF", snapshot["top_etf"])
    with right:
        _opportunity_card("Top Stock", snapshot["top_stock"])


def _render_opportunities(results: pd.DataFrame) -> None:
    st.subheader("Ranked Stock & ETF Opportunities")
    a, b, c = st.columns([1, 1, 2])
    with a:
        minimum_score = st.slider("Minimum score", 0, 100, 0, 5)
    with b:
        asset_types = st.multiselect("Asset type", ["STOCK", "ETF"], default=["STOCK", "ETF"])
    with c:
        decisions = st.multiselect("Decision", ["CANDIDATE", "WATCH", "WAIT"], default=["CANDIDATE", "WATCH", "WAIT"])

    filtered = filter_dashboard_results(results, minimum_score, decisions, asset_types)
    compact = dashboard_table(filtered)
    if compact.empty:
        st.warning("No opportunities match the current filters.")
        return

    st.dataframe(
        compact,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
            "Reward Risk": st.column_config.NumberColumn("R:R", format="%.2fR"),
            "Volume Ratio": st.column_config.NumberColumn("Volume", format="%.2fx"),
            "Suggested Entry": st.column_config.NumberColumn(format="$%.2f"),
            "Recommended Stop": st.column_config.NumberColumn(format="$%.2f"),
            "Resistance": st.column_config.NumberColumn(format="$%.2f"),
        },
    )

    selected_label = st.selectbox(
        "Open detailed coach review",
        options=[f"{row['Symbol']} · {row.get('Asset Type', 'ASSET')}" for _, row in filtered.iterrows()],
    )
    symbol = selected_label.split(" · ", 1)[0]
    selected = filtered[filtered["Symbol"].astype(str) == symbol].iloc[0]
    st.markdown(f"### {_decision_icon(selected['Decision'])} {symbol} — {selected.get('Asset Type', 'ASSET')} — {selected['Decision']}")
    st.caption(str(selected.get("Category", "")))
    overview, plan, coach = st.columns(3)
    with overview:
        st.write(f"**Score:** {int(selected['Total Score'])}/100")
        st.write(f"**Confidence:** {selected['Confidence']}")
        st.write(f"**Trend:** {selected['Trend']}")
        st.write(f"**Sector:** {selected.get('Sector Name') or 'N/A'} ({int(selected.get('Sector Score', 50))}/100)")
        st.write(f"**Industry:** {selected.get('Industry Name') or 'N/A'} ({int(selected.get('Industry Score', 50))}/100)")
    with plan:
        st.write(f"**Entry:** ${float(selected['Suggested Entry']):.2f}")
        st.write(f"**Stop:** ${float(selected['Recommended Stop']):.2f}")
        st.write(f"**Resistance:** ${float(selected['Resistance']):.2f}")
        st.write(f"**Reward / risk:** {float(selected['Reward Risk']):.2f}R")
    with coach:
        st.write(f"**Main blocker:** {selected['Coach Primary Blocker']}")
        st.write(f"**Next action:** {selected['Coach Immediate Action']}")
        st.write(f"**Risk note:** {selected['Coach Risk Note']}")
    st.success(str(selected["Coach Recommendation"]))
    st.markdown("#### Why this decision")
    for reason in selected.get("Why This Setup", []) or []:
        st.write(f"✓ {reason}")
    if selected.get("Why Not Higher"):
        st.markdown("#### Why not a higher score")
        for warning in selected.get("Why Not Higher", []) or []:
            st.write(f"⚠ {warning}")
    breakdown = pd.DataFrame(selected.get("Score Breakdown", []) or [])
    if not breakdown.empty:
        st.markdown("#### Transparent score breakdown")
        st.dataframe(breakdown, use_container_width=True, hide_index=True)



def _render_learning(snapshot: dict, journal: pd.DataFrame) -> None:
    st.subheader("Journal & Learning Engine")
    learning = snapshot["learning"]
    if learning["status"] == "NO_DATA":
        st.info("The journal is empty. Run Sentinel on several market days to build history.")
        return
    one, two, three, four = st.columns(4)
    one.metric("Entries reviewed", learning["total_entries"])
    two.metric("Average score", f"{learning['average_score']:.1f}/100")
    three.metric("Average R:R", f"{learning['average_reward_risk']:.2f}R")
    four.metric("Risk pass rate", f"{learning['risk_pass_rate']:.1f}%")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Emerging patterns")
        st.write(f"**Most frequent symbol:** {learning['most_frequent_symbol']}")
        st.write(f"**Highest average score:** {learning['highest_average_score_symbol']} ({learning['highest_average_score']:.1f})")
        st.write(f"**Highest average R:R:** {learning['highest_average_rr_symbol']} ({learning['highest_average_rr']:.2f}R)")
        st.write(f"**Most common trend:** {learning['most_common_trend']}")
    with right:
        st.markdown("#### Learning recommendations")
        for item in learning["recommendations"]:
            st.write(f"• {item}")
    if not journal.empty:
        st.markdown("#### Planned-opportunity history")
        st.dataframe(journal.sort_values("Scan Timestamp UTC", ascending=False), use_container_width=True, hide_index=True)


def main() -> None:
    st.title("🛡️ Project Sentinel")
    st.caption("US stocks + ETFs · Market, sector and industry intelligence · Coach · Journal · Learning")
    with st.sidebar:
        st.header("Control Centre")
        if st.button("Run New Scan", type="primary", use_container_width=True):
            _run_scan()
        st.write("The expanded universe includes stocks, broad-market ETFs, sector ETFs and industry ETFs.")
        st.divider()
        st.caption("Decision support only. No automatic trade execution.")

    if "sentinel_results" not in st.session_state:
        st.info("Select **Run New Scan** to build today's stock and ETF dashboard.")
        journal = read_journal()
        if not journal.empty:
            learning = generate_learning_report()["analysis"]
            a, b, c = st.columns(3)
            a.metric("Plans recorded", len(journal))
            b.metric("Average score", f"{learning['average_score']:.1f}/100")
            c.metric("Average R:R", f"{learning['average_reward_risk']:.2f}R")
        return

    market = st.session_state["sentinel_market"]
    results = st.session_state["sentinel_results"]
    journal = read_journal()
    sectors = st.session_state.get("sentinel_sectors", {})
    industries = st.session_state.get("sentinel_industries", {})
    snapshot = build_dashboard_snapshot(market, results, journal, sectors, industries)
    last_scan = st.session_state.get("sentinel_last_scan")
    if last_scan:
        st.caption(f"Last refreshed: {last_scan.strftime('%Y-%m-%d %H:%M:%S')}")

    _render_overview(snapshot)
    overview_tab, opportunities_tab, learning_tab = st.tabs(["Overview", "Stocks & ETFs", "Journal & Learning"])
    with overview_tab:
        _render_market(snapshot)
        st.divider()
        _render_sectors(snapshot)
        st.divider()
        _render_industries(snapshot)
        st.divider()
        _render_leaders(snapshot)
    with opportunities_tab:
        _render_opportunities(results)
    with learning_tab:
        _render_learning(snapshot, journal)


if __name__ == "__main__":
    main()
