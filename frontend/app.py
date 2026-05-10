import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8080")
TIMEOUT = 5

st.set_page_config(page_title="Nodes Dashboard", layout="wide")


def get_health():
    r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_nodes():
    r = requests.get(f"{API_URL}/api/nodes", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def register_node(name, host, port):
    return requests.post(
        f"{API_URL}/api/nodes",
        json={"name": name, "host": host, "port": port},
        timeout=TIMEOUT,
    )


def delete_node(name):
    return requests.delete(f"{API_URL}/api/nodes/{name}", timeout=TIMEOUT)


st.title("Nodes Registry Dashboard")
st.write("This dashboard lists all registered nodes from the API.")

try:
    health = get_health()
    st.write(f"API status: {health.get('status', 'unknown')}")
    st.write(f"Active nodes count: {health.get('nodes_count', 0)}")
    nodes_data = get_nodes()
except requests.RequestException as e:
    st.error(f"API unreachable: {e}")
    nodes_data = []

st.header("Registered Nodes")

if nodes_data:
    for n in nodes_data:
        st.write(
            f"Node name: {n.get('name','')} | "
            f"host: {n.get('host','')} | "
            f"port: {n.get('port','')} | "
            f"status: {n.get('status','')}"
        )
else:
    st.write("No nodes registered yet.")

st.header("Register a new node")
with st.form("register_form", clear_on_submit=True):
    name = st.text_input("name")
    host = st.text_input("host")
    port = st.number_input("port", min_value=1, max_value=65535, value=8080, step=1)
    submitted = st.form_submit_button("Register")
    if submitted:
        if not name or not host:
            st.warning("name and host are required")
        else:
            resp = register_node(name, host, int(port))
            if resp.status_code in (200, 201):
                st.success(f"Node {name} registered")
                st.rerun()
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")

st.header("Delete a node")
with st.form("delete_form", clear_on_submit=True):
    del_name = st.text_input("name to delete")
    del_submitted = st.form_submit_button("Delete")
    if del_submitted:
        if not del_name:
            st.warning("name is required")
        else:
            resp = delete_node(del_name)
            if resp.status_code in (200, 204):
                st.success(f"Node {del_name} deleted")
                st.rerun()
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")