import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Terms that indicate a card is graded
graded_terms = ['psa', 'bgs', 'sgc', 'cgc', 'beckett', 'graded']

# Fetch raw card listings from eBay
def get_raw_card_prices(search_term):
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}+raw&_sop=12"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select("li.s-item")[:20]
    results = []
    for item in items:
        title_el = item.select_one(".s-item__title")
        price_el = item.select_one(".s-item__price")
        link_el = item.select_one("a.s-item__link")
        if title_el and price_el and link_el:
            title = title_el.text.strip()
            if any(term in title.lower() for term in graded_terms):
                continue  # Skip graded cards
            try:
                price = float(price_el.text.replace('$', '').replace(',', '').split(' ')[0])
                results.append({
                    'title': title,
                    'price': price,
                    'link': link_el['href']
                })
            except:
                continue
    return results

# Estimate PSA 10 value based on sold listings with clear "PSA 10" titles
def get_psa10_price_estimate(search_term):
    query = f"{search_term} PSA 10"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Complete=1&LH_Sold=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select("li.s-item")[:20]
    prices = []
    for item in items:
        title_el = item.select_one(".s-item__title")
        price_el = item.select_one(".s-item__price")
        if title_el and price_el:
            title = title_el.text.strip()
            if "psa 10" not in title.lower():
                continue  # Ensure it's really a PSA 10 card
            try:
                price = float(price_el.text.replace('$', '').replace(',', '').split(' ')[0])
                prices.append(price)
            except:
                continue

    if prices:
        return sum(prices) / len(prices)
    else:
        return None

st.title("Card Flip Profit Analyzer")

search_term = st.text_input("Enter card search (e.g. '2020 Topps Chrome Luis Robert')")
grading_fee = st.number_input("Enter grading cost", value=25.00)
ebay_fee_percent = st.number_input("eBay final value fee %", value=13.0)

if search_term:
    with st.spinner('Fetching raw listings and PSA 10 sales...'):
        raw_cards = get_raw_card_prices(search_term)
        psa10_price = get_psa10_price_estimate(search_term)
        time.sleep(1)

    st.subheader("Raw Card Listings (Filtered)")
    if raw_cards:
        for card in raw_cards:
            st.markdown(f"[{card['title']}]({card['link']}) - ${card['price']:.2f}")
    else:
        st.write("No ungraded raw cards found.")

    st.subheader("Estimated PSA 10 Price")
    if psa10_price:
        st.write(f"${psa10_price:.2f}")
    else:
        st.write("No recent PSA 10 sales found.")

    if psa10_price:
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
