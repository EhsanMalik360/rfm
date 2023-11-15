import streamlit as st
import pandas as pd
from datetime import datetime

# Calculate RFM metrics
def calculate_rfm(data, date_col, id_col, spend_col):
    # Convert InvoiceDate to datetime
    data[date_col] = pd.to_datetime(data[date_col])

    # Calculate Recency, Frequency, and Monetary metrics
    max_date = data[date_col].max() + pd.to_timedelta(1, unit='d')
    rfm = data.groupby(id_col).agg({
        date_col: lambda x: (max_date - x.max()).days,
        id_col: 'count',
        spend_col: 'sum'
    }).rename(columns={date_col: 'Recency', id_col: 'Frequency', spend_col: 'Monetary'})

    return rfm

# Segment customers based on RFM scores
def segment_customers(rfm_data):
    # Quartile-based segmentation logic remains the same as in the previous code

# Streamlit app main function
def main():
    st.title("RFM Analysis App")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # Column selection
        st.write("Select the columns for RFM analysis")
        id_col = st.selectbox("Select Customer ID Column", data.columns)
        date_col = st.selectbox("Select Invoice Date Column", data.columns)
        spend_col = st.selectbox("Select Total Spend Column", data.columns)

        if st.button("Calculate RFM"):
            # Calculate RFM
            rfm_data = calculate_rfm(data, date_col, id_col, spend_col)

            # Segment customers
            segmented_data = segment_customers(rfm_data)

            # Display results
            st.write("RFM Analysis Results")
            st.dataframe(segmented_data)

            # Export button (optional)
            st.download_button(label="Download RFM Data", data=segmented_data.to_csv(), file_name='rfm_analysis.csv', mime='text/csv')

if __name__ == "__main__":
    main()
