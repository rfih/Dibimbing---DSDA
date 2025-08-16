import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="E-Commerce EDA", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce.csv")
    return df

df = load_data()

# Sidebar
st.sidebar.header("📂 EDA Navigation")
section = st.sidebar.radio("Choose Section", ["Dataset Overview", "Visualizations"])

# Main Title
st.title("📊 E-Commerce Data Analysis Dashboard")

if section == "Dataset Overview":
    st.subheader("🔍 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📌 Data Information")
    st.markdown(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
    st.markdown("**Column Types:**")
    st.code(df.dtypes.astype(str).to_string())

    st.subheader("⚠️ Missing Values")
    st.write(df.isnull().sum())

    st.subheader("📈 Basic Statistics")
    st.write(df.describe())

elif section == "Visualizations":
    st.subheader("📦 Quantity Distribution")
    fig1, ax1 = plt.subplots()
    sns.histplot(df["Quantity"], kde=True, ax=ax1)
    ax1.set_title("Distribution of Quantity")
    st.pyplot(fig1)

    st.subheader("💸 Unit Price Distribution")
    fig2, ax2 = plt.subplots()
    sns.histplot(df["UnitPrice"], kde=True, color='orange', ax=ax2)
    ax2.set_title("Distribution of Unit Price")
    st.pyplot(fig2)

    st.subheader("🌍 Top 10 Countries by Revenue")
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    top_countries = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(10)

    fig3, ax3 = plt.subplots()
    sns.barplot(x=top_countries.values, y=top_countries.index, palette="viridis", ax=ax3)
    ax3.set_title("Top Countries by Revenue")
    st.pyplot(fig3)

    st.subheader("🛒 Top 10 Products by Quantity Sold")
    top_products = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)

    fig4, ax4 = plt.subplots()
    sns.barplot(x=top_products.values, y=top_products.index, palette="crest", ax=ax4)
    ax4.set_title("Top Products by Quantity")
    st.pyplot(fig4)

    st.subheader("📊 Correlation Heatmap")
    fig5, ax5 = plt.subplots()
    sns.heatmap(df[["Quantity", "UnitPrice", "TotalPrice"]].corr(), annot=True, cmap="coolwarm", ax=ax5)
    ax5.set_title("Correlation Matrix")
    st.pyplot(fig5)