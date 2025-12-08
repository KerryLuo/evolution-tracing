import streamlit as st
from PIL import Image, ImageEnhance
from streamlit_paint import paint

st.set_page_config(page_title="Evolution Tracing Simulator", layout="wide")

# -------------------------------------------------------
# Load predetermined base image
# -------------------------------------------------------
BASE_IMAGE_PATH = "base_image.png"
base_img = Image.open(BASE_IMAGE_PATH).convert("RGB")

def dim_image(img, opacity=0.5):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(opacity)

dimmed_base = dim_image(base_img.copy(), opacity=0.5)

# -------------------------------------------------------
# Drawing function using streamlit-paint
# -------------------------------------------------------
def draw_trace(reference_img, key):
    w, h = reference_img.size
    st.write(f"#### {key}")

    result = paint(
        width=w,
        height=h,
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        background_image=reference_img,
        key=key,
    )

    if result.image is not None:
        return result.image.convert("L")

    return None

# -------------------------------------------------------
# App UI
# -------------------------------------------------------
st.title("✏️ Evolution Through Manual Tracing")

if "tree" not in st.session_state:
    st.session_state.tree = {0: [dimmed_base]}

st.header("1️⃣ Select Generations")
g = st.slider("Generations", min_value=1, max_value=6, value=3)

if st.button("Reset"):
    st.session_state.tree = {0: [dimmed_base]}
    st.experimental_rerun()

st.header("2️⃣ Trace Each Generation")

for gen in range(g):
    st.subheader(f"Generation {gen}")
    parents = st.session_state.tree.get(gen, [])
    children = []

    for i, parent_img in enumerate(parents):
        st.image(parent_img, caption=f"Parent {i+1}")

        child1 = draw_trace(parent_img, f"G{gen}_P{i}_C1")
        child2 = draw_trace(parent_img, f"G{gen}_P{i}_C2")

        if child1: children.append(child1)
        if child2: children.append(child2)

    if children:
        st.session_state.tree[gen+1] = children

st.header("3️⃣ Family Tree")

for gen, imgs in st.session_state.tree.items():
    st.subheader(f"Generation {gen}")
    cols = st.columns(4)
    for i, img in enumerate(imgs):
        with cols[i % 4]:
            st.image(img, caption=f"G{gen}-{i+1}")
