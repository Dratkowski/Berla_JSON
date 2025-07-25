import streamlit as st
import json
import pandas as pd
from io import BytesIO

def extract_lat_lon_with_velocity(data_json):
    gps_data = []
    for event in data_json.get("events", []):
        if event.get("tag") == "Navigation.Location":
            val = event.get("value", {})
            coord = val.get("coordinate", {})
            velocity = val.get("velocity", {})
            gps_data.append({
                "FixTime": val.get("fixTime"),
                "Latitude": coord.get("latitude"),
                "Longitude": coord.get("longitude"),
                "Speed_Kph": velocity.get("speed")
            })
    df = pd.DataFrame(gps_data)
    # Convert KPH to MPH
    df['Speed_Mph'] = df['Speed_Kph'].apply(lambda x: x * 0.621371 if pd.notnull(x) else None)
    return df

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='GPS Data')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

st.title("Lat/Lon + Speed/Bearing Extractor")

uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

if uploaded_file is not None:
    try:
        data_json = json.load(uploaded_file)
        st.success("JSON file loaded successfully.")
        df = extract_lat_lon_with_velocity(data_json)

        if df.empty:
            st.warning("No Navigation.Location events found in the JSON.")
        else:
            st.dataframe(df)

            excel_bytes = to_excel_bytes(df)

            st.download_button(
                label="Download Excel file",
                data=excel_bytes,
                file_name="extracted_gps_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a JSON file to get started.")
