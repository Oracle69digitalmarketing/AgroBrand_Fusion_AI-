# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 1: MVP Prototype Structure
# Focus: AI Assistant for Agribusiness (Option A)
# Enhancements: Improved Mocks, PDF Export Added
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# Import necessary libraries
import streamlit as st
import pandas as pd
from PIL import Image
import io
import time
from datetime import datetime
import random # Added for more dynamic mocks
from fpdf import FPDF # Added for PDF generation
import base64 # Added for PDF download link

# --- Improved Mocked Analysis Functions ---

MOCK_PRODUCTS = [
    {"product": "Catfish", "condition": "Fresh", "setting": "Harvest Basin"},
    {"product": "Plantain", "condition": "Ripe", "setting": "Bunch"},
    {"product": "Yam", "condition": "Large Tuber", "setting": "On Display"},
    {"product": "Bell Peppers", "condition": "Mixed Colors", "setting": "Basket"},
    {"product": "Tomatoes", "condition": "Firm", "setting": "Crate"}
]

def identify_product_via_web(image_bytes):
    """
    IMPROVED Placeholder: Simulates AI image recognition, randomly selects product.
    """
    st.info("Simulating image recognition...")
    time.sleep(1)
    chosen_product = random.choice(MOCK_PRODUCTS) # Randomly select from list
    confidence = random.uniform(0.75, 0.98) # Random confidence
    chosen_product['confidence'] = confidence
    return chosen_product

def fetch_market_price(product_name):
    """
    IMPROVED Placeholder: Simulates fetching market prices, includes more products.
    """
    st.info(f"Simulating market price fetch for {product_name}...")
    time.sleep(1)
    # Expanded mock data
    price_trends = {
        "Catfish": {"price_range": "₦1,800 – ₦2,200/kg", "location": "Shasha Market, Akure", "trend": "Rising slightly due to feed cost"},
        "Plantain": {"price_range": "₦800 – ₦1,200/bunch", "location": "Erekesan Market, Akure", "trend": "Stable, peak season approaching"},
        "Yam": {"price_range": "₦1,000 – ₦1,500/medium tuber", "location": "Oja Oba, Akure", "trend": "Fluctuating with supply"},
        "Bell Peppers": {"price_range": "₦1,500 – ₦2,000/small basket", "location": "Neighbourhood Mkt, Akure", "trend": "Generally stable"},
        "Tomatoes": {"price_range": "₦2,500 – ₦4,000/small basket", "location": "Shasha Market, Akure", "trend": "Seasonally high, risk of spoilage"},
        "Cocoa": {"price_range": "₦1,500,000 – ₦1,800,000/tonne", "location": "Ondo State Cooperatives", "trend": "High volatility, global factors"},
    }
    # Add a bit more dynamic text to trend
    base_info = price_trends.get(product_name, {"price_range": "N/A", "location": "N/A", "trend": "No specific data available"})
    adverbs = ["Currently", "Reportedly", "Generally", "Locally"]
    if base_info['trend'] != 'N/A':
         base_info['trend'] = f"{random.choice(adverbs)}: {base_info['trend']}"
    return base_info


# --- Helper Function for Content Generation ---
# (generate_campaign_content function remains the same as before)
def generate_campaign_content(product_info, market_data):
    # ... (function definition is unchanged) ...
    headline = "Quality Farm Products Available!"
    body = "Get the best farm-fresh products today."
    cta = "Contact us now to order! [Your Phone Number/WhatsApp]"
    hashtags = "#FarmFresh #NigeriaAgro #SupportLocalFarmers"
    if product_info and product_info.get('product'):
        product_name = product_info.get('product'); condition = product_info.get('condition', 'Quality')
        headline = f"Premium {condition} {product_name} - Available Now!"
        if market_data.get('location') and "Akure" in market_data.get('location'): headline += " In Akure!"
        body = f"Looking for top {condition.lower()} {product_name}? Look no further! "; #... (rest of body logic)
        if market_data.get('trend') and market_data.get('trend') != 'N/A': body += f"Market trend shows: {market_data.get('trend')}. Secure yours today! "
        body += f"Ideal for home use or business."
        cta = f"Order your {product_name} now! Call/WhatsApp [Your Phone Number/WhatsApp]."; #... (rest of cta logic)
        if market_data.get('location') and market_data.get('location') != 'N/A': cta += f" Pickup available near {market_data.get('location')}."
        product_tag = product_name.replace(" ", ""); hashtags_list = ["#FarmFresh", f"#{product_tag}", "#Akure", "#OndoState", "#NaijaMade", "#Agribusiness", "#SupportLocal"]; #... (rest of hashtag logic)
        if market_data.get('location') and "Shasha" in market_data.get('location'): hashtags_list.append("#ShashaMarket")
        if market_data.get('location') and "Erekesan" in market_data.get('location'): hashtags_list.append("#ErekesanMarket")
        if market_data.get('location') and "Oja Oba" in market_data.get('location'): hashtags_list.append("#OjaOba")
        hashtags = " ".join(hashtags_list)
    return {"headline": headline, "body": body, "cta": cta, "hashtags": hashtags}


# --- ADDED PDF Generation Function ---
def generate_campaign_pdf(product_info, market_data, campaign_copy, image=None):
    """
    Generates a PDF report with campaign suggestions and optionally an image.
    Inputs: product_info (dict), market_data (dict), campaign_copy (dict), image (PIL Image object)
    Output: PDF content as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)

    # Title
    pdf.cell(0, 10, "AgroBrand AI Campaign Suggestion", ln=True, align='C')
    pdf.ln(5)

    # Date Generated
    pdf.set_font("Arial", size=10)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 5, f"Generated on: {current_date} WAT", ln=True, align='R')
    pdf.ln(5)

    # Product Info Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Product & Market Information:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, f"- Product: {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)")
    pdf.multi_cell(0, 5, f"- Condition: {product_info.get('condition', 'N/A')}")
    pdf.multi_cell(0, 5, f"- Price ({market_data.get('location', 'N/A')}): {market_data.get('price_range', 'N/A')}")
    pdf.multi_cell(0, 5, f"- Market Trend: {market_data.get('trend', 'N/A')}")
    pdf.ln(5)

    # Insert Image if available
    if image:
        try:
            with io.BytesIO() as image_buffer:
                # Save PIL image to buffer in PNG format (PNG is safer for FPDF)
                image.save(image_buffer, format="PNG")
                image_buffer.seek(0)
                # Embed image from buffer
                pdf.image(image_buffer, x=pdf.get_x() + 120, y=pdf.get_y() - 30, w=60, type='PNG') # Position image to the right
                pdf.ln(5) # Add space after potential image height
        except Exception as e:
            st.warning(f"Could not embed image in PDF: {e}") # Non-fatal warning

    # Campaign Copy Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Generated Campaign Content:", ln=True)
    pdf.set_font("Arial", size=11)

    pdf.set_font("Arial", 'B', 11)
    pdf.write(5, "Headline: ")
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, campaign_copy['headline'])
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 11)
    pdf.write(5, "Body Text: ")
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, campaign_copy['body'])
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 11)
    pdf.write(5, "Call to Action (CTA): ")
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, campaign_copy['cta'])
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 11)
    pdf.write(5, "Hashtags: ")
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, campaign_copy['hashtags'])
    pdf.ln(5)

    # Footer
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "--- Generated by AgroBrand Fusion AI ---", ln=True, align='C')

    # Output PDF to a byte buffer
    pdf_output_buffer = io.BytesIO()
    pdf.output(pdf_output_buffer)
    return pdf_output_buffer.getvalue()

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
image_bytes = None
pil_image = None # Store the PIL image object
product_info = None
market_data = None
df = None
col1, col2 = st.columns(2)
with col1:
    st.subheader("Image Preview")
    if uploaded_image is not None:
        try:
            pil_image = Image.open(uploaded_image) # Store PIL image
            st.image(pil_image, caption=f"Uploaded: {uploaded_image.name}", use_column_width=True)
            uploaded_image.seek(0)
            image_bytes = uploaded_image.read()
        except Exception as e: st.error(f"Error displaying image: {e}")
    else: st.info("No image uploaded.")
with col2:
    st.subheader("Data Preview")
    if uploaded_file is not None:
        # ... (data reading logic remains same) ...
        try: # Added try block
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
            if df is not None: st.success(f"Loaded '{uploaded_file.name}'. Preview:"); st.dataframe(df.head())
            else: st.warning("Could not process file.")
        except Exception as e: st.error(f"Error reading data file: {e}"); df = None # Added exception handling
    else: st.info("No data file uploaded.")
st.markdown("---")

# --- 5. Analysis Results Section ---
# (Analysis logic remains the same, but uses improved mocks)
st.subheader("🤖 AI Analysis & Insights")
if image_bytes:
    product_info = identify_product_via_web(image_bytes)
    if product_info and product_info.get('product'):
        market_data = fetch_market_price(product_info['product'])
# (Display logic in columns remains the same)
col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)
with col_img_analysis: st.write("**Image Analysis:**"); # ... display product_info ...
if product_info: st.markdown(f"- **Product:** {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)"); st.markdown(f"- **Condition:** {product_info.get('condition', 'N/A')}"); st.markdown(f"- **Setting:** {product_info.get('setting', 'N/A')}")
else: st.info("Upload image.")
with col_mkt_analysis: st.write("**Market Insights:**"); # ... display market_data ...
if market_data: st.markdown(f"- **Price ({market_data.get('location', 'N/A')}):** {market_data.get('price_range', 'N/A')}"); st.markdown(f"- **Trend:** {market_data.get('trend', 'N/A')}")
else: st.info("Requires image analysis.")
with col_data_analysis: st.write("**Data Highlights:**"); # ... display df analysis ...
if df is not None:
    required_cols = ['Product', 'Revenue']; # ... (analysis logic) ...
    if all(col in df.columns for col in required_cols):
        try:
            df['Revenue_Clean'] = df['Revenue'].astype(str).str.replace('[₦,]', '', regex=True); df['Revenue_Clean'] = pd.to_numeric(df['Revenue_Clean'], errors='coerce')
            if df['Revenue_Clean'].isnull().any(): st.warning("Some 'Revenue' values non-numeric.")
            top_products = df.sort_values(by="Revenue_Clean", ascending=False).head(3); st.write("Top Products by Revenue:"); st.dataframe(top_products[['Product', 'Revenue']])
        except Exception as e: st.error(f"Error: {e}")
    else: st.warning("Needs 'Product' & 'Revenue' cols.")
else: st.info("Upload data file.")
st.markdown("---")


# --- 6. Generated Campaign Content Section ---
st.subheader("💡 Generated Campaign Content")
campaign_copy = None
if product_info and market_data:
    campaign_copy = generate_campaign_content(product_info, market_data)
    # (Display generated copy remains the same)
    st.write("**Suggested Headline:**"); st.markdown(f"> {campaign_copy['headline']}")
    st.write("**Suggested Body Text:**"); st.markdown(f"> {campaign_copy['body']}")
    st.write("**Suggested Call to Action (CTA):**"); st.markdown(f"> {campaign_copy['cta']}")
    st.write("**Suggested Hashtags:**"); st.text(campaign_copy['hashtags'])
    st.markdown("---")

    # --- Download Buttons ---
    col_txt, col_pdf = st.columns(2) # Place buttons side-by-side

    # .txt Download Button
    with col_txt:
        try:
            current_date_str = datetime.now().strftime("%Y%m%d")
            product_name_for_file = product_info.get('product', 'campaign').lower().replace(' ', '_')
            txt_file_name = f"{product_name_for_file}_campaign_{current_date_str}.txt"
            text_file_content = f"""--- AgroBrand AI Campaign Suggestions ---\nGenerated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} WAT\n\nProduct: {product_info.get('product', 'N/A')}\n\nHeadline:\n{campaign_copy['headline']}\n\nBody Text:\n{campaign_copy['body']}\n\nCall to Action (CTA):\n{campaign_copy['cta']}\n\nHashtags:\n{campaign_copy['hashtags']}\n\n--- Generated by AgroBrand Fusion AI ---"""
            st.download_button(
                label="Download Copy (.txt)",
                data=text_file_content.encode('utf-8'),
                file_name=txt_file_name,
                mime='text/plain'
            )
        except Exception as e: st.error(f"Error (TXT DL): {e}")

    # PDF Download Button - ADDED
    with col_pdf:
        try:
            # Generate PDF bytes (pass the PIL image object 'pil_image')
            pdf_bytes = generate_campaign_pdf(product_info, market_data, campaign_copy, pil_image)
            current_date_str = datetime.now().strftime("%Y%m%d")
            product_name_for_file = product_info.get('product', 'campaign').lower().replace(' ', '_')
            pdf_file_name = f"{product_name_for_file}_campaign_{current_date_str}.pdf"

            # Encode PDF bytes to base64 for download link
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            # Create download link using markdown
            pdf_download_link = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{pdf_file_name}">Download Report (.pdf)</a>'
            st.markdown(pdf_download_link, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error generating PDF download: {e}")

elif df is not None and 'Product' in df.columns:
    st.info("Upload a product image to generate campaign content and enable downloads.")
else:
    st.info("Upload a product image and/or data file to generate campaign suggestions.")

# --- 7. Footer ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

