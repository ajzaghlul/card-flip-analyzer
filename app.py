
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Placeholder function: Replace with eBay API or improved scraping
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
            results.append({
                'title': title.text,
                'price': float(price.text.replace('$', '').replace(',', '').split(' ')[0]),
                'link': link['href']
            })
    return results

# Placeholder PSA 10 lookup (mock data)
def get_psa10_price_estimate(search_term):
    # Simulate lookup: In production, query sold listings or use 130point API
    example_prices = {
        '2020 topps chrome luis robert': 90.00,
        '2018 prizm luka doncic': 500.00,
        '2021 optic cade cunningham': 150.00
    }
    return example_prices.get(search_term.lower(), 100.00)  # fallback default

st.title("Card Flip Profit Analyzer")

search_term = st.text_input("Enter card search (e.g. '2020 Topps Chrome Luis Robert')")
grading_fee = st.number_input("Enter grading cost", value=25.00)
ebay_fee_percent = st.number_input("eBay final value fee %", value=13.0)

if search_term:
    with st.spinner('Fetching data...'):
        raw_cards = get_raw_card_prices(search_term)
        psa10_price = get_psa10_price_estimate(search_term)

    st.subheader("Raw Card Listings")
    for card in raw_cards:
        st.markdown(f"[{card['title']}]({card['link']}) - ${card['price']:.2f}")

    st.subheader("Estimated PSA 10 Price")
    st.write(f"${psa10_price:.2f}")

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
