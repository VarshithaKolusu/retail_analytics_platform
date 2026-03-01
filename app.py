import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Retail & Customer Intelligence", layout="wide")
st.title("📊 Retail & Customer Intelligence Dashboard")

# =============================
# FILE UPLOAD
# =============================
uploaded_file = st.file_uploader("Upload Retail CSV", type=["csv"])

if uploaded_file is not None:

    raw_df = pd.read_csv(io.BytesIO(uploaded_file.read()), encoding="ISO-8859-1")
    st.success("CSV loaded successfully!")

    st.subheader("🛠 Map Your Columns")

    cols = raw_df.columns.tolist()

    c1, c2 = st.columns(2)

    with c1:
        order_col = st.selectbox("Order ID", cols)
        customer_col = st.selectbox("Customer ID", cols)
        sales_col = st.selectbox("Sales (Revenue)", cols)

    with c2:
        quantity_col = st.selectbox("Quantity", cols)
        date_col = st.selectbox("Date", cols)
        product_col = st.selectbox("Product", cols)

    apply_map = st.button("✅ Apply Mapping")

    if apply_map:

        df = raw_df.rename(columns={
            order_col: "order_id",
            customer_col: "customer_id",
            sales_col: "sales",
            quantity_col: "quantity",
            date_col: "date",
            product_col: "product"
        })

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

        # revenue = price × quantity
        df["sales"] = df["sales"] * df["quantity"]

        # clean
        df = df.dropna(subset=["customer_id", "sales", "quantity", "date"])
        df = df[df["quantity"] > 0]
        df = df[df["sales"] > 0]

        st.session_state["mapped_df"] = df
        st.success(f"✅ {len(df)} rows processed!")

# =============================
# AFTER MAPPING
# =============================
if "mapped_df" in st.session_state:

    df = st.session_state["mapped_df"]

    tab1, tab2 = st.tabs(["🛍 Retail & Segmentation", "🔮 Churn"])

    # ======================================
    # TAB 1 — RETAIL + SEGMENTATION
    # ======================================
    with tab1:

        st.header("Retail Analytics")

        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"{df['sales'].sum():,.0f}")
        c2.metric("Orders", df["order_id"].nunique())
        c3.metric("Customers", df["customer_id"].nunique())

        # ----------------------------
        # TOP PRODUCTS
        # ----------------------------
        st.subheader("Top Products")
        top_products = (
            df.groupby("product")["sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(top_products)

        # ----------------------------
        # IMPROVED MONTHLY TREND
        # ----------------------------
        st.subheader("Monthly Sales Trend")

        df["month"] = df["date"].dt.to_period("M").astype(str)

        monthly_sales = df.groupby("month").agg(
            revenue=("sales", "sum"),
            orders=("order_id", "nunique")
        ).reset_index()

        monthly_sales["avg_order_value"] = (
            monthly_sales["revenue"] / monthly_sales["orders"]
        )

        st.line_chart(
            monthly_sales.set_index("month")["avg_order_value"]
        )

        # =====================
        # CUSTOMER AGGREGATION
        # =====================
        st.subheader("Customer Aggregation")

        customer_df = df.groupby("customer_id").agg(
            total_sales=("sales", "sum"),
            frequency=("order_id", "count"),
            last_purchase=("date", "max"),
            first_purchase=("date", "min")
        ).reset_index()

        customer_df["tenure_days"] = (
            customer_df["last_purchase"] - customer_df["first_purchase"]
        ).dt.days

        max_date = df["date"].max()
        customer_df["inactive_days"] = (
            max_date - customer_df["last_purchase"]
        ).dt.days

        st.dataframe(customer_df.head())

        # =====================
        # BETTER SEGMENTATION
        # =====================
        st.subheader("Customer Segmentation")

        customer_df["segment"] = pd.qcut(
            customer_df["frequency"],
            3,
            labels=["Low Frequency", "Medium Frequency", "High Frequency"]
        )

        seg_counts = customer_df["segment"].value_counts()
        st.bar_chart(seg_counts)

    # ======================================
    # TAB 2 — CHURN
    # ======================================
    with tab2:

        st.header("Customer Churn Analysis")

        customer_df = df.groupby("customer_id").agg(
            total_sales=("sales", "sum"),
            frequency=("order_id", "count"),
            last_purchase=("date", "max"),
            first_purchase=("date", "min")
        ).reset_index()

        max_date = df["date"].max()
        customer_df["inactive_days"] = (
            max_date - customer_df["last_purchase"]
        ).dt.days

        customer_df["churn"] = (customer_df["inactive_days"] > 90).astype(int)

        customer_df["segment"] = pd.qcut(
            customer_df["frequency"],
            3,
            labels=["Low", "Medium", "High"]
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Customers", len(customer_df))
        c2.metric("Churn Rate %", f"{customer_df['churn'].mean()*100:.1f}")
        c3.metric("Avg Inactive Days", f"{customer_df['inactive_days'].mean():.0f}")

        st.subheader("Churn Distribution")
        st.bar_chart(customer_df["churn"].value_counts())

        st.subheader("Churn by Segment")
        churn_seg = customer_df.groupby("segment")["churn"].mean()*100
        st.bar_chart(churn_seg)

        st.subheader("Inactive Days vs Churn")
        inactive = customer_df.groupby("churn")["inactive_days"].mean()
        st.bar_chart(inactive)

else:
    st.info("Upload CSV and apply column mapping to start analysis.")