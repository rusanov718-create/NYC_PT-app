import streamlit as st
st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import requests
import sqlite3
from datetime import datetime

st.set_page_config(page_title="NYC Ticket Checker", page_icon="🚗", layout="centered")

st.title("🚗 NYC Parking & Camera Ticket Checker")
st.write("Check for NYC parking/camera tickets automatically using the public NYC Open Data API.")

# --- User inputs
plate = st.text_input("Enter your plate number", "").upper().strip()
state = st.text_input("Enter plate state (e.g. NY)", "NY").upper().strip()
check_btn = st.button("🔍 Check Now")

# --- Database (stores seen tickets)
conn = sqlite3.connect("tickets_web.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS seen(id TEXT PRIMARY KEY)")
conn.commit()

# --- Helper
def fetch_tickets(plate, state):
    url = "https://data.cityofnewyork.us/resource/nc67-uf89.json"
    params = {"plate": plate, "plate_state": state, "$limit": 50}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

# --- Main
if check_btn:
    if not plate:
        st.warning("Please enter a plate number.")
    else:
        with st.spinner("Checking NYC data..."):
            try:
                tickets = fetch_tickets(plate, state)
                new_tickets = []
                for t in tickets:
                    tid = t.get("summons_number")
                    if not tid:
                        continue
                    cur.execute("SELECT 1 FROM seen WHERE id=?", (tid,))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO seen VALUES(?)", (tid,))
                        conn.commit()
                        new_tickets.append(t)

                if new_tickets:
                    st.success(f"🎉 Found {len(new_tickets)} new ticket(s)!")
                    for t in new_tickets:
                        st.write(f"**Violation:** {t.get('violation')}")
                        st.write(f"📅 Date: {t.get('issue_date')}")
                        st.write(f"📍 Location: {t.get('street_name')}")
                        st.write("---")
                else:
                    st.info("✅ No new tickets found.")
            except Exception as e:
                st.error(f"Error checking data: {e}")

st.markdown("Data source: [NYC Open Data – Parking and Camera Violations](https://data.cityofnewyork.us/Transportation/Open-Parking-and-Camera-Violations/nc67-uf89)")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
