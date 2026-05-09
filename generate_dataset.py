"""
generate_dataset.py
-------------------
Generates "Electronics Store Sales - Retail Analytics Dataset.csv"
with the same columns as the Supermart dataset:
  Order ID, Customer Name, Category, Sub Category, City,
  Order Date, Region, Sales, Discount, Profit, State
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ── seed for reproducibility ──────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_ROWS = 5000

# ── Indian city/state/region mapping ─────────────────────────────────────────
CITY_DATA = [
    # (City, State, Region)
    ("Mumbai",       "Maharashtra",    "West"),
    ("Pune",         "Maharashtra",    "West"),
    ("Nagpur",       "Maharashtra",    "West"),
    ("Ahmedabad",    "Gujarat",        "West"),
    ("Surat",        "Gujarat",        "West"),
    ("Vadodara",     "Gujarat",        "West"),
    ("Delhi",        "Delhi",          "North"),
    ("Noida",        "Uttar Pradesh",  "North"),
    ("Gurgaon",      "Haryana",        "North"),
    ("Jaipur",       "Rajasthan",      "North"),
    ("Lucknow",      "Uttar Pradesh",  "North"),
    ("Chandigarh",   "Punjab",         "North"),
    ("Amritsar",     "Punjab",         "North"),
    ("Bengaluru",    "Karnataka",      "South"),
    ("Chennai",      "Tamil Nadu",     "South"),
    ("Hyderabad",    "Telangana",      "South"),
    ("Coimbatore",   "Tamil Nadu",     "South"),
    ("Kochi",        "Kerala",         "South"),
    ("Mysuru",       "Karnataka",      "South"),
    ("Visakhapatnam","Andhra Pradesh", "South"),
    ("Kolkata",      "West Bengal",    "East"),
    ("Bhubaneswar",  "Odisha",         "East"),
    ("Patna",        "Bihar",          "East"),
    ("Ranchi",       "Jharkhand",      "East"),
    ("Guwahati",     "Assam",          "East"),
    ("Bhopal",       "Madhya Pradesh", "Central"),
    ("Indore",       "Madhya Pradesh", "Central"),
    ("Raipur",       "Chhattisgarh",   "Central"),
    ("Nashik",       "Maharashtra",    "West"),
    ("Thiruvananthapuram", "Kerala",   "South"),
]

# ── Electronics category hierarchy ───────────────────────────────────────────
CATEGORIES = {
    "Mobiles & Tablets": {
        "sub_cats": ["Smartphones", "Feature Phones", "Tablets", "Mobile Accessories"],
        "price_range": (3000, 120000),
        "margin_range": (0.04, 0.18),
    },
    "Laptops & Computers": {
        "sub_cats": ["Laptops", "Desktops", "Monitors", "Computer Peripherals", "Storage Devices"],
        "price_range": (8000, 180000),
        "margin_range": (0.05, 0.20),
    },
    "Audio & Headphones": {
        "sub_cats": ["Earphones", "Headphones", "Bluetooth Speakers", "Soundbars", "Home Theatre"],
        "price_range": (299, 60000),
        "margin_range": (0.08, 0.28),
    },
    "Televisions": {
        "sub_cats": ["Smart TVs", "OLED TVs", "LED TVs", "Projectors"],
        "price_range": (7000, 250000),
        "margin_range": (0.04, 0.16),
    },
    "Cameras & Photography": {
        "sub_cats": ["DSLR Cameras", "Mirrorless Cameras", "Action Cameras", "Camera Lenses", "Tripods"],
        "price_range": (1500, 200000),
        "margin_range": (0.06, 0.22),
    },
    "Home Appliances": {
        "sub_cats": ["Refrigerators", "Washing Machines", "Microwaves", "Air Conditioners", "Geysers"],
        "price_range": (3500, 90000),
        "margin_range": (0.05, 0.18),
    },
    "Wearables & Fitness": {
        "sub_cats": ["Smartwatches", "Fitness Bands", "Smart Glasses", "Wireless Earbuds"],
        "price_range": (999, 55000),
        "margin_range": (0.10, 0.30),
    },
    "Gaming": {
        "sub_cats": ["Gaming Consoles", "Gaming Laptops", "Gaming Peripherals", "Games & Software"],
        "price_range": (999, 90000),
        "margin_range": (0.06, 0.22),
    },
    "Networking": {
        "sub_cats": ["Routers", "Switches", "Network Adapters", "Modems"],
        "price_range": (500, 25000),
        "margin_range": (0.08, 0.25),
    },
}

# ── Customer name pool ────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav", "Aditya", "Ananya", "Anjali", "Arjun", "Aryan", "Deepika",
    "Divya", "Gaurav", "Ishaan", "Kavya", "Kiran", "Manish", "Meera",
    "Neha", "Nikhil", "Pooja", "Priya", "Rahul", "Rajan", "Riya",
    "Rohit", "Sakshi", "Sanjay", "Sanvi", "Shruti", "Siddharth",
    "Sneha", "Suresh", "Tanvi", "Vaishnavi", "Vikram", "Vishal", "Zara",
    "Amit", "Bhavna", "Chirag", "Dhruv", "Ekta", "Farhan", "Geeta",
    "Harini", "Ishan", "Jaya", "Kunal", "Lalita", "Mahesh", "Naina",
    "Om", "Poonam", "Quamar", "Radhika", "Shalini", "Tejas", "Uday",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Mehta",
    "Joshi", "Reddy", "Nair", "Iyer", "Mishra", "Banerjee", "Das",
    "Kapoor", "Malhotra", "Bose", "Ghosh", "Yadav", "Sinha", "Shah",
    "Chauhan", "Tiwari", "Rao", "Pillai", "Menon", "Krishnan", "Rajan",
]


def random_customer_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_date(start: datetime, end: datetime) -> str:
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    return d.strftime("%d-%m-%Y")


def generate():
    start_date = datetime(2020, 1, 1)
    end_date   = datetime(2024, 12, 31)

    records = []
    cat_names = list(CATEGORIES.keys())

    for i in range(1, N_ROWS + 1):
        # Location
        city_row = random.choice(CITY_DATA)
        city, state, region = city_row

        # Category
        cat_name = random.choice(cat_names)
        cat_info = CATEGORIES[cat_name]
        sub_cat  = random.choice(cat_info["sub_cats"])

        # Financials
        base_price = round(random.uniform(*cat_info["price_range"]), 2)
        discount   = round(random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]), 2)
        sales      = round(base_price * (1 - discount), 2)
        margin_pct = random.uniform(*cat_info["margin_range"])
        # Higher discounts erode margin
        effective_margin = margin_pct - (discount * 0.6)
        profit = round(sales * effective_margin, 2)

        records.append({
            "Order ID":     f"ELEC{i:05d}",
            "Customer Name": random_customer_name(),
            "Category":     cat_name,
            "Sub Category": sub_cat,
            "City":         city,
            "Order Date":   random_date(start_date, end_date),
            "Region":       region,
            "Sales":        sales,
            "Discount":     discount,
            "Profit":       profit,
            "State":        state,
        })

    df = pd.DataFrame(records)

    # Sort by Order Date for realism
    df["_date_sort"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")
    df.sort_values("_date_sort", inplace=True)
    df.drop(columns=["_date_sort"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    out_path = "Electronics Store Sales - Retail Analytics Dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"✅  Saved {len(df)} rows → {out_path}")
    print(df.head(3).to_string())
    return df


if __name__ == "__main__":
    generate()
