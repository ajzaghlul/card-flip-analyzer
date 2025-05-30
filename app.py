import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape eBay Buy It Now listings
def scrape_ebay_raw(card_name):
    query = card_name.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_BIN=1&rt=nc"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    items = soup.find_all("li", class_="s-item")
    results = []
    
    for item in items:
        title = item.find("h3", class_="s-item__title")
        price = item.find("span", class_="s-item__price")
        link = item.find("a", class_="s-item__link")
        if title and price and link:
            results.append({
                "Title": title.text,
                "Price": price.text,
                "Link": link["href"]
            })
    
    return results

# Function to scrape eBay sold listings for PSA 10
def scrape_ebay_psa10(card_name):
    query = card_name.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}+PSA+10&_sop=13&LH_Sold=1&LH_Complete=1"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    items = soup.find_all("li", class_="s-item")
    prices = []
    
    for item in items:
        price = item.find("span", class_="s-item__price")
        if price:
            price_text = price.text.strip().replace("$", "").replace(",", "")
            try:
                price_value = float(price_text.split(" ")[0])
                prices.append(price_value)
            except:
                continue
    
    return prices

# Streamlit UI
st.title("Card Flip Analyzer")
st.write("Estimate flip potential between raw and PSA 10 cards.")

card_name = st.text_input("Enter Card Name:")

if st.button("Analyze"):
    if card_name:
        with st.spinner("Scraping eBay data..."):
            raw_listings = scrape_ebay_raw(card_name)
            psa10_prices = scrape_ebay_psa10(card_name)
        
        if raw_listings:
            raw_df = pd.DataFrame(raw_listings)
            st.subheader("Raw Card Listings")
            st.dataframe(raw_df)
        else:
            st.warning("No raw listings found.")
        
        if psa10_prices:
            psa10_avg = round(sum(psa10_prices) / len(psa10_prices), 2)
            st.subheader("PSA 10 Sold Price Estimate")
            st.write(f"Average PSA 10 Price: **${psa10_avg}**")
            
            # Example: assume grading fee = $25 and selling fee = 12.5%
            st.write("Potential Profits:")
            grading_fee = 25
            ebay_fee_pct = 0.125
            
            profit_data = []
            for raw in raw_listings:
                try:
                    raw_price = float(raw['Price'].replace("$", "").replace(",", "").split(" ")[0])
                    estimated_profit = psa10_avg - (raw_price + grading_fee + (psa10_avg * ebay_fee_pct))
                    profit_data.append({
                        "Raw Price": raw_price,
                        "PSA 10 Avg": psa10_avg,
                        "Est. Profit": round(estimated_profit, 2),
                        "Link": raw['Link']
                    })
                except:
                    continue
            
            if profit_data:
                profit_df = pd.DataFrame(profit_data)
                st.dataframe(profit_df)
            else:
                st.warning("Could not calculate profit.")
        else:
            st.warning("No PSA 10 sold listings found.")
    else:
        st.error("Please enter a card name.")
