import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Card Flip Analyzer")

st.write("""
This app helps you find potential flip opportunities by comparing raw card listings
to PSA 10 graded prices.
""")

# Simple search input
search_query = st.text_input("Enter card name (e.g., Michael Jordan rookie):", "")

if search_query:
    # For demonstration, let's fetch some dummy raw listings from eBay
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&_sop=12"
    
    try:
        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')

        listings = []
        for item in soup.select(".s-item"):
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            if title and price:
                listings.append({
                    "Title": title.get_text(strip=True),
                    "Price": price.get_text(strip=True)
                })

        if listings:
            df = pd.DataFrame(listings)
            st.write("Raw Listings:")
            st.dataframe(df)
        else:
            st.warning("No listings found. Try a different search term.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Placeholder for PSA 10 price comparison
    st.info("PSA 10 price comparison is coming soon! 🚀")

