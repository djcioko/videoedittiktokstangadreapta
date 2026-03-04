import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import numpy as np
import os

# Configurare interfață tip Studio
st.set_page_config(page_title="TikTok Production Studio", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Studio Video TikTok: Hand-Motion Alpha")

# --- COLOANE DE LUCRU ---
col_timeline, col_preview = st.columns([1, 1])

with col_timeline:
    st.subheader("🎞️ Canale Timeline (Layers)")
    
    with st.expander("LAYER 1: Fundal (Background)", expanded=True):
        bg_file = st.file_uploader("Urcă imaginea de fundal", type=["jpg", "png"], key="bg")

    with st.expander("LAYER 2: Obiect Mișcat (Produs)", expanded=True):
        obj_file = st.file_uploader("Urcă imaginea produsului", type=["jpg", "png"], key="obj")

    with st.expander("LAYER 3: Mâna Alpha (Master)", expanded=True):
        hand_file = st.file_uploader("Urcă clipul transparent (.webm)", type=["webm", "mov"], key="hand")

    st.subheader("⚙️ Control Mișcare & Render")
    durata = st.slider("Durată clip (secunde)", 1, 10, 5)
    viteza = st.slider("Viteză animație", 100, 1000, 400)
    directie = st.radio("Direcție mișcare", ["Stânga la Dreapta", "Dreapta la Stânga"], horizontal=True)

with col_preview:
    st.subheader("📺 Monitor Previzualizare (Preview)")
    if bg_file and obj_file:
        # Generăm un "Thumbnail" rapid pentru a vedea straturile
        img_bg = Image.open(bg_file).convert("RGBA").resize((1080, 1920))
        img_obj = Image.open(obj_file).convert("RGBA").resize((400, 400))
        # Simulăm poziția pe monitor
        img_bg.paste(img_obj, (340, 800), img_obj)
        st.image(img_bg, caption="Draft Vizual: Verifică poziția straturilor", width=300)
    else:
        st.info("Încarcă fișierele în timeline pentru a activa monitorul.")

# --- LOGICA DE RENDER (SAVE AS) ---
if st.button("🚀 GENEREAZĂ PRODUCȚIA FINALĂ"):
    if bg_file and hand_file and obj_file:
        with st.spinner("Se procesează canalele... Te rog așteaptă."):
            try:
                # Salvare fișiere temporare
                with open("temp_bg.png", "wb") as f: f.write(bg_file.read())
                with open("temp_hand.webm", "wb") as f: f.write(hand_file.read())
                with open("temp_obj.png", "wb") as f: f.write(obj_file.read())
                
                W, H = 1080, 1920 # Format TikTok
                
                # 1. Procesare Fundal
                bg_clip = ImageClip("temp_bg.png").set_duration(durata).resize(height=H)
                if bg_clip.w > W: bg_clip = bg_clip.crop(x_center=bg_clip.w/2, width=W)
                
                # 2. Logica de mișcare matematică (Sincronizare)
                def get_pos(t):
                    if directie == "Stânga la Dreapta":
                        x = -400 + (viteza * t)
                    else:
                        x = W + 100 - (viteza * t)
                    return (x, H/2)

                # 3. Stratul Mână (Alpha)
                hand_clip = (VideoFileClip("temp_hand.webm", has_mask=True)
                             .loop(duration=durata)
                             .resize(width=600)
                             .set_position(get_pos))

                # 4. Stratul Obiect (Urmărește mâna)
                # Îi dăm un mic offset (+100, +150) ca să pară că e sub palma mâinii
                obj_clip = (ImageClip("temp_obj.png")
                            .set_duration(durata)
                            .resize(width=400)
                            .set_position(lambda t: (get_pos(t)[0] + 100, get_pos(t)[1] + 150)))

                # 5. Compoziție Finală (Layering)
                final_video = CompositeVideoClip([bg_clip, obj_clip, hand_clip], size=(W, H))
                output_file = "tiktok_final.mp4"
                final_video.write_videofile(output_file, fps=30, codec="libx264", audio=False)
                
                # Afișare și Download
                st.video(output_file)
                with open(output_file, "rb") as f:
                    st.download_button("📥 DESCARCĂ VIDEO (SAVE AS)", f, file_name="video_tiktok.mp4")
                st.success("Randare finalizată cu succes!")

            except Exception as e:
                st.error(f"Eroare la randare: {e}")
    else:
        st.warning("⚠️ Toate canalele (1, 2 și 3) trebuie să conțină fișiere!")
