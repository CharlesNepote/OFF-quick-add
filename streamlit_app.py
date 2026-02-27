import streamlit as st
import openfoodfacts
import zxingcpp
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# API Setup
USER_AGENT = "OFF-Quick-Scan/1.0"
api = openfoodfacts.API(user_agent=USER_AGENT)

st.title("OFF Continuous Scanner ⚡")

# 1. Sidebar Config
with st.sidebar:
    st.header("Settings")
    target_country = st.text_input("Country", "France")
    target_category = st.text_input("Category", "")
    st.divider()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = None

# 2. Continuous Scan Logic
class BarcodeProcessor(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr224") # Small format for speed
        results = zxingcpp.read_barcodes(img)
        
        if results:
            barcode = results[0].text
            return barcode
        return None

# Webrtc streamer handles the continuous video feed
ctx = webrtc_streamer(
    key="barcode-scanner",
    video_transformer_factory=BarcodeProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": {"facingMode": "environment"}, "audio": False},
)

# 3. Handle Detection
# This part runs when a barcode is returned by the video thread
if ctx.video_transformer and ctx.video_transformer.last_result:
    barcode = ctx.video_transformer.last_result
    
    if barcode != st.session_state.last_scanned:
        st.session_state.last_scanned = barcode
        st.audio("https://www.soundjay.com/buttons/beep-07.mp3") # Audio feedback
        
        if username and password:
            try:
                api.authenticate(username, password)
                # Quick update logic
                update_payload = {
                    "code": barcode,
                    "countries": target_country,
                    "add_categories": target_category
                }
                api.product.update(update_payload)
                st.success(f"Sent: {barcode}")
            except Exception as e:
                st.error(f"Error: {e}")