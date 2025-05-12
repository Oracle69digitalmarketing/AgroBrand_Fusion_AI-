# --------------------------------------------------------------------------
# AgroBrand Fusion AI - Phase 2: UI/UX - Enhanced PDF Report
# Focus: AI Assistant for Agribusiness
# Enhancements: Added sales insights & disclaimers to PDF
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

# --- Credentials Setup Reminder & Product Map ---
PRODUCT_NAME_SYNONYM_MAP = {
    "bell pepper": "Pepper, Bell", "tomato": "Tomatoes", "tomatoes": "Tomatoes",
    "catfish": "Fish, Catfish (fresh)", "yam tuber": "Yam", "yam": "Yam",
    "orange": "Oranges, Sweet", "maize": "Maize (white)", "corn": "Maize (white)",
    "onion": "Onions", "fruit": None, "vegetable": None,
    "plantain": "Plantain (ripe / unripe)",
    "beans": "Beans (brown, dry / white, dry / green)",
    "rice": "Rice (local sold loose / imported)"
}

# --- Helper Functions ---
def identify_product_via_web(image_bytes):
    # (Full function definition from previous steps)
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
    st.info("👁️ Analyzing image with Google Vision AI..."); product_info_val = None
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
    if best_label: product_name = best_label.description.capitalize(); confidence = best_label.score; st.success(f"✅ Vision AI identified: {product_name} (Confidence: {confidence*100:.1f}%)"); product_info_val = {"product": product_name, "condition": "Unknown (via AI)", "setting": "Unknown (via AI)", "confidence": confidence}
    else: st.warning("Could not select a primary product label from Vision AI results.")
    return product_info_val

@st.cache_data
def load_world_bank_data(file_path="WB_Nigeria_Food_Prices.csv"):
    # (Full function definition from previous steps)
    try:
        df_wb = pd.read_csv(file_path)
        st.success(f"Successfully loaded World Bank data from '{file_path}'")
        column_map = {
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
    # (Full function definition with fallback transparency from previous steps)
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
    # (Full function definition as previously provided)
    headline = "Quality Farm Products Available!"
    body = "Get the best farm-fresh products today."; cta = "Contact us now to order! [Your Phone Number/WhatsApp]"; hashtags = "#FarmFresh #NigeriaAgro #SupportLocalFarmers"
    if product_info and product_info.get('product'): product_name = product_info.get('product'); condition = product_info.get('condition', 'Quality'); headline = f"Premium {condition} {product_name} - Available Now!";
    if market_data.get('location') and "Akure" in market_data.get('location'): headline += " In Akure!"
    body = f"Looking for top {condition.lower()} {product_name}? Look no further! ";
    if market_data.get('trend') and market_data.get('trend') != 'N/A': body += f"Market trend shows: {market_data.get('trend')}. Secure yours today! "
    body += f"Ideal for home use or business."; cta = f"Order your {product_name} now! Call/WhatsApp [Your Phone Number/WhatsApp].";
    if market_data.get('location') and market_data.get('location') != 'N/A': cta += f" Pickup available near {market_data.get('location').split('(')[0].strip()}."
    product_tag = product_name.replace(" ", ""); hashtags_list = ["#FarmFresh", f"#{product_tag}", "#Akure", "#OndoState", "#NaijaMade", "#Agribusiness", "#SupportLocal"];
    if market_data.get('location') and "Shasha" in market_data.get('location'): hashtags_list.append("#ShashaMarket")
    if market_data.get('location') and "Erekesan" in market_data.get('location'): hashtags_list.append("#ErekesanMarket")
    if market_data.get('location') and "Oja Oba" in market_data.get('location'): hashtags_list.append("#OjaOba")
    hashtags = " ".join(hashtags_list)
    return {"headline": headline, "body": body, "cta": cta, "hashtags": hashtags}

# --- MODIFIED PDF Generation Function ---
def generate_campaign_pdf(product_info, market_data, campaign_copy_dict, image=None, sales_insights_df=None, total_sales_revenue=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 12, "AgroBrand AI Campaign Suggestion", ln=True, align='C')
    pdf.ln(3)

    pdf.set_font("Arial", size=9)
    current_date_pdf = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Use a different variable name
    pdf.cell(0, 5, f"Generated on: {current_date_pdf} WAT", ln=True, align='R')
    pdf.ln(7)

    # --- Section 1: Product & Market Information ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Product & Market Information", ln=True, border='B')
    pdf.ln(2)
    pdf.set_font("Arial", size=11)
    if product_info:
        pdf.multi_cell(0, 6, f"- **Identified Product:** {product_info.get('product', 'N/A')} (Confidence: {product_info.get('confidence', 0)*100:.1f}%)")
        pdf.multi_cell(0, 6, f"- **AI Condition Note:** {product_info.get('condition', 'N/A')}")
    if market_data:
        pdf.multi_cell(0, 6, f"- **Market Price ({market_data.get('location', 'N/A')}):** {market_data.get('price', 'N/A')}")
        pdf.multi_cell(0, 6, f"- **Unit:** {market_data.get('unit', 'N/A')}")
        pdf.multi_cell(0, 6, f"- **Price Data Date:** {market_data.get('date', 'N/A')}")
    pdf.ln(5)

    # --- Section 2: Sales Data Highlights (from your sheet) ---
    if sales_insights_df is not None and not sales_insights_df.empty:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "2. Sales Data Highlights", ln=True, border='B')
        pdf.ln(2)
        pdf.set_font("Arial", size=10)
        if total_sales_revenue is not None:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, f"Total Calculated Revenue from Sheet: ₦{total_sales_revenue:,.0f}", ln=True)
            pdf.ln(1)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 7, "Top Product", border=1, fill=True, align='L') # Align left for product
        pdf.cell(60, 7, "Revenue", border=1, fill=True, align='R')    # Align right for revenue
        pdf.ln()
        pdf.set_font('Arial', '', 10)
        for index, row in sales_insights_df.head(5).iterrows():
            product_display_name = (str(row['Product'])[:45] + '...') if len(str(row['Product'])) > 48 else str(row['Product'])
            # Assuming 'Revenue' in sales_insights_df is the original string format
            revenue_display = str(row['Revenue']) if pd.notna(row['Revenue']) else "N/A"
            pdf.cell(100, 6, product_display_name, border=1)
            pdf.cell(60, 6, revenue_display, border=1, align='R')
            pdf.ln()
        pdf.ln(5)
    
    # Image - Placed after text blocks to simplify layout for now
    # Better placement might require more complex FPDF table layouts or fixed coordinates
    if image:
        pdf.ln(2) # Some space before image
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 6, "Uploaded Product Image:", ln=True)
        pdf.ln(2)
        try:
            with io.BytesIO() as image_buffer:
                image.save(image_buffer, format="PNG") # Use PNG for better compatibility
                image_buffer.seek(0)
                # Calculate width and height to fit, maintaining aspect ratio (max width 80)
                img_w, img_h = image.size
                aspect = img_h / img_w
                display_w = 80
                display_h = display_w * aspect
                if display_h > 60 : # Max height
                    display_h = 60
                    display_w = display_h / aspect
                
                current_x = pdf.get_x()
                page_width = pdf.w - 2 * pdf.l_margin # Usable page width
                img_x_centered = (page_width - display_w) / 2 + pdf.l_margin
                
                pdf.image(image_buffer, x=img_x_centered, w=display_w, h=display_h, type='PNG')
                pdf.ln(display_h + 5) # Move below image
        except Exception as e:
            st.warning(f"Could not embed image in PDF: {e}")
            pdf.set_font("Arial", 'I', 9)
            pdf.multi_cell(0,5, "(Image could not be embedded)")
            pdf.ln(5)


    # --- Section 3: AI-Generated Campaign Content ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. AI-Generated Campaign Content", ln=True, border='B')
    pdf.ln(2)
    pdf.set_font("Arial", size=11)
    if campaign_copy_dict:
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "Headline: "); pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, campaign_copy_dict['headline']); pdf.ln(3)
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "Body Text: "); pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, campaign_copy_dict['body']); pdf.ln(3)
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "Call to Action (CTA): "); pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, campaign_copy_dict['cta']); pdf.ln(3)
        pdf.set_font("Arial", 'B', 11); pdf.write(6, "Hashtags: "); pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, campaign_copy_dict['hashtags']); pdf.ln(7)
    else:
        pdf.multi_cell(0,6, "Campaign copy not generated.")
        pdf.ln(7)

    # --- Section 4: Important Notes & Disclaimers ---
    pdf.set_font("Arial", 'B', 14) # Section Title Font
    pdf.cell(0, 10, "4. Important Notes & Disclaimers", ln=True, border='B')
    pdf.ln(2)
    pdf.set_font("Arial", 'I', 9)
    disclaimer_text = (
        f"- Market price data from World Bank Monthly Estimates (last data point analyzed: {market_data.get('date', 'N/A') if market_data else 'N/A'}). "
        "These are monthly averages, not live daily prices, and should guide understanding of recent trends.\n"
        "- AI-generated marketing suggestions are starting points. Review and adapt them to your specific business and audience.\n"
        "- Sales data insights are based on the data you provided in the uploaded sheet."
    )
    pdf.multi_cell(0, 5, disclaimer_text)
    pdf.ln(5)

    # Footer with Page Number
    pdf.set_y(-15) # Position 1.5 cm from bottom
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"--- AgroBrand Fusion AI Report © {datetime.now().year} --- Page " + str(pdf.page_no()), 0, 0, 'C')

    return pdf.output(dest='S').encode('latin-1')
# --- END OF MODIFIED PDF Generation ---


# --- Initialize Session State Variables ---
editable_keys = ['editable_headline', 'editable_body', 'editable_cta', 'editable_hashtags']
# Added 'top_sales_products', 'total_sales_revenue' to data_keys
data_keys = ['df', 'pil_image', 'image_bytes', 'product_info', 'market_data', 'campaign_copy', 'top_sales_products', 'total_sales_revenue']
uploader_keys = ['image_uploader_key', 'file_uploader_key']
for key in data_keys + editable_keys:
    if key not in st.session_state: st.session_state[key] = None
for i, key in enumerate(uploader_keys):
    if key not in st.session_state: st.session_state[key] = f"{key}_{i}"

# --- 1. Page Configuration ---
st.set_page_config(page_title="AgroBrand Fusion AI", layout="wide", initial_sidebar_state="expanded")

# --- 2. Main Application Interface ---
st.title("🌾 AgroBrand Fusion AI")
st.markdown("Your AI Assistant for Agribusiness Marketing & Pricing Insights across Nigeria and beyond.")
st.markdown("*(Image Rec: Google Vision AI | Market Prices: World Bank Monthly Data)*")
with st.expander("ℹ️ Welcome & How to Use This App", expanded=False):
    st.markdown("""
    ### Welcome to AgroBrand Fusion AI! 👋

    Your AI-powered assistant for boosting your agribusiness marketing and pricing strategies here in Nigeria.

    **Here's how to get started:**

    1.  **📤 Upload Your Assets:**
        * Use the **sidebar on the left** to upload:
            * A clear **Product Image** (e.g., your catfish, yams, plantains).
            * Optionally, your **Sales/Cost Sheet** (CSV or Excel format) for data-driven insights.

    2.  **📂 View Previews:**
        * Navigate to the **"📂 Asset Previews"** tab to check if your files have loaded correctly.

    3.  **📊 Get AI Analysis & Insights:**
        * In the **"📊 AI Analysis"** tab:
            * Our AI (Google Vision) will attempt to identify your product from the image.
            * We'll then fetch estimated market prices using World Bank monthly data. (Note: This data is updated monthly, so it reflects recent trends rather than daily prices).
            * If you uploaded a sales sheet, see highlights like top products by revenue and total revenue.

    4.  **📝 Generate, Edit & Export Campaign Content:**
        * Head over to the **"📝 Campaign Content"** tab.
        * Review the AI-suggested marketing copy (headlines, body text, CTAs, hashtags).
        * **Click into any text area to edit the suggestions** to perfectly match your brand and message!
        * Download your finalized content as a `.txt` file or a more detailed `.pdf` report (which can include your product image & sales highlights).

    5.  **🔄 Start Over:**
        * Use the **"Reset All / Start Over"** button in the sidebar at any time to clear all uploads and results.

    **Tips for Best Results:**
    * Use clear, well-lit product images.
    * For data analysis, ensure your CSV/Excel file has columns named 'Product' and 'Revenue'.
    * **Crucial for Market Prices:**
        * Download the World Bank food price data CSV and place it as `WB_Nigeria_Food_Prices.csv` in the app's directory.
        * **Verify and adjust the `column_map` in the `load_world_bank_data` function within the script to match your CSV's exact column headers.**
        * **Continuously update the `PRODUCT_NAME_SYNONYM_MAP` in the script** as you test with different images to improve product matching between Vision AI and the World Bank data.

    We hope this tool empowers your business!
    ---
    *(Developed in Akure, Ondo State, Nigeria)*
    """)
st.markdown("---")

# --- 3. Sidebar for User Inputs ---
st.sidebar.header("📤 Upload Your Assets Here")
st.sidebar.caption("Provide your product image and optionally, your sales/cost data.")
uploaded_image = st.sidebar.file_uploader("1. Upload Product Image", type=["png", "jpg", "jpeg"], key=st.session_state.image_uploader_key, help="Upload a clear image of a single product.")
uploaded_file = st.sidebar.file_uploader("2. Upload Sales/Cost Sheet (CSV/Excel)", type=["csv", "xlsx"], key=st.session_state.file_uploader_key, help="For 'Data Highlights', ensure 'Product' & 'Revenue' columns exist.")
if st.sidebar.button("🔄 Reset All / Start Over"):
    keys_to_clear_on_reset = data_keys + editable_keys # This now includes 'top_sales_products', 'total_sales_revenue'
    for key in keys_to_clear_on_reset:
        if key in st.session_state: del st.session_state[key]
    st.session_state.image_uploader_key = f"image_uploader_{int(st.session_state.image_uploader_key.split('_')[-1]) + 1}"
    st.session_state.file_uploader_key = f"file_uploader_{int(st.session_state.file_uploader_key.split('_')[-1]) + 1}"
    st.rerun()

# --- Process Uploads and Store in Session State ---
if uploaded_image is not None:
    if st.session_state.image_bytes is None or (hasattr(st.session_state.pil_image, 'filename') and st.session_state.pil_image.filename != uploaded_image.name):
        try:
            st.session_state.pil_image = Image.open(uploaded_image)
            st.session_state.pil_image.filename = uploaded_image.name
            st.session_state.image_bytes = uploaded_image.getvalue()
            for key_to_clear in ['product_info', 'market_data', 'campaign_copy', 'top_sales_products', 'total_sales_revenue'] + editable_keys:
                 if key_to_clear in st.session_state: del st.session_state[key_to_clear]
        except Exception as e: st.error(f"Error processing uploaded image: {e}"); st.session_state.pil_image = None; st.session_state.image_bytes = None
if uploaded_file is not None:
    new_file_uploaded = False
    if st.session_state.df is None: new_file_uploaded = True
    elif hasattr(st.session_state.df, '_uploaded_filename') and st.session_state.df._uploaded_filename != uploaded_file.name: new_file_uploaded = True
    elif not hasattr(st.session_state.df, '_uploaded_filename'): new_file_uploaded = True
    if new_file_uploaded:
        try:
            if uploaded_file.name.endswith('.csv'): st.session_state.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')): st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.df._uploaded_filename = uploaded_file.name
            for key_to_clear in ['top_sales_products', 'total_sales_revenue']: # Clear previous sales analysis
                 if key_to_clear in st.session_state: del st.session_state[key_to_clear]
        except Exception as e: st.error(f"Error reading data file: {e}"); st.session_state.df = None

# --- Run Analysis if Inputs are Ready and results not yet in session_state ---
if st.session_state.image_bytes and not st.session_state.product_info:
    st.session_state.product_info = identify_product_via_web(st.session_state.image_bytes)
if st.session_state.product_info and st.session_state.product_info.get('product') and not st.session_state.market_data:
    st.session_state.market_data = fetch_market_price(st.session_state.product_info['product'])
if st.session_state.product_info and st.session_state.market_data and \
   st.session_state.market_data.get('price') not in ['N/A', 'Error'] and not st.session_state.campaign_copy:
    st.session_state.campaign_copy = generate_campaign_content(st.session_state.product_info, st.session_state.market_data)
    st.session_state.editable_headline = st.session_state.campaign_copy.get('headline', '')
    st.session_state.editable_body = st.session_state.campaign_copy.get('body', '')
    st.session_state.editable_cta = st.session_state.campaign_copy.get('cta', '')
    st.session_state.editable_hashtags = st.session_state.campaign_copy.get('hashtags', '')

# --- Main Content Area with TABS ---
tab1, tab2, tab3 = st.tabs(["📂 Asset Previews", "📊 AI Analysis", "📝 Campaign Content"])

with tab1:
    st.header("📂 Asset Previews")
    col1_preview, col2_preview = st.columns(2)
    with col1_preview:
        st.subheader("🖼️ Image Preview")
        if st.session_state.pil_image: st.image(st.session_state.pil_image, caption=f"Uploaded: {st.session_state.pil_image.filename if hasattr(st.session_state.pil_image, 'filename') else 'Image'}", use_column_width=True)
        else: st.info("No image uploaded. Please use the sidebar.")
    with col2_preview:
        st.subheader("📄 Data Preview")
        if st.session_state.df is not None: st.success(f"Data loaded. Preview:"); st.dataframe(st.session_state.df.head())
        else: st.info("No data file uploaded. Please use the sidebar.")
    st.markdown("---")

with tab2:
    st.header("📊 AI Analysis & Insights")
    col_img_analysis, col_mkt_analysis, col_data_analysis = st.columns(3)
    with col_img_analysis:
        st.subheader("👁️ Image Analysis")
        if st.session_state.product_info:
            st.markdown(f"**🎯 Identified Product:** {st.session_state.product_info.get('product', 'N/A')}")
            st.markdown(f"**📊 Confidence Score:** **{st.session_state.product_info.get('confidence', 0)*100:.1f}%**")
            st.markdown(f"**📋 Condition (from AI):** {st.session_state.product_info.get('condition', 'N/A')}")
            st.markdown(f"**🖼️ Setting (from AI):** {st.session_state.product_info.get('setting', 'N/A')}")
        else:
            st.info("Awaiting image upload for AI analysis results to appear here.")
    with col_mkt_analysis:
        st.subheader("📈 Market Insights (WB Data)")
        if st.session_state.market_data:
            st.markdown(f"- **Price ({st.session_state.market_data.get('location', 'N/A')}):** **{st.session_state.market_data.get('price', 'N/A')}**")
            st.markdown(f"- **Unit:** {st.session_state.market_data.get('unit', 'N/A')}")
            st.markdown(f"- **🗓️ Data Date:** **{st.session_state.market_data.get('date', 'N/A')}**")
            st.markdown(f"- **Source/Trend:** {st.session_state.market_data.get('trend', 'N/A')}")
        else:
            st.info("Awaiting image analysis & product match in WB data for insights.")
    # --- Updated col_data_analysis ---
    with col_data_analysis:
        st.subheader("💹 Data Highlights")
        if st.session_state.df is not None:
            required_cols = ['Product', 'Revenue']
            if not all(col in st.session_state.df.columns for col in required_cols):
                st.warning("For Data Highlights, CSV/Excel needs 'Product' & 'Revenue' columns.")
                st.session_state.total_sales_revenue = None
                st.session_state.top_sales_products = None
            else:
                try:
                    temp_df = st.session_state.df.copy()
                    if temp_df['Revenue'].dtype == 'object':
                        temp_df['Revenue_Clean'] = temp_df['Revenue'].astype(str).str.replace('₦', '', regex=False).str.replace(',', '', regex=False)
                        temp_df['Revenue_Clean'] = pd.to_numeric(temp_df['Revenue_Clean'], errors='coerce')
                    elif pd.api.types.is_numeric_dtype(temp_df['Revenue']):
                        temp_df['Revenue_Clean'] = temp_df['Revenue']
                    else:
                         temp_df['Revenue_Clean'] = pd.to_numeric(temp_df['Revenue'], errors='coerce')

                    if temp_df['Revenue_Clean'].isnull().all():
                        st.warning("Could not parse 'Revenue' into numbers. Check data format.")
                        st.session_state.total_sales_revenue = None
                        st.session_state.top_sales_products = None
                    else:
                        total_revenue = temp_df['Revenue_Clean'].sum()
                        st.session_state.total_sales_revenue = total_revenue
                        st.metric(label="💰 Total Revenue (from sheet)", value=f"₦{total_revenue:,.0f}")
                        st.markdown("---")
                        top_5_products = temp_df.dropna(subset=['Revenue_Clean']).sort_values(by="Revenue_Clean", ascending=False).head(5)
                        if not top_5_products.empty:
                            st.write("**Top 5 Products by Revenue:**")
                            chart_data = top_5_products.set_index('Product')['Revenue_Clean']
                            st.bar_chart(chart_data)
                            st.dataframe(top_5_products[['Product', 'Revenue', 'Revenue_Clean']].rename(columns={'Revenue_Clean': 'Revenue (Numeric)'}))
                            st.session_state.top_sales_products = top_5_products[['Product', 'Revenue']]
                        else:
                            st.info("No revenue data for top products after cleaning.")
                            st.session_state.top_sales_products = None
                except Exception as e:
                    st.error(f"Error analyzing sales data: {e}")
                    st.info("Ensure 'Revenue' column has parseable numeric data.")
                    st.session_state.total_sales_revenue = None
                    st.session_state.top_sales_products = None
        else:
            st.info("Awaiting data file upload (CSV/Excel) for highlights.")
            st.session_state.total_sales_revenue = None
            st.session_state.top_sales_products = None
    st.markdown("---")

with tab3:
    st.header("📝 Campaign Content & Export")
    if st.session_state.campaign_copy:
        st.subheader("✏️ Review & Edit Your Campaign Copy")
        st.text_area("Headline:", value=st.session_state.get('editable_headline', st.session_state.campaign_copy.get('headline', '')), height=100, key="editable_headline", help="Edit the AI-suggested headline here.")
        st.text_area("Body Text:", value=st.session_state.get('editable_body', st.session_state.campaign_copy.get('body', '')), height=250, key="editable_body", help="Refine the main body of your campaign message.")
        st.text_area("Call to Action (CTA):", value=st.session_state.get('editable_cta', st.session_state.campaign_copy.get('cta', '')), height=100, key="editable_cta", help="Adjust the call to action.")
        st.text_area("Hashtags:", value=st.session_state.get('editable_hashtags', st.session_state.campaign_copy.get('hashtags', '')), height=100, key="editable_hashtags", help="Modify or add relevant hashtags, space-separated.")
        st.markdown("---")
        st.subheader("⬇️ Download Assets")
        col_txt_dl, col_pdf_dl = st.columns(2)
        with col_txt_dl:
            try:
                current_date_str = datetime.now().strftime("%Y%m%d"); product_name_for_file = st.session_state.product_info.get('product', 'campaign').lower().replace(' ', '_'); txt_file_name = f"{product_name_for_file}_campaign_{current_date_str}.txt"
                text_file_content = f"""--- AgroBrand AI Campaign Suggestions ---\nGenerated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} WAT\n\nProduct: {st.session_state.product_info.get('product', 'N/A')}\n
Headline:
{st.session_state.editable_headline}

Body Text:
{st.session_state.editable_body}

Call to Action (CTA):
{st.session_state.editable_cta}

Hashtags:
{st.session_state.editable_hashtags}
\n--- Generated by AgroBrand Fusion AI ---"""
                st.download_button(label="Download Copy (.txt)", data=text_file_content.encode('utf-8'), file_name=txt_file_name, mime='text/plain')
            except Exception as e: st.error(f"Error preparing TXT download: {e}")
        with col_pdf_dl:
            try:
                edited_campaign_details_for_pdf = {"headline": st.session_state.editable_headline, "body": st.session_state.editable_body, "cta": st.session_state.editable_cta, "hashtags": st.session_state.editable_hashtags}
                pdf_bytes = generate_campaign_pdf(
                    st.session_state.product_info,
                    st.session_state.market_data,
                    edited_campaign_details_for_pdf,
                    st.session_state.pil_image,
                    sales_insights_df=st.session_state.top_sales_products, # Pass top products df
                    total_sales_revenue=st.session_state.total_sales_revenue # Pass total revenue
                )
                current_date_str = datetime.now().strftime("%Y%m%d"); product_name_for_file = st.session_state.product_info.get('product', 'campaign').lower().replace(' ', '_'); pdf_file_name = f"{product_name_for_file}_campaign_{current_date_str}.pdf"
                b64_pdf = base64.b64encode(pdf_bytes).decode(); pdf_download_link = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{pdf_file_name}">Download Report (.pdf)</a>'; st.markdown(pdf_download_link, unsafe_allow_html=True)
            except Exception as e: st.error(f"Error generating PDF download: {e}") # import traceback; st.text(traceback.format_exc()) # For debugging
    elif st.session_state.product_info and (not st.session_state.market_data or st.session_state.market_data.get('price') == 'N/A' or st.session_state.market_data.get('price') == 'Error'):
        st.warning(f"Successfully identified '{st.session_state.product_info.get('product')}' but could not find/retrieve its price. Campaign generation might be limited.")
    elif st.session_state.df is not None:
        st.info("Upload a product image for full campaign generation and download options.")
    else:
        st.info("Upload a product image and/or data file to generate campaign suggestions and enable downloads.")

# --- 7. Footer ---
st.markdown("---")
st.caption(f"Developed in Akure, Ondo State, Nigeria | AgroBrand Fusion AI © {datetime.now().year}")

