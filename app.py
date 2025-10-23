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
    age = st.selectbox("Age Group", ["Any", "Child", "Teen", "Young Woman", "Adult Woman", "Middle Aged", "Elderly"], index=3)
with col3:
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
    base = "A detailed pencil sketch portrait of"
    subject_parts = []

    if age != "Any":
        subject_parts.append(age.lower())
    if gender != "Any":
        subject_parts.append(gender.lower())
    if expression != "Neutral":
        subject_parts.append(f"{expression.lower()} expression")

    subject_description = " ".join(subject_parts) if subject_parts else "a person"

    # core artistic prompt
    prompt = (
        f"{base} {subject_description}, "
        f"{pose.lower()}, drawn on textured sketch paper using graphite pencils. "
        f"Fine pencil strokes, detailed shading, natural proportions, cross-hatching technique, "
        f"light and shadow contrast, hand-drawn feel, artistic imperfections preserved."
    )

    # user extra notes
    if prompt_user.strip():
        prompt += f" {prompt_user.strip()}"

    # strong negative prompt
    negative = (
        "no color, no watercolor, no digital paint, no 3d render, no realism, no ink, no marker, "
        "no background clutter, no text, no watermark, no logo, no signature, no cartoon style, no anime."
    )

    return f"{prompt} --negative: {negative}"

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