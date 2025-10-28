import streamlit as st
import os
import cv2
from PIL import Image
import numpy as np
from clean.preprocess import clean_all_images
from clean.preprocess_debug import preprocess_image

from aligning.align_robust import align_robust
from pathlib import Path

# ──────────────────────────────
# 🔧 Directory setup
# ──────────────────────────────
UPLOAD_DIR = "uploads"
CLEAN_OUT = "clean/outputs"
DEBUG_OUT = "clean/outputs_debug"
ALIGNED_OUT = "aligning/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CLEAN_OUT, exist_ok=True)
os.makedirs(DEBUG_OUT, exist_ok=True)
os.makedirs(ALIGNED_OUT, exist_ok=True)

st.set_page_config(page_title="AI Grader - Sheet Alignment", layout="wide")
st.title("📄 AI Grader – Sheet Alignment System")

st.markdown(
    "<style> img {display: block; margin-left: auto; margin-right: auto;} </style>",
    unsafe_allow_html=True,
)

# ──────────────────────────────
# 📂 Upload image
# ──────────────────────────────
uploaded = st.file_uploader("Upload a handwritten answer sheet", type=["png", "jpg", "jpeg"])
if uploaded:
    upload_path = os.path.join(UPLOAD_DIR, uploaded.name)
    with open(upload_path, "wb") as f:
        f.write(uploaded.getbuffer())

    st.success(f"✅ Uploaded: {uploaded.name}")

    # ──────────────────────────────
    # ⚙ Step 1: Cleaning
    # ──────────────────────────────
    cleaned_path = os.path.join(CLEAN_OUT, uploaded.name)
    preprocess_image(upload_path, cleaned_path)


    st.divider()

    st.subheader("🧹 Cleaning Results")

    # Get debug versions
    stages = ["1_grayscale", "2_contrast", "3_denoised", "4_binary"]
    debug_images = []
    for stage in stages:
        stage_path = os.path.join(DEBUG_OUT, f"{Path(uploaded.name).stem}__{stage}.png")
        if os.path.exists(stage_path):
            debug_images.append((stage.replace("_", " ").capitalize(), stage_path))

    # UI – Show buttons for each debug stage
    for label, img_path in debug_images:
        with st.expander(f"🔍 {label}"):
            st.image(img_path, use_container_width=True, caption=label)

    st.divider()

    # ──────────────────────────────
    # ⚙ Step 2: Alignment
    # ──────────────────────────────
    aligned_path = os.path.join(ALIGNED_OUT, f"aligned_{uploaded.name}")
    if st.button("📐 Run Alignment"):
        with st.spinner("Aligning... please wait ⏳"):
            report = align_robust(cleaned_path, aligned_path, debug=True)

        st.success("✅ Alignment complete!")
        st.image(aligned_path, use_container_width=True, caption="Aligned Output")

        st.markdown("### 📊 Alignment Report")
        st.code(report, language="text")

else:
    st.info("👆 Upload an answer sheet to begin.")
