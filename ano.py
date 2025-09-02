import streamlit as st
import os, json, hashlib, base64, random, time

# ====== FILES ======
USER_DATA_FILE = "users.json"
CHAT_FILE = "chat.json"

# ====== PASSWORD HELPERS ======
def hash_password(password: str, salt: str = None):
    import hashlib, base64, os
    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest()
    pwdhash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    pwdhash = base64.b64encode(pwdhash).decode("ascii")
    return pwdhash, salt

def verify_password(stored_password, provided_password, salt):
    pwdhash, _ = hash_password(provided_password, salt)
    return pwdhash == stored_password

# ====== USERS ======
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ====== CHAT ======
def load_chat():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# ====== SESSION ======
if "page" not in st.session_state:
    st.session_state["page"] = "auth"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "anon_tag" not in st.session_state:
    st.session_state["anon_tag"] = f"Anon-{random.randint(100,999)}"

# ====== STYLE ======
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #000428, #004e92);
            color: white;
        }
        .chat-bubble {
            background-color: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 12px;
            margin: 5px 0;
            font-size: 16px;
        }
        .chat-bubble:hover {
            background-color: rgba(0,255,200,0.2);
        }
        .title {
            text-align:center;
            font-size: 32px;
            font-weight: bold;
            text-shadow: 0 0 10px cyan;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ====== AUTH PAGE ======
def auth_page():
    st.markdown("<div class='title'>🔐 Anonymous Chatroom</div>", unsafe_allow_html=True)
    users = load_users()
    login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign up"])

    with login_tab:
        with st.form("login_form"):
            uname = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("🚀 Log in"):
                if uname not in users:
                    st.error("❌ Username not found")
                else:
                    stored_pwd = users[uname]["password"]
                    salt = users[uname]["salt"]
                    if verify_password(stored_pwd, pwd, salt):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = uname
                        st.session_state["anon_tag"] = f"Anon-{random.randint(100,999)}"
                        st.session_state["page"] = "chat"
                        st.rerun()
                    else:
                        st.error("❌ Wrong password")

    with signup_tab:
        with st.form("signup_form"):
            uname_new = st.text_input("New Username")
            pwd_new = st.text_input("Password", type="password")
            pwd_confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("✨ Sign up"):
                if uname_new in users:
                    st.error("❌ Username already taken")
                elif not uname_new or not pwd_new or not pwd_confirm:
                    st.error("❌ Fill all fields")
                elif pwd_new != pwd_confirm:
                    st.error("❌ Passwords do not match")
                else:
                    hashed_pwd, salt = hash_password(pwd_new)
                    users[uname_new] = {"password": hashed_pwd, "salt": salt}
                    save_users(users)
                    st.success("✅ Signup successful! Please login now")

# ====== CHAT PAGE ======
def chat_page():
    st.sidebar.success(f"🟢 Logged in as {st.session_state['username']}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["page"] = "auth"
        st.rerun()

    st.markdown("<div class='title'>🌍 Public Anonymous Chatroom</div>", unsafe_allow_html=True)

    # Load & display chat
    messages = load_chat()
    for msg in messages[-50:]:  # show last 50
        st.markdown(f"<div class='chat-bubble'><b>{msg['user']}:</b> {msg['text']}</div>", unsafe_allow_html=True)

    # Input
    user_msg = st.chat_input("Type your anonymous message…")
    if user_msg:
        new_msg = {"user": st.session_state["anon_tag"], "text": user_msg}
        messages.append(new_msg)
        save_chat(messages)
        st.rerun()

# ====== ROUTER ======
if st.session_state["page"] == "auth":
    auth_page()
elif st.session_state["page"] == "chat":
    chat_page()
