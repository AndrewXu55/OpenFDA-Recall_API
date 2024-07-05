import streamlit as st
import requests
import pandas as pd
import datetime

api_link = "http://127.0.0.1:8000/recalls"
url = "https://download.open.fda.gov/device/recall/device-recall-0001-of-0001.json.zip"
correct_inputs = True

st.set_page_config(
    page_title="FDA Recall",
    page_icon=":📊:",
    layout="centered",
    initial_sidebar_state="auto",
)
st.title("Open FDA Recall Information")
st.divider()
st.markdown("This website fetches [OpenFDA Device Recall data](" + \
            url+") based on inputted filters. You can input those filters in \
            the left sidebar. Press the :blue-background[Fetch Data] button when \
            ready. Enjoy!")


# Sidebar Contents
st.sidebar.title("Filters:")
start = st.sidebar.date_input("Select a Start Date", value = None, 
                          min_value=datetime.date(2002, 1, 1),
                          max_value=datetime.date(2024, 6, 14))

end = st.sidebar.date_input("Select a End Date", value = None, 
                      min_value=datetime.date(2002, 1, 1),
                      max_value=datetime.date(2024, 6, 14))

# Check if start date is before end date
if start and end and start > end:
    st.sidebar.error("Error: Make sure the start date is before the end date!")
    correct_inputs = False
else:
    correct_inputs = True

specialties = st.sidebar.multiselect(
    "Select Medical Specialties:",
        options=[
            'Anesthesiology', 'Cardiovascular', 'Clinical Chemistry', 
            'Clinical Toxicology', 'Dental', 'Ear, Nose, Throat', 
            'Gastroenterology, Urology', 'General Hospital', 
            'General, Plastic Surgery', 'Hematology', 'Immunology', 
            'Medical Genetics', 'Microbiology', 'Neurology', 
            'Obstetrics/Gynecology', 'Ophthalmic', 'Orthopedic', 
            'Pathology', 'Physical Medicine', 'Radiology', 'Unknown'
        ], placeholder="Default: Any")

entry_class = st.sidebar.selectbox(
    "Select Entry Class:",
    ('1', '2', '3', 'U', 'N', 'f'), 
   index = None, 
   placeholder="Default: Any")

quantity = st.sidebar.number_input("Input the minimum quantity of the device: ",
                         min_value= 0, step = 1)


# Fetches the Data
def fetch():
    params = {"min_quantity": int(quantity)}
    if start:
        params["start_date"] = start
    if end:
        params["end_date"] = end
    if specialties:
        params["specialties"] = '_'.join(specialties)
    if entry_class:
        params["device_class"] = entry_class
        
    response = requests.get(api_link, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

if st.button("Fetch Data: "):
    if correct_inputs:
        now = datetime.datetime.now()
        with st.spinner("Fetching Data..."):
            data = fetch()
        if data:
            df = pd.DataFrame(data)
            time = (datetime.datetime.now()- now).total_seconds()
            st.success(f"Fetching Succeeded! It took {time:.2f} secs.")
            st.write("Here is the 50 most recent entries from the filtered data:")
            st.write(df)
        elif data == []:
            st.write("None of the entries followed that filter. Please try again.")
        else:
            st.write("API failed. Please try again.")
    else:
        st.error("Make sure your input filters have no errors!")