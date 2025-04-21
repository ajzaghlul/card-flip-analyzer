
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

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

# Estimate PSA 10 value by pulling eBay sold listings
import json

def get_psa10_price_estimate(search_term):
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.130point.com',
            'Referer': 'https://www.130point.com/cardlookup.htm',
            'User-Agent': 'Mozilla/5.0'
        }

        payload = {
            'searchterm': f'{search_term} PSA 10'
        }

        response = requests.post('https://www.130point.com/ajax/search_card', headers=headers, data=payload)
        data = json.loads(response.text)

        prices = []
        for item in data:
            title = item.get('title', '').lower()
            price_str = item.get('price', '')
            if "psa 10" in title and price_str and "$" in price_str:
                try:
                    price = float(price_str.replace('$', '').replace(',', '').strip())
                    prices.append(price)
                except:
                    continue

        if prices:
            return sum(prices) / len(prices)
        else:
            return None
    except Exception as e:
        print("Error pulling from 130point:", e)
        return None

st.title("Card Flip Profit Analyzer")

search_term = st.text_input("Enter card search (e.g. '2020 Topps Chrome Luis Robert')")
grading_fee = st.number_input("Enter grading cost", value=25.00)
ebay_fee_percent = st.number_input("eBay final value fee %", value=13.0)

if search_term:
    with st.spinner('Fetching raw listings and PSA 10 estimates...'):
        raw_cards = get_raw_card_prices(search_term)
        psa10_price = get_psa10_price_estimate(search_term)
        time.sleep(1)

    st.subheader("Raw Card Listings")
    for card in raw_cards:
        st.markdown(f"[{card['title']}]({card['link']}) - ${card['price']:.2f}")

    st.subheader("Estimated PSA 10 Price (Based on Sold Listings)")
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
