import pandas as pd
import os

def clean_data():

    file_path = "data/raw_sales.csv"

    if not os.path.exists(file_path):
        print("❌ Dataset not found in data/ folder.")
        return

    df = pd.read_csv(file_path)

    if df.empty:
        print("❌ Dataset is empty.")
        return

    print("\n📌 Uploaded Dataset Columns:")
    print(list(df.columns))

    # ==============================
    # REQUIRED FIELDS
    # ==============================
    required_fields = {
        "quantity": None,
        "date": None
    }

    # ==============================
    # OPTIONAL FIELDS
    # ==============================
    optional_fields = {
        "order_id": None,
        "customer_id": None,
        "price": None,
        "cost": None
    }

    # ------------------------------
    # Map REQUIRED fields
    # ------------------------------
    print("\n🔎 Map REQUIRED fields:\n")

    for field in required_fields:
        user_input = input(f"Enter column name for '{field}': ").strip()

        if user_input not in df.columns:
            print(f"❌ Column '{user_input}' not found. This field is mandatory.")
            return

        required_fields[field] = user_input

    # ------------------------------
    # Map OPTIONAL fields
    # ------------------------------
    print("\n🔎 Map OPTIONAL fields (press Enter to skip):\n")

    for field in optional_fields:
        user_input = input(f"Enter column name for '{field}' (or press Enter to skip): ").strip()

        if user_input == "":
            continue

        if user_input not in df.columns:
            print(f"⚠️ Column '{user_input}' not found. Skipping.")
            continue

        optional_fields[field] = user_input

    # ------------------------------
    # Rename columns
    # ------------------------------
    rename_dict = {}

    for key, value in required_fields.items():
        rename_dict[value] = key

    for key, value in optional_fields.items():
        if value is not None:
            rename_dict[value] = key

    df = df.rename(columns=rename_dict)

    # ------------------------------
    # Convert data types
    # ------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    if "cost" in df.columns:
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

    # ------------------------------
    # Remove invalid rows
    # ------------------------------
    df = df.dropna(subset=["quantity", "date"])
    df = df[df["quantity"] > 0]

    # ------------------------------
    # Calculate Sales
    # ------------------------------
    if "price" in df.columns:
        df["sales"] = df["quantity"] * df["price"]
    else:
        print("⚠️ Price not provided. Sales cannot be calculated.")

    # ------------------------------
    # Calculate Profit
    # ------------------------------
    if "cost" in df.columns and "sales" in df.columns:
        df["profit"] = df["sales"] - df["cost"]

    # ------------------------------
    # Save cleaned data
    # ------------------------------
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/cleaned_sales.csv", index=False)

    print("\n✅ Data cleaned successfully!")
    print("📁 Saved to: data/processed/cleaned_sales.csv")


if __name__ == "__main__":
    clean_data()