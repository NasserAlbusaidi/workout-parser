import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Coach Report Generator",
    page_icon="🚴",
    layout="centered"
)

# --- SIDEBAR: API SETUP ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Try to get key from environment variable first
    env_key = os.getenv("GEMINI_API_KEY")
    
    api_key = st.text_input(
        "Gemini API Key",
        value=env_key if env_key else "",
        type="password",
        help="Get your key from Google AI Studio"
    )
    
    st.markdown("---")
    st.markdown("""
    **Optimization Focus:**
    This tool specifically scans for:
    - 🚩 **L/R Imbalance** (>52/48)
    - 🚩 **Swim Drag** (Buoy vs No Buoy)
    - 🚩 **High Fatigue** (TSS Spikes)
    """)

# --- MAIN APP ---
st.title("🏃‍♂️ Nasser's Workout Parser")
st.caption("Upload a screenshot -> Get a coach-ready summary.")

uploaded_file = st.file_uploader("Upload Workout Screenshot", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file and api_key:
    try:
        # Display the image efficiently
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Screenshot", use_container_width=True)

        with st.spinner("Analyzing data & calculating metrics..."):
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # --- THE OPTIMIZED PROMPT ---
            # This prompts the AI to act as a data analyst, not just an OCR reader.
            prompt = """
            You are an expert triathlon data analyst. Analyze this workout screenshot. 
            
            Extract the data and format it into a CLEAN, TEXT-BASED report for a coach. 
            Do NOT use markdown tables (they are hard to copy to WhatsApp). Use simple lists.

            **REQUIRED OUTPUT FORMAT:**

            **[Date] | [Activity Type (Swim/Bike/Run)]**
            * **Stats:** [Distance] | [Time] | [Avg Pace or Speed] | [Avg HR] | [Avg Power/NP (if bike/run)]
            
            **Laps/Intervals:**
            (List the meaningful laps. Focus on the main set. Format: "Lap #: Dist @ Pace/Power - Notes")
            * 1: ...
            * 2: ...
            
            **Mechanical & Physio Check (CRITICAL):**
            * **L/R Balance:** [Extract Value]. (IF imbalance is >52/48, Add: "**FLAG: Imbalance Detected**")
            * **Cadence:** [Extract Value]
            * **TSS/Load:** [Extract Value]
            * **Equipment:** [Detect if mentioned, e.g., "Orbea Orca" or "Wetsuit"]

            **Coach's Insights (Auto-Generated):**
            * Compare the pacing/power consistency.
            * If Swim: Calculate the pace difference between fast laps (buoy?) and slow laps (no buoy?).
            * If Bike: Check if L/R balance worsened over time (fatigue indicator).
            * If Run: Check Ground Contact Time if visible.

            **Notes:**
            * Keep it concise.
            * If data is missing (e.g., no L/R balance), output "N/A".
            """

            # Call API
            response = model.generate_content([prompt, image])
            
            # --- RESULTS SECTION ---
            st.success("Analysis Complete!")
            
            st.subheader("📋 Copy This Text")
            st.code(response.text, language=None)
            
            # Additional logic: Quick Health Check based on the output
            if "FLAG" in response.text:
                st.error("⚠️ Mechanical Issue Detected (L/R Balance or Drag). Check the summary.")

    except Exception as e:
        st.error(f"Error: {e}")

elif not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")