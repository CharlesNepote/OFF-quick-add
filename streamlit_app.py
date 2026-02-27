import streamlit as st
import openfoodfacts
from streamlit_barcode_scanner import st_barcode_scanner

# OFF API Setup
# Please replace with your actual email to follow OFF's terms of use
USER_AGENT = "QuickOFFContext/1.0 (Contact: your@email.com)"
api = openfoodfacts.API(user_agent=USER_AGENT)

st.set_page_config(page_title="OFF Quick Context", page_icon="🌍")
st.title("OFF Quick Context 🚀")

# 1. Persistent settings
if 'country' not in st.session_state:
    st.session_state.country = "France"
if 'category' not in st.session_state:
    st.session_state.category = ""

with st.sidebar:
    st.header("Settings")
    st.session_state.country = st.text_input("My Current Country", st.session_state.country)
    st.session_state.category = st.text_input("Product Category", st.session_state.category)
    username = st.text_input("OFF Username")
    password = st.text_input("OFF Password", type="password")

# 2. Live Scanner
st.subheader("Scan Barcode")
# The scanner returns the barcode string once detected
barcode = st_barcode_scanner()

if barcode:
    st.success(f"Barcode: {barcode}")
    
    if not (username and password):
        st.warning("⚠️ Credentials missing in sidebar.")
    else:
        try:
            # Check existing product data
            product = api.product.get(barcode)
            
            if product:
                name = product.get('product_name', 'Unknown Product')
                st.info(f"Checking: **{name}**")
                
                # Compare current data with targets
                existing_countries = [c.strip().lower() for c in product.get('countries', '').split(',')]
                target_country = st.session_state.country.strip().lower()
                
                update_data = {"code": barcode}
                needs_update = False
                
                # Logic: Update only if missing
                if target_country not in existing_countries:
                    update_data["countries"] = st.session_state.country
                    needs_update = True
                
                if st.session_state.category:
                    # add_categories avoids overwriting existing ones
                    update_data["add_categories"] = st.session_state.category
                    needs_update = True
                
                if needs_update:
                    api.authenticate(username, password)
                    result = api.product.update(update_data)
                    if result.get("status") == 1:
                        st.balloons()
                        st.success("✅ Successfully updated!")
                    else:
                        st.error(f"Error: {result.get('status_verbose')}")
                else:
                    st.info("ℹ️ Product already has this country/category.")
            else:
                st.error("❌ Product not found in database.")
        except Exception as e:
            st.error(f"API Error: {e}")

st.divider()
st.caption("Scan a product to automatically add your current country and category.")