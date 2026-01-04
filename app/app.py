#app.py
import streamlit as st

from .services import AuthDienst


from app.pages.admin import admin_seite
from app.pages.ticket_create import ui_ticket_erstellen
from app.pages.kanban import kanban_seite

class AppUI:
    """Streamlit-Oberfläche"""

    def __init__(self):
        st.set_page_config(
            page_title="Ticketsystem",
            layout="wide",
            page_icon="🎫"
        )

        st.markdown(
            """
            <style>
                .stButton button { 
                    border-radius: 5px; 
                }
                div[data-testid="stExpander"] { 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                }
            </style>
            """,
            unsafe_allow_html=True
        )



    def seite_login(self):
        """Zeigt Login-Formular und führt Authentifizierung durch."""

        st.title("🎫 Ticketsystem Login")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.form("login_form"):
                st.subheader("Anmelden")

                u = st.text_input("Benutzername / Email")
                p = st.text_input("Passwort", type="password")

                if st.form_submit_button("🔐 Anmelden"):
                    user = AuthDienst.login(u, p)

                    if user:
                        st.session_state.update(
                            {
                                "user_id": user["id"],
                                "role": user["role"],
                                "username": user["username"]
                            }
                        )
                        st.success("✅ Erfolgreich angemeldet!")
                        st.rerun()
                    else:
                        st.error("❌ Ungültige Zugangsdaten")


    def profil_seite(self):
        """Zeigt Profilinformationen und bietet Logout an."""
        st.header("👤 Profil")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                f"""
                ### Angemeldet als

                **Benutzername:** {st.session_state.username}  
                **Rolle:** {st.session_state.role}
                """
            )

            if st.button(
                    "🚪 Logout",
                    use_container_width=True,
                    type="primary",
            ):
                for k in ["user_id", "role", "username"]:
                    st.session_state.pop(k, None)

                st.success("✅ Erfolgreich abgemeldet!")
                st.rerun()

def main():
    """Entry-Point: baut UI auf und routet zwischen Seiten."""
    app = AppUI()

    if "user_id" not in st.session_state:
        app.seite_login()
        return

    st.sidebar.title("🎫 Ticketsystem")
    st.sidebar.markdown(
        f"**👤 Benutzer:**  {st.session_state.get('username','-')}"
    )
    st.sidebar.markdown(
        f"**🛡️ Rolle:**  {st.session_state.get('role','-')}"
    )
    st.sidebar.divider()

    menue = [
        "📋 Kanban-Board",
        "➕ Ticket erstellen"
    ]

    if st.session_state.get("role") == "admin":
        menue.append("🛠️ Verwaltung")

    auswahl = st.sidebar.radio(
        "Navigation",
        menue,
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    if st.sidebar.button("🚪 Logout"):
        for k in ["user_id", "role", "username"]:
            st.session_state.pop(k, None)
        st.rerun()

    # Routing zu den Seiten
    if auswahl == "📋 Kanban-Board":
        kanban_seite()

    elif auswahl == "➕ Ticket erstellen":
        ui_ticket_erstellen()

    elif auswahl == "🛠️ Verwaltung":
        admin_seite()



if __name__ == "__main__":
    main()
