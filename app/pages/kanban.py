# app/pages/kanban.py
from typing import Any, Dict, List
import streamlit as st

from app.services import (
    TicketDienst,
    PRIO_WERTE,
    KANBAN_STATUS,
    NEXT_STATUS,
    PREV_STATUS,
)

from app.components import zeige_statistiken, kanban
from app.db.database import daten_abfragen

def kanban_seite():
    """Zeigt das Kanban-Board mit Filtern und gruppierten Tickets."""
    st.header("🎫 Ticket Kanban-Board")
    zeige_statistiken()

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    suchtext = col1.text_input("🔍 Suche")

    statusliste = daten_abfragen(
        "SELECT ID_Status AS id, Name FROM status ORDER BY ID_Status"
    )
    filter_status = col2.selectbox(
        "📁 Status",
        ["Alle"] + [s["Name"] for s in statusliste],
        )

    filter_prio = col3.selectbox(
        "⚠️ Priorität",
        ["Alle"] + PRIO_WERTE,
        )
    zeige_arch = col4.checkbox("📦 Archiv")

    id_status = (
        None
        if filter_status == "Alle"
        else next(
            (s["id"] for s in statusliste if s["Name"] == filter_status),
            None,
        )
    )

    prior = None if filter_prio == "Alle" else filter_prio

    tickets = TicketDienst.liste_tickets(
        archiviert=zeige_arch,
        suchbegriff=suchtext or None,
        id_status=id_status,
        prioritaet=prior,
    )

    if not tickets:
        st.info("ℹ️ Keine Tickets gefunden.")
        return

    # ---------------------------
    # KANBAN: feste Spalten
    # ---------------------------
    gruppiert: Dict[str, List[Dict[str, Any]]] = {
        s: [] for s in KANBAN_STATUS
    }

    for t in tickets:
        status = t.get("status_name") or "Neu"
        if status not in gruppiert:
            status = "Neu"
        gruppiert[status].append(t)

    cols = st.columns(len(KANBAN_STATUS))

    for idx, status in enumerate(KANBAN_STATUS):
        with cols[idx]:
            st.subheader(f"{status} ({len(gruppiert[status])})")

            if not gruppiert[status]:
                st.caption("— keine Tickets —")

            for t in gruppiert[status]:
                with st.container():
                    kanban(t)

                    # ---------------------------
                    # Status-Buttons (Kanban)
                    # ---------------------------
                    btn_left, btn_right = st.columns(2)

                    # ⬅️ Zurück
                    if status in PREV_STATUS:
                        if btn_left.button("⬅️", key=f"prev_{t['ID_Ticket']}"):
                            status_id = daten_abfragen(
                                "SELECT ID_Status FROM status WHERE Name=%s",
                                (PREV_STATUS[status],),
                            )[0]["ID_Status"]

                            TicketDienst.update_ticket(
                                t["ID_Ticket"],
                                ID_Status=status_id,
                                Geändert_von=st.session_state.user_id,
                            )
                            st.rerun()

                    # ➡️ Weiter
                    if status in NEXT_STATUS:
                        if btn_right.button("➡️", key=f"next_{t['ID_Ticket']}"):
                            status_id = daten_abfragen(
                                "SELECT ID_Status FROM status WHERE Name=%s",
                                (NEXT_STATUS[status],),
                            )[0]["ID_Status"]

                            TicketDienst.update_ticket(
                                t["ID_Ticket"],
                                ID_Status=status_id,
                                Geändert_von=st.session_state.user_id,
                            )
                            st.rerun()


