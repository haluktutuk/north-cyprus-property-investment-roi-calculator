import pandas as pd
import streamlit as st

def calculate_roi(
    property_price,
    annual_appreciation_rate,
    holding_period_years,
    purchase_fees,
    transfer_tax_rate,
    vat_rate,
    annual_maintenance_cost,
    months_to_completion,
    language
):
    initial_investment = property_price * 0.35
    remaining_debt = property_price * 0.65
    post_completion_payment = property_price * 0.3
    total_taxes = property_price * (purchase_fees + transfer_tax_rate + vat_rate)
    
    annual_roi_data = []
    cumulative_net_profit, cumulative_investment = -initial_investment, initial_investment
    total_rental_income, total_maintenance_fees = 0, 0
    total_instalment_payments, total_net_profit, total_appreciation = 0, -initial_investment, 0
    property_value = property_price
    
    # Add Year 0 (Initial investment)
    annual_roi_data.append([
        "0", property_value, 0.0, 0.0, 0.0, 0.0, 0.0, -initial_investment, remaining_debt
    ])
    
    # Initialize appreciation rate at +5% more for the first two years
    appreciation_rate = round(annual_appreciation_rate + 0.05, 3)
    
    for year in range(1, holding_period_years + 1):
        if year == (months_to_completion // 12) + 1:
            appreciation_rate = round(annual_appreciation_rate, 3)  # Reset to base rate after completion
        elif year > (months_to_completion // 12) + 1:
            appreciation_rate = max(0, round(appreciation_rate - 0.01, 3))  # Decrease by 1% per year after completion
        
        appreciation_amount = round(property_value * appreciation_rate, 1)
        property_value = round(property_value + appreciation_amount, 1)
        total_appreciation += appreciation_amount
        
        annual_rental_income = round((property_value * 0.01) * 12, 1) if year > (months_to_completion // 12) else 0.0
        
        # Increase maintenance fees by 15% each year after completion
        if year > (months_to_completion // 12):
            annual_maintenance_cost *= 1.15
        
        annual_maintenance_expense = round(annual_maintenance_cost, 1) if year > (months_to_completion // 12) else 0.0
        
        annual_payment = round(min(post_completion_payment / 2, remaining_debt), 1) if remaining_debt > 0 else 0.0
        remaining_debt = round(remaining_debt - annual_payment, 1)
        cumulative_investment += annual_payment
        
        # Remove initial investment from year 1 net profit calculation
        annual_net_profit = round((annual_rental_income - annual_maintenance_expense - annual_payment) + appreciation_amount, 1)
        
        cumulative_net_profit += annual_net_profit
        total_rental_income += annual_rental_income
        total_maintenance_fees += annual_maintenance_expense
        total_instalment_payments += annual_payment
        total_net_profit += annual_net_profit
        
        annual_roi_data.append([
            str(year), property_value, round(appreciation_rate * 100, 1), appreciation_amount, annual_rental_income, 
            annual_maintenance_expense, annual_payment, annual_net_profit, remaining_debt
        ])
    
    column_names = {
        "en": ["Year", "Property Value", "Appreciation Rate (%)", "Appreciation Amount", "Rental Income", "Maintenance Fees", "Instalment Payments", "Net Profit", "Remaining Debt"],
        "tr": ["Yıl", "Mülk Değeri", "Değer Artış Oranı (%)", "Değer Artış Miktarı", "Kira Geliri", "Bakım Ücreti", "Taksit Ödemeleri", "Net Kar", "Kalan Borç"]
    }
    
    df_results = pd.DataFrame(
        annual_roi_data, columns=column_names[language]
    )
    
    totals_row = pd.DataFrame([[
        "Total", property_value, 0.0, total_appreciation, total_rental_income, total_maintenance_fees, 
        total_instalment_payments, total_net_profit, 0.0]],
        columns=column_names[language])
    df_results = pd.concat([df_results, totals_row], ignore_index=True)
    
    # Update global ROI to include appreciation amount in total net profit
    adjusted_total_net_profit = total_net_profit + total_appreciation
    global_roi = round((adjusted_total_net_profit / cumulative_investment) * 100, 1) if cumulative_investment > 0 else 0.0
    
    return df_results, global_roi, adjusted_total_net_profit

st.title("North Cyprus Real Estate ROI Calculator")

property_price = st.number_input("Property Price (GBP)", min_value=10000, value=165000, step=1000)
annual_appreciation_rate = st.number_input("Initial Annual Appreciation Rate (%)", min_value=0.0, value=8.0, step=0.1) / 100
holding_period_years = st.number_input("Holding Period (Years)", min_value=1, value=7, step=1)
purchase_fees = st.number_input("Purchase Fees (%)", min_value=0.0, value=6.0, step=0.1) / 100
transfer_tax_rate = st.number_input("Transfer Tax Rate (%)", min_value=0.0, value=6.0, step=0.1) / 100
vat_rate = st.number_input("VAT Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
annual_maintenance_cost = st.number_input("Annual Maintenance Cost (GBP)", min_value=0, value=1000, step=100)
months_to_completion = st.number_input("Months to Completion Date", min_value=1, value=30, step=1)
language = st.radio("Select Language", ("en", "tr"))

if st.button("Calculate ROI"):
    df, global_roi, global_profit = calculate_roi(
        property_price,
        annual_appreciation_rate,
        holding_period_years,
        purchase_fees,
        transfer_tax_rate,
        vat_rate,
        annual_maintenance_cost,
        months_to_completion,
        language
    )
    st.dataframe(df)
    st.subheader(f"Global ROI: {global_roi}%")
    st.subheader(f"Global Profit: £{global_profit}")
