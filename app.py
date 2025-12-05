import streamlit as st
import requests
import socket

st.set_page_config(page_title="AI Competitor Battlecard Agent", layout="wide")

# ---------------------------------------------------------
# AUTO-DETECT BACKEND URL (Docker vs Local)
# ---------------------------------------------------------
hostname = socket.gethostname().lower()

if "competitor-frontend" in hostname or "docker" in hostname:
    BASE_URL = "http://backend:8000"
else:
    BASE_URL = "http://localhost:8000"

# ---------------------------------------------------------
# STREAMLIT STATE SETUP
# ---------------------------------------------------------
if "root_company" not in st.session_state:
    st.session_state.root_company = None

if "root_category" not in st.session_state:
    st.session_state.root_category = None

if "root_industry" not in st.session_state:
    st.session_state.root_industry = None

if "root_keywords" not in st.session_state:
    st.session_state.root_keywords = []

if "competitors" not in st.session_state:
    st.session_state.competitors = []  # list of {"name":..., "url":...}

if "battlecards" not in st.session_state:
    st.session_state.battlecards = {}  # keyed by domain


# ---------------------------------------------------------
# SIDEBAR UI
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ App State")

    st.write("**Backend URL:**", BASE_URL)

    st.write("### Root Company")
    st.write(st.session_state.root_company)

    st.write("### Category")
    st.write(st.session_state.root_category)

    st.write("### Competitors")
    if st.session_state.competitors:
        for c in st.session_state.competitors:
            st.write(f"- {c['name']} ({c['url']})")
    else:
        st.write("No competitors yet.")


# ---------------------------------------------------------
# MAIN UI: STEP 1 — Infer Category
# ---------------------------------------------------------
st.title("🧠 AI Competitor Battlecard Agent")

st.subheader("Step 1 — Enter Primary Company URL")

primary_url = st.text_input(
    "Company URL",
    placeholder="https://stripe.com",
)

if st.button("Infer Category"):
    if not primary_url.strip():
        st.error("Please enter a valid URL.")
    else:
        try:
            resp = requests.post(
                f"{BASE_URL}/infer_category",
                json={"url": primary_url},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()

                st.session_state.root_company = primary_url
                st.session_state.root_category = data["state"]["root_category"]
                st.session_state.root_industry = data["state"]["root_industry"]
                st.session_state.root_keywords = data["state"]["root_keywords"]

                st.success("Category inferred successfully!")
                st.experimental_rerun()

            else:
                st.error(f"Error: {resp.text}")

        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------------------------------------------------------
# If category not set → stop here
# ---------------------------------------------------------
if not st.session_state.root_category:
    st.stop()


# ---------------------------------------------------------
# MAIN UI: STEP 2 — Manual Competitor Validation
# ---------------------------------------------------------
st.subheader("Step 2 — Add Competitors (Validated by AI)")

competitor_url = st.text_input(
    "Competitor URL",
    placeholder="https://example.com",
    key="competitor_url_input",
)

if st.button("Validate & Add Competitor"):
    if not competitor_url.strip():
        st.error("Please enter a URL.")
    else:
        try:
            resp = requests.post(
                f"{BASE_URL}/validate_company",
                json={
                    "url": competitor_url,
                    "category": st.session_state.root_category,
                },
                timeout=30,
            )
            data = resp.json()

            if data.get("allowed"):
                st.session_state.competitors.append(
                    {"name": data["name"], "url": competitor_url}
                )
                st.success(f"Added competitor: {data['name']}")
                st.experimental_rerun()
            else:
                st.error(f"Rejected: {data.get('reason')}")

        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------------------------------------------------------
# MAIN UI: STEP 3 — Analyze Competitors
# ---------------------------------------------------------
st.subheader("Step 3 — Analyze Competitors")

for c in st.session_state.competitors:
    if st.button(f"Analyze {c['name']}"):
        try:
            resp = requests.post(
                f"{BASE_URL}/analyze_competitor",
                json={"url": c["url"]},
                timeout=60,
            )
            if resp.status_code == 200:
                st.session_state.battlecards[c["url"]] = resp.json()
                st.success(f"Battlecard ready for {c['name']}")
            else:
                st.error(f"Error: {resp.text}")

        except Exception as e:
            st.error(f"Request failed: {e}")


# ---------------------------------------------------------
# MAIN UI: STEP 4 — Show Comparison Table
# ---------------------------------------------------------
st.subheader("Step 4 — Comparison Table")

if st.session_state.battlecards:
    for url, bc in st.session_state.battlecards.items():
        st.write(f"### {url}")
        st.json(bc)  # placeholder — we will style this next

else:
    st.info("No battlecards yet.")
