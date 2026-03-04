import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx
import numpy as np
import os

# Configurare pagină
st.set_page_config(page_title="TikTok Alpha Motion Editor", layout="wide")

st.title("🎬 Editor Video TikTok - Alpha Motion")
st.info("Sfat: Pentru transparență, folosește un fișier .webm pentru mână.")

# --- SIDEBAR PENTRU CONTROLUL MIȘCĂRII ---
st.sidebar.header("⚙️ Setări Animație")
durata = st.sidebar.slider("Durată Video (secunde)", 1, 10, 5)
viteza = st.sidebar.slider("Viteză Mișcare (pixeli/secunda)", 100, 1000, 400)
directie = st.sidebar.selectbox("Direcție Mișcare", 
                                ["Stânga la Dreapta", "Dreapta la Stânga", "Sus în Jos", "Jos în Sus"])

# --- ZONA DE UPLOAD ---
col1, col2 = st.columns(2)
with col1:
    bg_file = st.file_uploader("1. Fundal (Imagine JPG/PNG)", type=["jpg", "png"])
    hand_file = st.file_uploader("2. Mână Transparentă (Video .webm/.mov)", type=["webm", "mov"])

with col2:
    obj_files = st.file_uploader("3. Obiecte de mișcat (Poți urca mai multe)", type=["jpg", "png"], accept_multiple_files=True)

# --- PROCESARE VIDEO ---
if st.button("🚀 GENEREAZĂ VIDEO PENTRU TIKTOK"):
    if bg_file and hand_file and obj_files:
        with st.spinner("Se randează video-ul... Te rog așteaptă."):
            try:
                # Salvare temporară fișiere
                with open("bg_temp.png", "wb") as f: f.write(bg_file.read())
                with open("hand_temp.webm", "wb") as f: f.write(hand_file.read())
                
                W, H = 1080, 1920 # Rezoluție TikTok
                
                # 1. Creare Fundal (Vertical)
                bg = ImageClip("bg_temp.png").set_duration(durata).resize(height=H)
                if bg.w > W: 
                    bg = bg.crop(x_center=bg.w/2, width=W)
                else:
                    bg = bg.resize(width=W)

                # 2. Funcția de mișcare matematică
                def path_function(t):
                    if directie == "Stânga la Dreapta":
                        return (-300 + viteza * t, H/2 - 200)
                    elif directie == "Dreapta la Stânga":
                        return (W + 100 - viteza * t, H/2 - 200)
                    elif directie == "Sus în Jos":
                        return (W/2 - 200, -300 + viteza * t)
                    else: # Jos în Sus
                        return (W/2 - 200, H + 100 - viteza * t)

                # 3. Pregătire Mână (Alpha Layer)
                mana = (VideoFileClip("hand_temp.webm", has_mask=True)
                        .loop(duration=durata)
                        .resize(width=500)
                        .set_position(path_function))

                # 4. Pregătire Canale Obiecte (Toate urmăresc mâna)
                clips = [bg]
                for i, obj in enumerate(obj_files):
                    temp_obj_path = f"obj_{i}.png"
                    with open(temp_obj_path, "wb") as f: f.write(obj.read())
                    
                    # Fiecare obiect este plasat sub mână cu un mic decalaj (offset)
                    o_clip = (ImageClip(temp_obj_path)
                              .set_duration(durata)
                              .resize(width=400)
                              .set_position(lambda t, idx=i: (path_function(t)[0] + 50, path_function(t)[1] + 150)))
                    clips.append(o_clip)
                
                # Mâna se adaugă ultima ca să fie peste obiecte
                clips.append(mana)

                # 5. Compoziția și Exportul
                video_final = CompositeVideoClip(clips, size=(W, H))
                output_name = "tiktok_result.mp4"
                
                # Folosim libx264 pentru compatibilitate maximă cu TikTok
                video_final.write_videofile(output_name, fps=30, codec="libx264", audio=False)

                # Afișare Rezultat
                st.video(output_name)
                with open(output_name, "rb") as file:
                    st.download_button(label="📥 Descarcă Video", 
                                     data=file, 
                                     file_name="video_tiktok_creat.mp4", 
                                     mime="video/mp4")
                
                st.success("Succes! Video-ul a fost generat.")

            except Exception as e:
                st.error(f"Eroare tehnică: {e}")
                st.info("Asigură-te că fișierul 'mână' are canal Alpha (transparență).")
    else:
        st.warning("⚠️ Te rog încarcă Fundalul, Mâna și cel puțin o Poză!")

# Curățare fișiere temporare (opțional)
