import streamlit as st
import requests
import json

st.title("🔍 Test 130point Sold Listings")

card_name = st.text_input("Enter a card to search (e.g. '2020 Topps Chrome Luis Robert')")

def get_sales(search_term):
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

if card_name:
    st.write("Searching 130point...")
    results = get_sales(card_name)

    if results:
        for item in results[:10]:
            st.write(f"**{item.get('title')}** — {item.get('price')}")
    else:
        st.warning("No results found or 130point is not responding.")
