import pandas as pd
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

st.set_page_config(
    page_title="WİSREM Gayrimenkul North Cyprus Real Estate ROI Calculator"
)

st.title("WİSREM Gayrimenkul Ocean Life")

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
    },
}

# User Inputs
property_price = Decimal(
    st.slider(
        labels[language]["property_price"],
        min_value=50000,
        max_value=500000,
        value=165000,
        step=5000,
    )
)
annual_appreciation_rate = (
    Decimal(
        st.slider(
            labels[language]["annual_appreciation_rate"],
            min_value=3.0,
            max_value=65.0,
            value=8.0,
            step=1.0,
        )
    )
    / 100
)
holding_period_years = st.slider(
    labels[language]["holding_period_years"], min_value=1, max_value=10, value=7, step=1
)
annual_maintenance_cost = Decimal(
    st.slider(
        labels[language]["annual_maintenance_cost"],
        min_value=1000,
        max_value=10000,
        value=1000,
        step=500,
    )
)
months_to_completion = st.slider(
    labels[language]["months_to_completion"],
    min_value=1,
    max_value=36,
    value=30,
    step=1,
)

# Default values
purchase_fees = Decimal("3.0") / 100
transfer_tax_rate = Decimal("6.0") / 100
vat_rate = Decimal("5.0") / 100
solicitor_fees = Decimal("1000")


def format_currency(value):
    """Format numbers as GBP currency string, leave non-numeric values unchanged."""
    if isinstance(value, (int, float, Decimal)):
        return f"£{Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"
    return value


def calculate_roi():
    # Add additional costs to the initial property price
    total_purchase_price = (
        property_price * (1 + purchase_fees + transfer_tax_rate + vat_rate)
        + solicitor_fees
    )
    total_purchase_price = total_purchase_price.quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    # Initialize financial values
    initial_investment = (total_purchase_price * Decimal("0.35")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    remaining_debt = (total_purchase_price * Decimal("0.65")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    post_completion_payment = (total_purchase_price * Decimal("0.3")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    completion_year = (months_to_completion // 12) + 1

    total_appreciation = Decimal("0")
    total_rental_income = Decimal("0")
    total_maintenance_fees = Decimal("0")
    total_instalment_payments = Decimal("0")
    global_profit = -initial_investment
    property_value = property_price
    cumulative_investment = initial_investment

    results = []

    for year in range(0, holding_period_years + 1):
        if year == 0:
            results.append(
                [
                    year,
                    property_value,
                    "0%",
                    0,
                    0,
                    0,
                    0,
                    -initial_investment,
                    remaining_debt,
                ]
            )
            continue

        # Appreciation calculations
        appreciation_rate = (
            annual_appreciation_rate + Decimal("0.05")
            if year <= completion_year
            else max(
                Decimal("0"),
                annual_appreciation_rate
                - (Decimal(year - completion_year - 1) * Decimal("0.01")),
            )
        )
        appreciation_amount = (property_value * appreciation_rate).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        property_value += appreciation_amount
        total_appreciation += appreciation_amount

        annual_rental_income = (
            (property_value * Decimal("0.01") * Decimal("12")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            if year >= completion_year
            else Decimal("0")
        )
        annual_maintenance_expense = (
            (
                annual_maintenance_cost
                * (Decimal("1.15") ** (year - completion_year + 1))
            ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            if year >= completion_year
            else Decimal("0")
        )

        annual_payment = (
            min(post_completion_payment / 2, remaining_debt)
            if remaining_debt > 0
            else Decimal("0")
        )
        remaining_debt = max(Decimal("0"), remaining_debt - annual_payment)
        cumulative_investment += annual_payment

        annual_net_profit = (
            appreciation_amount
            + annual_rental_income
            - annual_maintenance_expense
            - annual_payment
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        global_profit += annual_net_profit
        total_rental_income += annual_rental_income
        total_maintenance_fees += annual_maintenance_expense
        total_instalment_payments += annual_payment

        results.append(
            [
                year,
                property_value,
                f"{round(appreciation_rate * 100, 1)}%",
                appreciation_amount,
                annual_rental_income,
                annual_maintenance_expense,
                annual_payment,
                annual_net_profit,
                remaining_debt,
            ]
        )

    column_names = {
        "en": [
            "Year",
            "Property Value",
            "Appreciation Rate (%)",
            "Appreciation Amount",
            "Rental Income",
            "Maintenance Fees",
            "Instalment Payments",
            "Net Profit",
            "Remaining Debt",
        ],
        "tr": [
            "Yıl",
            "Mülk Değeri",
            "Değer Artış Oranı (%)",
            "Değer Artış Miktarı",
            "Kira Geliri",
            "Bakım Ücreti",
            "Taksit Ödemeleri",
            "Net Kar",
            "Kalan Borç",
        ],
    }

    df_results = pd.DataFrame(results, columns=column_names[language])

    last_year_property_value = results[-1][1]
    last_year_remaining_debt = results[-1][-1] or 0

    adjusted_global_profit = global_profit - last_year_remaining_debt

    summary_row = pd.DataFrame(
        [
            [
                labels[language]["summary"],
                last_year_property_value,
                "",
                total_appreciation,
                total_rental_income,
                total_maintenance_fees,
                total_instalment_payments,
                adjusted_global_profit,
                last_year_remaining_debt,
            ]
        ],
        columns=column_names[language],
    )

    df_results["Year"] = df_results["Year"].astype(str)
    summary_row["Year"] = summary_row["Year"].astype(str)

    df_results = pd.concat([df_results, summary_row], ignore_index=True)

    global_roi = (
        round((adjusted_global_profit / cumulative_investment) * 100, 1)
        if cumulative_investment > 0
        else 0.0
    )

    return df_results, global_roi, adjusted_global_profit


if st.button(labels[language]["calculate"]):
    df, global_roi, global_profit = calculate_roi()

    st.dataframe(df.style.format(format_currency).hide(axis="index"))

    st.subheader(f"{labels[language]['global_roi']}: {global_roi}%")
    st.subheader(
        f"{labels[language]['global_profit']}: {format_currency(global_profit)}"
    )
