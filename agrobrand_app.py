# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 2: Real Image Recognition Integration
# Focus: AI Assistant for Agribusiness (Option A)
# Enhancements: Google Vision AI replaces image mock
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# --- Core Libraries ---
import streamlit as st
import pandas as pd
from PIL import Image
import io
import time
from datetime import datetime
import random
import base64
import os
import json

# --- PDF Generation ---
from fpdf import FPDF # Requires: pip install fpdf

# --- Google Cloud Vision AI Integration ---
# Requires: pip install google-cloud-vision
# Requires: Google Cloud Project setup, Vision API enabled, Billing enabled
# Requires: Service Account Key JSON file & Credentials Setup (see notes below)
from google.cloud import vision
from google.oauth2 import service_account

# --- Credentials Setup Reminder ---
# For Local Testing: Set Environment Variable 'GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/keyfile.json'
# For Deployment (Streamlit Cloud): Set Secret 'google_cloud_credentials_json' = content of keyfile.json


# --- NEW FUNCTION: Real Image Recognition using Google Cloud Vision API ---
def identify_product_via_web(image_bytes):
    """
    Uses Google Cloud Vision API to identify labels in the provided image bytes.
    Handles credential loading securely (Streamlit Secrets or ENV Variable).
    Returns a dictionary similar to the mock, or None on failure.
    """
    credentials = None
    client = None
    # --- 1. Load Credentials Securely ---
    try:
        creds_json_str = st.secrets["google_cloud_credentials_json"]
        creds_info = json.loads(creds_json_str)
        credentials = service_account.Credentials.from_service_account_info(creds_info)
    except KeyError:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            try:
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
            except Exception as e:
                st.error(f"Error loading credentials from file path [{credentials_path}]: {e}")
                return None
        else:
            st.error("Google Cloud credentials not found. Configure secrets or GOOGLE_APPLICATION_CREDENTIALS env var.")
            return None
    except Exception as e:
        st.error(f"An error occurred loading credentials: {e}")
        return None

    # --- 2. Instantiate Vision AI Client ---
    try:
        if credentials: client = vision.ImageAnnotatorClient(credentials=credentials)
        else: client = vision.ImageAnnotatorClient() # Try Application Default Credentials
    except Exception as e:
        st.error(f"Failed to create Vision AI client: {e}")
        return None

    # --- 3. Prepare Image and Call API ---
    st.info("👁️ Analyzing image with Google Vision AI...")
    product_info = None
    try:
        with st.spinner('Calling Vision API...'):
            image = vision.Image(content=image_bytes)
            response = client.label_detection(image=image)
            if response.error.message:
                st.error(f"Vision API Error: {response.error.message}")
                return None
            labels = response.label_annotations
    except Exception as e:
        st.error(f"Vision API call failed: {e}")
        return None

    # --- 4. Parse Response and Format Output ---
    if not labels:
        st.warning("Vision AI did not detect any labels for this image.")
        return None

    best_label = None; highest_score = 0.0
    plausible_keywords = ["fruit", "vegetable", "food", "plant", "crop", "fish", "yam", "plantain", "pepper", "tomato", "catfish", "cassava", "maize", "okra", "onion", "garlic", "ginger", "cabbage", "lettuce", "mango", "orange", "pineapple", "banana", "pawpaw"]
    print("--- Vision AI Labels ---") # Debugging
    for label in labels:
        print(f"- {label.description} (Score: {label.score:.3f})")
        is_plausible = any(keyword.lower() in label.description.lower() for keyword in plausible_keywords)
        if is_plausible and label.score > highest_score: best_label = label; highest_score = label.score
        elif not best_label and label.score > highest_score: best_label = label; highest_score = label.score
    print("------------------------")

    if best_label:
        product_name = best_label.description.capitalize()
        confidence = best_label.score
        st.success(f"✅ Vision AI identified: {product_name} (Confidence: {confidence*100:.1f}%)")
        product_info = {"product": product_name, "condition": "Unknown (via AI)", "setting": "Unknown (via AI)", "confidence": confidence}
    else:
        st.warning("Could not select a primary product label from Vision AI results.")

    return product_info
# --- END OF NEW FUNCTION ---


# --- Mocked Market Price Fetch (Still Mocked for Now) ---
def fetch_market_price(product_name):
    """
    IMPROVED Placeholder: Simulates fetching market prices, includes more products.
    (This will be the next function to replace in Phase 2)
    """
    st.info(f"Simulating market price fetch for {product_name}...")
    time.sleep(0.5) # Reduced sleep time
    price_trends = {
        "Catfish": {"price_range": "₦1,800 – ₦2,200/kg", "location": "Shasha Market, Akure", "trend": "Rising slightly due to feed cost"},
        "Plantain": {"price_range": "₦800 – ₦1,200/bunch", "location": "Erekesan Market, Akure", "trend": "Stable, peak season approaching"},
        "Yam": {"price_range": "₦1,000 – ₦1,500/medium tuber", "location": "Oja Oba, Akure", "trend": "Fluctuating with supply"},
        "Bell pepper": {"price_range": "₦1,500 – ₦2,000/small basket", "location": "Neighbourhood Mkt, Akure", "trend": "Generally stable"}, # Adjusted name based on Vision AI output possibility
        "Tomato": {"price_range": "₦2,500 – ₦4,000/small basket", "location": "Shasha Market, Akure", "trend": "Seasonally high, risk of spoilage"},
        "Fruit": {"price_range": "Varies widely", "location": "General Markets, Akure", "trend": "Depends on specific fruit"}, # Handle generic labels
        "Vegetable": {"price_range": "Varies widely", "location": "General Markets, Akure", "trend": "Depends on specific vegetable"}, # Handle generic labels
        "Food": {"price_range": "N/A", "location": "N/A", "trend": "Too generic for pricing"},
        "Cocoa": {"price_range": "₦1,500,000 – ₦1,800,000/tonne", "location": "Ondo State Cooperatives", "trend": "High volatility, global factors"},
    }
    base_info = price_trends.get(product_name, {"price_range": "N/A", "location": "N/A", "trend": "No specific data available"})
    adverbs = ["Currently", "Reportedly", "Generally", "Locally"]
    if base_info['trend'] != 'N/A' and 'No specific data' not in base_info['trend']:
         base_info['trend'] = f"{random.choice(adverbs)}: {base_info['trend']}"
    return base_info


# --- Helper Function for Content Generation ---
# (generate_campaign_content function remains the same)
def generate_campaign_content(product_info, market_data):
    # ... (definition unchanged) ...
    headline = "Quality Farm Products Available!" # ... (rest of logic unchanged)
    body = "Get the best farm-fresh products today."; cta = "Contact us now to order! [Your Phone Number/WhatsApp]"; hashtags = "#FarmFresh #NigeriaAgro #SupportLocalFarmers"
    if product_info and product_info.get('product'): product_name = product_info.get('product'); condition = product_info.get('condition', 'Quality'); headline = f"Premium {condition} {product_name} - Available Now!"; # ...
    if market_data.get('location') and "Akure" in market_data.get('location'): headline += " In Akure!" # ... (rest of logic unchanged)
    body = f"Looking for top {condition.lower()} {product_name}? Look no further! "; # ... (rest of logic unchanged)
    if market_data.get('trend') and market_data.get('trend') != 'N/A': body += f"Market trend shows: {market_data.get('trend')}. Secure yours today! " # ... (rest of logic unchanged)
    body += f"Ideal for home use or business."; cta = f"Order your {product_name} now! Call/WhatsApp [Your Phone Number/WhatsApp]."; # ... (rest of logic unchanged)
    if market_data.get('location') and market_data.get('location') != 'N/A': cta += f" Pickup available near {market_data.get('location')}." # ... (rest of logic unchanged)
    product_tag = product_name.replace(" ", ""); hashtags_list = ["#FarmFresh", f"#{product_tag}", "#Akure", "#OndoState", "#NaijaMade", "#Agribusiness", "#SupportLocal"]; # ... (rest of logic unchanged)
    if market_data.get('location') and "Shasha" in market_data.get('location'): hashtags_list.append("#ShashaMarket") # ... (rest of logic unchanged)
    if market_data.get('location') and "Erekesan" in market_data.get('location'): hashtags_list.append("#ErekesanMarket") # ... (rest of logic unchanged)
    if market_data.get('location') and "Oja Oba" in market_data.get('location'): hashtags_list.append("#OjaOba") # ... (rest of logic unchanged)
    hashtags = " ".join(hashtags_list)
    return {"headline": headline, "body": body, "cta": cta, "hashtags": hashtags}


# --- PDF Generation Function ---
# (generate_campaign_pdf function remains the same)
def generate_campaign_pdf(product_info, market_data, campaign_copy, image=None):
    # ... (definition unchanged) ...
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "AgroBrand AI Campaign Suggestion", ln=True, align='C'); pdf.ln(5); # ... (rest of PDF generation logic)
    pdf.set_font("Arial", size=10); current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); pdf.cell(0, 5, f"Generated on: {current_date} WAT", ln=True, align='R'); pdf.ln(5); # ...
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Product & Market Information:", ln=True); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, f"- Product: {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)"); pdf.multi_cell(0, 5, f"- Condition: {product_info.get('condition', 'N/A')}"); pdf.multi_cell(0, 5, f"- Price ({market_data.get('location', 'N/A')}): {market_data.get('price_range', 'N/A')}"); pdf.multi_cell(0, 5, f"- Market Trend: {market_data.get('trend', 'N/A')}"); pdf.ln(5); # ...
    if image: try: # ... (image embedding logic)
            with io.BytesIO() as image_buffer: image.save(image_buffer, format="PNG"); image_buffer.seek(0); pdf.image(image_buffer, x=pdf.get_x() + 120, y=pdf.get_y() - 30, w=60, type='PNG'); pdf.ln(5)
        except Exception as e: st.warning(f"Could not embed image in PDF: {e}") # ...
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Generated Campaign Content:", ln=True); pdf.set_font("Arial", size=11); # ... (rest of campaign copy writing to PDF)
    pdf.set_font("Arial", 'B', 11); pdf.write(5, "Headline: "); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, campaign_copy['headline']); pdf.ln(2); # ...
    pdf.set_font("Arial", 'B', 11); pdf.write(5, "Body Text: "); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, campaign_copy['body']); pdf.ln(2); # ...
    pdf.set_font("Arial", 'B', 11); pdf.write(5, "Call to Action (CTA): "); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, campaign_copy['cta']); pdf.ln(2); # ...
    pdf.set_font("Arial", 'B', 11); pdf.write(5, "Hashtags: "); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, campaign_copy['hashtags']); pdf.ln(5); # ...
    pdf.set_font("Arial", 'I', 8); pdf.cell(0, 10, "--- Generated by AgroBrand Fusion AI ---", ln=True, align='C'); pdf_output_buffer = io.BytesIO(); pdf.output(pdf_output_buffer); return pdf_output_buffer.getvalue()


# --- 1. Page Configuration ---
st.set_page_config(page_title="AgroBrand Fusion AI", layout="wide")

# --- 2. Main Application Interface ---
st.title("🌾 AgroBrand Fusion AI")
st.markdown("Your AI Assistant for Agribusiness Marketing & Pricing Insights across Nigeria and beyond.")
st.markdown("*(Now with Real Image Recognition via Google Cloud Vision!)*") # Added note
st.markdown("---")

# --- 3. Sidebar for User Inputs ---
# (Sidebar remains the same)
st.sidebar.header("Upload Your Assets Here")
uploaded_image = st.sidebar.file_uploader("1. Upload Product Image", type=["png", "jpg", "jpeg"])
uploaded_file = st.sidebar.file_uploader("2. Upload Sales/Cost Sheet", type=["csv", "xlsx"])

# --- 4. Asset Previews ---
# (Previews section remains the same)
image_bytes = None; pil_image = None; product_info = None; market_data = None; df = None # Initialize
col1, col2 = st.columns(2)
with col1: st.subheader("Image Preview"); # ... (image preview logic)
if uploaded_image is not None: try: pil_image = Image.open(uploaded_image); st.image(pil_image, caption=f"Uploaded: {uploaded_image.name}", use_column_width=True); uploaded_image.seek(0); image_bytes = uploaded_image.read() except Exception as e: st.error(f"Error displaying image: {e}")
else: st.info("No image uploaded.")
with col2: st.subheader("Data Preview"); # ... (data preview logic)
if uploaded_file is not None: try: # ... (file reading)
    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
    if df is not None: st.success(f"Loaded '{uploaded_file.name}'. Preview:"); st.dataframe(df.head())
    else: st.warning("Could not process file.")
except Exception as e: st.error(f"Error reading data file: {e}"); df = None
else: st.info("No data file uploaded.")
st.markdown("---")

# --- 5. Analysis Results Section ---
# (Logic calling identify_product_via_web and fetch_market_price remains the same)
st.subheader("🤖 AI Analysis & Insights")
if image_bytes:
    # This now calls the REAL Vision AI function
    product_info = identify_product_via_web(image_bytes)
    if product_info and product_info.get('product'):
        # This still calls the MOCKED market price function
        market_data = fetch_market_price(product_info['product'])

# (Display logic in columns remains the same)
col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)
with col_img_analysis: st.write("**Image Analysis:**"); # ... (display product_info)
if product_info: st.markdown(f"- **Product:** {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)"); st.markdown(f"- **Condition:** {product_info.get('condition', 'N/A')}"); st.markdown(f"- **Setting:** {product_info.get('setting', 'N/A')}")
else: st.info("Upload image for AI analysis.")
with col_mkt_analysis: st.write("**Market Insights:**"); # ... (display market_data)
if market_data: st.markdown(f"- **Price ({market_data.get('location', 'N/A')}):** {market_data.get('price_range', 'N/A')}"); st.markdown(f"- **Trend:** {market_data.get('trend', 'N/A')}")
else: st.info("Requires image analysis first.")
with col_data_analysis: st.write("**Data Highlights:**"); # ... (display df analysis)
if df is not None:
    required_cols = ['Product', 'Revenue']; # ... (df analysis logic)
    if all(col in df.columns for col in required_cols):
        try: df['Revenue_Clean'] = df['Revenue'].astype(str).str.replace('[₦,]', '', regex=True); df['Revenue_Clean'] = pd.to_numeric(df['Revenue_Clean'], errors='coerce'); #...
        if df['Revenue_Clean'].isnull().any(): st.warning("Some 'Revenue' values non-numeric.") #...
        top_products = df.sort_values(by="Revenue_Clean", ascending=False).head(3); st.write("Top Products by Revenue:"); st.dataframe(top_products[['Product', 'Revenue']])
        except Exception as e: st.error(f"Error: {e}")
    else: st.warning("Needs 'Product' & 'Revenue' cols.")
else: st.info("Upload data file for analysis.")
st.markdown("---")


# --- 6. Generated Campaign Content Section ---
# (Content generation and download button logic remains the same)
st.subheader("💡 Generated Campaign Content")
campaign_copy = None
if product_info and market_data:
    campaign_copy = generate_campaign_content(product_info, market_data)
    # (Display logic remains same)
    st.write("**Suggested Headline:**"); st.markdown(f"> {campaign_copy['headline']}") # ...
    st.write("**Suggested Body Text:**"); st.markdown(f"> {campaign_copy['body']}") # ...
    st.write("**Suggested Call to Action (CTA):**"); st.markdown(f"> {campaign_copy['cta']}") # ...
    st.write("**Suggested Hashtags:**"); st.text(campaign_copy['hashtags']) # ...
    st.markdown("---")
    # (Download button logic remains same)
    col_txt, col_pdf = st.columns(2)
    with col_txt: try: # ... TXT Download ...
        current_date_str = datetime.now().strftime("%Y%m%d"); product_name_for_file = product_info.get('product', 'campaign').lower().replace(' ', '_'); txt_file_name = f"{product_name_for_file}_campaign_{current_date_str}.txt"; # ...
        text_file_content = f"""--- AgroBrand AI Campaign Suggestions ---\nGenerated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} WAT\n\nProduct: {product_info.get('product', 'N/A')}\n\nHeadline:\n{campaign_copy['headline']}\n\nBody Text:\n{campaign_copy['body']}\n\nCall to Action (CTA):\n{campaign_copy['cta']}\n\nHashtags:\n{campaign_copy['hashtags']}\n\n--- Generated by AgroBrand Fusion AI ---"""; # ...
        st.download_button(label="Download Copy (.txt)", data=text_file_content.encode('utf-8'), file_name=txt_file_name, mime='text/plain')
    except Exception as e: st.error(f"Error (TXT DL): {e}") # ...
    with col_pdf: try: # ... PDF Download ...
        pdf_bytes = generate_campaign_pdf(product_info, market_data, campaign_copy, pil_image); current_date_str = datetime.now().strftime("%Y%m%d"); product_name_for_file = product_info.get('product', 'campaign').lower().replace(' ', '_'); pdf_file_name = f"{product_name_for_file}_campaign_{current_date_str}.pdf"; # ...
        b64_pdf = base64.b64encode(pdf_bytes).decode(); pdf_download_link = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{pdf_file_name}">Download Report (.pdf)</a>'; st.markdown(pdf_download_link, unsafe_allow_html=True)
    except Exception as e: st.error(f"Error generating PDF download: {e}") # ...

elif df is not None and 'Product' in df.columns:
    st.info("Upload a product image for full campaign generation and download options.")
else:
    st.info("Upload a product image and/or data file to generate campaign suggestions.")


# --- 7. Footer ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

