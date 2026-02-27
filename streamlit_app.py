import streamlit as st
import openfoodfacts
from PIL import Image
import zxingcpp

# API Config
USER_AGENT = "QuickOFF/1.0 (your@email.com)"
api = openfoodfacts.API(user_agent=USER_AGENT)

st.title("OFF Quick Context 🚀")

with st.sidebar:
    st.header("Settings")
    country = st.text_input("Target Country", "France")
    category = st.text_input("Target Category", "")
    username = st.text_input("OFF Username")
    password = st.text_input("OFF Password", type="password")

# Camera input (native & reliable)
img_file = st.camera_input("Take a photo of the barcode")

if img_file:
    # 1. Decode Barcode
    img = Image.open(img_file)
    results = zxingcpp.read_barcodes(img)
    
    if not results:
        st.error("No barcode found. Try to get closer and be steady.")
    else:
        barcode = results[0].text
        st.success(f"Barcode detected: {barcode}")
        
        # 2. Open Food Facts Logic
        if username and password:
            try:
                api.authenticate(username, password)
                product = api.product.get(barcode)
                
                if product:
                    st.write(f"Product: **{product.get('product_name', 'Unknown')}**")
                    
                    # Logic: Only update if missing
                    curr_countries = [c.strip().lower() for c in product.get('countries', '').split(',')]
                    
                    update_data = {"code": barcode}
                    needs_update = False
                    
                    if country.lower() not in curr_countries:
                        update_data["countries"] = country
                        needs_update = True
                    
                    if category:
                        update_data["add_categories"] = category
                        needs_update = True
                        
                    if needs_update:
                        res = api.product.update(update_data)
                        if res.get("status") == 1:
                            st.balloons()
                            st.success("Updated on Open Food Facts!")
                        else:
                            st.error(f"Failed: {res.get('status_verbose')}")
                    else:
                        st.info("Information already present.")
                else:
                    st.error("Product not found on OFF.")
            except Exception as e:
                st.error(f"Error: {e}")
