# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 2: Real Market Price Data Integration
# Focus: AI Assistant for Agribusiness
# Enhancements: World Bank Data replaces market price mock
# Origin Context: Akure, Ondo State, Nigeria
# Date: May 12, 2025
# --------------------------------------------------------------------------

# --- Core Libraries ---
import streamlit as st
import pandas as pd
from PIL import Image
import io
import time # Still used for some UI simulation, but less critical for core logic now
from datetime import datetime
import random # Still used for some UI simulation
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

# --- Real Image Recognition using Google Cloud Vision API ---
# (identify_product_via_web function definition remains here as defined previously)
def identify_product_via_web(image_bytes):
    credentials = None; client = None # ... (rest of the function definition as before) ...
    try: creds_json_str = st.secrets["google_cloud_credentials_json"]; creds_info = json.loads(creds_json_str); credentials = service_account.Credentials.from_service_account_info(creds_info)
    except KeyError:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path: try: credentials = service_account.Credentials.from_service_account_file(credentials_path)
            except Exception as e: st.error(f"Error loading credentials from file path [{credentials_path}]: {e}"); return None
        else: st.error("Google Cloud credentials not found. Configure secrets or GOOGLE_APPLICATION_CREDENTIALS env var."); return None
    except Exception as e: st.error(f"An error occurred loading credentials: {e}"); return None
    try:
        if credentials: client = vision.ImageAnnotatorClient(credentials=credentials)
        else: client = vision.ImageAnnotatorClient()
    except Exception as e: st.error(f"Failed to create Vision AI client: {e}"); return None
    st.info("👁️ Analyzing image with Google Vision AI..."); product_info = None
    try:
        with st.spinner('Calling Vision API...'): image = vision.Image(content=image_bytes); response = client.label_detection(image=image)
            if response.error.message: st.error(f"Vision API Error: {response.error.message}"); return None
            labels = response.label_annotations
    except Exception as e: st.error(f"Vision API call failed: {e}"); return None
    if not labels: st.warning("Vision AI did not detect any labels for this image."); return None
    best_label = None; highest_score = 0.0; plausible_keywords = ["fruit", "vegetable", "food", "plant", "crop", "fish", "yam", "plantain", "pepper", "tomato", "catfish", "cassava", "maize", "okra", "onion", "garlic", "ginger", "cabbage", "lettuce", "mango", "orange", "pineapple", "banana", "pawpaw"]
    # print("--- Vision AI Labels ---"); # Debugging
    for label in labels: # print(f"- {label.description} (Score: {label.score:.3f})") # Debugging
        is_plausible = any(keyword.lower() in label.description.lower() for keyword in plausible_keywords)
        if is_plausible and label.score > highest_score: best_label = label; highest_score = label.score
        elif not best_label and label.score > highest_score: best_label = label; highest_score = label.score
    # print("------------------------"); # Debugging
    if best_label: product_name = best_label.description.capitalize(); confidence = best_label.score; st.success(f"✅ Vision AI identified: {product_name} (Confidence: {confidence*100:.1f}%)"); product_info = {"product": product_name, "condition": "Unknown (via AI)", "setting": "Unknown (via AI)", "confidence": confidence}
    else: st.warning("Could not select a primary product label from Vision AI results.")
    return product_info


# --- NEW FUNCTIONS for World Bank Data ---
@st.cache_data # Cache the data loading and preprocessing
def load_world_bank_data(file_path="WB_Nigeria_Food_Prices.csv"):
    """
    Loads and preprocesses the World Bank Food Price data from a local CSV file.
    Returns a Pandas DataFrame or None if loading fails.
    CRITICAL: User must download the CSV and adjust column_map if necessary.
    """
    try:
        df_wb = pd.read_csv(file_path)
        st.success(f"Successfully loaded World Bank data from '{file_path}'")
        # --- Basic Preprocessing ---
        # !!! ADJUST THIS MAPPING BASED ON YOUR ACTUAL CSV HEADERS !!!
        column_map = {
            'date': 'Date', 'Date': 'Date', 'observation_date': 'Date', # Common date column names
            'market': 'Market_Name', 'Market': 'Market_Name', 'market_name': 'Market_Name',
            'product': 'Product_Name', 'Product': 'Product_Name', 'product_name': 'Product_Name', 'item_name': 'Product_Name',
            'unit': 'Unit', 'Unit': 'Unit', 'unit_of_measure': 'Unit',
            'price': 'Price', 'Price': 'Price', 'value': 'Price'
        }
        df_wb.rename(columns={k: v for k, v in column_map.items() if k in df_wb.columns}, inplace=True)
        required_cols = ['Date', 'Market_Name', 'Product_Name', 'Unit', 'Price']
        if not all(col in df_wb.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df_wb.columns]
            st.error(f"WB data CSV missing required columns: {missing}. Check file/column_map.")
            return None
        try:
            df_wb['Date'] = pd.to_datetime(df_wb['Date'])
        except Exception as date_err:
            st.error(f"Error parsing 'Date' in WB data: {date_err}. Check date format.")
            return None
        df_wb['Price'] = pd.to_numeric(df_wb['Price'], errors='coerce')
        df_wb.dropna(subset=['Price', 'Product_Name', 'Market_Name'], inplace=True) # Drop rows with critical missing data
        st.info(f"World Bank data processed: {len(df_wb)} records, latest date: {df_wb['Date'].max().strftime('%Y-%m-%d') if not df_wb.empty else 'N/A'}")
        return df_wb
    except FileNotFoundError:
        st.error(f"CRITICAL: World Bank data file not found at '{file_path}'. Download it and place it in the script's directory.")
        return None
    except Exception as e:
        st.error(f"Error loading/processing World Bank data: {e}")
        return None

def fetch_market_price(product_name):
    """
    Fetches the most recent market price for a product from the loaded World Bank data.
    (Replaces the previous mock function)
    """
    st.info(f"Looking up '{product_name}' in World Bank data...")
    df_world_bank = load_world_bank_data()
    if df_world_bank is None or df_world_bank.empty:
        st.warning("World Bank price data is unavailable for lookup.")
        return {"price": "N/A", "unit": "", "location": "WB Data Unavailable", "date": "N/A", "trend": ""}
    try:
        # Attempt to match product name (case-insensitive, partial match)
        # For better matching, consider a mapping dictionary or fuzzy matching later
        product_match_filter = df_world_bank['Product_Name'].str.contains(product_name, case=False, na=False)
        product_df = df_world_bank[product_match_filter]

        # Try exact match if partial yields nothing or Vision AI is specific
        if product_df.empty:
            exact_match_filter = df_world_bank['Product_Name'].str.lower() == product_name.lower()
            product_df = df_world_bank[exact_match_filter]

        if product_df.empty:
            st.warning(f"No price data found for '{product_name}' in the World Bank dataset.")
            return {"price": "N/A", "unit": "", "location": "Product Not Found in WB Data", "date": "N/A", "trend": ""}

        latest_date = product_df['Date'].max()
        latest_date_str = latest_date.strftime('%Y-%m-%d')
        latest_product_df = product_df[product_df['Date'] == latest_date].copy()
        market_priority = ["Akure", "Ibadan", "Lagos"] # Prioritize these markets
        result_row = None
        for market in market_priority:
            market_match_filter = latest_product_df['Market_Name'].str.contains(market, case=False, na=False)
            market_df_filtered = latest_product_df[market_match_filter]
            if not market_df_filtered.empty:
                result_row = market_df_filtered.iloc[0]; break
        if result_row is None and not latest_product_df.empty:
            result_row = latest_product_df.iloc[0] # Fallback to first available market

        if result_row is not None:
            price = result_row['Price']; unit = result_row['Unit']; location = result_row['Market_Name']
            try: formatted_price = f"₦{price:,.2f}" if pd.notna(price) else "N/A"
            except (ValueError, TypeError): formatted_price = str(price) if pd.notna(price) else "N/A"
            st.success(f"Found price for '{product_name}' in '{location}' on {latest_date_str}")
            return {"price": formatted_price, "unit": unit if pd.notna(unit) else "", "location": location if pd.notna(location) else "Unknown Market", "date": latest_date_str, "trend": f"Source: WB Monthly Data ({latest_date_str})"}
        else:
            st.warning(f"Could not find specific market price for '{product_name}' on {latest_date_str}.")
            return {"price": "N/A", "unit": "", "location": "Market Not Found for Date", "date": latest_date_str, "trend": ""}
    except Exception as e:
        st.error(f"Error during price lookup for '{product_name}': {e}")
        return {"price": "Error", "unit": "", "location": "Lookup Failed", "date": "N/A", "trend": ""}
# --- END OF NEW World Bank Data Functions ---


# --- Helper Function for Content Generation ---
# (generate_campaign_content function remains the same)
def generate_campaign_content(product_info, market_data): # ... (definition unchanged)
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
def generate_campaign_pdf(product_info, market_data, campaign_copy, image=None): # ... (definition unchanged)
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "AgroBrand AI Campaign Suggestion", ln=True, align='C'); pdf.ln(5); # ... (rest of PDF generation logic)
    pdf.set_font("Arial", size=10); current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); pdf.cell(0, 5, f"Generated on: {current_date} WAT", ln=True, align='R'); pdf.ln(5); # ...
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Product & Market Information:", ln=True); pdf.set_font("Arial", size=11); pdf.multi_cell(0, 5, f"- Product: {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)"); pdf.multi_cell(0, 5, f"- Condition: {product_info.get('condition', 'N/A')}"); pdf.multi_cell(0, 5, f"- Price ({market_data.get('location', 'N/A')}): {market_data.get('price', 'N/A')}"); pdf.multi_cell(0, 5, f"- Unit: {market_data.get('unit', 'N/A')}"); pdf.multi_cell(0, 5, f"- Data Date: {market_data.get('date', 'N/A')}"); pdf.multi_cell(0, 5, f"- Market Trend/Source: {market_data.get('trend', 'N/A')}"); pdf.ln(5); # Added Unit, Date, updated Trend/Source for PDF
    if image: try: # ... (image embedding logic)
            with io.BytesIO() as image_buffer: image.save(image_buffer, format="PNG"); image_buffer.seek(0); pdf.image(image_buffer, x=pdf.get_x() + 120, y=pdf.get_y() - 35, w=60, type='PNG'); pdf.ln(5) # Adjusted y offset
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
st.markdown("*(Image Recognition: Google Vision AI | Market Prices: World Bank Monthly Data)*") # Updated note
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
st.subheader("🤖 AI Analysis & Insights")
if image_bytes:
    product_info = identify_product_via_web(image_bytes) # Uses Google Vision AI
    if product_info and product_info.get('product'):
        market_data = fetch_market_price(product_info['product']) # Uses World Bank Data
# (Display logic in columns remains the same, but ensure new fields like 'date', 'unit' from market_data are shown)
col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)
with col_img_analysis: st.write("**Image Analysis:**"); # ... display product_info
if product_info: st.markdown(f"- **Product:** {product_info.get('product', 'N/A')} ({product_info.get('confidence', 0)*100:.1f}%)"); st.markdown(f"- **Condition:** {product_info.get('condition', 'N/A')}"); st.markdown(f"- **Setting:** {product_info.get('setting', 'N/A')}")
else: st.info("Upload image for AI analysis.")
with col_mkt_analysis: st.write("**Market Insights (WB Data):**"); # Updated title
if market_data:
    st.markdown(f"- **Price ({market_data.get('location', 'N/A')}):** {market_data.get('price', 'N/A')}")
    st.markdown(f"- **Unit:** {market_data.get('unit', 'N/A')}")
    st.markdown(f"- **Data Date:** {market_data.get('date', 'N/A')}")
    st.markdown(f"- **Source/Trend:** {market_data.get('trend', 'N/A')}") # Now indicates WB data and date
else: st.info("Requires successful image analysis & product match in WB data.")
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
st.subheader("💡 Generated Campaign Content") # ... (rest of the section)
campaign_copy = None
if product_info and market_data and market_data.get('price') != 'N/A': # Ensure we have valid market data
    campaign_copy = generate_campaign_content(product_info, market_data)
    st.write("**Suggested Headline:**"); st.markdown(f"> {campaign_copy['headline']}")
    st.write("**Suggested Body Text:**"); st.markdown(f"> {campaign_copy['body']}")
    st.write("**Suggested Call to Action (CTA):**"); st.markdown(f"> {campaign_copy['cta']}")
    st.write("**Suggested Hashtags:**
