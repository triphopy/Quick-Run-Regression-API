from __future__ import annotations

import streamlit as st

DEFAULT_STATE = {
    "apis": [],
    "selected_ids": set(),
    "selected_group": "All",
    "results": [],
    "last_run_complete": False,
    "active_tab": "Run Test",
    "log_filter": "All",
    "log_group_filter": "All Groups",
    "current_run_id": "",
    "current_output_dir": "",
    "last_input_filename": "",
    "last_run_mode": "",
    "last_run_error": "",
    "environment_name": "UAT",
    "base_url": "",
    "selection_version": 0,
    "last_uploaded_token": "",
    "api_search": "",
    "log_search": "",
    "last_run_notice": "",
    "log_sort_by": "Duration (High to Low)",
    "log_slow_only": False,
    "auth_type": "None",
    "auth_value": "",
    "auth_header_name": "Authorization",
    "request_timeout_seconds": 30.0,
    "cleanup_keep_latest": 20,
    "cleanup_notice": "",
    "cleanup_confirm_open": False,
    "cleanup_pending_count": 0,
    "cleanup_pending_paths": [],
    "cleanup_target_label": "runs",
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_loaded_data(*, filename: str = "") -> None:
    st.session_state.selected_ids = set()
    st.session_state.results = []
    st.session_state.last_run_complete = False
    st.session_state.current_run_id = ""
    st.session_state.current_output_dir = ""
    st.session_state.last_input_filename = filename
    st.session_state.last_run_mode = ""
    st.session_state.last_run_error = ""
    st.session_state.last_run_notice = ""
    st.session_state.api_search = ""
    st.session_state.log_group_filter = "All Groups"
    st.session_state.cleanup_notice = ""
    st.session_state.cleanup_confirm_open = False
    st.session_state.cleanup_pending_count = 0
    st.session_state.cleanup_pending_paths = []
    st.session_state.cleanup_target_label = "runs"
    st.session_state.selection_version += 1
