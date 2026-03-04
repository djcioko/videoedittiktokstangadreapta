import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image
import os

# Configurare stil Studio Dark
st.set_page_config(page_title="Video Motion Studio", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #111111; }
    .stSidebar { background-color: #1a1a1a; }
    div.stButton > button:first-child {
        background-color: #00cc66;
        color: white;
        height: 3em;
        font-size: 20px;
        font-weight: bold;
    }
    .layer-box {
        border: 1px solid #333;
        padding: 10px;
        border-radius: 5px;
        background-color: #222;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Studio Motion Pro (Alpha Layers)")

# --- ZONA DE MONTAJ (LAYOUT) ---
col_preview, col_layers = st.columns([1.5, 1])

with col_layers:
    st.subheader("📼 Canale de Lucru (Layers)")
    
    with st.container():
        st.markdown("<div class='layer-box'>", unsafe_allow_html=True)
        bg_file = st.file_uploader("Layer 1: Fundal", type=["jpg", "png"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='layer-box'>", unsafe_allow_html=True)
        obj_file = st.file_uploader("Layer 2: Obiect/Produs", type=["jpg", "png"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='layer-box'>", unsafe_allow_html=True)
        hand_file = st.file_uploader("Layer 3: Mâna (Alpha Video)", type=["webm", "mov"])
        st.markdown("</div>", unsafe_allow_html=True)

with col_preview:
    st.subheader("📺 Monitor de Control")
    if bg_file and obj_file:
        # Generăm Preview Visual
        bg_img = Image.open(bg_file).convert("RGBA").resize((1080, 1920))
        obj_img = Image.open(obj_file).convert("RGBA").resize((450, 450))
        
        # Centrare preview
        bg_img.paste(obj_img, (315, 800), obj_img)
        st.image(bg_img, width=380)
    else:
        st.info("Încarcă elementele pentru a activa monitorul de previzualizare.")

# --- TIMELINE & CONTROL (JOS) ---
st.divider()
st.subheader("⏳ Timeline & Setări Mișcare")
c1, c2, c3, c4 = st.columns(4)

with c1:
    durata = st.number_input("Durată Video (sec)", 1, 10, 5)
with c2:
    viteza = st.select_slider("Viteză Mișcare", options=[200, 400, 600, 800], value=400)
with c3:
    directie = st.selectbox("Direcție Animație", ["Stânga la Dreapta", "Dreapta la Stânga"])
with c4:
    offset_y = st.slider("Poziție Verticală Obiect", 400, 1500, 900)

# --- RENDER BUTTON ---
if st.button("🚀 RENDER & SAVE VIDEO (TIKTOK FORMAT)"):
    if bg_file and hand_file and obj_file:
        with st.spinner("Producția este în curs..."):
            try:
                # Salvare temp
                with open("b.png", "wb") as f: f.write(bg_file.read())
                with open("o.png", "wb") as f: f.write(obj_file.read())
                with open("h.webm", "wb") as f: f.write(hand_file.read())
                
                W, H = 1080, 1920
                
                # Logică Mișcare
                def get_pos(t):
                    x = -500 + (viteza * t) if directie == "Stânga la Dreapta" else W + 200 - (viteza * t)
                    return (x, offset_y)

                # Clips
                bg = ImageClip("b.png").set_duration(durata).resize(height=H)
                if bg.w > W: bg = bg.crop(x_center=bg.w/2, width=W)
                
                obj = ImageClip("o.png").set_duration(durata).resize(width=450).set_position(lambda t: (get_pos(t)[0]+50, get_pos(t)[1]+50))
                hand = VideoFileClip("h.webm", has_mask=True).loop(duration=durata).resize(width=650).set_position(get_pos)

                final = CompositeVideoClip([bg, obj, hand], size=(W, H))
                final.write_videofile("out.mp4", fps=30, codec="libx264", audio=False)
                
                st.video("out.mp4")
                with open("out.mp4", "rb") as f:
                    st.download_button("📥 SALVEAZĂ VIDEO", f, file_name="tiktok.mp4")
            except Exception as e:
                st.error(f"Eroare: {e}")
