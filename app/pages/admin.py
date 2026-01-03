#admin.py
import pandas as pd
import streamlit as st

from app.services import TicketDienst, AuthDienst, PRIO_WERTE
from app.db.repositories import Mitarbeiter
from app.db.database import daten_abfragen
from app.utils import datum_formatieren

def tickets_verwalten():
    """Admin-Ansicht: Tickets ansehen und editieren."""

    st.header("🔧 Admin: Tickets verwalten")

    zeige_arch = st.checkbox("📦 Archivierte anzeigen")
    tickets = TicketDienst.liste_tickets(
        archiviert=zeige_arch
    )

    if not tickets:
        st.info("ℹ️ Keine Tickets vorhanden")
        return

    benutzer = Mitarbeiter.liste_aktiv()
    benutzer_map = {u["id"]: u["username"] for u in benutzer}
    benutzer_ids = [None] + [u["id"] for u in benutzer]

    for t in tickets:
        with (((st.expander(
                f"#{t['ID_Ticket']} — {t['Titel']}",
                expanded=False,
        )))):
            st.markdown(f"**Ticket #{t['ID_Ticket']}**")

            st.caption(
                f"Erstellt: "
                f"{datum_formatieren(t.get('Erstellt_am'))} | "
                f"Aktualisiert: "
                f"{datum_formatieren(t.get('Geändert_am'))}"
            )

            st.write(
                t.get("Beschreibung", "")
            )

            c1, c2, c3, c4 = st.columns(4)

            status_namen = [
                s["Name"]
                for s in daten_abfragen(
                    "SELECT ID_Status AS id, Name FROM status ORDER BY ID_Status"
                )
            ]

            status = c1.selectbox(
                "Status",
                status_namen,
                index=0,
                key=f"st_{t['ID_Ticket']}",
            )

            prio_index = (
                PRIO_WERTE.index(t.get("Priorität"))
                if t.get("Priorität") in PRIO_WERTE
                else 1
            )

            prio = c2.selectbox(
                "Priorität",
                PRIO_WERTE,
                index=prio_index,
                key=f"pr_{t['ID_Ticket']}",
            )

            cur = t.get("Geändert_von")

            a_index = (
                0
                if cur in (None, 0)
                else (
                    benutzer_ids.index(cur)
                    if cur in benutzer_ids
                    else 0
                )
            )

            assignee = c4.selectbox(
                "Bearbeiter",
                benutzer_ids,
                index=a_index,
                format_func=lambda v: "—" if v is None else benutzer_map.get(v, "?"),
                key=f"as_adm_{t['ID_Ticket']}",
            )

            arch = st.checkbox(
                "📦 Archivieren",
                value=bool(t.get("Archiviert", 0)),
                key=f"arch_adm_{t['ID_Ticket']}",
            )

            if st.button(
                    "💾 Speichern",
                    key=f"save_adm_{t['ID_Ticket']}",
            ):
                status_row = daten_abfragen(
                    "SELECT ID_Status FROM status WHERE Name=%s",
                    (status,),
                )

                status_id = (
                    status_row[0]["ID_Status"]
                    if status_row
                    else None
                )

                felder = {
                    "ID_Status": status_id,
                    "Priorität": prio,
                    "Geändert_von": assignee,
                    "Archiviert": int(arch),

                }
                TicketDienst.update_ticket(
                    t["ID_Ticket"],
                    **felder,
                )

                st.success("✅ Gespeichert")
                st.rerun()

def admin_seite():
    st.header("🛠️ Verwaltung")

    tab_tickets, tab_users = st.tabs(
        ["🎫 Tickets", "👥 Benutzer"]
    )

    with tab_tickets:
        tickets_verwalten()

    with tab_users:
        st.header("🗄️ Benutzerverwaltung")

    users = Mitarbeiter.liste_aktiv()

    if users:
        st.dataframe(
            pd.DataFrame(users),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Keine Benutzer vorhanden")

    st.divider()

    with st.form("new_user"):
        st.subheader("➕ Neuen Benutzer anlegen")

        col1, col2, col3 = st.columns(3)

        name = col1.text_input("Name")
        email = col2.text_input("Email")
        pw = col3.text_input(
            "Passwort",
            type="password",
        )

        if st.form_submit_button("✅ Anlegen"):
            if name and email and pw:
                AuthDienst.erstelle_mitarbeiter(
                    name,
                    email,
                    pw,
                    None,
                )
                st.success("✅ Benutzer angelegt.")
                st.rerun()
            else:
                st.error(
                    "❌ Name, Email und Passwort erforderlich."
                )

    st.divider()

    st.subheader("🗑️ Benutzer deaktivieren")

    users = Mitarbeiter.liste_aktiv()

    if not users:
        st.info("Keine aktiven Benutzer vorhanden.")
    else:
        victim = st.selectbox(
            "Benutzer auswählen",
            users,
            format_func=lambda x: x["username"],
        )

        confirm = st.text_input(
            "Zur Bestätigung Benutzernamen erneut eingeben"
        )

        sure = st.checkbox("Ich bin sicher")

        is_self = (
                "user_id" in st.session_state
                and victim["id"] == st.session_state["user_id"]
        )

        if is_self:
            st.warning(
                "⚠️ Du kannst dich nicht selbst deaktivieren."
            )

        if st.button(
                "🗑️ Benutzer deaktivieren",
                disabled=is_self
                         or not sure or confirm != victim["username"],
        ):
            Mitarbeiter.mitarbeiter_deaktivieren(
                victim["id"]
            )
            st.success(
                f"✅ Benutzer '{victim['username']}' wurde deaktiviert."
            )
            st.rerun()