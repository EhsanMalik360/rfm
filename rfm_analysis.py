import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to calculate RFM metrics
def calculate_rfm(data, date_col, id_col, spend_col):
    try:
        data[date_col] = pd.to_datetime(data[date_col])
    except Exception as e:
        st.error(f"Error converting Invoice Date column to datetime: {e}")
        return None

    max_date = data[date_col].max() + pd.to_timedelta(1, unit='d')
    rfm = data.groupby(id_col).agg({
        date_col: lambda x: (max_date - x.max()).days,
        spend_col: 'sum'
    }).rename(columns={date_col: 'Recency', spend_col: 'Monetary'})
    rfm['Frequency'] = data.groupby(id_col)[id_col].count()
    rfm.reset_index(inplace=True)
    return rfm

# Function to segment customers based on RFM scores
def segment_customers(rfm_data):
    quartiles = rfm_data.quantile(q=[0.25, 0.5, 0.75])
    def RScore(x, p, d): return 4 if x <= d[p][0.25] else 3 if x <= d[p][0.50] else 2 if x <= d[p][0.75] else 1
    def FMScore(x, p, d): return 1 if x <= d[p][0.25] else 2 if x <= d[p][0.50] else 3 if x <= d[p][0.75] else 4
    rfm_data['R_Quartile'] = rfm_data['Recency'].apply(RScore, args=('Recency', quartiles))
    rfm_data['F_Quartile'] = rfm_data['Frequency'].apply(FMScore, args=('Frequency', quartiles))
    rfm_data['M_Quartile'] = rfm_data['Monetary'].apply(FMScore, args=('Monetary', quartiles))
    rfm_data['RFM_Score'] = rfm_data['R_Quartile'].map(str) + rfm_data['F_Quartile'].map(str) + rfm_data['M_Quartile'].map(str)
    segmentation_map = {
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

# Function to check data types and convert if possible
def validate_data_types(data, date_col, id_col, spend_col):
    if not pd.api.types.is_numeric_dtype(data[spend_col]):
        try:
            data[spend_col] = pd.to_numeric(data[spend_col])
        except ValueError:
            return "Total Spend column should be numeric or convertible to numeric."

    if data[id_col].dtype != 'O':
        data[id_col] = data[id_col].astype(str)

    return None

# Streamlit app main function
def main():
    st.title("RFM Analysis App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        st.write("Select the columns for RFM analysis")
        id_col = st.selectbox("Select Customer ID Column", data.columns)
        date_col = st.selectbox("Select Invoice Date Column", data.columns)
        spend_col = st.selectbox("Select Total Spend Column", data.columns)

        if st.button("Calculate RFM"):
            error_message = validate_data_types(data, date_col, id_col, spend_col)
            if error_message:
                st.error(error_message)
            else:
                rfm_data = calculate_rfm(data, date_col, id_col, spend_col)
                if rfm_data is not None:
                    segmented_data = segment_customers(rfm_data)

                    st.write("RFM Analysis Results")
                    st.dataframe(segmented_data)

                    st.write("Segment Distribution")
                    fig = plot_segment_distribution(segmented_data)
                    st.pyplot(fig)

                    st.download_button(label="Download RFM Data",
                                       data=segmented_data.to_csv(index=False),
                                       file_name='rfm_analysis.csv',
                                       mime='text/csv')

                if __name__ == "__main__":
                    main()
