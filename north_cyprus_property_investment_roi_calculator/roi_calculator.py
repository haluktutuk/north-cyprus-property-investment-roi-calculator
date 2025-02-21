import pandas as pd
import streamlit as st

st.set_page_config(page_title="North Cyprus Real Estate ROI Calculator")

st.title("North Cyprus Real Estate ROI Calculator")

# Language selection
language = st.radio("Select Language / Dil Seçimi", ("en", "tr"))

# Labels
labels = {
    "en": {
        "property_price": "Property Price (GBP)",
        "annual_appreciation_rate": "Initial Annual Appreciation Rate (%)",
        "holding_period_years": "Holding Period (Years)",
        "annual_maintenance_cost": "Annual Maintenance Cost (GBP)",
        "months_to_completion": "Months to Completion Date",
        "calculate": "Calculate ROI",
        "global_roi": "Global ROI",
        "global_profit": "Global Profit",
        "summary": "Summary",
    },
    "tr": {
        "property_price": "Mülk Fiyatı (GBP)",
        "annual_appreciation_rate": "Başlangıç Yıllık Değer Artış Oranı (%)",
        "holding_period_years": "Yatırım Süresi (Yıl)",
        "annual_maintenance_cost": "Yıllık Bakım Ücreti (GBP)",
        "months_to_completion": "Tamamlanma Süresi (Ay)",
        "calculate": "ROI Hesapla",
        "global_roi": "Genel ROI",
        "global_profit": "Genel Kar",
        "summary": "Özet",
    }
}

# User Inputs
property_price = st.slider(labels[language]["property_price"], min_value=50000, max_value=500000, value=165000, step=5000)
annual_appreciation_rate = st.slider(labels[language]["annual_appreciation_rate"], min_value=8.0, max_value=65.0, value=8.0, step=1.0) / 100
holding_period_years = st.slider(labels[language]["holding_period_years"], min_value=1, max_value=10, value=7, step=1)
annual_maintenance_cost = st.slider(labels[language]["annual_maintenance_cost"], min_value=1000, max_value=3000, value=1000, step=100)
months_to_completion = st.slider(labels[language]["months_to_completion"], min_value=1, max_value=36, value=30, step=1)

# Default values
purchase_fees = 6.0 / 100
transfer_tax_rate = 6.0 / 100
vat_rate = 5.0 / 100

def format_currency(amount: float) -> str:
    """Format numbers as GBP currency string."""
    return f"£{amount:,.0f}"

def calculate_roi():
    initial_investment = property_price * 0.35
    remaining_debt = property_price * 0.65
    post_completion_payment = property_price * 0.3
    completion_year = (months_to_completion // 12) + 1

    # Tracking variables
    total_appreciation, total_rental_income, total_maintenance_fees, total_instalment_payments = 0, 0, 0, 0
    total_net_profit = -initial_investment
    property_value = property_price
    cumulative_investment = initial_investment

    results = []

    for year in range(0, holding_period_years + 1):
        if year == 0:
            results.append([year, property_value, "0%", 0, 0, 0, 0, -initial_investment, remaining_debt])
            continue
        
        # Appreciation calculations
        appreciation_rate = annual_appreciation_rate + 0.05 if year <= completion_year else max(0, annual_appreciation_rate - ((year - completion_year) * 0.01))
        appreciation_amount = round(property_value * appreciation_rate)
        property_value = round(property_value + appreciation_amount)
        total_appreciation += appreciation_amount

        # Rental income & maintenance cost after completion
        annual_rental_income = round(property_value * 0.01 * 12) if year >= completion_year else 0
        annual_maintenance_expense = round(annual_maintenance_cost * (1.15 ** (year - completion_year + 1))) if year >= completion_year else 0

        # Annual payments
        annual_payment = round(min(post_completion_payment / 2, remaining_debt)) if remaining_debt > 0 else 0
        remaining_debt = max(0, remaining_debt - annual_payment)
        cumulative_investment += annual_payment

        # Net profit calculation
        annual_net_profit = round(appreciation_amount + annual_rental_income - annual_maintenance_expense - annual_payment)
        total_net_profit += annual_net_profit
        total_rental_income += annual_rental_income
        total_maintenance_fees += annual_maintenance_expense
        total_instalment_payments += annual_payment

        results.append([
            year, property_value, f"{round(appreciation_rate * 100, 1)}%",
            appreciation_amount, annual_rental_income, annual_maintenance_expense,
            annual_payment, annual_net_profit, remaining_debt
        ])

    column_names = {
        "en": ["Year", "Property Value", "Appreciation Rate (%)", "Appreciation Amount", 
               "Rental Income", "Maintenance Fees", "Instalment Payments", "Net Profit", "Remaining Debt"],
        "tr": ["Yıl", "Mülk Değeri", "Değer Artış Oranı (%)", "Değer Artış Miktarı", 
               "Kira Geliri", "Bakım Ücreti", "Taksit Ödemeleri", "Net Kar", "Kalan Borç"]
    }

    df_results = pd.DataFrame(results, columns=column_names[language])

    # Summary row (show last year's property value & leave appreciation column empty)
    last_year_property_value = format_currency(results[-1][1])  # Get last year's property value
    last_year_remaining_debt = results[-1][-1]  # Get last year's remaining debt

    summary_row = pd.DataFrame([[
        labels[language]["summary"], last_year_property_value, "", 
        "", total_rental_income or 0, total_maintenance_fees or 0, 
        total_instalment_payments or 0, total_net_profit or 0, format_currency(last_year_remaining_debt or 0)
    ]], columns=column_names[language])

    # Convert "Year" column to string to prevent Arrow errors
    df_results["Year"] = df_results["Year"].astype(str)
    summary_row["Year"] = summary_row["Year"].astype(str)

    # Ensure numeric columns remain numeric
    numeric_cols = df_results.columns[3:]  
    summary_row[numeric_cols] = summary_row[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Concatenate the final DataFrame
    df_results = pd.concat([df_results, summary_row], ignore_index=True)

    # ROI Calculation
    global_roi = round((total_net_profit / cumulative_investment) * 100, 1) if cumulative_investment > 0 else 0.0

    return df_results, global_roi, total_net_profit

if st.button(labels[language]["calculate"]):
    df, global_roi, global_profit = calculate_roi()
    
    # Display data with formatting
    for col in df.columns[1:]:  # Skip 'Year' column
        if df[col].dtype == float or df[col].dtype == int:
            df[col] = df[col].apply(lambda x: format_currency(x) if pd.notna(x) else "")

    st.dataframe(df)
    st.subheader(f"{labels[language]['global_roi']}: {global_roi}%")
    st.subheader(f"{labels[language]['global_profit']}: {format_currency(global_profit)}")
