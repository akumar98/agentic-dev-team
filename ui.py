import sys

import streamlit as st

from agent.main import build_crew_result


def render_app() -> None:
    st.set_page_config(
        page_title="Investor App Planner",
        page_icon="🧠",
        layout="wide",
    )
    st.title("Product Idea to PRD and Engineering Plan")
    st.write(
        "Enter an idea, then generate PRD, architecture, implementation tasks, and test strategy."
    )

    idea = st.text_area(
        "Product Idea",
        value=(
            "Build an investor CRM with login, investor profiles, notes, tasks, "
            "dashboard metrics, and search/filtering."
        ),
        height=160,
    )

    if st.button("Generate Plan", type="primary"):
        if not idea.strip():
            st.warning("Please enter an idea first.")
            return

        with st.spinner("Running multi-agent workflow..."):
            result = build_crew_result(idea)

        st.subheader("Generated Output")
        st.markdown(result)


def main() -> int:
    # Lets console script "agent-ui" launch Streamlit correctly.
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__]
    return stcli.main()


if __name__ == "__main__":
    render_app()