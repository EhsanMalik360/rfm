import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dateutil import parser
from datetime import datetime


# Function to calculate RFM metrics
# Function to calculate RFM metrics
def calculate_rfm(data, date_col, id_col, spend_col):
    # Attempt to parse the date column into a standard format
    data[date_col] = data[date_col].apply(lambda x: parser.parse(x, fuzzy=True))

    # Calculate Recency, Frequency, and Monetary metrics
    max_date = data[date_col].max() + pd.to_timedelta(1, unit='d')
    rfm = data.groupby(id_col).agg({
        date_col: lambda x: (max_date - x.max()).days,
        spend_col: 'sum'
    }).rename(columns={date_col: 'Recency', spend_col: 'Monetary'})
    rfm['Frequency'] = data.groupby(id_col)[id_col].count()

    # Reset index to keep CustomerID in the DataFrame
    rfm.reset_index(inplace=True)

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

    def RScore(x, p, d): return 4 if x <= d[p][0.25] else 3 if x <= d[p][0.50] else 2 if x <= d[p][0.75] else 1
    def FMScore(x, p, d): return 1 if x <= d[p][0.25] else 2 if x <= d[p][0.50] else 3 if x <= d[p][0.75] else 4
    rfm_data['R_Quartile'] = rfm_data['Recency'].apply(RScore, args=('Recency', quartiles))
    rfm_data['F_Quartile'] = rfm_data['Frequency'].apply(FMScore, args=('Frequency', quartiles))
    rfm_data['M_Quartile'] = rfm_data['Monetary'].apply(FMScore, args=('Monetary', quartiles))

    # Combine RFM scores
    rfm_data['RFM_Score'] = rfm_data['R_Quartile'].map(str) + rfm_data['F_Quartile'].map(str) + rfm_data[
        'M_Quartile'].map(str)

    # Segmentation labels (customize as needed)
    rfm_data['RFM_Score'] = rfm_data['R_Quartile'].map(str) + rfm_data['F_Quartile'].map(str) + rfm_data['M_Quartile'].map(str)
    segmentation_map = {
        '111': 'Best Customers',
        '411': 'New Customers',
        '444': 'Lost Cheap Customers',
        '111': 'Best Customers', '411': 'New Customers', '444': 'Lost Cheap Customers',
        # Add more segments as needed
    }
    rfm_data['Segment'] = rfm_data['RFM_Score'].map(segmentation_map)

    return rfm_data

# Function to plot segment distribution
def plot_segment_distribution(segmented_data):
    segment_counts = segmented_data['Segment'].value_counts()
    plt.figure(figsize=(10, 6))
    segment_counts.plot(kind='bar')
    plt.title('Customer Distribution across RFM Segments')
    plt.xlabel('Segment')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45)
    return plt

# Streamlit app main function
def main():
    st.title("RFM Analyzer")

    # Option to use a sample dataset
    if st.checkbox('Use Sample Dataset'):
        # Load your sample dataset here
        # Replace 'path_to_sample_dataset.csv' with the path or URL to your sample dataset
        data = pd.read_csv('retail.csv')
    else:
        # File uploader for user's own data
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
        else:
            data = None

    st.write("Please use the standard format for Customer ID, Invoice Date and Total Spend from sample dataset for accurate RFM Analysis.")
    # Add a download button for the sample dataset
    with open('retail.csv', 'rb') as file:
        st.download_button(
            label="Download Sample Dataset",
            data=file,
            file_name='retail.csv',
            mime='text/csv'
        )


    if data is not None:
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
            # Plotting segment distribution
            st.write("Segment Distribution")
            fig = plot_segment_distribution(segmented_data)
            st.pyplot(fig)
            # Export button
            st.download_button(label="Download RFM Data", data=segmented_data.to_csv(index=False), file_name='rfm_analysis.csv', mime='text/csv')

if __name__ == "__main__":
    main()