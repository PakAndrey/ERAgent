import streamlit as st
import pandas as pd

import pandasai as pai
from pandasai_litellm.litellm import LiteLLM
import os
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

import streamlit as st
import pandas as pd
from fredapi import Fred
import altair as alt

# --- Configuration ---
fred = Fred(api_key=st.secrets["FRED_API_KEY"])


# Store selected series in session state
if "selected_series" not in st.session_state:
    st.session_state.selected_series = {}

# Sidebar UI
with st.sidebar:
    st.header("🔍 Search & Add Series")

    # Search bar
    search_query = st.text_input("Search FRED:")

    # Search results
    if search_query:
        results = fred.search(search_query)
        if not results.empty:
            st.markdown("**Top Results:**")
            for idx, row in results.head(5).iterrows():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.caption(row["title"])
                with col2:
                    if st.button("➕", key=f"add_{idx}"):
                        if len(st.session_state.selected_series) < 5:
                            st.session_state.selected_series[idx] = row['title']
                            st.rerun()

    # Selected Series
    if st.session_state.selected_series:
        st.markdown("---")
        st.subheader("🗂️ Selected")
        for sid, title in st.session_state.selected_series.items():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.caption(title)
            with col2:
                if st.button("❌", key=f"remove_{sid}"):
                    del st.session_state.selected_series[sid]
                    st.rerun()

    # Optional: display a count or summary in the main area
    st.markdown(f"**Series selected: {len(st.session_state.selected_series)} / 5**")

    # Combine time series
    if st.session_state.selected_series:
        df_all = None
        for sid in st.session_state.selected_series:
            df = fred.get_series(sid).to_frame(name=sid)
            df.index.name = "DATE"
            df.index = pd.to_datetime(df.index)

            if df_all is None:
                df_all = df
            else:
                df_all = pd.concat([df_all, df], axis=1)

        df_all.dropna(how='all', inplace=True)
        df_all.interpolate(method='time', inplace=True)
        df_all.sort_index(inplace=True)

        # Show selection box to choose which series to display
        default_series = list(st.session_state.selected_series)[-1:]  # Latest added as default
        options = list(st.session_state.selected_series.values())
        series_keys = list(st.session_state.selected_series.keys())

        label_map = {v: k for k, v in st.session_state.selected_series.items()}  # Reverse lookup

        selected_labels = st.multiselect(
            "Choose series to display:",
            options=options,
            default=[options[-1]] if options else []
        )

        selected_sids = [label_map[label] for label in selected_labels]

        if selected_sids:
            df_display = df_all[selected_sids]
            # st.dataframe(df_display)
            st.line_chart(df_display, use_container_width=True)
        else:
            st.info("Select at least one series to display.")

        # Save full combined data (not just filtered)
        df_all.to_csv('combined_fred_data.csv', index=True)

# # --- Session State ---
# if "selected_series" not in st.session_state:
#     st.session_state.selected_series = {}

# if "series_limit" not in st.session_state:
#     st.session_state.series_limit = 5

# # --- Display Current Selections ---
# st.subheader("🧺 Selected Time Series")
# if st.session_state.selected_series:
#     for sid, data in st.session_state.selected_series.items():
#         st.markdown(f"• **{data['title']}** ({sid})")
# else:
#     st.info("No time series selected yet.")

# if len(st.session_state.selected_series) >= st.session_state.series_limit:
#     st.warning(f"You've reached the limit of {st.session_state.series_limit} time series.")
#     st.stop()

# # --- Search Interface ---
# st.subheader("🔍 Search FRED")
# search_term = st.text_input("Enter a search term to find a time series")

# if search_term:
#     results = fred.search(search_term)
#     results = results[['title']].drop_duplicates()
#     results = results[~results.index.isin(st.session_state.selected_series.keys())]

#     if not results.empty:
#         series_id = st.selectbox("Select a time series to add", results.index,
#                                  format_func=lambda x: results.loc[x, "title"])
#         if st.button("➕ Add Series"):
#             if series_id not in st.session_state.selected_series:
#                 st.session_state.selected_series[series_id] = {
#                     "title": results.loc[series_id, "title"],
#                     "data": fred.get_series(series_id)
#                 }
#                 st.rerun()
#     else:
#         st.info("No new time series found or all found series are already added.")

# # --- Show Combined Data ---
# if st.session_state.selected_series:
#     combined_df = pd.DataFrame()
#     for sid, item in st.session_state.selected_series.items():
#         series = item["data"].rename(item["title"])
#         combined_df = pd.concat([combined_df, series], axis=1)

#     combined_df.index.name = "Date"
#     df = combined_df.dropna(how="all")

#     st.subheader("📊 Combined Data")
#     st.line_chart(df)
#     st.dataframe(df.tail(10))

#     # Download
#     csv = df.to_csv().encode('utf-8')
#     st.download_button("Download CSV", data=csv, file_name="fred_combined.csv", mime="text/csv")


# st.title("🔍 Search & Visualize FRED Time Series")

# # --- Search ---
# search_query = st.text_input("Enter search term (e.g., 'inflation', 'GDP', 'unemployment'):")

# if search_query:
#     st.write(f"Searching FRED for: **{search_query}**...")
#     try:
#         search_results = fred.search(search_query)
#         if not search_results.empty:
#             search_results = search_results[['title']]  # show only title
#             selected_series = st.selectbox("Select a time series:", search_results.index, format_func=lambda x: search_results.loc[x, "title"])
            
#             # --- Retrieve and plot selected data ---
#             data = fred.get_series(selected_series)
#             df = pd.DataFrame(data, columns=["Value"])
#             df.index.name = "Date"

#             st.line_chart(df)
#             st.dataframe(df.tail(10))  # show last few rows
#         else:
#             st.warning("No matching series found.")
#     except Exception as e:
#         st.error(f"Error: {e}")




# For OpenAI models
llm = LiteLLM(model="gemini/gemini-2.5-flash-lite")

pai.config.set({
    "llm": llm
})

if os.path.exists('combined_fred_data.csv'):
    df = pai.read_csv('combined_fred_data.csv')

# Streamlit UI
st.title("Economic Research Assistant")

with st.form(key="prompt_form"):
    prompt = st.text_input("Enter your prompt:")
    submitted = st.form_submit_button("Submit")
def handle_response(response):
    # If it's an object with .type and .value attributes
    if hasattr(response, "type") and hasattr(response, "value"):
        rtype = getattr(response, "type")
        rval = getattr(response, "value")

        match rtype:
            case "dataframe":
                st.dataframe(rval)
            case "string":
                st.write(rval)
            case "number":
                st.metric("Result", rval)
            case "chart":
                if rval:
                    st.image(rval)
                else:
                    st.warning("Chart could not be displayed.")
            case "error":
                st.error(rval)
            case _:
                st.warning(f"Unsupported response type: {rtype}")
        with st.expander("Show executed code"):
            st.code(response.last_code_executed, language='python')
    else:
        st.warning("Unrecognized response format.")

# Process on submit
if submitted and prompt and df is not None:
    try:
        # df = pai.SmartDataframe(df_all)
        response = df.chat(prompt)
        handle_response(response)
    
    except Exception as e:
        st.error(f"Exception: {e}")