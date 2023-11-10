import streamlit as st
import pandas as pd
from datetime import datetime

def load_data(uploaded_file):
    for encoding in ['utf-8', 'ISO-8859-1', 'latin1']:
        try:
            return pd.read_csv(uploaded_file, encoding=encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("Unable to find the correct encoding. Please check your file.")

st.title('RFM Analysis Tool')

uploaded_file = st.file_uploader("Upload your CSV", type="csv")
if uploaded_file is not None:
    try:
        data = load_data(uploaded_file)
        st.write('Raw data')
        st.write(data)

        if st.button('Analyze'):
            # User input for columns
            id_col = st.selectbox('Select Customer ID Column', data.columns)
            date_col = st.selectbox('Select Invoice Date Column', data.columns)
            money_col = st.selectbox('Select Monetary Value Column', data.columns)

            # Data Validation
            if not pd.api.types.is_numeric_dtype(data[money_col]):
                st.error("Selected monetary value column is not numeric. Please choose a correct column.")
                st.stop()

            try:
                data[date_col] = pd.to_datetime(data[date_col])
            except Exception as e:
                st.error(f"Error converting date column: {e}")
                st.stop()

            # RFM analysis
            latest_date = data[date_col].max() + pd.DateOffset(days=1)
            rfm = data.groupby(id_col).agg({
                date_col: lambda x: (latest_date - x.max()).days,
                id_col: 'count',
                money_col: 'sum'
            }).rename(columns={date_col: 'Recency', id_col: 'Frequency', money_col: 'MonetaryValue'})

            rfm['R'] = pd.qcut(rfm['Recency'], 4, ['1','2','3','4'], duplicates='drop')
            rfm['F'] = pd.qcut(rfm['Frequency'], 4, ['4','3','2','1'], duplicates='drop')
            rfm['M'] = pd.qcut(rfm['MonetaryValue'], 4, ['4','3','2','1'], duplicates='drop')
            rfm['RFM_Segment'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
            rfm['RFM_Score'] = rfm[['R', 'F', 'M']].sum(axis=1)

            st.write('RFM Analysis')
            st.write(rfm)
            st.bar_chart(rfm['RFM_Segment'].value_counts())

    except UnicodeDecodeError as e:
        st.error(f'Error reading file: {e}')
else:
    st.info('Awaiting CSV file to be uploaded.')
