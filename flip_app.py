import streamlit as st

st.set_page_config(page_title="Flip-Advisor", layout="wide")

def safe_div(a, b):
    return a / b if b else 0.0

def money(x):
    return f"${x:,.0f}"

def pct(x):
    return f"{x*100:,.1f}%"

def calculate(
    purchase_price, arv, rehab_budget, holding_months,
    buy_closing_pct, sell_closing_pct,
    annual_taxes, annual_insurance,
    monthly_utilities, monthly_hoa, monthly_misc,
    permits_and_fees, staging,
    use_financing, down_payment_pct, interest_rate_annual, points_pct
):
    buy_closing_cost = purchase_price * buy_closing_pct
    sell_closing_cost = arv * sell_closing_pct

    monthly_taxes = annual_taxes / 12.0
    monthly_insurance = annual_insurance / 12.0

    monthly_carry = (
        monthly_taxes
        + monthly_insurance
        + monthly_utilities
        + monthly_hoa
        + monthly_misc
    )
    holding_cost_total = monthly_carry * holding_months

    loan_amount = 0.0
    down_payment = 0.0
    financing_cost_total = 0.0

    if use_financing:
        down_payment = purchase_price * down_payment_pct
        loan_amount = max(purchase_price - down_payment, 0.0)
        monthly_interest_rate = interest_rate_annual / 12.0
        interest_total = loan_amount * monthly_interest_rate * holding_months
        points_cost = loan_amount * points_pct
        financing_cost_total = interest_total + points_cost
    else:
        down_payment = purchase_price

    total_investment = (
        purchase_price
        + buy_closing_cost
        + rehab_budget
        + holding_cost_total
        + financing_cost_total
        + permits_and_fees
        + staging
    )

    net_sale_proceeds = arv - sell_closing_cost
    profit = net_sale_proceeds - total_investment

    roi = safe_div(profit, total_investment)
    annualized_roi = roi * (12.0 / holding_months)

    max_offer_70 = (arv * 0.70) - rehab_budget

    # Simple deal score (0–100)
    # Heavier weight on margin and speed. Adjust to taste.
    profit_margin = safe_div(profit, arv)  # profit as % of sale price
    speed_factor = min(1.0, 6.0 / holding_months)  # best at <= 6 months
    score = max(0.0, min(100.0, (profit_margin * 400.0) + (speed_factor * 40.0)))

    return {
        "buy_closing_cost": buy_closing_cost,
        "sell_closing_cost": sell_closing_cost,
        "monthly_carry": monthly_carry,
        "holding_cost_total": holding_cost_total,
        "loan_amount": loan_amount,
        "down_payment": down_payment,
        "financing_cost_total": financing_cost_total,
        "total_investment": total_investment,
        "net_sale_proceeds": net_sale_proceeds,
        "profit": profit,
        "roi": roi,
        "annualized_roi": annualized_roi,
        "max_offer_70": max_offer_70,
        "score": score,
    }

st.title("🏚️ House Flip Calculator ")
st.caption("Plug in a deal. Get profit, ROI, annualized ROI, 70% rule max offer, plus flags. Created by Keith Betts")

with st.sidebar:
    st.header("Deal Inputs")

    purchase_price = st.number_input("Purchase Price", min_value=0.0, value=150000.0, step=5000.0)
    arv = st.number_input("After Repair Value (ARV)", min_value=0.0, value=260000.0, step=5000.0)
    rehab_budget = st.number_input("Rehab Budget", min_value=0.0, value=40000.0, step=2000.0)
    holding_months = st.number_input("Holding Months", min_value=1, value=6, step=1)

    st.divider()
    st.subheader("Closing Costs")
    buy_closing_pct = st.number_input("Buy Closing % (0.03 = 3%)", min_value=0.0, max_value=0.2, value=0.03, step=0.005, format="%.3f")
    sell_closing_pct = st.number_input("Sell Closing % (0.06 = 6%)", min_value=0.0, max_value=0.2, value=0.06, step=0.005, format="%.3f")

    st.divider()
    st.subheader("Holding Costs")
    annual_taxes = st.number_input("Annual Property Taxes", min_value=0.0, value=3000.0, step=250.0)
    annual_insurance = st.number_input("Annual Insurance", min_value=0.0, value=1500.0, step=250.0)
    monthly_utilities = st.number_input("Monthly Utilities", min_value=0.0, value=400.0, step=50.0)
    monthly_hoa = st.number_input("Monthly HOA", min_value=0.0, value=0.0, step=25.0)
    monthly_misc = st.number_input("Monthly Misc/Maintenance", min_value=0.0, value=0.0, step=25.0)

    st.divider()
    st.subheader("One-time Extras")
    permits_and_fees = st.number_input("Permits & Fees", min_value=0.0, value=0.0, step=250.0)
    staging = st.number_input("Staging", min_value=0.0, value=0.0, step=250.0)

    st.divider()
    st.subheader("Financing (optional)")
    use_financing = st.toggle("Use Financing", value=False)

    down_payment_pct = 0.20
    interest_rate_annual = 0.10
    points_pct = 0.02

    if use_financing:
        down_payment_pct = st.number_input("Down Payment % (0.20 = 20%)", min_value=0.0, max_value=1.0, value=0.20, step=0.05, format="%.2f")
        interest_rate_annual = st.number_input("Interest Rate Annual (0.10 = 10%)", min_value=0.0, max_value=1.0, value=0.10, step=0.01, format="%.2f")
        points_pct = st.number_input("Lender Points % (0.02 = 2%)", min_value=0.0, max_value=0.2, value=0.02, step=0.005, format="%.3f")
    else:
        st.info("Financing is OFF. ROI uses total cash invested (purchase+costs).")

r = calculate(
    purchase_price, arv, rehab_budget, int(holding_months),
    buy_closing_pct, sell_closing_pct,
    annual_taxes, annual_insurance,
    monthly_utilities, monthly_hoa, monthly_misc,
    permits_and_fees, staging,
    use_financing, down_payment_pct, interest_rate_annual, points_pct
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Profit", money(r["profit"]))
col2.metric("ROI", pct(r["roi"]))
col3.metric("Annualized ROI (simple)", pct(r["annualized_roi"]))
col4.metric("Deal Score (0–100)", f'{r["score"]:.0f}')

st.divider()

left, right = st.columns([1, 1])

with left:
    st.subheader("Cost Breakdown")
    st.write(
        {
            "Buy Closing Cost": money(r["buy_closing_cost"]),
            "Rehab Budget": money(rehab_budget),
            "Monthly Carry": money(r["monthly_carry"]),
            "Holding Cost Total": money(r["holding_cost_total"]),
            "Financing Cost Total": money(r["financing_cost_total"]),
            "Permits & Fees": money(permits_and_fees),
            "Staging": money(staging),
            "Total Investment": money(r["total_investment"]),
        }
    )

with right:
    st.subheader("Sale & Rules")
    st.write(
        {
            "ARV": money(arv),
            "Sell Closing Cost": money(r["sell_closing_cost"]),
            "Net Sale Proceeds": money(r["net_sale_proceeds"]),
            "70% Rule Max Offer": money(r["max_offer_70"]),
        }
    )

    st.divider()
    st.subheader("Flags")

    if purchase_price > r["max_offer_70"]:
        st.error("Purchase price is ABOVE the 70% rule max offer (higher risk / thin margin).")
    else:
        st.success("Purchase price is within the 70% rule max offer (better margin).")

    if r["profit"] <= 0:
        st.warning("Profit is not positive. Re-check ARV, rehab, holding, and selling costs.")
    else:
        st.success("Profit is positive based on inputs.")

    if holding_months > 9:
        st.warning("Long holding period. Carry + market risk increases with time.")
    elif holding_months <= 6:
        st.success("Holding period is in a fast-flip range (≤ 6 months).")

st.divider()
st.caption("Tip: Add a contingency (10–15% of rehab) to avoid surprises, and rerun the deal.")
