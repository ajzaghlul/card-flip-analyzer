
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import altair as alt
from datetime import datetime

# Fetch raw card listings from eBay
def get_raw_card_prices(search_term):
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}+raw&_sop=12"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select("li.s-item")[:10]
    results = []
    for item in items:
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one("a.s-item__link")
        if title and price and link:
            try:
                results.append({
                    'title': title.text,
                    'price': float(price.text.replace('$', '').replace(',', '').split(' ')[0]),
                    'link': link['href']
                })
            except:
                continue
    return results

# Estimate PSA 10 value and collect price history
def get_psa10_price_history(search_term):
    query = f"{search_term} PSA 10"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Complete=1&LH_Sold=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select("li.s-item")[:15]
    sales_data = []
    for item in items:
        price_tag = item.select_one(".s-item__price")
        date_tag = item.select_one(".s-item__title--tagblock .POSITIVE")
        if price_tag:
            try:
                price = float(price_tag.text.replace('$', '').replace(',', '').split(' ')[0])
                # Use current time as placeholder if no date is available
                date = datetime.now()
                sales_data.append({'price': price, 'date': date})
            except:
                continue

    if sales_data:
        df = pd.DataFrame(sales_data)
        return df, df["price"].mean()
    else:
        return pd.DataFrame(), 100.00  # fallback

st.title("Card Flip Profit Analyzer")

search_term = st.text_input("Enter card search (e.g. '2020 Topps Chrome Luis Robert')")
grading_fee = st.number_input("Enter grading cost", value=25.00)
ebay_fee_percent = st.number_input("eBay final value fee %", value=13.0)

if search_term:
    with st.spinner('Fetching raw listings and PSA 10 sales history...'):
        raw_cards = get_raw_card_prices(search_term)
        psa10_df, psa10_price = get_psa10_price_history(search_term)
        time.sleep(1)

    st.subheader("Raw Card Listings")
    for card in raw_cards:
        st.markdown(f"[{card['title']}]({card['link']}) - ${card['price']:.2f}")

    st.subheader("Estimated PSA 10 Price (Based on Sold Listings)")
    st.write(f"${psa10_price:.2f}")

    if not psa10_df.empty:
        st.subheader("PSA 10 Sold Price History")
        psa10_df['Sold Date'] = pd.to_datetime(psa10_df['date'])
        chart = alt.Chart(psa10_df).mark_line(point=True).encode(
            x='Sold Date:T',
            y='price:Q'
        ).properties(width=700, height=400)
        st.altair_chart(chart)

    st.subheader("Profit Analysis")
    data = []
    for card in raw_cards:
        total_cost = card['price'] + grading_fee
        sale_price = psa10_price
        net_after_fees = sale_price * (1 - ebay_fee_percent / 100)
        profit = net_after_fees - total_cost
        data.append({
            'Title': card['title'],
            'Raw Price': card['price'],
            'Total Cost': total_cost,
            'PSA 10 Sale (Est)': sale_price,
            'Net After Fees': net_after_fees,
            'Profit': profit
        })

    df = pd.DataFrame(data)
    st.dataframe(df.style.format("{:.2f}"))
