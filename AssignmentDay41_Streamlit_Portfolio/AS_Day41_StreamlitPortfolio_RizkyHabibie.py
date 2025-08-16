import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
from typing import Tuple

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from pathlib import Path

st.set_page_config(page_title="E-Commerce EDA Workflow", layout="wide")

GH_USERNAME = "rfih"   
DISPLAY_NAME = "Rizky Febri Ibra Habibie"  
TAGLINE = "Data • PM • Manufacturing"      

st.sidebar.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
      <img src="https://github.com/{GH_USERNAME}.png" width="44" height="44" style="border-radius:50%;object-fit:cover;border:1px solid #e6e6e6"/>
      <div style="line-height:1.2">
        <div style="font-weight:600">{DISPLAY_NAME if DISPLAY_NAME else GH_USERNAME}</div>
        <a href="https://github.com/{GH_USERNAME}" target="_blank" style="text-decoration:none;color:#4c8bf5;">
          github.com/{GH_USERNAME}
        </a><br/>
        <span style="font-size:12px;color:#666;">{TAGLINE}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()

#Data Loading
@st.cache_data
def load_data() -> pd.DataFrame:
    # 1) Try multiple local paths
    here = Path(__file__).resolve().parent
    candidates = [
        here / "data" / "ecommerce.csv",          # same folder /data
        here / "ecommerce.csv",                   # same folder
        here.parent / "data" / "ecommerce.csv",   # repo root /data
        here.parent / "ecommerce.csv",            # repo root
        Path.cwd() / "data" / "ecommerce.csv",    # CWD /data
        Path.cwd() / "ecommerce.csv",             # CWD
    ]
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p, encoding="ISO-8859-1")
            break
    else:
        # 2) Allow manual upload as a fallback (so you can still demo on Cloud)
        st.warning(
            "Could not find **ecommerce.csv** in the repository.\n\n"
            "Please upload the file here, or add it to one of these paths:\n"
            + "\n".join(f"- `{str(p)}`" for p in candidates)
        )
        uploaded = st.file_uploader("Upload ecommerce.csv", type=["csv"], key="csv_upload")
        if uploaded is None:
            st.stop()
        df = pd.read_csv(uploaded, encoding="ISO-8859-1")

    # Normalize columns & types (unchanged from your pipeline)
    df.columns = [c.strip() for c in df.columns]
    df["InvoiceDate"] = pd.to_datetime(df.get("InvoiceDate"), errors="coerce")
    df["Quantity"]    = pd.to_numeric(df.get("Quantity"), errors="coerce")
    df["UnitPrice"]   = pd.to_numeric(df.get("UnitPrice"), errors="coerce")
    if "Country" not in df.columns:    df["Country"] = "Unknown"
    if "Description" not in df.columns: df["Description"] = "Unknown Product"
    if "InvoiceNo" not in df.columns:   df["InvoiceNo"] = np.arange(len(df))
    if "CustomerID" not in df.columns:  df["CustomerID"] = np.nan

    df["TotalPrice"] = (df["Quantity"] * df["UnitPrice"]).fillna(0)
    df = df.dropna(subset=["InvoiceDate"])
    return df

df_raw = load_data()

def outlier_mask_iqr(s: pd.Series, k: float = 1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    mask = ~s.between(lower, upper)
    return mask, lower, upper

def outlier_mask_zscore(s: pd.Series, z: float = 3.0):
    mu, sd = s.mean(), s.std(ddof=0)
    if not sd or np.isnan(sd):
        return pd.Series(False, index=s.index), mu - z * 0, mu + z * 0
    zscores = (s - mu) / sd
    return (zscores.abs() > z), mu - z * sd, mu + z * sd

def clean_data(
    df: pd.DataFrame,
    drop_missing_customer: bool,
    remove_nonpositive: bool,
    drop_dupes: bool,
    outlier_method: str,
    iqr_k: float,
    z_thresh: float,
    cols_for_outliers: Tuple[str, ...],
    drop_outliers: bool,
):
    dfx = df.copy()

    issues = {
        "missing_total": int(dfx.isnull().sum().sum()),
        "duplicates_total": int(dfx.duplicated().sum()),
        "nonpositive_qty": int((dfx["Quantity"] <= 0).sum()),
        "nonpositive_price": int((dfx["UnitPrice"] <= 0).sum()),
        "missing_customerid": int(dfx["CustomerID"].isna().sum()) if "CustomerID" in dfx.columns else None,
    }

    outliers = {}
    combined = pd.Series(False, index=dfx.index)
    for col in cols_for_outliers:
        if col not in dfx.columns:
            outliers[col] = {"count": None, "lower": None, "upper": None}
            continue
        series = dfx[col].astype(float)
        if outlier_method == "IQR":
            mask, lower, upper = outlier_mask_iqr(series.dropna(), k=iqr_k)
        else:
            mask, lower, upper = outlier_mask_zscore(series.dropna(), z=z_thresh)
        mask = mask.reindex(dfx.index, fill_value=False)
        outliers[col] = {"count": int(mask.sum()), "lower": lower, "upper": upper}
        combined |= mask

    if drop_missing_customer and "CustomerID" in dfx.columns:
        dfx = dfx.dropna(subset=["CustomerID"])
    if remove_nonpositive:
        dfx = dfx[(dfx["Quantity"] > 0) & (dfx["UnitPrice"] > 0)]
    if drop_dupes:
        dfx = dfx.drop_duplicates()
    if drop_outliers:
        dfx = dfx.loc[~combined]

    dfx["TotalPrice"] = (dfx["Quantity"] * dfx["UnitPrice"]).fillna(0)
    return dfx, issues, outliers

def coerce_date_range(date_input_val, min_dt, max_dt):
    if isinstance(date_input_val, tuple) and len(date_input_val) == 2:
        d1, d2 = date_input_val
    else:
        d1 = d2 = date_input_val
    d1 = d1 or min_dt
    d2 = d2 or max_dt
    start_dt = datetime.combine(d1, datetime.min.time())
    end_dt = datetime.combine(d2, datetime.max.time())
    return start_dt, end_dt

#Layout
st.markdown("""
<h1 style="margin:0;">🛒 E-Commerce EDA Workflow</h1>
<p style="color:#666;margin:4px 0 0;">Data Cleaning • Dashboard • RFM • Multivariate</p>
""", unsafe_allow_html=True)

DATASET_NAME = "E-Commerce Transactions (ecommerce.csv)"
PROGRAM = "Dibimbing.id — Data Science & Data Analysis Bootcamp"
COHORT = "March–November"

has_date = "InvoiceDate" in df_raw.columns and not df_raw["InvoiceDate"].isna().all()
date_min = df_raw["InvoiceDate"].min().date() if has_date else None
date_max = df_raw["InvoiceDate"].max().date() if has_date else None
countries = int(df_raw["Country"].nunique()) if "Country" in df_raw.columns else None
customers = int(df_raw["CustomerID"].nunique()) if "CustomerID" in df_raw.columns else None

facts = [
    f"- **Shape:** {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns",
    f"- **Date range:** {date_min} → {date_max}" if has_date else None,
    f"- **Countries:** {countries}" if countries is not None else None,
    f"- **Customers:** {customers}" if customers is not None else None,
]
facts_md = "\n".join([x for x in facts if x])

intro_md = f"""
**Portfolio Project** — *{DATASET_NAME}*  
This app is one of my portfolio projects from **{PROGRAM} ({COHORT})**.

It demonstrates an end-to-end EDA workflow:
- **Data Cleaning:** missing values, duplicates, non-positive checks, and **outlier handling (IQR/Z-score)** with *before vs after* visuals.
- **Analysis Result:** interactive dashboard (filters, KPIs, revenue charts), **RFM segmentation**, and **PCA + KMeans** multivariate analysis.

**Dataset Facts**  
{facts_md}

**Tech Stack:** Streamlit · pandas · matplotlib/seaborn · scikit-learn  
**Last updated:** {datetime.today().date()}
"""

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    st.info(intro_md)
    st.button("Hide introduction", key="hide_intro_btn",
              on_click=lambda: st.session_state.update(show_intro=False))

st.divider()

with st.sidebar.expander("ℹ️ About this app", expanded=False):
    st.markdown(
        """
- EDA workflow: **Cleaning → Dashboard → RFM → Multivariate**
- Uses cleaned data for analysis tabs
        """
    )

st.sidebar.markdown("# Navigation")
tab_clean, tab_analysis = st.tabs(["🧹 Data Cleaning", "📊 Analysis Result"])

# TAB 1: DATA CLEANING
with tab_clean:
    st.title("Data Cleaning (Original vs Cleaned)")

    st.sidebar.header("Cleaning Controls")
    drop_missing_customer = st.sidebar.checkbox(
        "Drop rows with missing CustomerID", value=True, key="clean_drop_missing_customer"
    )
    remove_nonpositive = st.sidebar.checkbox(
        "Remove non-positive Quantity/UnitPrice", value=True, key="clean_remove_nonpositive"
    )
    drop_dupes = st.sidebar.checkbox("Drop duplicates", value=True, key="clean_drop_dupes")

    st.sidebar.subheader("Outlier Handling")
    outlier_method = st.sidebar.selectbox("Method", ["IQR", "Z-score"], index=0, key="clean_outlier_method")
    iqr_k = st.sidebar.slider("IQR k", 1.0, 3.0, 1.5, 0.1, key="clean_iqr_k")
    z_thresh = st.sidebar.slider("Z-score threshold", 2.0, 5.0, 3.0, 0.1, key="clean_z_thresh")
    cols_for_outliers = st.sidebar.multiselect(
        "Columns for outlier check",
        options=[c for c in ["Quantity", "UnitPrice"] if c in df_raw.columns],
        default=[c for c in ["Quantity", "UnitPrice"] if c in df_raw.columns],
        key="clean_cols_for_outliers",
    )
    drop_outliers = st.sidebar.checkbox("Remove outliers", value=True, key="clean_drop_outliers")

    st.sidebar.divider()

    st.sidebar.subheader("Viewing Filters (for previews)")
    min_dt = df_raw["InvoiceDate"].min().date()
    max_dt = df_raw["InvoiceDate"].max().date()
    date_range_clean = st.sidebar.date_input(
        "Date Range",
        value=(min_dt, max_dt),
        min_value=min_dt, max_value=max_dt,
        key="clean_date_range"
    )
    view_start, view_end = coerce_date_range(date_range_clean, min_dt, max_dt)

    countries_view = ["(All)"] + sorted(df_raw["Country"].dropna().unique().tolist())
    country_sel = st.sidebar.selectbox("Country (preview)", countries_view, index=0, key="clean_country_preview")

    df_clean, issues, outliers = clean_data(
        df_raw,
        drop_missing_customer=drop_missing_customer,
        remove_nonpositive=remove_nonpositive,
        drop_dupes=drop_dupes,
        outlier_method=outlier_method,
        iqr_k=iqr_k,
        z_thresh=z_thresh,
        cols_for_outliers=tuple(cols_for_outliers),
        drop_outliers=drop_outliers,
    )

    def apply_view_filters(dfin: pd.DataFrame, start_dt: datetime, end_dt: datetime, country: str):
        mask = dfin["InvoiceDate"].between(start_dt, end_dt)
        if country != "(All)":
            mask &= dfin["Country"] == country
        return dfin.loc[mask]

    raw_view = apply_view_filters(df_raw, view_start, view_end, country_sel)
    clean_view = apply_view_filters(df_clean, view_start, view_end, country_sel)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Raw Rows", f"{len(df_raw):,}")
    m2.metric("Clean Rows", f"{len(df_clean):,}")
    m3.metric("Missing Values (raw)", f"{issues['missing_total']:,}")
    m4.metric("Duplicates (raw)", f"{issues['duplicates_total']:,}")

    st.markdown("#### Missing Values per Column (Raw)")
    st.write(df_raw.isnull().sum())

    st.markdown("#### Non-positive Values (Raw)")
    st.write({"Quantity ≤ 0": issues["nonpositive_qty"], "UnitPrice ≤ 0": issues["nonpositive_price"]})

    st.markdown("### 📌 Outlier Analysis (Raw)")
    out_df = []
    for col, info in outliers.items():
        out_df.append({
            "Column": col,
            "Outlier Count (raw)": info["count"],
            "Lower Bound": info["lower"],
            "Upper Bound": info["upper"],
            "Method": outlier_method,
            "Param": f"k={iqr_k}" if outlier_method == "IQR" else f"z={z_thresh}",
        })
    st.dataframe(pd.DataFrame(out_df), use_container_width=True)

    st.divider()
    st.subheader("🔎 Data Preview — Before vs After (same filters)")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Before (Raw)**")
        st.dataframe(raw_view.head(25), use_container_width=True)
    with c2:
        st.markdown("**After (Cleaned)**")
        st.dataframe(clean_view.head(25), use_container_width=True)

    st.subheader("📊 Distributions — Before vs After")
    fig1, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(raw_view["Quantity"].dropna(), kde=True, ax=ax[0])
    ax[0].set_title("Quantity (Before)")
    sns.histplot(clean_view["Quantity"].dropna(), kde=True, ax=ax[1])
    ax[1].set_title("Quantity (After)")
    st.pyplot(fig1, use_container_width=True)

    fig2, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(raw_view["UnitPrice"].dropna(), kde=True, ax=ax[0], color="tab:orange")
    ax[0].set_title("Unit Price (Before)")
    sns.histplot(clean_view["UnitPrice"].dropna(), kde=True, ax=ax[1], color="tab:orange")
    ax[1].set_title("Unit Price (After)")
    st.pyplot(fig2, use_container_width=True)

    st.subheader("📦 Boxplots — Before vs After")
    fig3, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(y=raw_view["Quantity"].dropna(), ax=ax[0])
    ax[0].set_title("Quantity (Before)")
    sns.boxplot(y=clean_view["Quantity"].dropna(), ax=ax[1])
    ax[1].set_title("Quantity (After)")
    st.pyplot(fig3, use_container_width=True)

    fig4, ax = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(y=raw_view["UnitPrice"].dropna(), ax=ax[0], color="tab:orange")
    ax[0].set_title("Unit Price (Before)")
    sns.boxplot(y=clean_view["UnitPrice"].dropna(), ax=ax[1], color="tab:orange")
    ax[1].set_title("Unit Price (After)")
    st.pyplot(fig4, use_container_width=True)

    st.divider()

# TAB 2: ANALYSIS RESULT
with tab_analysis:
    st.title("📊 Analysis Result")
    sub_dash, sub_rfm, sub_multi = st.tabs(["📺 Dashboard", "🧮 RFM", "🧪 Multivariate"])

    dfC = df_clean.copy()

    with sub_dash:
        st.sidebar.header("🔧 Filters (Dashboard)")
        sel_countries = st.sidebar.multiselect(
            "Country",
            ["(All)"] + sorted(dfC["Country"].dropna().unique().tolist()),
            default=["(All)"],
            key="dash_countries",
        )
        descriptions = dfC["Description"].dropna().value_counts().head(500).index.tolist()
        sel_products = st.sidebar.multiselect(
            "Product (top 500 by frequency)",
            ["(All)"] + descriptions,
            default=["(All)"],
            key="dash_products",
        )
        min_dt = dfC["InvoiceDate"].min().date()
        max_dt = dfC["InvoiceDate"].max().date()
        date_range_dash = st.sidebar.date_input(
            "Date Range",
            value=(min_dt, max_dt),
            min_value=min_dt, max_value=max_dt,
            key="dash_date_range",
        )
        start_dt, end_dt = coerce_date_range(date_range_dash, min_dt, max_dt)

        mask = dfC["InvoiceDate"].between(start_dt, end_dt)
        if sel_countries and "(All)" not in sel_countries:
            mask &= dfC["Country"].isin(sel_countries)
        if sel_products and "(All)" not in sel_products:
            mask &= dfC["Description"].isin(sel_products)
        filtered = dfC.loc[mask].copy()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue", f"${filtered['TotalPrice'].sum():,.2f}")
        k2.metric("Transactions", f"{filtered['InvoiceNo'].nunique():,}")
        k3.metric("Units Sold", f"{filtered['Quantity'].sum():,}")
        k4.metric("Unique Products", f"{filtered['Description'].nunique():,}")
        st.caption(f"Date Filter: **{start_dt.date()} → {end_dt.date()}** · Rows: **{len(filtered):,}**")

        st.divider()
        sns.set_theme(context="notebook")

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.subheader("🌍 Top Countries by Revenue")
            rev_by_country = (
                filtered.groupby("Country", dropna=False)["TotalPrice"]
                .sum().sort_values(ascending=False).head(15)
            )
            fig, ax = plt.subplots()
            rev_by_country.plot(kind="barh", ax=ax)
            ax.invert_yaxis()
            ax.set_xlabel("Revenue"); ax.set_ylabel("")
            st.pyplot(fig, use_container_width=True)

        with c2:
            st.subheader("🛒 Top Products by Quantity")
            top_prod = (
                filtered.groupby("Description", dropna=False)["Quantity"]
                .sum().sort_values(ascending=False).head(15)
            )
            fig, ax = plt.subplots()
            top_prod.plot(kind="barh", ax=ax)
            ax.invert_yaxis()
            ax.set_xlabel("Units Sold"); ax.set_ylabel("")
            st.pyplot(fig, use_container_width=True)

        st.divider()
        c3, c4 = st.columns(2, gap="large")
        with c3:
            st.subheader("📈 Daily Revenue")
            daily = filtered.set_index("InvoiceDate").resample("D")["TotalPrice"].sum().fillna(0)
            fig, ax = plt.subplots()
            daily.plot(ax=ax)
            ax.set_ylabel("Revenue"); ax.set_xlabel("")
            st.pyplot(fig, use_container_width=True)

        with c4:
            st.subheader("💲Quantity & Unit Price Distributions")
            fig = plt.figure(figsize=(8, 5))
            ax1 = plt.subplot(2, 1, 1)
            sns.histplot(filtered["Quantity"], kde=True, ax=ax1); ax1.set_title("Quantity Distribution")
            ax2 = plt.subplot(2, 1, 2)
            sns.histplot(filtered["UnitPrice"], kde=True, ax=ax2); ax2.set_title("Unit Price Distribution")
            plt.tight_layout(); st.pyplot(fig, use_container_width=True)

        st.divider()
        st.subheader("🧾 Filtered Data")
        st.dataframe(filtered.head(50), use_container_width=True)

    #SUBTAB RFM 
    with sub_rfm:
        st.subheader("🧮 RFM Segmentation (Customer-level)")
        if dfC["CustomerID"].isna().all():
            st.info("CustomerID is not available in this dataset, so RFM cannot be computed.")
        else:
            use_full = st.checkbox("Compute RFM on full cleaned dataset (ignore date filter)", value=True, key="rfm_full")
            min_dt_r, max_dt_r = dfC["InvoiceDate"].min().date(), dfC["InvoiceDate"].max().date()
            date_range_rfm = st.date_input(
                "RFM Date Range (if not full)",
                value=(min_dt_r, max_dt_r),
                min_value=min_dt_r, max_value=max_dt_r,
                key="rfm_date_range",
            )
            start_rfm, end_rfm = coerce_date_range(date_range_rfm, min_dt_r, max_dt_r)

            df_r = dfC.copy()
            if not use_full:
                df_r = df_r[df_r["InvoiceDate"].between(start_rfm, end_rfm)]

            ref_date = df_r["InvoiceDate"].max().normalize()
            tx = df_r.dropna(subset=["CustomerID"]).copy()
            tx["CustomerID"] = tx["CustomerID"].astype(str)

            r = tx.groupby("CustomerID")["InvoiceDate"].max().apply(lambda d: (ref_date - d.normalize()).days)
            f = tx.groupby("CustomerID")["InvoiceNo"].nunique()
            m = tx.groupby("CustomerID")["TotalPrice"].sum()

            rfm = pd.DataFrame({"Recency": r, "Frequency": f, "Monetary": m}).reset_index()

            def qscore(s, q=5, reverse=False):
                try:
                    cats = pd.qcut(s.rank(method="first"), q, labels=False, duplicates="drop") + 1
                except Exception:
                    cats = pd.Series(1, index=s.index)
                if reverse:
                    cats = q + 1 - cats
                return cats

            rfm["R_Score"] = qscore(rfm["Recency"], q=5, reverse=True)
            rfm["F_Score"] = qscore(rfm["Frequency"], q=5, reverse=False)
            rfm["M_Score"] = qscore(rfm["Monetary"], q=5, reverse=False)
            rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Customers", f"{rfm.shape[0]:,}")
            k2.metric("Avg Recency (days)", f"{rfm['Recency'].mean():.1f}")
            k3.metric("Median Frequency", f"{rfm['Frequency'].median():.0f}")
            k4.metric("Total Monetary", f"${rfm['Monetary'].sum():,.2f}")

            st.markdown("#### Top Customers by Monetary")
            top_m = rfm.sort_values("Monetary", ascending=False).head(15)
            fig, ax = plt.subplots()
            sns.barplot(y="CustomerID", x="Monetary", data=top_m, ax=ax)
            ax.set_ylabel(""); ax.set_title("Top 15 Customers (Monetary)")
            st.pyplot(fig, use_container_width=True)

            st.markdown("#### Frequency vs Monetary (colored by R score)")
            fig, ax = plt.subplots()
            sc = ax.scatter(rfm["Frequency"], rfm["Monetary"], c=rfm["R_Score"], alpha=0.7)
            ax.set_xlabel("Frequency"); ax.set_ylabel("Monetary")
            cbar = plt.colorbar(sc); cbar.set_label("R_Score (higher=more recent)")
            st.pyplot(fig, use_container_width=True)

            st.markdown("#### RFM Table (sample)")
            st.dataframe(rfm.sort_values("RFM_Score", ascending=False).head(50), use_container_width=True)

    #SUBTAB MULTIVARIATE 
    with sub_multi:
        st.subheader(" Multivariate Analysis (Customer aggregates + Clusters)")

        if dfC.empty:
            st.info("No rows available after cleaning/filters. Relax the cleaning options or broaden the date range.")
        else:
            try:
                from sklearn.preprocessing import StandardScaler
                from sklearn.decomposition import PCA
                from sklearn.cluster import KMeans
                sklearn_ok = True
            except Exception:
                sklearn_ok = False

            if not sklearn_ok:
                st.error(
                    "scikit-learn is required for PCA & KMeans.\n"
                    "Install locally with: `pip install scikit-learn` (or `conda install scikit-learn`)."
                )
            else:
                if ("CustomerID" not in dfC.columns) or dfC["CustomerID"].isna().all():
                    st.info("CustomerID not available — running transaction-level multivariate features.")

                    feats_tx = dfC[["Quantity", "UnitPrice", "TotalPrice"]].copy()
                    feats_tx = feats_tx.replace([np.inf, -np.inf], np.nan).dropna()
                    if feats_tx.empty:
                        st.warning("No numeric rows available for transactions after NaN/Inf removal.")
                    else:
                        max_rows = int(min(10000, len(feats_tx)))
                        sample_n = st.slider(
                            "Sample rows (transactions)", min_value=300, max_value=max_rows,
                            value=min(1500, max_rows), step=100, key="ml_sample_tx"
                        )
                        feats_tx = feats_tx.sample(sample_n, random_state=42)

                        st.markdown("#### Correlation Heatmap (transactions)")
                        corr_tx = feats_tx.corr(numeric_only=True)
                        fig, ax = plt.subplots()
                        sns.heatmap(corr_tx, annot=True, cmap="coolwarm", ax=ax)
                        st.pyplot(fig, use_container_width=True)

                        scaler = StandardScaler()
                        Xs = scaler.fit_transform(feats_tx)
                        pca = PCA(n_components=2, random_state=42)
                        PCs = pca.fit_transform(Xs)
                        evr = pca.explained_variance_ratio_

                        k = st.slider("KMeans clusters (k)", 2, 8, 3, 1, key="ml_k_tx")
                        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(PCs)
                        labs = km.labels_

                        st.markdown(f"Explained variance (PC1, PC2): **{evr[0]:.2%}**, **{evr[1]:.2%}**")
                        fig, ax = plt.subplots()
                        sc = ax.scatter(PCs[:, 0], PCs[:, 1], c=labs, alpha=0.7)
                        ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.set_title("PCA (transactions) with KMeans")
                        st.pyplot(fig, use_container_width=True)

                else:
                    use_full_ml = st.checkbox(
                        "Use full cleaned dataset for multivariate (ignore date filter)", True, key="ml_full"
                    )
                    min_dt_m, max_dt_m = dfC["InvoiceDate"].min().date(), dfC["InvoiceDate"].max().date()
                    date_range_ml = st.date_input(
                        "Date Range (if not full)", value=(min_dt_m, max_dt_m),
                        min_value=min_dt_m, max_value=max_dt_m, key="ml_date_range",
                    )
                    start_ml, end_ml = coerce_date_range(date_range_ml, min_dt_m, max_dt_m)

                    base = dfC.copy()
                    if not use_full_ml:
                        base = base[base["InvoiceDate"].between(start_ml, end_ml)]

                    base = base.dropna(subset=["CustomerID"]).copy()
                    if base.empty:
                        st.warning("No customers available in the selected date range after cleaning.")
                    else:
                        base["CustomerID"] = base["CustomerID"].astype(str)
                        last_date = base["InvoiceDate"].max().normalize()

                        agg = base.groupby("CustomerID").agg(
                            LastPurchase=("InvoiceDate", "max"),
                            Frequency=("InvoiceNo", "nunique"),
                            Monetary=("TotalPrice", "sum"),
                            TotalQty=("Quantity", "sum"),
                            AvgUnitPrice=("UnitPrice", "mean"),
                        ).reset_index()
                        agg["Recency"] = (last_date - agg["LastPurchase"].dt.normalize()).dt.days
                        agg.drop(columns=["LastPurchase"], inplace=True)

                        if len(agg) < 5:
                            st.warning("Not enough customers to run PCA/KMeans (need at least 5). Try broadening filters.")
                        else:
                            st.markdown("#### Correlation Heatmap (customer aggregates)")
                            corr_c = agg[["Recency","Frequency","Monetary","TotalQty","AvgUnitPrice"]].corr(numeric_only=True)
                            fig, ax = plt.subplots()
                            sns.heatmap(corr_c, annot=True, cmap="coolwarm", ax=ax)
                            st.pyplot(fig, use_container_width=True)

                            feats = agg[["Recency","Frequency","Monetary","TotalQty","AvgUnitPrice"]].fillna(0)
                            scaler = StandardScaler()
                            Xs = scaler.fit_transform(feats)
                            pca = PCA(n_components=2, random_state=42)
                            PCs = pca.fit_transform(Xs)
                            evr = pca.explained_variance_ratio_

                            k = st.slider("KMeans clusters (k)", 2, 8, 3, 1, key="ml_k")
                            km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(PCs)
                            labs = km.labels_

                            st.markdown(f"Explained variance (PC1, PC2): **{evr[0]:.2%}**, **{evr[1]:.2%}**")
                            fig, ax = plt.subplots()
                            sc = ax.scatter(PCs[:, 0], PCs[:, 1], c=labs, alpha=0.8)
                            ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.set_title("PCA (customers) with KMeans")
                            st.pyplot(fig, use_container_width=True)

                            show_tbl = agg.copy()
                            show_tbl["Cluster"] = labs
                            st.markdown("#### Sample of Clustered Customers")
                            st.dataframe(show_tbl.sort_values("Cluster").head(50), use_container_width=True)
                            

