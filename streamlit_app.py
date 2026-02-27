import streamlit as st
import openfoodfacts
import zxingcpp
from PIL import Image

# API Setup
# Use a clear User-Agent as per OFF policy
USER_AGENT = "OFF-Quick-Add/1.0 (Contact: your@email.com)"
api = openfoodfacts.API(user_agent=USER_AGENT)

st.set_page_config(page_title="OFF Quick Add", page_icon="📸")
st.title("OFF Quick Context Add 🚀")

# 1. Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    target_country = st.text_input("Target Country", "France")
    target_category = st.text_input("Target Category (Optional)", "")
    st.divider()
    username = st.text_input("OFF Username")
    password = st.text_input("OFF Password", type="password")

# 2. Scanning Interface
st.subheader("Scan Product")
# st.camera_input is the most reliable way on mobile browsers
img_file = st.camera_input("Take a clear photo of the barcode")

# 3. Processing Logic
if img_file:
    # Decoding the barcode from the image
    img = Image.open(img_file)
    results = zxingcpp.read_barcodes(img)
    
    if not results:
        st.error("❌ No barcode detected. Please ensure the barcode is flat, well-lit, and centered.")
    else:
        barcode = results[0].text
        st.success(f"✅ Barcode detected: {barcode}")
        
        if not (username and password):
            st.warning("⚠️ Please provide your OFF credentials in the sidebar.")
        else:
            try:
                # Authenticate and fetch product
                api.authenticate(username, password)
                product = api.product.get(barcode)
                
                if product:
                    product_name = product.get('product_name', 'Unknown Product')
                    st.write(f"Product: **{product_name}**")
                    
                    # Logic: Check if update is actually needed
                    current_countries = [c.strip().lower() for c in product.get('countries', '').split(',')]
                    
                    update_payload = {"code": barcode}
                    needs_update = False
                    
                    # Check country
                    if target_country.lower() not in current_countries:
                        update_payload["countries"] = target_country
                        needs_update = True
                        st.info(f"Adding country: {target_country}")
                        
                    # Check category
                    if target_category:
                        # Note: we use 'add_categories' to append rather than replace
                        update_payload["add_categories"] = target_category
                        needs_update = True
                        st.info(f"Adding category: {target_category}")
                    
                    if needs_update:
                        response = api.product.update(update_payload)
                        if response.get("status") == 1:
                            st.balloons()
                            st.success("Successfully updated on Open Food Facts!")
                        else:
                            st.error(f"API Error: {response.get('status_verbose')}")
                    else:
                        st.info("ℹ️ Product already contains this information.")
                else:
                    st.error("❌ Product not found in Open Food Facts database.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.divider()
st.caption("Powered by official Open Food Facts Python SDK.")