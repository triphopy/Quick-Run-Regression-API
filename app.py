import time
import shutil
from pathlib import Path

import streamlit as st

from src.config import DEFAULT_ENVIRONMENT, output_dir, output_root_dir, project_root, temp_dir
from src.dashboard import build_group_summary, build_run_summary, worst_group_summary
from src.exporter import export_results_csv, export_results_xlsx
from src.models import RunResult
from src.parser import REQUIRED_COLUMNS, parse_csv_file, parse_csv_text
from src.runner import create_run_id, execute_mock_run, execute_run
from src.selector import filter_test_cases, get_groups, select_all_ids
from src.state import init_state, reset_loaded_data
from src.ui import inject_css, metric_card


st.set_page_config(
    page_title="SONIC Regression Dashboard",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed",
)


MOCK_CSV = """group,api_name,method,endpoint,expected_status
Authentication,Login,POST,/auth/login,200
Authentication,Logout,POST,/auth/logout,200
Authentication,Refresh Token,POST,/auth/refresh,200
Order,Get Order List,GET,/order/list,200
Order,Create Order,POST,/order/create,201
Order,Update Order,PUT,/order/update,200
Order,Cancel Order,DELETE,/order/cancel,200
Payment,Process Payment,POST,/payment/process,200
Payment,Payment Status,GET,/payment/status,200
Payment,Refund,POST,/payment/refund,200
Customer,Get Profile,GET,/customer/profile,200
Customer,Update Profile,PUT,/customer/update,200
Customer,Order History,GET,/customer/history,200
Customer,Delete Account,DELETE,/customer/delete,200
Inventory,List Items,GET,/inventory/list,200
Inventory,Add Item,POST,/inventory/add,201
Inventory,Update Item,PUT,/inventory/update,200
Report,Daily Report,GET,/report/daily,200
Report,Monthly Report,GET,/report/monthly,200
Report,Export Report,POST,/report/export,200
"""

METHOD_COLORS = {
    "GET": "#1ea672",
    "POST": "#2f7cf6",
    "PUT": "#d89c1d",
    "DELETE": "#e04f5f",
}
ENVIRONMENT_OPTIONS = ["DEV", "UAT", "PROD", "CUSTOM"]
AUTH_TYPE_OPTIONS = ["None", "Bearer", "API Key"]
SAMPLE_FILES = {
    "Public API Smoke": project_root() / "assets" / "public_api_smoke.csv",
    "Public API Extended": project_root() / "assets" / "public_api_extended.csv",
    "Team Realistic": project_root() / "assets" / "team_api_realistic.csv",
    "Failure Examples": project_root() / "assets" / "team_api_failure_examples.csv",
    "Demo Mix": project_root() / "assets" / "team_api_demo_mix.csv",
}
TEMPLATE_FILES = {
    "Basic Template": project_root() / "assets" / "basic_template.csv",
    "Advanced Template": project_root() / "assets" / "advanced_template.csv",
}


def current_results(preview_count: int | None = None) -> list[RunResult]:
    if st.session_state.results:
        results = st.session_state.results
    else:
        results = []
    return results[:preview_count] if preview_count is not None else results


def sync_checkbox_state_from_selection() -> None:
    version = st.session_state.selection_version
    for api in st.session_state.apis:
        st.session_state[f"api_{version}_{api.id}"] = api.id in st.session_state.selected_ids


def sync_selection_from_checkbox_state(apis) -> None:
    version = st.session_state.selection_version
    visible_ids = {api.id for api in apis}
    st.session_state.selected_ids -= visible_ids
    for api in apis:
        if st.session_state.get(f"api_{version}_{api.id}", False):
            st.session_state.selected_ids.add(api.id)


def get_selected_count_for_view(apis) -> int:
    version = st.session_state.selection_version
    visible_ids = {api.id for api in apis}
    selected_ids = set(st.session_state.selected_ids) - visible_ids
    for api in apis:
        if st.session_state.get(f"api_{version}_{api.id}", api.id in st.session_state.selected_ids):
            selected_ids.add(api.id)
    return len(selected_ids)


def toggle_api_selection(api_id: int) -> None:
    if api_id in st.session_state.selected_ids:
        st.session_state.selected_ids.discard(api_id)
    else:
        st.session_state.selected_ids.add(api_id)

    version = st.session_state.selection_version
    st.session_state[f"api_{version}_{api_id}"] = api_id in st.session_state.selected_ids


def load_uploaded_file(uploaded_file) -> None:
    st.session_state.apis = parse_csv_file(uploaded_file.read(), uploaded_file.name)
    reset_loaded_data(filename=uploaded_file.name)
    st.session_state.last_uploaded_token = f"{uploaded_file.name}:{uploaded_file.size}"
    sync_checkbox_state_from_selection()


def load_sample_csv(sample_name: str) -> None:
    sample_path = SAMPLE_FILES[sample_name]
    st.session_state.apis = parse_csv_file(sample_path.read_bytes(), sample_path.name)
    reset_loaded_data(filename=sample_path.name)
    st.session_state.last_uploaded_token = ""
    sync_checkbox_state_from_selection()


def run_selected_apis() -> None:
    selected = [api for api in st.session_state.apis if api.id in st.session_state.selected_ids]
    if not selected:
        return

    run_id = create_run_id()
    progress_box = st.container()
    progress_text = progress_box.empty()
    progress_bar = progress_box.progress(0)

    for index, api in enumerate(selected, start=1):
        pct = int(index / len(selected) * 100)
        progress_text.markdown(
            f"**Executing SONIC Regression**  \nRunning: `{api.method} {api.endpoint}`"
        )
        progress_bar.progress(pct)
        time.sleep(0.08)

    artifacts = execute_run(
        run_id,
        selected,
        environment_base_url=st.session_state.base_url.strip(),
        default_auth_type="" if st.session_state.auth_type == "None" else st.session_state.auth_type,
        default_auth_value=st.session_state.auth_value,
        default_auth_header_name=st.session_state.auth_header_name,
        default_timeout_seconds=float(st.session_state.request_timeout_seconds),
        allow_mock_fallback=True,
    )
    st.session_state.results = artifacts.results
    st.session_state.last_run_complete = True
    st.session_state.active_tab = "Dashboard"
    st.session_state.current_run_id = run_id
    st.session_state.current_output_dir = str(artifacts.output_dir)
    st.session_state.last_run_mode = artifacts.mode
    st.session_state.last_run_error = artifacts.error
    st.session_state.last_run_notice = (
        f"Run completed: {len(selected)} APIs on "
        f"{st.session_state.environment_name or DEFAULT_ENVIRONMENT}"
    )
    progress_text.empty()
    progress_bar.empty()


def render_header() -> None:
    st.markdown('<div class="header-wrap">', unsafe_allow_html=True)
    left, right = st.columns([3, 1])
    with left:
        st.markdown('<div class="brand">SONIC</div>', unsafe_allow_html=True)
    with right:
        if st.session_state.last_run_complete:
            st.markdown(
                '<div class="run-status">LAST RUN COMPLETE</div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")


def open_group_log(group_name: str) -> None:
    st.session_state.active_tab = "Log"
    st.session_state.log_group_filter = group_name
    st.session_state.log_filter = "All"
    st.session_state.log_search = ""
    st.rerun()


def cleanup_old_runs(keep_latest: int) -> int:
    run_dirs = [path for path in output_root_dir().iterdir() if path.is_dir() and path.name.startswith("run_")]
    run_dirs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    to_delete = run_dirs[max(keep_latest, 0):]
    deleted = 0
    current_run_dir = output_dir(st.session_state.current_run_id) if st.session_state.current_run_id else None
    for run_dir in to_delete:
        if current_run_dir is not None and run_dir == current_run_dir:
            continue
        shutil.rmtree(run_dir, ignore_errors=True)
        deleted += 1
    return deleted


def cleanup_temp_files() -> int:
    temp_files = [path for path in temp_dir().iterdir() if path.is_file()]
    deleted = 0
    current_payload = Path(st.session_state.current_output_dir).parent / "temp-placeholder"
    current_run_id = st.session_state.current_run_id
    for temp_file in temp_files:
        if current_run_id and temp_file.name.startswith(f"{current_run_id}_"):
            continue
        temp_file.unlink(missing_ok=True)
        deleted += 1
    return deleted


@st.dialog("Confirm Cleanup")
def render_cleanup_confirm_dialog(removable_count: int) -> None:
    st.write(
        f"This will delete {removable_count} {st.session_state.cleanup_target_label}."
    )
    if st.session_state.cleanup_target_label == "older run folder(s)":
        st.caption(
            f"Keep latest runs: {int(st.session_state.cleanup_keep_latest)} | Base folder: {output_root_dir()}"
        )
    else:
        st.caption(f"Base folder: {temp_dir()}")
    if st.session_state.cleanup_pending_paths:
        st.caption("Items to delete:")
        for path in st.session_state.cleanup_pending_paths:
            st.write(f"- {path}")
    if st.session_state.cleanup_target_label == "older run folder(s)":
        st.caption("This action removes saved run artifacts from data/output.")
    else:
        st.caption("This action removes generated payload files from data/temp.")
    confirm_col, cancel_col = st.columns(2)
    if confirm_col.button("Confirm Cleanup", type="primary", use_container_width=True):
        if st.session_state.cleanup_target_label == "older run folder(s)":
            deleted_count = cleanup_old_runs(int(st.session_state.cleanup_keep_latest))
            st.session_state.cleanup_notice = f"Deleted {deleted_count} old run folder(s)."
        else:
            deleted_count = cleanup_temp_files()
            st.session_state.cleanup_notice = f"Deleted {deleted_count} temp file(s)."
        st.session_state.cleanup_confirm_open = False
        st.session_state.cleanup_pending_count = 0
        st.session_state.cleanup_pending_paths = []
        st.session_state.cleanup_target_label = "runs"
        st.rerun()
    if cancel_col.button("Cancel", use_container_width=True):
        st.session_state.cleanup_confirm_open = False
        st.session_state.cleanup_pending_count = 0
        st.session_state.cleanup_pending_paths = []
        st.session_state.cleanup_target_label = "runs"
        st.rerun()


def render_tabs() -> None:
    tabs = ["Run Test", "Dashboard", "Log"]
    cols = st.columns(len(tabs))
    for idx, tab in enumerate(tabs):
        kind = "primary" if st.session_state.active_tab == tab else "secondary"
        if cols[idx].button(tab, use_container_width=True, type=kind):
            st.session_state.active_tab = tab
            st.rerun()


def render_run_page() -> None:
    if st.session_state.last_run_notice:
        st.success(st.session_state.last_run_notice)

    st.subheader("Upload API List")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            upload_token = f"{uploaded_file.name}:{uploaded_file.size}"
            if st.session_state.last_uploaded_token != upload_token:
                load_uploaded_file(uploaded_file)
                st.success(f"Loaded {uploaded_file.name}")
        except Exception as exc:
            st.error(str(exc))
    st.caption("Required CSV columns: group, api_name, method, endpoint, expected_status")
    with st.expander("Samples And Templates", expanded=False):
        st.caption("Load sample data")
        sample_select_col, sample_action_col = st.columns([2.2, 1])
        sample_names = list(SAMPLE_FILES.keys())
        selected_sample = sample_select_col.selectbox(
            "Sample file",
            sample_names,
            index=0,
            key="sample_file_select",
            label_visibility="collapsed",
        )
        if sample_action_col.button("Load Sample", use_container_width=True):
            load_sample_csv(selected_sample)
            st.success(f"Loaded {Path(SAMPLE_FILES[selected_sample]).name}")

        st.caption("Download templates")
        template_cols = st.columns(len(TEMPLATE_FILES))
        for idx, template_name in enumerate(TEMPLATE_FILES):
            template_path = TEMPLATE_FILES[template_name]
            template_cols[idx].download_button(
                template_name,
                data=template_path.read_bytes(),
                file_name=template_path.name,
                mime="text/csv",
                use_container_width=True,
                key=f"download_template_{idx}",
            )

    env_col, url_col = st.columns([0.9, 2.1])
    with env_col:
        env_index = (
            ENVIRONMENT_OPTIONS.index(st.session_state.environment_name)
            if st.session_state.environment_name in ENVIRONMENT_OPTIONS
            else len(ENVIRONMENT_OPTIONS) - 1
        )
        st.session_state.environment_name = st.selectbox(
            "Environment",
            ENVIRONMENT_OPTIONS,
            index=env_index,
        )
    with url_col:
        st.session_state.base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url,
            placeholder="https://uat-api.example.com",
            help="Used by the real runner when CSV endpoints are relative paths like /auth/login",
        ).strip()

    auth_col, auth_value_col, auth_extra_col = st.columns([0.9, 1.5, 0.9])
    with auth_col:
        auth_index = (
            AUTH_TYPE_OPTIONS.index(st.session_state.auth_type)
            if st.session_state.auth_type in AUTH_TYPE_OPTIONS
            else 0
        )
        st.session_state.auth_type = st.selectbox(
            "Auth Type",
            AUTH_TYPE_OPTIONS,
            index=auth_index,
        )
    with auth_value_col:
        st.session_state.auth_value = st.text_input(
            "Auth Value",
            value=st.session_state.auth_value,
            type="password",
            placeholder="Token or API key",
            help="Global default auth used by the real runner. CSV row values can override this. Use placeholders like {{TOKEN}} or {{API_KEY}} in CSV fields when needed.",
        )
    with auth_extra_col:
        if st.session_state.auth_type == "API Key":
            st.session_state.auth_header_name = st.text_input(
                "Header Name",
                value=st.session_state.auth_header_name,
                placeholder="X-API-Key",
            ).strip() or "Authorization"
        else:
            st.session_state.request_timeout_seconds = float(
                st.select_slider(
                "Timeout (s)",
                options=list(range(1, 121)),
                value=int(float(st.session_state.request_timeout_seconds)),
            )
            )

    if st.session_state.auth_type == "API Key":
        timeout_col = st.columns([1])[0]
        with timeout_col:
            st.session_state.request_timeout_seconds = float(
                st.select_slider(
                "Timeout (s)",
                options=list(range(1, 121)),
                value=int(float(st.session_state.request_timeout_seconds)),
                key="timeout_secondary",
            )
            )

    st.caption(
        "Columns: group, api_name, method, endpoint, expected_status"
        " | optional: request_body, headers, auth_type, auth_value, auth_header_name, timeout_seconds, response_json_path, expected_value, match_type, expected_contains"
    )
    st.caption(
        "Placeholders supported in CSV: {{TOKEN}}, {{API_KEY}}, {{AUTH_VALUE}}, {{AUTH_HEADER_NAME}}, {{BASE_URL}}"
    )
    if st.session_state.apis:
        st.caption(
            f"{len(st.session_state.apis)} APIs loaded from {st.session_state.last_input_filename or 'current file'}"
        )

    st.subheader("Select APIs To Run")

    if not st.session_state.apis:
        st.info("Upload a CSV file or use mock data to continue.")
        return

    groups = get_groups(st.session_state.apis)
    selected_group = st.selectbox(
        "Group",
        groups,
        index=groups.index(st.session_state.selected_group)
        if st.session_state.selected_group in groups
        else 0,
    )
    st.session_state.selected_group = selected_group

    st.session_state.api_search = st.text_input(
        "Search API",
        value=st.session_state.api_search,
        placeholder="Search by API name or endpoint",
    ).strip()

    apis = filter_test_cases(st.session_state.apis, st.session_state.selected_group)
    if st.session_state.api_search:
        query = st.session_state.api_search.lower()
        apis = [
            api
            for api in apis
            if query in api.api_name.lower() or query in api.endpoint.lower()
        ]
    all_ids = select_all_ids(apis)
    all_selected = bool(all_ids) and all_ids.issubset(st.session_state.selected_ids)
    count = get_selected_count_for_view(apis)

    summary_col, run_col = st.columns([3, 1])
    with summary_col:
        summary_text = f"{len(apis)} APIs in view - {count} selected"
        if count:
            summary_text += f" - est. {count * 3}-{count * 5}s"
        st.caption(summary_text)
    with run_col:
        if st.button(
            f"Run {count} APIs",
            key="run_top",
            disabled=count == 0,
            use_container_width=True,
            type="primary",
        ):
            run_selected_apis()
            st.rerun()

    st.caption("Tip: use the header checkbox to select all visible rows in the current filter.")

    if not apis:
        st.markdown(
            """
            <div class="empty-state">
              <div class="empty-title">No APIs match this filter</div>
              <div class="empty-copy">Try clearing the search text or switching the group filter to bring rows back into view.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    header_key = (
        f"select_visible_{st.session_state.selection_version}_"
        f"{st.session_state.selected_group}_{st.session_state.api_search}"
    )
    header = st.columns([0.08, 0.14, 0.36, 0.24, 0.18])
    header_checked = header[0].checkbox(
        "",
        value=all_selected,
        key=header_key,
        label_visibility="collapsed",
    )
    header[1].markdown("**METHOD**")
    header[2].markdown("**ENDPOINT**")
    header[3].markdown("**API NAME**")
    header[4].markdown("**GROUP**")

    if header_checked != all_selected:
        if header_checked:
            st.session_state.selected_ids |= all_ids
        else:
            st.session_state.selected_ids -= all_ids
        st.session_state.selection_version += 1
        sync_checkbox_state_from_selection()
        st.rerun()

    version = st.session_state.selection_version
    for api in apis:
        row = st.columns([0.08, 0.14, 0.36, 0.24, 0.18])
        row[0].checkbox(
            "",
            key=f"api_{version}_{api.id}",
            label_visibility="collapsed",
        )

        color = METHOD_COLORS.get(api.method, "#61738a")
        row[1].markdown(
            f'<span class="method-pill" style="color:{color};background:{color}22;">{api.method}</span>',
            unsafe_allow_html=True,
        )
        row[2].markdown(f"`{api.endpoint}`")
        row[3].write(api.api_name)
        row[4].write(api.group)

    sync_selection_from_checkbox_state(apis)

    st.write("")
    bottom_left, bottom_right = st.columns([1, 1.6])
    with bottom_left:
        if st.button(
            f"Run {count} APIs",
            key="run_bottom",
            disabled=count == 0,
            use_container_width=True,
            type="primary",
        ):
            run_selected_apis()
            st.rerun()
    with bottom_right:
        if count:
            st.caption(f"Estimated duration: {count * 3}-{count * 5} seconds")
        if not st.session_state.base_url:
            st.caption("Tip: set Base URL before using the real Robot runner.")
    if st.session_state.last_run_error:
        st.warning(st.session_state.last_run_error)


def render_dashboard_panel(preview: bool = False) -> None:
    results = current_results()
    st.caption("DASHBOARD")
    st.subheader("Regression Summary")

    if not results:
        st.info("No run data yet.")
        return

    summary = build_run_summary(
        results,
        run_id=st.session_state.current_run_id or "preview",
        environment=st.session_state.environment_name or DEFAULT_ENVIRONMENT,
    )
    group_summaries = build_group_summary(results)
    worst_group = worst_group_summary(group_summaries)
    started = summary.started_at.strftime("%Y-%m-%d %H:%M:%S") if summary.started_at else "-"
    finished = summary.finished_at.strftime("%Y-%m-%d %H:%M:%S") if summary.finished_at else "-"
    worst_group_label = (
        f"{worst_group.group} ({worst_group.pass_rate:.0f}%)" if worst_group else "-"
    )

    st.markdown(
        f"""
        <div class="meta-bar">
          <div class="meta-item">
            <div class="meta-label">Started</div>
            <div class="meta-value">{started}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Finished</div>
            <div class="meta-value">{finished}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Groups Covered</div>
            <div class="meta-value">{len(group_summaries)}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Worst Group</div>
            <div class="meta-value">{worst_group_label}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Run ID: {st.session_state.current_run_id or 'preview'} - env: {st.session_state.environment_name or DEFAULT_ENVIRONMENT} - mode: {st.session_state.last_run_mode or 'preview'} - source: {st.session_state.last_input_filename or 'No file loaded'}"
    )

    col1, col2 = st.columns(2)
    with col1:
        metric_card("Total APIs", str(summary.total), "Uploaded in current test set", "linear-gradient(135deg,#2f7cf6,#5ba7ff)")
    with col2:
        metric_card("Passed", str(summary.passed), f"{round(summary.pass_rate)}% pass rate", "linear-gradient(135deg,#1ea672,#49c38f)")

    col3, col4 = st.columns(2)
    with col3:
        metric_card("Failed", str(summary.failed), "Needs investigation", "linear-gradient(135deg,#db4a5a,#f36b72)")
    with col4:
        metric_card("Avg Duration", f"{summary.avg_duration_seconds:.2f}s", "Across selected APIs", "linear-gradient(135deg,#d89c1d,#f0be52)")

    st.markdown('<div class="section-tight"><strong>Results by Group</strong></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-help">Click a result count to open its filtered log view.</div>',
        unsafe_allow_html=True,
    )
    for group_summary in group_summaries:
        pct = group_summary.passed / group_summary.total if group_summary.total else 0
        label_col, bar_wrap_col, count_col = st.columns([1.4, 2.15, 0.35])
        label_col.write(group_summary.group)
        inner_bar_col, _ = bar_wrap_col.columns([0.82, 0.18])
        inner_bar_col.progress(pct)
        if count_col.button(
            f"{group_summary.passed}/{group_summary.total}",
            key=f"group_log_{group_summary.group}",
            type="tertiary",
            use_container_width=True,
        ):
            open_group_log(group_summary.group)

    if preview and not st.session_state.results:
        st.caption("Preview uses the current uploaded list until a run is executed.")


def render_log_panel(preview: bool = False) -> None:
    results = current_results()
    st.caption("LOG")
    st.subheader("Latest Execution")

    if not results:
        st.info("No log data yet.")
        return

    filters = ["All", "Passed", "Failed"]
    current_filter = st.segmented_control(
        "Log Filter",
        filters,
        selection_mode="single",
        default=st.session_state.log_filter if st.session_state.log_filter in filters else "All",
        key="log_segment",
        label_visibility="collapsed",
    )
    st.session_state.log_filter = current_filter

    st.session_state.log_search = st.text_input(
        "Search Log",
        value=st.session_state.log_search,
        placeholder="Search by endpoint, API name, group, status, or error",
        key="log_search_input",
    ).strip()

    group_options = ["All Groups"] + sorted({item.group for item in results})
    filter_group_col, sort_col, slow_col = st.columns([1.4, 1.8, 0.8])
    with filter_group_col:
        group_index = (
            group_options.index(st.session_state.log_group_filter)
            if st.session_state.log_group_filter in group_options
            else 0
        )
        st.session_state.log_group_filter = st.selectbox(
            "Group",
            group_options,
            index=group_index,
            key="log_group_filter_select",
        )
    with sort_col:
        sort_options = [
            "Duration (High to Low)",
            "Duration (Low to High)",
            "Status",
            "API Name",
        ]
        sort_index = (
            sort_options.index(st.session_state.log_sort_by)
            if st.session_state.log_sort_by in sort_options
            else 0
        )
        st.session_state.log_sort_by = st.selectbox(
            "Sort By",
            sort_options,
            index=sort_index,
            key="log_sort_by_select",
        )
    with slow_col:
        st.write("")
        st.session_state.log_slow_only = st.checkbox(
            "Slow only",
            value=st.session_state.log_slow_only,
            key="log_slow_only_toggle",
            help="Show only APIs with duration above 3 seconds",
        )

    view = results
    if current_filter == "Passed":
        view = [item for item in results if item.result == "PASSED"]
    elif current_filter == "Failed":
        view = [item for item in results if item.result == "FAILED"]

    if st.session_state.log_group_filter != "All Groups":
        view = [item for item in view if item.group == st.session_state.log_group_filter]

    if st.session_state.log_slow_only:
        view = [item for item in view if item.duration_seconds > 3]

    if st.session_state.log_search:
        query = st.session_state.log_search.lower()
        view = [
            item
            for item in view
            if query in item.endpoint.lower()
            or query in item.api_name.lower()
            or query in item.group.lower()
            or query in item.result.lower()
            or query in item.error_message.lower()
            or query in str(item.actual_status).lower()
        ]

    if st.session_state.log_sort_by == "Duration (High to Low)":
        view = sorted(view, key=lambda item: item.duration_seconds, reverse=True)
    elif st.session_state.log_sort_by == "Duration (Low to High)":
        view = sorted(view, key=lambda item: item.duration_seconds)
    elif st.session_state.log_sort_by == "Status":
        status_order = {"FAILED": 0, "ERROR": 1, "PASSED": 2, "SKIPPED": 3}
        view = sorted(
            view,
            key=lambda item: (
                status_order.get(item.result, 9),
                item.duration_seconds * -1,
                item.api_name.lower(),
            ),
        )
    elif st.session_state.log_sort_by == "API Name":
        view = sorted(view, key=lambda item: item.api_name.lower())

    st.caption(f"{len(view)} log entries")

    display_items = view[:8] if preview and not st.session_state.results else view

    for item in display_items:
        status_class = "status-pass" if item.result == "PASSED" else "status-fail"
        with st.expander(
            f"{item.method} {item.endpoint}  |  {item.result}  |  {item.actual_status}  |  {item.duration_seconds:.1f}s",
            expanded=item.result == "FAILED",
        ):
            st.caption(f"Group: {item.group}")
            st.markdown(
                f'<span class="{status_class}">{item.result}</span>',
                unsafe_allow_html=True,
            )
            st.caption("Endpoint")
            st.code(f"{item.method} {item.endpoint}", language="text")
            if item.error_message:
                st.error(item.error_message)
                st.caption("Error Text")
                st.code(item.error_message, language="text")
            else:
                st.success(f"Response received successfully in {item.duration_seconds:.1f}s")

            jira_note = "\n".join(
                [
                    f"API: {item.method} {item.endpoint}",
                    f"Group: {item.group}",
                    f"Result: {item.result}",
                    f"Expected Status: {item.expected_status}",
                    f"Actual Status: {item.actual_status}",
                    f"Duration: {item.duration_seconds:.3f}s",
                    f"Run ID: {item.run_id}",
                    f"Error: {item.error_message or '-'}",
                ]
            )
            st.caption("Jira Note")
            st.code(jira_note, language="text")

    if preview and not st.session_state.results:
        st.caption("Preview entries come from mock-ready local data.")


def render_export_panel() -> None:
    if st.session_state.results and st.session_state.current_run_id:
        run_output_dir = output_dir(st.session_state.current_run_id)
        csv_path = export_results_csv(
            st.session_state.results,
            run_output_dir / "result.csv",
            environment=st.session_state.environment_name,
        )
        failed_results = [item for item in st.session_state.results if item.result != "PASSED"]
        failed_csv_path = export_results_csv(
            failed_results,
            run_output_dir / "failed_only_result.csv",
            environment=st.session_state.environment_name,
        )

        xlsx_error = ""
        xlsx_bytes = None
        xlsx_path = run_output_dir / "result.xlsx"
        failed_xlsx_bytes = None
        failed_xlsx_error = ""
        failed_xlsx_path = run_output_dir / "failed_only_result.xlsx"
        try:
            export_results_xlsx(
                st.session_state.results,
                xlsx_path,
                environment=st.session_state.environment_name,
            )
            xlsx_bytes = xlsx_path.read_bytes()
        except RuntimeError as exc:
            xlsx_error = str(exc)
        try:
            export_results_xlsx(
                failed_results,
                failed_xlsx_path,
                environment=st.session_state.environment_name,
            )
            failed_xlsx_bytes = failed_xlsx_path.read_bytes()
        except RuntimeError as exc:
            failed_xlsx_error = str(exc)

        st.caption("EXPORT")
        with st.expander("Download Results", expanded=False):
            st.caption(
                f"Run: {st.session_state.current_run_id} | env: {st.session_state.environment_name} | mode: {st.session_state.last_run_mode or 'n/a'}"
            )

            st.caption("All results")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "All Results CSV",
                    data=csv_path.read_bytes(),
                    file_name=f"{st.session_state.current_run_id}_result.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col2:
                if xlsx_bytes is not None:
                    st.download_button(
                        "All Results XLSX",
                        data=xlsx_bytes,
                        file_name=f"{st.session_state.current_run_id}_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                else:
                    st.button("All Results XLSX", disabled=True, use_container_width=True)
                    st.caption(xlsx_error)

            st.caption("Failed only")
            col3, col4 = st.columns(2)
            with col3:
                st.download_button(
                    "Download Failed CSV",
                    data=failed_csv_path.read_bytes(),
                    file_name=f"{st.session_state.current_run_id}_failed_only.csv",
                    mime="text/csv",
                    use_container_width=True,
                    disabled=not failed_results,
                )
            with col4:
                if failed_xlsx_bytes is not None:
                    st.download_button(
                        "Download Failed XLSX",
                        data=failed_xlsx_bytes,
                        file_name=f"{st.session_state.current_run_id}_failed_only.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        disabled=not failed_results,
                    )
                else:
                    st.button("Download Failed XLSX", disabled=True, use_container_width=True)
                    if failed_xlsx_error:
                        st.caption(failed_xlsx_error)

        with st.expander("Robot Artifacts", expanded=False):
            st.caption(f"Run folder: {run_output_dir}")
            artifact_col1, artifact_col2, artifact_col3 = st.columns(3)
            log_path = run_output_dir / "log.html"
            report_path = run_output_dir / "report.html"
            xml_path = run_output_dir / "output.xml"
            with artifact_col1:
                st.download_button(
                    "Download log.html",
                    data=log_path.read_bytes() if log_path.exists() else b"",
                    file_name=log_path.name,
                    mime="text/html",
                    use_container_width=True,
                    disabled=not log_path.exists(),
                )
            with artifact_col2:
                st.download_button(
                    "Download report.html",
                    data=report_path.read_bytes() if report_path.exists() else b"",
                    file_name=report_path.name,
                    mime="text/html",
                    use_container_width=True,
                    disabled=not report_path.exists(),
                )
            with artifact_col3:
                st.download_button(
                    "Download output.xml",
                    data=xml_path.read_bytes() if xml_path.exists() else b"",
                    file_name=xml_path.name,
                    mime="application/xml",
                    use_container_width=True,
                    disabled=not xml_path.exists(),
                )

    st.caption("CLEANUP")
    with st.expander("Cleanup Old Runs", expanded=False):
        run_dirs = [path for path in output_root_dir().iterdir() if path.is_dir() and path.name.startswith("run_")]
        run_dirs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        cleanup_options = list(range(0, max(len(run_dirs), 1) + 1))
        current_keep = min(int(st.session_state.cleanup_keep_latest), max(len(run_dirs), 1))
        st.session_state.cleanup_keep_latest = st.select_slider(
            "Keep latest runs",
            options=cleanup_options,
            value=current_keep,
        )
        removable_count = max(len(run_dirs) - int(st.session_state.cleanup_keep_latest), 0)
        st.caption(f"Found {len(run_dirs)} run folders. This will remove {removable_count} older run folders.")
        if st.button("Clean Old Runs", use_container_width=True, disabled=removable_count == 0):
            pending_paths = [str(path) for path in run_dirs[int(st.session_state.cleanup_keep_latest):]]
            current_run_dir = output_dir(st.session_state.current_run_id) if st.session_state.current_run_id else None
            st.session_state.cleanup_pending_paths = [
                path for path in pending_paths if current_run_dir is None or path != str(current_run_dir)
            ]
            st.session_state.cleanup_confirm_open = True
            st.session_state.cleanup_pending_count = len(st.session_state.cleanup_pending_paths)
            st.session_state.cleanup_target_label = "older run folder(s)"

    with st.expander("Cleanup Temp Files", expanded=False):
        temp_files = [path for path in temp_dir().iterdir() if path.is_file()]
        current_run_id = st.session_state.current_run_id
        removable_temp_files = [
            path for path in temp_files if not (current_run_id and path.name.startswith(f"{current_run_id}_"))
        ]
        st.caption(f"Found {len(temp_files)} temp file(s) in {temp_dir()}.")
        if removable_temp_files:
            st.caption(f"This will remove {len(removable_temp_files)} temp file(s).")
        else:
            st.caption("No removable temp files found.")
        if st.button("Clean Temp Files", use_container_width=True, disabled=not removable_temp_files):
            st.session_state.cleanup_pending_paths = [str(path) for path in removable_temp_files]
            st.session_state.cleanup_confirm_open = True
            st.session_state.cleanup_pending_count = len(removable_temp_files)
            st.session_state.cleanup_target_label = "temp file(s)"

    if st.session_state.cleanup_confirm_open and st.session_state.cleanup_pending_count > 0:
        render_cleanup_confirm_dialog(int(st.session_state.cleanup_pending_count))

    if st.session_state.cleanup_notice:
        st.success(st.session_state.cleanup_notice)


def render_dashboard_page() -> None:
    render_dashboard_panel(preview=False)
    render_export_panel()


def render_log_page() -> None:
    render_log_panel(preview=False)


def main() -> None:
    init_state()
    inject_css()
    render_header()
    render_tabs()
    st.write("")

    if st.session_state.active_tab == "Run Test":
        render_run_page()
    elif st.session_state.active_tab == "Dashboard":
        render_dashboard_page()
    else:
        render_log_page()
        render_export_panel()


if __name__ == "__main__":
    main()
