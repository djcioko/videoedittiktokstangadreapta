import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import os

st.set_page_config(page_title="Alpha Motion Studio Pro", layout="wide")

# Interfață stil Editor Video
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stSlider { padding-top: 0px; }
    .preview-box { border: 2px solid #333; border-radius: 10px; padding: 10px; background: #000; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Studio Editare: Calibrare & Motion")

# --- PANOU DE CONTROL (LAYERS) ---
col_ctrl, col_prev = st.columns([1, 1.2])

with col_ctrl:
    st.subheader("📼 Canale Timeline")
    
    with st.expander("📁 Layer 1: Fundal", expanded=True):
        bg_file = st.file_uploader("Urcă Background", type=["jpg", "png"], key="bg")
    
    with st.expander("🖼️ Layer 2: Obiect / Produs", expanded=True):
        obj_file = st.file_uploader("Urcă Poză Produs", type=["jpg", "png"], key="obj")
        if obj_file:
            obj_scale = st.slider("Mărime Produs (%)", 10, 200, 100)
            obj_y_offset = st.slider("Poziție Verticală (Y)", 0, 1920, 960)
            obj_x_offset = st.slider("Aliniere față de Mână (X)", -300, 300, 50)

    with st.expander("🖐️ Layer 3: Mâna Alpha", expanded=True):
        hand_file = st.file_uploader("Urcă Video Mână (.webm)", type=["webm", "mov"], key="hand")
        if hand_file:
            hand_scale = st.slider("Mărime Mână (%)", 10, 200, 100)

    st.divider()
    durata = st.number_input("Durată Totală (secunde)", 1, 15, 5)
    viteza = st.select_slider("Viteză Mișcare", options=[200, 400, 600, 800, 1000], value=400)
    directie = st.radio("Sensul Mișcării", ["Stânga -> Dreapta", "Dreapta -> Stânga"], horizontal=True)

with col_prev:
    st.subheader("📺 Monitor Previzualizare Live")
    if bg_file and obj_file:
        # Generare Preview cu PIL
        bg_img = Image.open(bg_file).convert("RGBA").resize((1080, 1920))
        
        # Procesare Produs
        obj_raw = Image.open(obj_file).convert("RGBA")
        new_size = (int(400 * (obj_scale/100)), int(400 * (obj_scale/100)))
        obj_img = obj_raw.resize(new_size)
        
        # Poziționare statică pentru preview (Centru)
        bg_img.paste(obj_img, (540 - (new_size[0]//2) + obj_x_offset, obj_y_offset), obj_img)
        
        st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
        st.image(bg_img, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("ℹ️ Aceasta este o simulare a așezării straturilor.")
    else:
        st.info("Încarcă fișierele pentru a calibra mărimea și poziția.")

# --- BUTON RENDER ---
if st.button("🚀 GENEREAZĂ CLIPUL FINAL (SAVE MP4)"):
    if bg_file and hand_file and obj_file:
        with st.spinner("Se procesează producția..."):
            try:
                # Salvare temp fișiere
                with open("b.png", "wb") as f: f.write(bg_file.read())
                with open("o.png", "wb") as f: f.write(obj_file.read())
                with open("h.webm", "wb") as f: f.write(hand_file.read())

                W, H = 1080, 1920

                # Logică Mișcare Sincronizată
                def get_pos(t):
                    if directie == "Stânga -> Dreapta":
                        x = -500 + (viteza * t)
                    else:
                        x = W + 100 - (viteza * t)
                    return (x, obj_y_offset)

                # Creare Clipuri MoviePy
                bg = ImageClip("b.png").set_duration(durata).resize(height=H)
                if bg.w > W: bg = bg.crop(x_center=bg.w/2, width=W)

                obj_w = int(400 * (obj_scale/100))
                obj = (ImageClip("o.png")
                       .set_duration(durata)
                       .resize(width=obj_w)
                       .set_position(lambda t: (get_pos(t)[0] + obj_x_offset, get_pos(t)[1])))

                hand_w = int(600 * (hand_scale/100))
                hand = (VideoFileClip("h.webm", has_mask=True)
                        .loop(duration=durata)
                        .resize(width=hand_w)
                        .set_position(get_pos))

                # Mixaj Final
                final = CompositeVideoClip([bg, obj, hand], size=(W, H))
                final.write_videofile("productie_finala.mp4", fps=30, codec="libx264", audio=False)
                
                st.video("productie_finala.mp4")
                with open("productie_finala.mp4", "rb") as f:
                    st.download_button("📥 SALVEAZĂ VIDEO (MP4)", f, file_name="tiktok_edit.mp4")
            
            except Exception as e:
                st.error(f"Eroare tehnică la randare: {e}")
