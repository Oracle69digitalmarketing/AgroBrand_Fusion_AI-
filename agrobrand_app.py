# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 1: MVP Prototype Structure
# Focus: AI Assistant for Agribusiness (Option A)
# Scope: Nigeria-wide / Global Agribusiness Insights
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# Import necessary libraries
import streamlit as st
import pandas as pd
from PIL import Image
import io
import time # For simulated delays in mock functions

# --- Mocked Analysis Functions ---
def identify_product_via_web(image_bytes):
    st.info("Simulating image recognition...")
    time.sleep(1)
    return {"product": "Catfish", "condition": "Fresh", "setting": "Harvest Basin", "confidence": 0.85}

def fetch_market_price(product_name):
    st.info(f"Simulating market price fetch for {product_name}...")
    time.sleep(1)
    price_trends = {
        "Catfish": {"price_range": "₦1,800 – ₦2,200/kg", "location": "Shasha Market, Akure", "trend": "Rising slightly due to feed cost"},
        "Plantain": {"price_range": "₦800 – ₦1,200/bunch", "location": "Erekesan Market, Akure", "trend": "Stable, peak season approaching"},
        "Cocoa": {"price_range": "₦1,500,000 – ₦1,800,000/tonne", "location": "Ondo State Cooperatives", "trend": "High volatility, global factors"},
    }
    return price_trends.get(product_name, {"price_range": "N/A", "location": "N/A", "trend": "No specific data available"})

# --- Helper Function for Content Generation ---
def generate_campaign_content(product_info, market_data):
    headline = "Quality Farm Products Available!"
    body = "Get the best farm-fresh products today."
    cta = "Contact us now to order! [Your Phone Number/WhatsApp]"
    hashtags = "#FarmFresh #NigeriaAgro #SupportLocalFarmers"
    if product_info and product_info.get('product'):
        product_name = product_info.get('product')
        condition = product_info.get('condition', 'Quality')
        headline = f"Premium {condition} {product_name} - Available Now!"
        if market_data.get('location') and "Akure" in market_data.get('location'): headline += " In Akure!"
        body = f"Looking for top {condition.lower()} {product_name}? Look no further! "
        if market_data.get('trend') and market_data.get('trend') != 'N/A': body += f"Market trend shows: {market_data.get('trend')}. Secure yours today! "
        body += f"Ideal for home use or business."
        cta = f"Order your {product_name} now! Call/WhatsApp [Your Phone Number/WhatsApp]."
        if market_data.get('location') and market_data.get('location') != 'N/A': cta += f" Pickup available near {market_data.get('location')}."
        product_tag = product_name.replace(" ", "")
        hashtags_list = ["#FarmFresh", f"#{product_tag}", "#Akure", "#OndoState", "#NaijaMade", "#Agribusiness", "#SupportLocal"]
        if market_data.get('location') and "Shasha" in market_data.get('location'): hashtags_list.append("#ShashaMarket")
        if market_data.get('location') and "Erekesan" in market_data.get('location'): hashtags_list.append("#ErekesanMarket")
        hashtags = " ".join(hashtags_list)
    return {"headline": headline, "body": body, "cta": cta, "hashtags": hashtags}

# --- 1. Page Configuration ---
st.set_page_config(page_title="AgroBrand Fusion AI", layout="wide")

# --- 2. Main Application Interface ---
st.title("🌾 AgroBrand Fusion AI")
st.markdown("Your AI Assistant for Agribusiness Marketing & Pricing Insights across Nigeria and beyond.")
st.markdown("---")

# --- 3. Sidebar for User Inputs ---
st.sidebar.header("Upload Your Assets Here")
uploaded_image = st.sidebar.file_uploader("1. Upload Product Image", type=["png", "jpg", "jpeg"])
uploaded_file = st.sidebar.file_uploader("2. Upload Sales/Cost Sheet", type=["csv", "xlsx"])

# --- 4. Asset Previews ---
# Initialize shared variables
image_bytes = None
product_info = None
market_data = None
df = None

col1, col2 = st.columns(2) # Create two columns for previews

with col1:
    st.subheader("Image Preview")
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption=f"Uploaded: {uploaded_image.name}", use_column_width=True)
            uploaded_image.seek(0)
            image_bytes = uploaded_image.read()
        except Exception as e:
            st.error(f"Error displaying image: {e}")
    else:
        st.info("No image uploaded.")

with col2:
    st.subheader("Data Preview")
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            if df is not None:
                st.success(f"Loaded '{uploaded_file.name}'. Preview:")
                st.dataframe(df.head())
            else: st.warning("Could not process file.")
        except Exception as e:
            st.error(f"Error reading data file: {e}"); df = None
    else:
        st.info("No data file uploaded.")
st.markdown("---")


# --- 5. Analysis Results Section ---
st.subheader("🤖 AI Analysis & Insights")

# Run analyses only if inputs are available
if image_bytes:
    product_info = identify_product_via_web(image_bytes)
    if product_info and product_info.get('product'):
        market_data = fetch_market_price(product_info['product'])

# Display Analysis Results
col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)

with col_img_analysis:
    st.write("**Image Analysis:**")
    if product_info:
        st.markdown(f"- **Product:** {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)")
        st.markdown(f"- **Condition:** {product_info.get('condition', 'N/A')}")
        st.markdown(f"- **Setting:** {product_info.get('setting', 'N/A')}")
    else: st.info("Upload image.")

with col_mkt_analysis:
    st.write("**Market Insights:**")
    if market_data:
        st.markdown(f"- **Price ({market_data.get('location', 'N/A')}):** {market_data.get('price_range', 'N/A')}")
        st.markdown(f"- **Trend:** {market_data.get('trend', 'N/A')}")
    else: st.info("Requires image analysis.")

with col_data_analysis:
    st.write("**Data Highlights:**")
    if df is not None:
        required_cols = ['Product', 'Revenue']
        if all(col in df.columns for col in required_cols):
            try:
                df['Revenue_Clean'] = df['Revenue'].astype(str).str.replace('[₦,]', '', regex=True)
                df['Revenue_Clean'] = pd.to_numeric(df['Revenue_Clean'], errors='coerce')
                if df['Revenue_Clean'].isnull().any(): st.warning("Some 'Revenue' values non-numeric.")
                top_products = df.sort_values(by="Revenue_Clean", ascending=False).head(3) # Show top 3
                st.write("Top Products by Revenue:")
                st.dataframe(top_products[['Product', 'Revenue']])
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Needs 'Product' & 'Revenue' cols.")
    else: st.info("Upload data file.")
st.markdown("---")


# --- 6. Generated Campaign Content Section --- ADDED SECTION ---
st.subheader("💡 Generated Campaign Content")

# Generate content only if we have product info from image analysis
if product_info and market_data:
    campaign_copy = generate_campaign_content(product_info, market_data) # Call helper function

    st.write("**Suggested Headline:**")
    st.markdown(f"> {campaign_copy['headline']}") # Use blockquote markdown

    st.write("**Suggested Body Text:**")
    st.markdown(f"> {campaign_copy['body']}")

    st.write("**Suggested Call to Action (CTA):**")
    st.markdown(f"> {campaign_copy['cta']}")

    st.write("**Suggested Hashtags:**")
    st.text(campaign_copy['hashtags']) # Use st.text for plain text display of hashtags

# Add alternative message if analysis results aren't available
elif df is not None and 'Product' in df.columns:
    # Basic message if only data file is uploaded
    st.info("Upload a product image to generate more specific campaign content. Based on your data, focus marketing efforts on top products.")
else:
    st.info("Upload a product image and/or data file to generate campaign suggestions.")


# --- 7. Footer ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

