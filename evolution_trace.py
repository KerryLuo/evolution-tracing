import streamlit as st
from streamlit_canvas import st_canvas
from PIL import Image, ImageEnhance

st.set_page_config(page_title="Evolution Tracing Simulator", layout="wide")

# -------------------------------
# Load predetermined base image
# -------------------------------
BASE_IMAGE_PATH = "base_image.png"
base_img = Image.open(BASE_IMAGE_PATH).convert("RGB")

# Dim image (simulate 50% opacity visually)
def dim_image(img, opacity=0.5):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(opacity)

dimmed_base = dim_image(base_img.copy(), opacity=0.5)

# --------------------------------
# Title + Explanation
# --------------------------------
st.title("✏️ Evolution Through Manual Tracing")
st.write("""
Trace the image to create **two children**.  
Each child then becomes a **parent**, and you trace **its two children**, and so on.
""")

# --------------------------------
# Session State Setup
# --------------------------------
if "generations" not in st.session_state:
    st.session_state.generations = 1

if "tree" not in st.session_state:
    st.session_state.tree = {0: [dimmed_base]}

# --------------------------------
# Drawing Function
# --------------------------------
def draw_trace(reference_img, key):
    w, h = reference_img.size

    canvas = st_canvas(
        stroke_width=4,
        stroke_color="black",
        background_image=reference_img,
        height=h,
        width=w,
        drawing_mode="freedraw",
        key=key,
    )

    if canvas.image_data is not None:
        return Image.fromarray(canvas.image_data.astype("uint8")).convert("L")

    return None

# --------------------------------
# Main Evolution Loop
# --------------------------------
st.header("1️⃣ Choose number of generations")
g = st.slider("Generations (binary branching)", 1, 6, 3)

start = st.button("Start Evolution")

if start:
    st.session_state.generations = g
    st.session_state.tree = {0: [dimmed_base]}
    st.experimental_rerun()

# --------------------------------
# Build Generations
# --------------------------------
st.header("2️⃣ Trace each generation")

for gen in range(st.session_state.generations):
    st.subheader(f"Generation {gen}")

    parents = st.session_state.tree.get(gen, [])
    children = []

    for i, parent_img in enumerate(parents):
        st.markdown(f"### Parent {i+1}")

        st.image(parent_img, caption="Reference (50% dimmed)")

        child1 = draw_trace(parent_img, f"Gen_{gen}_Parent_{i}_Child_1")
        child2 = draw_trace(parent_img, f"Gen_{gen}_Parent_{i}_Child_2")

        if child1:
            children.append(child1)
        if child2:
            children.append(child2)

    if children:
        st.session_state.tree[gen + 1] = children

# --------------------------------
# Family Tree Display
# --------------------------------
st.header("3️⃣ Family Tree")

for gen, imgs in st.session_state.tree.items():
    st.subheader(f"Generation {gen}")

    cols = st.columns(min(len(imgs), 5))

    for idx, img in enumerate(imgs):
        with cols[idx % len(cols)]:
            st.image(img, caption=f"G{gen}-{idx+1}")
            if st.button(f"Zoom G{gen}-{idx+1}", key=f"zoom_{gen}_{idx}"):
                st.image(img, caption="Zoomed", width=800)
