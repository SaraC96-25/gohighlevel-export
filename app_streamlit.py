import streamlit as st
import requests
import csv
import time
import os

# --- CONFIGURAZIONE FISSA ---
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6Ind0WWVNV0pLY283MmhxSXd0cjJWIiwidmVyc2lvbiI6MSwiaWF0IjoxNzQ1ODM2OTg5NDc5LCJzdWIiOiI4aDdBa2UzbHV6SHg3eWR4alhkOSJ9.w-Wab0mlhGlugXIMn_BFA_BrkOMqKsFPQlrD3UsWoF4"  # <-- La tua API KEY qui
API_BASE_URL = "https://rest.gohighlevel.com/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- FUNZIONI ---

def get_contacts():
    contacts = []
    page = 1
    while True:
        response = requests.get(f"{API_BASE_URL}/contacts?page={page}&limit=100", headers=HEADERS)
        data = response.json()
        if "contacts" not in data or not data["contacts"]:
            break
        contacts.extend(data["contacts"])
        page += 1
    return contacts

def get_notes(contact_id):
    try:
        response = requests.get(f"{API_BASE_URL}/contacts/{contact_id}/notes", headers=HEADERS)
        if response.status_code == 200:
            notes = response.json().get("notes", [])
            return " | ".join(note.get("body", "") for note in notes)
    except:
        pass
    return ""

def export_to_csv(contacts, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Contact ID", "Name", "Email", "Phone", "Notes"])
        writer.writeheader()
        for contact in contacts:
            notes = get_notes(contact["id"]) or ""
            writer.writerow({
                "Contact ID": contact["id"],
                "Name": f'{contact.get("firstName", "")} {contact.get("lastName", "")}',
                "Email": contact.get("email", ""),
                "Phone": contact.get("phone", ""),
                "Notes": notes
            })
            time.sleep(0.1)

# --- APP STREAMLIT ---

st.title("📤 GoHighLevel - Esporta Contatti")
st.write("Premi il bottone qui sotto per scaricare il file CSV dei contatti con note.")

if st.button("Esporta Contatti"):
    with st.spinner('Recupero contatti e generazione file...'):
        contacts = get_contacts()
        if contacts:
            filename = "contatti_gohighlevel.csv"
            export_to_csv(contacts, filename)
            st.success(f"Esportazione completata! File salvato come {filename}")
            with open(filename, "rb") as f:
                st.download_button("Scarica il CSV", f, file_name=filename)
        else:
            st.error("Nessun contatto trovato o errore API.")
