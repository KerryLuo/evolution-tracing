import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageEnhance
import math

st.set_page_config(page_title="Evolution Tracing Simulator", layout="wide")

# -------------------------------
# Load predetermined base image
# -------------------------------
BASE_IMAGE_PATH = "base_image.png"   # <-- replace with your own lineart file
base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")

# Reduce opacity for tracing reference
def dim_image(img, opacity=0.5):
    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)
    return img

dimmed_base = dim_image(base_img.copy(), opacity=0.5)

# --------------------------------
# Title + Explanation
# --------------------------------
st.title("✏️ Evolution Through Manual Tracing")
st.write("""
Trace the image to create **two children**.  
Each child then becomes a **parent**, and you trace **its two children**, and so on.

This creates an **evolutionary family tree** built entirely from human-made drawing drift.
""")

# --------------------------------
# Session State Setup
# --------------------------------
if "generations" not in st.session_state:
    st.session_state.generations = 1

if "tree" not in st.session_state:
    st.session_state.tree = {0: [dimmed_base]}  # generation 0 contains the base ref

if "drawings" not in st.session_state:
    st.session_state.drawings = {}  # store child drawings for each parent


# --------------------------------
# Drawing Function
# --------------------------------
def draw_trace(reference_img, label):
    w, h = reference_img.size

    st.subheader(label)

    canvas = st_canvas(
        fill_color="rgba(255,255,255,0)",
        stroke_width=4,
        stroke_color="black",
        background_image=reference_img,
        height=h,
        width=w,
        drawing_mode="freedraw",
        key=label,
    )

    if canvas.image_data is not None:
        drawn = Image.fromarray(canvas.image_data.astype("uint8")).convert("L")
        return drawn

    return None


# --------------------------------
# Main Evolution Loop
# --------------------------------
st.header("1️⃣ Choose number of generations")
g = st.slider("Generations (binary branching)", 1, 6, 3)

start = st.button("Start Evolution Process")

if start:
    st.session_state.generations = g
    st.session_state.tree = {0: [dimmed_base]}
    st.session_state.drawings = {}
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
        st.markdown(f"### Parent {i+1} (Generation {gen})")

        colA, colB = st.columns(2)

        with colA:
            st.image(parent_img, caption="Reference (50% opacity)")

        # Each parent gets two children to trace
        child1 = draw_trace(parent_img, f"Gen{gen}_Parent{i}_Child1")
        child2 = draw_trace(parent_img, f"Gen{gen}_Parent{i}_Child2")

        # Save output if drawn
        if child1 is not None:
            children.append(child1)
        if child2 is not None:
            children.append(child2)

    # Store next generation
    if len(children) > 0:
        st.session_state.tree[gen + 1] = children


# --------------------------------
# Display Family Tree
# --------------------------------
st.header("3️⃣ Family Tree Output")

if st.session_state.generations in st.session_state.tree:
    generations = st.session_state.tree

    for gen, imgs in generations.items():
        st.subheader(f"Generation {gen}")

        cols = st.columns(min(len(imgs), 5))

        for idx, img in enumerate(imgs):
            with cols[idx % len(cols)]:
                st.image(img, caption=f"G{gen} - #{idx+1}")
                if st.button(f"Zoom G{gen}-{idx+1}", key=f"zoom_{gen}_{idx}"):
                    st.image(img, caption="Zoomed View", width=800)

