from fastapi import FastAPI
import uvicorn
import json

app = FastAPI()

@app.get('/hello')
def example_route(name: str | None=None) -> str:
    """
    Returns a greeting string using the provided name.
    If no name is provided, a gener ic greeting is returned
    instead.

    Arguments
    ---------
    name: An optional query parameter used in the greeting

    Returns
    -------
    A string of a greeting
    """

    if name is None:
        return "Hello!"
    
    return f"Hello, {name}!"

# Load JSON Data
def load_data():
    with open('device_recall.json', 'r') as file:
        return json.load(file)

# Get first 50 Rows after a inputted filter
@app.get('/recalls')
def retrieve(start_date: str = None, end_date: str = None, specialties: str \
             = None, device_class: str = None, min_quantity:int = 0):
    data = load_data()['results']
    
    # Convert Specialties into a set rather than a string
    if specialties:
        specialties = set(specialties.split('_'))

    # Helper Function that verifies the entry passes all the inputted filters
    def verify(entry):
        entry_date = entry.get("event_date_posted", None)
        entry_specialty = entry.get("openfda", {}) \
                .get("medical_specialty_description", None)
        entry_class = entry.get("openfda", {}).get("device_class", None)
        entry_quantity = entry.get("product_quantity", None)

        # More Processing on Quantity since Entries are Volatile
        if min_quantity:
            try:
                entry_quantity = entry_quantity.split(maxsplit=1)[0]
                entry_quantity = int(entry_quantity.replace(',', ''))
            except: # Problem with entry types
                entry_quantity = None

        return all((
            start_date is None or (entry_date and start_date <= entry_date),
            end_date is None or (entry_date and entry_date <= end_date),
            specialties is None or (entry_specialty and entry_specialty in \
                specialties),
            device_class is None or (entry_class and entry_class == \
                                     device_class),
            min_quantity == 0 or (entry_quantity and int(entry_quantity) \
                                    > min_quantity)
        ))
    
    recall_data = [
        {
            "recall_id": entry.get("cfres_id", "N/A"),
            "date_of_recall": entry.get("event_date_posted", "N/A"),
            "code_info": entry.get("code_info", "N/A"),
            "recalling_firm": entry.get("recalling_firm", "N/A"),
            "reason_for_recall": entry.get("reason_for_recall", "N/A"),
            "product_quantity": entry.get("product_quantity", "N/A"),
            "device_name": entry.get("openfda", {}).get("device_name", "N/A"),
            "medical_specialty_description": entry.get("openfda", {}) \
                .get("medical_specialty_description", "N/A"),
            "device_class": entry.get("openfda", {}).get("device_class", "N/A")
        } for entry in data if verify(entry)
    ]
    
    recall_data.sort(key=lambda x: "0" if x["date_of_recall"] == "N/A" else \
                     x["date_of_recall"], reverse=True)
    return recall_data[:50]

if __name__ == '__main__':
    uvicorn.run(app)