import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np
import os

# Configurare stil Studio
st.set_page_config(page_title="Studio Producție TikTok", layout="wide")

st.title("🎬 Studio Producție: Mâna Alpha")

# --- INTERFAȚĂ COLOANE ---
col_setari, col_preview = st.columns([1, 2])

with col_setari:
    st.header("🎚️ Consolă Control")
    bg_file = st.file_uploader("Canal 1: Fundal (JPG/PNG)", type=["jpg", "png"])
    hand_file = st.file_uploader("Canal 2: Mâna Alpha (.webm)", type=["webm", "mov"])
    obj_files = st.file_uploader("Canal 3: Obiecte/Produse (JPG/PNG)", type=["jpg", "png"], accept_multiple_files=True)
    
    st.divider()
    durata = st.slider("Lungime Clip (sec)", 1, 10, 5)
    viteza = st.slider("Viteza Mișcării", 100, 800, 400)
    directie = st.selectbox("Direcție", ["Stânga la Dreapta", "Dreapta la Stânga"])

with col_preview:
    st.header("📺 Monitor Previzualizare")
    if bg_file and obj_files:
        # Previzualizare rapidă (Thumbnail)
        img_bg = Image.open(bg_file).convert("RGBA").resize((1080, 1920))
        img_obj = Image.open(obj_files[0]).convert("RGBA").resize((400, 400))
        img_bg.paste(img_obj, (340, 900), img_obj)
        st.image(img_bg, caption="Draft Vizual (Layer 1 + Layer 3)", width=300)
    else:
        st.info("Încarcă fișierele pentru a vedea preview-ul straturilor.")

# --- BUTONUL DE SALVARE (RENDER) ---
if st.button("🚀 EXECUȚĂ PRODUCȚIA (SAVE AS MP4)"):
    if bg_file and hand_file and obj_files:
        with st.spinner("Se randează video-ul..."):
            try:
                # Salvare temporară fișiere
                with open("temp_bg.png", "wb") as f: f.write(bg_file.read())
                with open("temp_hand.webm", "wb") as f: f.write(hand_file.read())
                
                W, H = 1080, 1920
                
                # 1. Background
                bg = ImageClip("temp_bg.png").set_duration(durata).resize(height=H)
                if bg.w > W: bg = bg.crop(x_center=bg.w/2, width=W)
                
                # 2. Funcție mișcare
                def move_logic(t):
                    if directie == "Stânga la Dreapta":
                        return (-300 + viteza * t, H/2)
                    return (W + 100 - viteza * t, H/2)

                # 3. Mâna (Canal Alpha)
                mana = (VideoFileClip("temp_hand.webm", has_mask=True)
                        .loop(duration=durata)
                        .resize(width=500)
                        .set_position(move_logic))

                # 4. Obiectele
                clips = [bg]
                for i, obj in enumerate(obj_files):
                    path = f"temp_obj_{i}.png"
                    with open(path, "wb") as f: f.write(obj.read())
                    o_clip = (ImageClip(path)
                              .set_duration(durata)
                              .resize(width=400)
                              .set_position(lambda t: (move_logic(t)[0] + 50, move_logic(t)[1] + 100)))
                    clips.append(o_clip)
                
                clips.append(mana)

                # 5. Export Final
                video = CompositeVideoClip(clips, size=(W, H))
                video.write_videofile("final.mp4", fps=30, codec="libx264", audio=False)
                
                st.video("final.mp4")
                with open("final.mp4", "rb") as f:
                    st.download_button("📥 DESCARCĂ REZULTATUL", f, file_name="tiktok_final.mp4")
                    
            except Exception as e:
                st.error(f"Eroare: {e}")
    else:
        st.warning("Lipsesc fișiere din canale!")
