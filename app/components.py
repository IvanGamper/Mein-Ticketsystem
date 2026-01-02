# components.py
from typing import Any, Dict, List
import streamlit as st
from app.services import TicketDienst
from app.utils import datum_formatieren

def zeige_statistiken():
    """Zeigt Kennzahlen als Metriken."""
    stats = TicketDienst.stats()
    col1, col2 = st.columns(2)
    col1.metric("Gesamt", stats.get("total", 0))
    col2.metric("📦 Archiviert", stats.get("archiviert", 0))
    st.divider()

def kanban(t):
    """Rendert eine Ticket-Karte (Kurzinfo)."""

    prio = t.get("Priorität", "-")

    st.markdown(
        f"**#{t['ID_Ticket']} — {t.get('Titel','-')}**"
    )

    st.caption(
        f"📁 {t.get('status_name','-')} • "
        f"⏰ {datum_formatieren(t.get('Geändert_am'))}"
    )
    st.write(
        (t.get("Beschreibung") or "")[:200]
    )

    st.caption(
        f"👤 {t.get('creator_name','?')}"
    )