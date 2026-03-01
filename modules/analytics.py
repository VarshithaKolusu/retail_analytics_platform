import pandas as pd
import os
import matplotlib.pyplot as plt

def run_analytics():

    file_path = "data/processed/cleaned_sales.csv"

    if not os.path.exists(file_path):
        print("❌ Cleaned dataset not found. Run data_cleaning.py first.")
        return

    df = pd.read_csv(file_path)

    print("\n📊 RETAIL INTELLIGENCE REPORT")
    print("================================")

    # ------------------------------
    # BASIC KPIs
    # ------------------------------
    if "sales" in df.columns:
        total_revenue = df["sales"].sum()
        print(f"💰 Total Revenue: {total_revenue:,.2f}")

    if "quantity" in df.columns:
        total_units = df["quantity"].sum()
        print(f"📦 Total Units Sold: {total_units}")

    if "profit" in df.columns:
        total_profit = df["profit"].sum()
        print(f"📈 Total Profit: {total_profit:,.2f}")

    # ------------------------------
    # MONTHLY REVENUE TREND
    # ------------------------------
    if "date" in df.columns and "sales" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = df["date"].dt.to_period("M")

        monthly_revenue = df.groupby("month")["sales"].sum()

        plt.figure()
        monthly_revenue.plot()
        plt.title("Monthly Revenue Trend")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # ------------------------------
    # TOP PRODUCTS
    # ------------------------------
    if "item" in df.columns:
        top_products = (
            df.groupby("item")["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        plt.figure()
        top_products.plot(kind="bar")
        plt.title("Top 5 Products by Quantity")
        plt.xlabel("Product")
        plt.ylabel("Units Sold")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # ------------------------------
    # REVENUE BY STORE
    # ------------------------------
    if "store" in df.columns and "sales" in df.columns:
        store_revenue = (
            df.groupby("store")["sales"]
            .sum()
            .sort_values(ascending=False)
        )

        plt.figure()
        store_revenue.plot(kind="bar")
        plt.title("Revenue by Store")
        plt.xlabel("Store")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    run_analytics()