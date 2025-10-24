import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import random

# ----------------------------
# 🔧 APP CONFIG
# ----------------------------
st.set_page_config(page_title="Gemini Pencil Sketch Generator", page_icon="✏", layout="centered")
st.title("✏ Gemini Text-to-Image — Pencil Sketch Portrait Generator")

# ----------------------------
# 🔑 BACKEND API KEY (fixed)
# ----------------------------
API_KEY = "AIzaSyB9LdtEWGEpNotTf6h1KdfQEAtjkws0i34"  # 🔒 Replace this with your actual Google Gemini API key
client = genai.Client(api_key=API_KEY)

# ----------------------------
# 🎛 User Controls
# ----------------------------
st.header("🧠 Describe Your Portrait")

col1, col2, col3 = st.columns(3)
with col1:
    gender = st.selectbox("Gender", ["Any", "Male", "Female"], index=2)
with col2:
    age = st.selectbox("Age Group", ["Any", "18-24 months", "20-30 years", "30-40 years", "40-50 years", "50-60 years"], index=3)
with col3:
    ethnicity = st.selectbox("Ethnicity", ["Any", "Caucasian/White", "Hispanic/Latino", "African-American/African", "South Asian", "East Asian", "Middle-Eastern"], index=1)

pose = st.selectbox("Pose", ["Front view", "3/4 view", "Side profile", "Looking down", "Looking up"], index=0)
expression = st.selectbox("Facial Expression", ["Neutral", "Slight Smile", "Full Smile", "Serious", "Calm"], index=1)

# --- Settings ---
st.header("⚙ Generation Settings")

col1, col2, col3 = st.columns(3)
with col1:
    num_images = st.slider("Number of Images", 1, 4, 1)
with col2:
    aspect = st.selectbox("Aspect Ratio", ["AUTO", "1:1", "4:3", "16:9"], index=1)
with col3:
    seed = st.number_input("Seed Value", min_value=0, value=random.randint(1, 9999))

model_choice = st.selectbox(
    "🧩 Choose Model",
    ["imagen-4.0-generate-001", "imagen-3.0-generate-002"],
    index=0,
)

# --- Optional custom details ---
prompt_user = st.text_area(
    "💡 Add any extra artistic details (optional):",
    placeholder="Example: wearing a scarf, light pencil shading around the eyes, background of vintage paper"
)

# ----------------------------
# 🪄 PROMPT BUILDER
# ----------------------------
def build_prompt():
    # --- POSITIVE PROMPT ---
    positive = "hand-drawn graphite pencil sketch portrait of a good looking"

    # Demographics
    if expression != "Neutral":
        positive += f" {expression.lower()}"
    if ethnicity != "Any":
        positive += f" {ethnicity.lower()}"
    if gender != "Any":
        positive += f" {gender.lower()}"
    if age != "Any":
        positive += f", {age.lower()}"

    # Pose and Framing
    positive += " looks at her age, close-up head and upper shoulders,"
    if pose == "Front view":
        positive += " front view, looking directly at viewer, clear eye contact,"
    else:
        positive += f" {pose.lower()},"
    positive += " gentle closed-mouth smile; medium size hair, clothes: lightweight crewneck sweater;"

    # Artistic Style
    positive += " visible pencil strokes, sketchy lines, hand-drawn marks, subtle cross-hatching, paper texture, matte shading, black and white, finished complete portrait, clean framing, full head visible, soft diffuse lighting, traditional pencil rendering, unsigned artwork, no signature, clean sketch"

    # User extra notes
    if prompt_user.strip():
        positive += f", {prompt_user.strip()}"

    # --- NEGATIVE PROMPT ---
    negative = (
        "signature, artist signature, initials, text, letters, watermark, logo, stamp, copyright, monogram, "
        "vector clean outlines, inked lineart, comic inking, cell shading, digital paint, CGI, 3D render, "
        "fully rendered/polished finish, complete hair, global smooth gradients, blending stump/smudge/charcoal wash, "
        "sepia/warm tone/color tint, beauty/cinematic/high-key lighting, glossy skin, specular highlights, rim light, HDR, "
        "pores, microdetail, veins, measurement marks, crosshair, eye-line, multiple guidelines, random strokes, "
        "scribbles, swatches, test marks, margin marks, dust, frame, border, vignette, big/oversized/doll eyes, "
        "strong catchlights, eyeliner, mascara, long eyelashes, teeth, jewelry, hats, bows, slogans, "
        "cropped head, partial head, head out of frame."
    )

    return f"{positive} --negative: {negative}"

# ----------------------------
# 🚀 IMAGE GENERATION
# ----------------------------
if st.button("✨ Generate Pencil Sketch"):
    with st.spinner("Drawing your pencil sketch... please wait ✏"):
        try:
            prompt_final = build_prompt()
            st.info(f"🧾 *Generated Prompt:*\n\n{prompt_final}")

            cfg = types.GenerateImagesConfig(
                number_of_images=num_images,
                aspect_ratio=None if aspect == "AUTO" else aspect,
            )

            response = client.models.generate_images(
                model=model_choice,
                prompt=prompt_final,
                config=cfg,
            )

            if not hasattr(response, "generated_images") or not response.generated_images:
                st.error("❌ No image generated. Try another model or change prompt.")
            else:
                st.success(f"✅ Generated {len(response.generated_images)} image(s) successfully!")

                for i, gi in enumerate(response.generated_images):
                    try:
                        image_bytes = gi.image.image_bytes
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        st.image(pil_image, caption=f"✏ Sketch #{i+1}", use_container_width=True)

                        buf = io.BytesIO()
                        pil_image.save(buf, format="PNG")
                        st.download_button(
                            label=f"⬇ Download Sketch #{i+1}",
                            data=buf.getvalue(),
                            file_name=f"pencil_sketch_{i+1}.png",
                            mime="image/png",
                        )
                    except Exception as inner_e:
                        st.warning(f"⚠ Could not display one image: {inner_e}")
        except Exception as e:
            st.error(f"❌ Generation failed: {e}")
