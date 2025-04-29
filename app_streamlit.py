import streamlit as st
import requests
import csv
import time
import os

# --- CONFIGURAZIONE FISSA ---
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6Ind0WWVNV0pLY283MmhxSXd0cjJWIiwidmVyc2lvbiI6MSwiaWF0IjoxNzQ1ODM2OTg5NDc5LCJzdWIiOiI4aDdBa2UzbHV6SHg3eWR4alhkOSJ9.w-Wab0mlhGlugXIMn_BFA_BrkOMqKsFPQlrD3UsWoF4"  # <-- La tua API KEY vera!
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
    total_contacts = len(contacts)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Contact ID", "Name", "Email", "Phone", "Notes", "Di che cosa si occupa la tua azienda?"])
        writer.writeheader()

        # Progress bar
        progress_bar = st.progress(0)

        for i, contact in enumerate(contacts):
            notes = get_notes(contact["id"]) or ""

            # Estrazione campo customField
            business_type = ''
            if 'customField' in contact and len(contact['customField']) > 0:
                business_type = contact['customField'][0].get('value', '')

            writer.writerow({
                "Contact ID": contact["id"],
                "Name": f'{contact.get("firstName", "")} {contact.get("lastName", "")}',
                "Email": contact.get("email", ""),
                "Phone": contact.get("phone", ""),
                "Notes": notes,
                "Di che cosa si occupa la tua azienda?": business_type
            })
            time.sleep(0.05)
            progress_bar.progress((i + 1) / total_contacts)

# --- APP STREAMLIT ---

st.title("\ud83d\udce4 GoHighLevel - Esporta Contatti")
st.write("Premi il bottone qui sotto per scaricare il file CSV dei contatti con note e informazioni aziendali.")

if st.button("\ud83d\ude80 Esporta Contatti"):
    with st.spinner('Recupero contatti e generazione file...'):
        contacts = get_contacts()
        if contacts:
            filename = "contatti_gohighlevel.csv"
            export_to_csv(contacts, filename)
            st.success(f"\u2705 Esportazione completata! Scarica il file qui sotto.")
            with open(filename, "rb") as f:
                st.download_button("\ud83d\udcc5 Scarica il CSV", f, file_name=filename)
        else:
            st.error("\u274c Nessun contatto trovato o errore API.")
