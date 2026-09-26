import streamlit as st

from app import analyze_bug_description, get_driver, import_demo_data


st.title("Smashing Bugs")

if "driver" not in st.session_state:
    st.session_state.driver = get_driver()
    import_demo_data(st.session_state.driver)

bug_description = st.text_area(
    "Describe the bug",
    placeholder="Example: users are getting logged out whenever the database connection times out.",
    height=180,
)

if st.button("Analyze bug"):
    if not bug_description.strip():
        st.warning("Please enter a bug description first.")
    else:
        try:
            result = analyze_bug_description(st.session_state.driver, bug_description)
            st.write(result)
        except Exception as exc:
            st.error(f"Bug analysis failed: {exc}")

