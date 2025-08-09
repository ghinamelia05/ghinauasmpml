import streamlit as st
import pandas as pd

# Konfigurasi
REQUIRED_COLUMNS = ['Timestamp', 'Status', 'Amount (INR)', 'Sender UPI ID']

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("transactions.csv")
        
        # Validasi kolom
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"Kolom wajib tidak ditemukan: {missing_cols}")
            return None
            
        # Konversi tipe data
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Amount (INR)'] = pd.to_numeric(df['Amount (INR)'], errors='coerce')
        df['Bank'] = df['Sender UPI ID'].str.extract(r'@(.+)$')
        
        return df.dropna(subset=['Bank', 'Amount (INR)'])
        
    except FileNotFoundError:
        st.error("File 'transactions.csv' tidak ditemukan.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    return None

# Main App
def main():
    st.title("Analisis Transaksi UPI")
    df = load_data()
    
    if df is not None:
        if df.empty:
            st.warning("Data transaksi kosong!")
            return
            
        # Filter Tanggal
        min_date = df['Timestamp'].min().date()
        max_date = df['Timestamp'].max().date()
        date_range = st.date_input("Rentang Tanggal", [min_date, max_date])
        
        # Filter Amount
        min_amount = st.number_input("Minimum Amount (INR)", 
                                   min_value=0, 
                                   value=0,
                                   step=100)
        
        # Apply filters
        filtered_df = df[
            (df['Timestamp'].dt.date >= date_range[0]) & 
            (df['Timestamp'].dt.date <= date_range[1]) &
            (df['Amount (INR)'] >= min_amount)
        ]
        
        # Tampilkan Statistik
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Transaksi", len(filtered_df))
            st.metric("Transaksi Sukses", filtered_df[filtered_df['Status']=='SUCCESS'].shape[0])
        with col2:
            st.metric("Transaksi Gagal", filtered_df[filtered_df['Status']=='FAILED'].shape[0])
            st.metric("Rata-rata Nilai", f"₹{filtered_df['Amount (INR)'].mean():.2f}")
        
        # Visualisasi
        st.subheader("Distribusi Status Transaksi")
        st.bar_chart(filtered_df['Status'].value_counts())
        
        # Analisis Bank
        st.subheader("Analisis Bank")
        bank_stats = filtered_df.groupby('Bank')['Status'].value_counts().unstack()
        bank_stats['Total'] = bank_stats.sum(axis=1)
        st.bar_chart(bank_stats.sort_values('Total', ascending=False).drop('Total', axis=1))

if __name__ == "__main__":
    main()