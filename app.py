import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import numpy as np

st.title("🎬 Editor Video Custom: Mâna care Mișcă Poze")

# 1. UPLOAD UI
bg_file = st.file_uploader("1. Încarcă Fundalul (Imagine)", type=["png", "jpg"])
obj_file = st.file_uploader("2. Încarcă Poza care trebuie mișcată", type=["png", "jpg"])
hand_file = st.file_uploader("3. Încarcă Clipul cu Mâna (Alpha/Transparent)", type=["mov", "webm"])

if st.button("Generează Video TikTok"):
    if bg_file and obj_file and hand_file:
        with st.spinner("Se procesează..."):
            
            # Setări format vertical TikTok
            W, H = 1080, 1920
            duration = 5
            
            # Creare Fundal
            bg = ImageClip(bg_file.name).set_duration(duration).resize(height=H)
            
            # Funcția de mișcare (Exemplu: Stânga -> Dreapta)
            def coordonate_miscare(t):
                # t merge de la 0 la 5 secunde
                x_start = -200
                viteza = 300
                return (x_start + viteza * t, H / 2)

            # Poza care este „împinsă”
            obiect = (ImageClip(obj_file.name)
                      .set_duration(duration)
                      .resize(width=400)
                      .set_position(lambda t: (coordonate_miscare(t)[0] - 100, H/2))) # offset de 100px față de mână

            # Mâna (deasupra tuturor)
            mana = (VideoFileClip(hand_file.name, has_mask=True)
                    .set_duration(duration)
                    .resize(width=500)
                    .set_position(coordonate_miscare))

            # Combinare straturi: Fundal -> Obiect -> Mână
            video_final = CompositeVideoClip([bg, obiect, mana], size=(W, H))
            
            # Export
            output_path = "tiktok_export.mp4"
            video_final.write_videofile(output_path, fps=30, codec="libx264")
            
            st.video(output_path)
            st.success("Gata! Poți descărca clipul.")
    else:
        st.error("Te rog încarcă toate fișierele!")
