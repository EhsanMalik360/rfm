import streamlit as st
import pandas as pd
from datetime import datetime


# Function to try multiple encodings
def load_data(uploaded_file):
    for encoding in ['utf-8', 'ISO-8859-1', 'latin1']:
        try:
            return pd.read_csv(uploaded_file, encoding=encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("Unable to find the correct encoding. Please check your file.")


# Set title of the app
st.title('RFM Analysis Tool')

# File uploader widget
uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    try:
        # Try loading the data with different encodings
        data = load_data(uploaded_file)

        # Display the dataframe
        st.write('Raw data')
        st.write(data)

        # User input for unique identifier, date, and monetary value columns
        id_col = st.selectbox('Select Customer ID Column', data.columns)
        date_col = st.selectbox('Select Invoice Date Column', data.columns)
        money_col = st.selectbox('Select Monetary Value Column', data.columns)

        # Process the data when 'Analyze' button is clicked
        if st.button('Analyze'):
            # Convert date column to datetime
            data[date_col] = pd.to_datetime(data[date_col])

            # Calculate Recency, Frequency, Monetary values for each customer
            latest_date = data[date_col].max() + pd.DateOffset(days=1)
            rfm = data.groupby(id_col).agg({
                date_col: lambda x: (latest_date - x.max()).days,
                id_col: 'count',
                money_col: 'sum'
            })

            # Rename the columns
            rfm.rename(columns={date_col: 'Recency',
                                id_col: 'Frequency',
                                money_col: 'MonetaryValue'}, inplace=True)


            # RFM scoring
            def get_qcut(series, labels, n_quantiles=4):
                unique_vals = series.nunique()
                if unique_vals < n_quantiles:
                    return pd.cut(series, bins=unique_vals, labels=labels[:unique_vals], duplicates='drop')
                else:
                    return pd.qcut(series, q=n_quantiles, labels=labels, duplicates='drop')


            #rfm['R'] = get_qcut(rfm['Recency'], ['1', '2', '3', '4'])
            #rfm['F'] = get_qcut(rfm['Frequency'], ['4', '3', '2', '1'])
            #rfm['M'] = get_qcut(rfm['MonetaryValue'], ['4', '3', '2', '1'])

            #rfm['RFM_Segment'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
            #rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)

            # Display RFM segmentation
            st.write('RFM Analysis')
            st.write(rfm)

            # Optional: Display RFM segments distribution
            st.bar_chart(rfm['RFM_Segment'].value_counts())
    except UnicodeDecodeError as e:
        st.error(f'Error reading file: {e}')
else:
    st.info('Awaiting CSV file to be uploaded.')
