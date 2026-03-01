import streamlit as st
import pandas as pd
import io
import re
from collections import Counter
from textblob import TextBlob

st.set_page_config(page_title="Retail & Customer Intelligence", layout="wide")
st.title("📊 Retail & Customer Intelligence Dashboard")

# =============================
# SENTIMENT FUNCTION
# =============================
def get_sentiment(text):
    score = TextBlob(str(text)).sentiment.polarity
    if score > 0.1:
        return "Positive"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"

# =============================
# STOPWORDS (REMOVE USELESS WORDS)
# =============================
stopwords = {
    "the","and","that","this","with","have","they","them","from",
    "amazon","were","been","being","there","their","about",
    "would","could","should","after","before","when","where",
    "your","very","really","also","just","into","over","more",
    "will","than","then","because","while","what","which"
}

def extract_keywords(text_series):
    words = []
    for text in text_series:
        tokens = re.findall(r"\b[a-z]{4,}\b", str(text).lower())
        meaningful = [w for w in tokens if w not in stopwords]
        words.extend(meaningful)
    return Counter(words).most_common(10)

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

        df["sales"] = df["sales"] * df["quantity"]

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

    tab1, tab2, tab3 = st.tabs(
        ["🛍 Retail & Segmentation", "🔮 Churn", "🧠 Sentiment"]
    )

    # ======================================
    # TAB 1 — RETAIL + SEGMENTATION
    # ======================================
    with tab1:

        st.header("Retail Analytics")

        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue", f"{df['sales'].sum():,.0f}")
        c2.metric("Orders", df["order_id"].nunique())
        c3.metric("Customers", df["customer_id"].nunique())

        st.subheader("Top Products")
        top_products = (
            df.groupby("product")["sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(top_products)

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

        st.dataframe(customer_df.head(), use_container_width=True)

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

    # ======================================
    # TAB 3 — SENTIMENT
    # ======================================
    with tab3:

        st.header("Amazon Review Insights")

        uploaded_reviews = st.file_uploader(
            "Upload Amazon Reviews CSV",
            type=["csv"],
            key="reviews"
        )

        if uploaded_reviews is not None:
            reviews = pd.read_csv(
                uploaded_reviews,
                encoding="ISO-8859-1",
                on_bad_lines="skip",
                engine="python"
            )

            if "Review Text" not in reviews.columns:
                st.error("CSV must contain 'Review Text'")
            else:
                reviews["sentiment"] = reviews["Review Text"].apply(get_sentiment)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Reviews", len(reviews))
                c2.metric("Positive", (reviews["sentiment"]=="Positive").sum())
                c3.metric("Negative", (reviews["sentiment"]=="Negative").sum())
                c4.metric("Neutral", (reviews["sentiment"]=="Neutral").sum())

                st.subheader("🔴 Top Customer Pain Points")
                neg_reviews = reviews[reviews["sentiment"]=="Negative"]["Review Text"].dropna()
                pain = extract_keywords(neg_reviews)
                pain_df = pd.DataFrame(pain, columns=["Issue","Mentions"])
                st.dataframe(pain_df, use_container_width=True)

                st.subheader("🟢 What Customers Love")
                pos_reviews = reviews[reviews["sentiment"]=="Positive"]["Review Text"].dropna()
                love = extract_keywords(pos_reviews)
                love_df = pd.DataFrame(love, columns=["Aspect","Mentions"])
                st.dataframe(love_df, use_container_width=True)

                st.subheader("Critical Reviews")
                worst = reviews[reviews["sentiment"]=="Negative"][["Review Text"]].head(10)
                st.dataframe(worst, use_container_width=True)

else:
    st.info("Upload CSV and apply mapping to start analysis.")