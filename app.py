import streamlit as st
import requests
import json
import pandas as pd

# 130point Sold Listings API (Unofficial)
def get_130point_sales(search_term):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.130point.com',
        'Referer': 'https://www.130point.com/cardlookup.htm',
        'User-Agent': 'Mozilla/5.0'
    }
    data = {'searchterm': search_term}
    response = requests.post('https://www.130point.com/ajax/search_card', headers=headers, data=data)
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return []

# Parse sold listings
def parse_sales(data, psa_filter=False):
    sales = []
    for item in data:
        title = item.get('title', '').lower()
        price_str = item.get('price', '')
        if "$" not in price_str:
            continue
        try:
            price = float(price_str.replace('$', '').replace(',', '').strip())
        except:
            continue
        if psa_filter:
            if "psa 10" in title:
                sales.append({'title': item['title'], 'price': price})
        else:
            if not any(x in title for x in ["psa", "bgs", "sgc", "cgc", "beckett", "auto", "autograph", "signed"]):
                sales.append({'title': item['title'], 'price': price})
    return sales

# Streamlit UI
st.title("📈 Card Flip Analyzer")
search_term = st.text_input("Enter card name (e.g. 2020 Topps Chrome Luis Robert)")
grading_fee = st.number_input("PSA grading fee ($)", value=25.00)
ebay_fee_percent = st.number_input("eBay + PayPal fees (%)", value=13.0)

if search_term:
    with st.spinner("Fetching data from 130point..."):
        raw_data = get_130point_sales(search_term)
        psa10_data = get_130point_sales(search_term + " PSA 10")

    raw_sales = parse_sales(raw_data, psa_filter=False)
    psa10_sales = parse_sales(psa10_data, psa_filter=True)

    st.subheader("🟢 Raw Card Sales")
    if raw_sales:
        raw_df = pd.DataFrame(raw_sales)
        st.dataframe(raw_df)
    else:
        st.write("No raw card sales found.")

    st.subheader("🔵 PSA 10 Sales")
    if psa10_sales:
        psa_df = pd.DataFrame(psa10_sales)
        avg_psa_price = psa_df['price'].mean()
        st.dataframe(psa_df)
        st.write(f"**Average PSA 10 Sale:** ${avg_psa_price:.2f}")
    else:
        st.write("No PSA 10 sales found.")
        avg_psa_price = None

    if raw_sales and avg_psa_price:
        st.subheader("💰 Flip Profit Estimates")
        profit_data = []
        for card in raw_sales:
            total_cost = card['price'] + grading_fee
            net_sale = avg_psa_price * (1 - ebay_fee_percent / 100)
            profit = net_sale - total_cost
            profit_data.append({
                'Raw Title': card['title'],
                'Raw Price': card['price'],
                'Total Cost': total_cost,
                'Est. PSA 10 Sale': avg_psa_price,
                'Net After Fees': net_sale,
                'Estimated Profit': profit
            })

        profit_df = pd.DataFrame(profit_data)
        st.dataframe(profit_df.style.format("${:.2f}"))
