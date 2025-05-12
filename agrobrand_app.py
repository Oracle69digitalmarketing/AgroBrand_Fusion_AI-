# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 2: UI/UX Improvement (Tabs & Reset)
# Focus: AI Assistant for Agribusiness
# Enhancements: Tabs for main content, Reset button, Session State usage
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
from fpdf import FPDF

# --- Google Cloud Vision AI Integration ---
from google.cloud import vision
from google.oauth2 import service_account

# --- Credentials Setup Reminder & Product Map (Keep as before) ---
# ... (PRODUCT_NAME_SYNONYM_MAP definition) ...
PRODUCT_NAME_SYNONYM_MAP = {
    "bell pepper": "Pepper, Bell", "tomato": "Tomatoes", "tomatoes": "Tomatoes",
    "catfish": "Fish, Catfish (fresh)", "yam tuber": "Yam", "yam": "Yam",
    "orange": "Oranges, Sweet", "maize": "Maize (white)", "corn": "Maize (white)",
    "onion": "Onions", "fruit": None, "vegetable": None,
    "plantain": "Plantain (ripe / unripe)",
    "beans": "Beans (brown, dry / white, dry / green)",
    "rice": "Rice (local sold loose / imported)"
}

# --- Helper Functions (identify_product_via_web, load_world_bank_data, fetch_market_price,
#                     generate_campaign_content, generate_campaign_pdf - keep as defined previously) ---

def identify_product_via_web(image_bytes):
    # (Function definition as previously provided - handles credentials, API call, parsing)
    credentials = None; client = None
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
    for label in labels:
        is_plausible = any(keyword.lower() in label.description.lower() for keyword in plausible_keywords)
        if is_plausible and label.score > highest_score: best_label = label; highest_score = label.score
        elif not best_label and label.score > highest_score: best_label = label; highest_score = label.score
    if best_label: product_name = best_label.description.capitalize(); confidence = best_label.score; st.success(f"✅ Vision AI identified: {product_name} (Confidence: {confidence*100:.1f}%)"); product_info = {"product": product_name, "condition": "Unknown (via AI)", "setting": "Unknown (via AI)", "confidence": confidence}
    else: st.warning("Could not select a primary product label from Vision AI results.")
    return product_info

@st.cache_data
def load_world_bank_data(file_path="WB_Nigeria_Food_Prices.csv"):
    # (Function definition as previously provided - loads and preprocesses CSV)
    # !!! REMEMBER TO ADJUST column_map based on your CSV !!!
    try:
        df_wb = pd.read_csv(file_path)
        st.success(f"Successfully loaded World Bank data from '{file_path}'")
        column_map = { # Example mapping - ADJUST TO YOUR CSV
            'date': 'Date', 'Date': 'Date', 'observation_date': 'Date',
            'market': 'Market_Name', 'Market': 'Market_Name', 'market_name': 'Market_Name',
            'product': 'Product_Name', 'Product': 'Product_Name', 'product_name': 'Product_Name', 'item_name': 'Product_Name',
            'unit': 'Unit', 'Unit': 'Unit', 'unit_of_measure': 'Unit',
            'price': 'Price', 'Price': 'Price', 'value': 'Price'
        }
        df_wb.rename(columns={k: v for k, v in column_map.items() if k in df_wb.columns}, inplace=True)
        required_cols = ['Date', 'Market_Name', 'Product_Name', 'Unit', 'Price']
        if not all(col in df_wb.columns for col in required_cols): missing = [col for col in required_cols if col not in df_wb.columns]; st.error(f"WB data CSV missing: {missing}. Check file/map."); return None
        try: df_wb['Date'] = pd.to_datetime(df_wb['Date'])
        except Exception as date_err: st.error(f"Error parsing 'Date' in WB data: {date_err}."); return None
        df_wb['Price'] = pd.to_numeric(df_wb['Price'], errors='coerce')
        df_wb.dropna(subset=['Price', 'Product_Name', 'Market_Name'], inplace=True)
        st.info(f"World Bank data processed: {len(df_wb)} records, latest date: {df_wb['Date'].max().strftime('%Y-%m-%d') if not df_wb.empty else 'N/A'}")
        return df_wb
    except FileNotFoundError: st.error(f"CRITICAL: WB data file '{file_path}' not found. Download & place it correctly."); return None
    except Exception as e: st.error(f"Error loading/processing WB data: {e}"); return None

def fetch_market_price(product_name_from_vision):
    # (Function definition with IMPROVED MARKET FALLBACK TRANSPARENCY, as provided previously)
    st.info(f"Looking up '{product_name_from_vision}' (from Vision AI) in World Bank data...")
    df_world_bank = load_world_bank_data()
    if df_world_bank is None or df_world_bank.empty: st.warning("WB price data unavailable."); return {"price": "N/A", "unit": "", "location": "WB Data Unavailable", "date": "N/A", "trend": ""}
    product_df = pd.DataFrame(); search_term_for_wb = product_name_from_vision.lower(); match_type_info = ""
    try:
        exact_match_filter = df_world_bank['Product_Name'].str.lower() == search_term_for_wb
        product_df = df_world_bank[exact_match_filter]
        if not product_df.empty: match_type_info = f"exact match for '{search_term_for_wb}'"
        if product_df.empty:
            mapped_name = PRODUCT_NAME_SYNONYM_MAP.get(search_term_for_wb)
            if mapped_name:
                match_type_info = f"mapped '{product_name_from_vision}' to '{mapped_name}'"
                search_term_for_wb = mapped_name.lower()
                exact_match_filter_mapped = df_world_bank['Product_Name'].str.lower() == search_term_for_wb
                product_df = df_world_bank[exact_match_filter_mapped]
                if product_df.empty:
                    contains_filter_mapped = df_world_bank['Product_Name'].str.contains(mapped_name, case=False, na=False)
                    product_df = df_world_bank[contains_filter_mapped]
                    if not product_df.empty: match_type_info += ", then partial match"
            elif mapped_name is None: st.warning(f"'{product_name_from_vision}' too generic per map."); return {"price": "N/A", "unit": "", "location": "Product Too Generic", "date": "N/A", "trend": ""}
        if product_df.empty and PRODUCT_NAME_SYNONYM_MAP.get(product_name_from_vision.lower()) is not None :
            match_type_info = f"broad partial match for original '{product_name_from_vision}'"
            search_term_for_wb = product_name_from_vision
            contains_filter_original = df_world_bank['Product_Name'].str.contains(search_term_for_wb, case=False, na=False)
            product_df = df_world_bank[contains_filter_original]
        if not product_df.empty and match_type_info: st.info(f"Product search: Used {match_type_info}.")
        elif not product_df.empty and not match_type_info: st.info("Product search: Defaulted to a match.")
        else: st.warning(f"No price data for '{product_name_from_vision}' in WB dataset."); return {"price": "N/A", "unit": "", "location": "Product Not Found in WB Data", "date": "N/A", "trend": ""}

        latest_date = product_df['Date'].max(); latest_date_str = latest_date.strftime('%Y-%m-%d')
        latest_product_df = product_df[product_df['Date'] == latest_date].copy()
        primary_target_market = "Akure"; market_priority = [primary_target_market, "Ibadan", "Lagos"]; result_row = None; market_source_info = ""
        for market_name_to_check in market_priority:
            market_match_filter = latest_product_df['Market_Name'].str.contains(market_name_to_check, case=False, na=False)
            market_df_filtered = latest_product_df[market_match_filter]
            if not market_df_filtered.empty:
                result_row = market_df_filtered.iloc[0]
                if market_name_to_check == primary_target_market: market_source_info = f"{result_row['Market_Name']} (Primary Target)"
                else: market_source_info = f"{result_row['Market_Name']} (Fallback from {primary_target_market})"
                break
        if result_row is None and not latest_product_df.empty: result_row = latest_product_df.iloc[0]; market_source_info = f"{result_row['Market_Name']} (General Fallback; {primary_target_market} N/A)"
        if result_row is not None:
            price = result_row['Price']; unit = result_row['Unit']; location_display = market_source_info if market_source_info else result_row['Market_Name']
            try: formatted_price = f"₦{price:,.2f}" if pd.notna(price) else "N/A"
            except (ValueError, TypeError): formatted_price = str(price) if pd.notna(price) else "N/A"
            st.success(f"Price for '{product_name_from_vision}' (as '{result_row['Product_Name']}'): {formatted_price} per {unit if pd.notna(unit) else ''} in {location_display} on {latest_date_str}")
            return {"price": formatted_price, "unit": unit if pd.notna(unit) else "", "location": location_display, "date": latest_date_str, "trend": f"Source: WB Monthly Data ({latest_date_str})"}
        else: st.warning(f"No market price for '{product_name_from_vision}' on {latest_date_str}."); return {"price": "N/A", "unit": "", "location": "Market Not Found for Date", "date": latest_date_str, "trend": ""}
    except Exception as e: st.error(f"Error during price lookup for '{product_name_from_vision}': {e}"); return {"price": "Error", "unit": "", "location": "Lookup Failed", "date": "N/A", "trend": ""}

def generate_campaign_content(product_info, market_data):
    # (Function definition as previously provided)
    headline = "Quality Farm Products Available!" # ... (rest of logic unchanged)
    body = "Get the best farm-fresh products today."; cta = "Contact us now to order! [Your Phone Number/WhatsApp]"; hashtags = "#FarmFresh #NigeriaAgro #SupportLocalFarmers"
    if product_info and product_info.get('product'): product_name = product_info.get('product'); condition = product_info.get('condition', 'Quality'); headline = f"Premium {condition} {product_name} - Available Now!"; # ...
    if market_data.get('location') and "Akure" in market_data.get('location'): headline += " In Akure!" # ... (rest of logic unchanged)
    body = f"Looking for top {condition.lower()} {product_name}? Look no further! "; # ... (rest of logic unchanged)
    if market_data.get('trend') and market_data.get('trend') != 'N/A': body += f"Market trend shows: {market_data.get('trend')}. Secure yours today! " # ... (rest of logic unchanged)
    body += f"Ideal for home use or business."; cta = f"Order your {product_name} now! Call/WhatsApp [Your Phone Number/WhatsApp]."; # ... (rest of logic unchanged)
    if market_data.get('location') and market_data.get('location') != 'N/A': cta += f" Pickup available near {market_data.get('location').split('(')[0].strip()}." # Get base location for CTA
    product_tag = product_name.replace(" ", ""); hashtags_list = ["#FarmFresh", f"#{product_tag}", "#Akure", "#OndoState", "#NaijaMade", "#Agribusiness", "#SupportLocal"]; # ... (rest of logic unchanged)
    if market_data.get('location') and "Shasha" in market_data.get('location'): hashtags_list.append("#ShashaMarket") # ... (rest of logic unchanged)
    if market_data.get('location') and "Erekesan" in market_data.get('location'): hashtags_list.append("#ErekesanMarket") # ... (rest of logic unchanged)
    if market_data.get('location') and "Oja Oba" in market_data.get('location'): hashtags_list.append("#OjaOba") # ... (rest of logic unchanged)
    hashtags = " ".join(hashtags_list)
    return {"headline": headline, "body": body, "cta": cta, "hashtags": hashtags}

def generate_campaign_pdf(product_info, market_data, campaign_copy, image=None):
    # (Function definition as previously provided, with updated market_data fields)
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

# --- Initialize Session State Variables ---
# This helps manage state across reruns and for the reset button
if 'df' not in st.session_state: st.session_state.df = None
if 'pil_image' not in st.session_state: st.session_state.pil_image = None
if 'image_bytes' not in st.session_state: st.session_state.image_bytes = None
if 'product_info' not in st.session_state: st.session_state.product_info = None
if 'market_data' not in st.session_state: st.session_state.market_data = None
if 'campaign_copy' not in st.session_state: st.session_state.campaign_copy = None
# Keys for file uploaders to allow reset. Needs to be consistent.
if 'image_uploader_key' not in st.session_state: st.session_state.image_uploader_key = "image_uploader_0"
if 'file_uploader_key' not in st.session_state: st.session_state.file_uploader_key = "file_uploader_0"


# --- 1. Page Configuration ---
st.set_page_config(page_title="AgroBrand Fusion AI", layout="wide")

# --- 2. Main Application Interface ---
st.title("🌾 AgroBrand Fusion AI")
st.markdown("Your AI Assistant for Agribusiness Marketing & Pricing Insights across Nigeria and beyond.")
st.markdown("*(Image Rec: Google Vision AI | Market Prices: World Bank Monthly Data)*")
st.markdown("---")

# --- 3. Sidebar for User Inputs ---
st.sidebar.header("Upload Your Assets Here")

# Use session state keys for uploaders to help with reset
uploaded_image = st.sidebar.file_uploader(
    "1. Upload Product Image",
    type=["png", "jpg", "jpeg"],
    key=st.session_state.image_uploader_key, # Use session state key
    help="Upload a clear image of a single product. Good lighting helps AI accuracy."
)
uploaded_file = st.sidebar.file_uploader(
    "2. Upload Sales/Cost Sheet (CSV/Excel)",
    type=["csv", "xlsx"],
    key=st.session_state.file_uploader_key, # Use session state key
    help="For 'Data Highlights', ensure columns 'Product' and 'Revenue' exist."
)

# ADDED RESET BUTTON
if st.sidebar.button("🔄 Reset All / Start Over"):
    # Clear all session state variables we've defined
    keys_to_clear = ['df', 'pil_image', 'image_bytes', 'product_info', 'market_data', 'campaign_copy']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    # Increment uploader keys to force them to reset
    st.session_state.image_uploader_key = f"image_uploader_{int(st.session_state.image_uploader_key.split('_')[-1]) + 1}"
    st.session_state.file_uploader_key = f"file_uploader_{int(st.session_state.file_uploader_key.split('_')[-1]) + 1}"
    st.rerun()


# --- Process Uploads and Store in Session State ---
# Image Upload Processing
if uploaded_image is not None:
    if st.session_state.pil_image is None or st.session_state.pil_image.filename != uploaded_image.name : # process if new image
        try:
            st.session_state.pil_image = Image.open(uploaded_image)
            # For image_bytes, we need to read from the uploaded_file object as it's a stream
            # This should ideally be done once per upload, store bytes in session_state
            st.session_state.image_bytes = uploaded_image.getvalue() # Get bytes for API
        except Exception as e:
            st.error(f"Error processing uploaded image: {e}")
            st.session_state.pil_image = None
            st.session_state.image_bytes = None
# Data File Upload Processing
if uploaded_file is not None:
    if st.session_state.df is None: # Process if no df in session or if you want to re-process on new upload
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                st.session_state.df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading data file: {e}")
            st.session_state.df = None


# --- Run Analysis if Inputs are Ready (and not already run for current inputs) ---
# Store results in session_state
if st.session_state.image_bytes and not st.session_state.product_info: # Only run if image bytes exist and no product_info yet
    st.session_state.product_info = identify_product_via_web(st.session_state.image_bytes)

if st.session_state.product_info and st.session_state.product_info.get('product') and not st.session_state.market_data:
    st.session_state.market_data = fetch_market_price(st.session_state.product_info['product'])

if st.session_state.product_info and st.session_state.market_data and \
   st.session_state.market_data.get('price') not in ['N/A', 'Error'] and not st.session_state.campaign_copy:
    st.session_state.campaign_copy = generate_campaign_content(st.session_state.product_info, st.session_state.market_data)


# --- Main Content Area with TABS ---
tab1, tab2, tab3 = st.tabs(["📤 Uploads & Previews", "📊 AI Analysis & Insights", "📝 Generated Content & Export"])

with tab1:
    st.header("📂 Asset Previews")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼️ Image Preview")
        if st.session_state.pil_image:
            st.image(st.session_state.pil_image, caption=f"Uploaded: {st.session_state.pil_image.filename if hasattr(st.session_state.pil_image, 'filename') else 'Image'}", use_column_width=True)
        else:
            st.info("No image uploaded or processed yet. Please use the sidebar.")
    with col2:
        st.subheader("📄 Data Preview")
        if st.session_state.df is not None:
            st.success(f"Data loaded. Preview:")
            st.dataframe(st.session_state.df.head())
        else:
            st.info("No data file uploaded or processed yet. Please use the sidebar.")
    st.markdown("---")

with tab2:
    st.header("🤖 AI Analysis & Insights")
    col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)
    with col_img_analysis:
        st.subheader("👁️ Image Analysis")
        if st.session_state.product_info:
            st.markdown(f"- **Product:** {st.session_state.product_info.get('product', 'N/A')} (Confidence: {st.session_state.product_info.get('confidence', 0)*100:.1f}%)")
            st.markdown(f"- **Condition:** {st.session_state.product_info.get('condition', 'N/A')}")
            st.markdown(f"- **Setting:** {st.session_state.product_info.get('setting', 'N/A')}")
        else:
            st.info("Upload an image for AI analysis results to appear here.")
    with col_mkt_analysis:
        st.subheader("📈 Market Insights (WB Data)")
        if st.session_state.market_data:
            st.markdown(f"- **Price ({st.session_state.market_data.get('location', 'N/A')}):** {st.session_state.market_data.get('price', 'N/A')}")
            st.markdown(f"- **Unit:** {st.session_state.market_data.get('unit', 'N/A')}")
            st.markdown(f"- **🗓️ Data Date:** {st.session_state.market_data.get('date', 'N/A')}")
            st.markdown(f"- **Source/Trend:** {st.session_state.market_data.get('trend', 'N/A')}")
        else:
            st.info("Requires successful image analysis & product match in WB data for insights.")
    with col_data_analysis:
        st.subheader("💹 Data Highlights")
        if st.session_state.df is not None:
            required_cols = ['Product', 'Revenue']
            if all(col in st.session_state.df.columns for col in required_cols):
                try:
                    temp_df = st.session_state.df.copy() # Work on a copy
                    temp_df['Revenue_Clean'] = temp_df['Revenue'].astype(str).str.replace('[₦,]', '', regex=True)
                    temp_df['Revenue_Clean'] = pd.to_numeric(temp_df['Revenue_Clean'], errors='coerce')
                    if temp_df['Revenue_Clean'].isnull().any(): st.warning("Some 'Revenue' values non-numeric.")
                    top_products = temp_df.sort_values(by="Revenue_Clean", ascending=False).head(3)
                    st.write("Top Products by Revenue:")
                    st.dataframe(top_products[['Product', 'Revenue']])
                except Exception as e: st.error(f"Error analyzing data: {e}")
            else: st.warning("For Data Highlights, CSV/Excel needs 'Product' & 'Revenue' columns.")
        else:
            st.info("Upload a data file for highlights.")
    st.markdown("---")

with tab3:
    st.header("💡 Generated Campaign Content & Export")
    if st.session_state.campaign_copy:
        st.subheader("🗣️ Suggested Campaign Copy")
        st.write("**Headline:**"); st.markdown(f"> {st.session_state.campaign_copy['headline']}")
        st.write("**Body Text:**"); st.markdown(f"> {st.session_state.campaign_copy['body']}")
        st.write("**Call to Action (CTA):**"); st.markdown(f"> {st.session_state.campaign_copy['cta']}")
        st.write("**Hashtags:**"); st.text(st.session_state.campaign_copy['hashtags'])
        st.markdown("---")
        st.subheader("⬇️ Download Assets")
        col_txt_dl, col_pdf_dl = st.columns(2)
        with col_txt_dl:
            try:
                current_date_str = datetime.now().strftime("%Y%m%d")
                product_name_for_file = st.session_state.product_info.get('product', 'campaign').lower().replace(' ', '_')
                txt_file_name = f"{product_name_for_file}_campaign_{current_date_str}.txt"
                text_file_content = f"""--- AgroBrand AI Campaign Suggestions ---\nGenerated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} WAT\n\nProduct: {st.session_state.product_info.get('product', 'N/A')}\n\nHeadline:\n{st.session_state.campaign_copy['headline']}\n\nBody Text:\n{st.session_state.campaign_copy['body']}\n\nCall to Action (CTA):\n{st.session_state.campaign_copy['cta']}\n\nHashtags:\n{st.session_state.campaign_copy['hashtags']}\n\n--- Generated by AgroBrand Fusion AI ---"""
                st.download_button(label="Download Copy (.txt)", data=text_file_content.encode('utf-8'), file_name=txt_file_name, mime='text/plain')
            except Exception as e: st.error(f"Error preparing TXT download: {e}")
        with col_pdf_dl:
            try:
                pdf_bytes = generate_campaign_pdf(st.session_state.product_info, st.session_state.market_data, st.session_state.campaign_copy, st.session_state.pil_image)
                current_date_str = datetime.now().strftime("%Y%m%d")
                product_name_for_file = st.session_state.product_info.get('product', 'campaign').lower().replace(' ', '_')
                pdf_file_name = f"{product_name_for_file}_campaign_{current_date_str}.pdf"
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                pdf_download_link = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{pdf_file_name}">Download Report (.pdf)</a>'
                st.markdown(pdf_download_link, unsafe_allow_html=True)
            except Exception as e: st.error(f"Error generating PDF download: {e}")
    elif st.session_state.product_info and (not st.session_state.market_data or st.session_state.market_data.get('price') == 'N/A' or st.session_state.market_data.get('price') == 'Error'):
        st.warning(f"Successfully identified '{st.session_state.product_info.get('product')}' but could not find/retrieve its price in/from the World Bank dataset. Campaign generation and downloads might be limited or unavailable.")
    elif st.session_state.df is not None: # Check if df is loaded (from session state)
        st.info("Upload a product image for full campaign generation and download options.")
    else:
        st.info("Upload a product image and/or data file to generate campaign suggestions and enable downloads.")

# --- 7. Footer ---
st.markdown("---")
st.caption("Developed in Akure | Providing Nationwide Insights | © 2025")

