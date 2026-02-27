import streamlit as st
import openfoodfacts
import zxingcpp
import requests
from PIL import Image

# Configuration
USER_AGENT = "OFF-Quick-Add/2.2 (Contact: your@email.com)"

st.set_page_config(page_title="OFF Quick Context", page_icon="📸")
st.title("OFF Quick Add 🚀")

# --- CATEGORY SEARCH LOGIC ---
def search_off_categories(query):
    """Fetch official categories from OFF Suggest API."""
    if len(query) < 4:
        return []
    
    # suggest.pl is the fastest endpoint for taxonomy autocompletion
    url = f"https://world.openfoodfacts.org/cgi/suggest.pl?tagtype=categories&term={query}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
        if response.status_code == 200:
            return response.json()  # API returns a plain list of strings
    except:
        return []
    return []

# --- SIDEBAR (SETTINGS) ---
with st.sidebar:
    st.header("Global Settings")
    target_country = st.text_input("Target Country", "France")
    
    st.divider()
    st.subheader("Category Selection")
    # Search input field
    cat_input = st.text_input("Search category (min. 4 chars)", key="cat_search_input")
    
    # Only re-fetch when the query actually changes
    last_query = st.session_state.get('last_query', '')
    cat_options = st.session_state.get('last_options', [])

    if len(cat_input) >= 4 and cat_input != last_query:
        with st.spinner("Searching categories..."):
            cat_options = search_off_categories(cat_input)
            st.session_state['last_query'] = cat_input
            st.session_state['last_options'] = cat_options
    
    selected_category = st.selectbox(
        "Select official category", 
        options=cat_options,
        help="Taxonomy results from Open Food Facts"
    )
    
    st.divider()
    username = st.text_input("OFF Username")
    password = st.text_input("OFF Password", type="password")

# --- MAIN SCANNING AREA ---
st.subheader("1. Capture Barcode")
# Note: Streamlit handles the 'rear camera' preference automatically on mobile 
# by prioritizing the 'environment' camera for this component.
img_file = st.camera_input("Snap the product's barcode")

if img_file:
    # Barcode Decoding
    img = Image.open(img_file)
    results = zxingcpp.read_barcodes(img)
    
    if not results:
        st.error("❌ No barcode detected. Ensure the barcode is flat and well-lit.")
    else:
        barcode = results[0].text
        st.success(f"✅ Barcode detected: {barcode}")
        
        # --- UPDATE LOGIC ---
        if not (username and password):
            st.warning("⚠️ Please provide your OFF credentials in the sidebar.")
        else:
            try:
                with st.spinner("Updating Open Food Facts..."):
                    # Credentials are passed at API instantiation, not via authenticate()
                    api = openfoodfacts.API(
                        user_agent=USER_AGENT,
                        username=username,
                        password=password
                    )
                    product = api.product.get(barcode)
                    
                    if product:
                        p_name = product.get('product_name', 'Unknown')
                        st.info(f"Product: **{p_name}**")
                        
                        countries_str = product.get('countries', '') or ''
                        existing_countries = [c.strip().lower() for c in countries_str.split(',')]
                        
                        update_payload = {"code": barcode}
                        needs_push = False
                        
                        # Add country if missing
                        if target_country.lower() not in existing_countries:
                            update_payload["countries"] = target_country
                            needs_push = True
                            
                        # Add category if selected
                        if selected_category:
                            update_payload["add_categories"] = selected_category
                            needs_push = True
                        
                        if needs_push:
                            res = api.product.update(update_payload)
                            if res.get("status") == 1:
                                st.balloons()
                                st.success(f"Successfully updated {barcode}!")
                            else:
                                st.error(f"API Error: {res.get('status_verbose')}")
                        else:
                            st.info("ℹ️ Product already contains this information.")
                    else:
                        st.error("❌ Product not found in database.")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("v2.2 | Optimized for Mobile Rear Camera")