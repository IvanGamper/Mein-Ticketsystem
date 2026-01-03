# app/pages/ticket_create.py
import streamlit as st

from app.services import TicketDienst, PRIO_WERTE
from app.db.database import daten_abfragen


def ui_ticket_erstellen():
    """Formular zum Anlegen eines neuen Tickets (UI layer)."""

    st.header("➕ Neues Ticket erstellen")

    with st.form("create_ticket_form"):
        titel = st.text_input("📝 Titel")
        beschreibung = st.text_area(
            "📄 Beschreibung",
            height=200
        )

        col1, col2 = st.columns(2)

        prio = col1.selectbox(
            "⚠️ Priorität",
            PRIO_WERTE,
            index=1
        )

        kunden = daten_abfragen(
            "SELECT ID_Kunde AS id, Name FROM kunde ORDER BY Name"
        )

        kundeliste = [None] + [k["id"] for k in kunden]
        kunden_map = {k["id"]: k["Name"] for k in kunden}

        kunde = col2.selectbox(
            "🔎 Kunde",
            kundeliste,
            format_func=lambda v: "—" if v is None else kunden_map.get(v, "?"),
        )

        if st.form_submit_button("✅ Ticket anlegen"):
            if not titel or not beschreibung:
                st.error(
                    "❌ Titel und Beschreibung dürfen nicht leer sein."
                )
            else:
                TicketDienst.svc_ticket_erstellen(
                    titel.strip(),
                    beschreibung.strip(),
                    prio, kunde,
                    st.session_state.user_id,
                )
                st.success("✅ Ticket angelegt!")
                st.balloons()
                st.rerun()