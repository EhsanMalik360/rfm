import streamlit as st
import pandas as pd
from datetime import datetime


# Function to calculate RFM metrics
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


# Function to segment customers based on RFM scores
def segment_customers(rfm_data):
    # Quartile-based segmentation
    quartiles = rfm_data.quantile(q=[0.25, 0.5, 0.75])

    # Function to assign R, F, M segments
    def RScore(x, p, d):
        if x <= d[p][0.25]:
            return 1
        elif x <= d[p][0.50]:
            return 2
        elif x <= d[p][0.75]:
            return 3
        else:
            return 4

    def FMScore(x, p, d):
        if x <= d[p][0.25]:
            return 4
        elif x <= d[p][0.50]:
            return 3
        elif x <= d[p][0.75]:
            return 2
        else:
            return 1

    rfm_data['R_Quartile'] = rfm_data['Recency'].apply(RScore, args=('Recency', quartiles))
    rfm_data['F_Quartile'] = rfm_data['Frequency'].apply(FMScore, args=('Frequency', quartiles))
    rfm_data['M_Quartile'] = rfm_data['Monetary'].apply(FMScore, args=('Monetary', quartiles))

    # Combine RFM scores
    rfm_data['RFM_Score'] = rfm_data['R_Quartile'].map(str) + rfm_data['F_Quartile'].map(str) + rfm_data[
        'M_Quartile'].map(str)

    # Segmentation labels (customize as needed)
    segmentation_map = {
        '111': 'Best Customers',
        '411': 'New Customers',
        '444': 'Lost Cheap Customers',
        # Add more segments as needed
    }
    rfm_data['Segment'] = rfm_data['RFM_Score'].map(segmentation_map)

    return rfm_data


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
            st.download_button(label="Download RFM Data", data=segmented_data.to_csv(index=False),
                               file_name='rfm_analysis.csv', mime='text/csv')


if __name__ == "__main__":
    main()
