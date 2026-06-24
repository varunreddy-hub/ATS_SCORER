import streamlit as st
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from MainApp.frontend.services import supabase_client

st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

for key, default in [
    ("access_token", None),
    ("refresh_token", None),
    ("user_id", None),
    ("user_email", None),
    ("auth_error", None),
    ("auth_info", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def _extract_user(result):
    user = result.get("user") or {}
    if isinstance(user, dict):
        uid = user.get("id", "")
        email = user.get("email", "")
    else:
        uid = getattr(user, "id", "")
        email = getattr(user, "email", "")
    return uid, email

if not st.session_state.access_token and "code" in st.query_params:
    result = supabase_client.exchange_code_for_session(st.query_params["code"])
    st.query_params.clear()
    if "error" in result:
        st.session_state.auth_error = f"Google sign-in failed: {result['error']}"
    else:
        st.session_state.access_token = result.get("access_token")
        st.session_state.refresh_token = result.get("refresh_token")
        uid, email = _extract_user(result)
        st.session_state.user_id = uid
        st.session_state.user_email = email
        st.rerun()

def load_css():
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        with open(css_path, 'r') as f:
            return f'<style>{f.read()}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'

with st.sidebar:
    st.markdown("## Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()

    if st.button("🎯 ATS Scorer", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()

    if st.button("📊 History", use_container_width=True):
        st.session_state.current_view = 'history'
        st.rerun()

    if st.button("📚 Resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()

    st.markdown("---")
    st.markdown("### 👤 Account")

    if st.session_state.access_token:
        st.caption(f"Signed in as **{st.session_state.user_email}**")
        if st.button("Sign out", use_container_width=True):
            supabase_client.sign_out(st.session_state.access_token)
            for k in ("access_token", "refresh_token", "user_id", "user_email"):
                st.session_state[k] = None
            st.rerun()
    else:
        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None
        if st.session_state.auth_info:
            st.info(st.session_state.auth_info)
            st.session_state.auth_info = None

        tab_in, tab_up = st.tabs(["Sign in", "Sign up"])

        with tab_in:
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_pw")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                result = supabase_client.sign_in_with_password(email, password)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                else:
                    st.session_state.access_token = result.get("access_token")
                    st.session_state.refresh_token = result.get("refresh_token")
                    uid, email = _extract_user(result)
                    st.session_state.user_id = uid
                    st.session_state.user_email = email
                    st.rerun()

        with tab_up:
            with st.form("signup_form", clear_on_submit=False):
                email_up = st.text_input("Email", key="signup_email")
                password_up = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
                submitted_up = st.form_submit_button("Create account", use_container_width=True)
            if submitted_up:
                result = supabase_client.sign_up_with_password(email_up, password_up)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                elif result.get("pending_confirmation"):
                    st.session_state.auth_info = (
                        f"Check your inbox — confirmation email sent to {email_up}."
                    )
                else:
                    st.session_state.access_token = result.get("access_token")
                    st.session_state.refresh_token = result.get("refresh_token")
                    uid, email_up = _extract_user(result)
                    st.session_state.user_id = uid
                    st.session_state.user_email = email_up
                st.rerun()

        st.markdown("<div style='text-align:center; margin: 8px 0; color:#94a3b8;'>or</div>",
                    unsafe_allow_html=True)

        oauth = supabase_client.google_oauth_url()
        if "error" in oauth:
            st.caption(f"Google sign-in unavailable: {oauth['error']}")
        else:
            st.link_button(
                "Continue with Google",
                url=oauth["url"],
                use_container_width=True,
            )

if st.session_state.current_view == 'landing':
    from MainApp.frontend.views import landing
    landing.render()

elif st.session_state.current_view == 'scorer':
    from MainApp.frontend.views import scorer
    scorer.render()

elif st.session_state.current_view == 'history':
    from MainApp.frontend.views import history
    history.render()

elif st.session_state.current_view == 'resources':
    from MainApp.frontend.views import resources
    resources.render()