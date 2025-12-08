import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageEnhance

st.set_page_config(page_title="Evolution Tracing Simulator", layout="wide")

# -------------------------------------------------------
# Load predetermined base image
# -------------------------------------------------------
BASE_IMAGE_PATH = "base_image.png"  # put this in the repo root
base_img = Image.open(BASE_IMAGE_PATH).convert("RGB")


def dim_image(img, opacity=0.5):
    """Visually dim the reference image (simulated 50% opacity)."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(opacity)


dimmed_base = dim_image(base_img.copy(), opacity=0.5)

# -------------------------------------------------------
# Drawing function using streamlit-drawable-canvas
# -------------------------------------------------------
def draw_trace(reference_img, key):
    w, h = reference_img.size

    st.markdown(f"**Trace: {key}**")

    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # transparent fill
        stroke_width=4,
        stroke_color="black",
        background_color="#FFFFFF",
        background_image=reference_img,  # the dimmed parent
        update_streamlit=False,          # only update on interaction
        height=h,
        width=w,
        drawing_mode="freedraw",
        point_display_radius=0,
        display_toolbar=False,           # no erase/undo toolbar
        key=key,
    )

    if canvas_result.image_data is not None:
        # canvas_result.image_data is a NumPy array (H, W, 4)
        return Image.fromarray(canvas_result.image_data.astype("uint8")).convert("L")

    return None


# -------------------------------------------------------
# App UI
# -------------------------------------------------------
st.title("✏️ Evolution Through Manual Tracing")
st.write(
    """
Trace a simple lineart animal over multiple generations.

- Start from a base image (Generation 0).
- Each **parent** produces **two children** by tracing.
- Each child becomes the parent of the next generation.
- At the end, you see the whole **evolution family tree**.
"""
)

# Initialize session state
if "tree" not in st.session_state:
    # Generation 0: just the base dimmed reference image
    st.session_state.tree = {0: [dimmed_base]}

if "generations" not in st.session_state:
    st.session_state.generations = 3

# -------------------------------------------------------
# Controls
# -------------------------------------------------------
st.header("1️⃣ Select number of generations")
g = st.slider("Generations (binary branching)", 1, 6, st.session_state.generations)

col1, col2 = st.columns(2)
with col1:
    if st.button("Start / Restart"):
        st.session_state.generations = g
        st.session_state.tree = {0: [dimmed_base]}
        st.experimental_rerun()

with col2:
    st.write(f"Current generations: **{st.session_state.generations}**")

# -------------------------------------------------------
# Build Generations
# -------------------------------------------------------
st.header("2️⃣ Trace each generation")

for gen in range(st.session_state.generations):
    st.subheader(f"Generation {gen}")
    parents = st.session_state.tree.get(gen, [])
    children = []

    for i, parent_img in enumerate(parents):
        st.markdown(f"### Parent {i + 1} (Gen {gen})")
        st.image(parent_img, caption="Reference (dimmed parent)")

        # Two children traced from this parent
        child1 = draw_trace(parent_img, f"G{gen}_P{i}_C1")
        child2 = draw_trace(parent_img, f"G{gen}_P{i}_C2")

        if child1 is not None:
            children.append(child1)
        if child2 is not None:
            children.append(child2)

    if children:
        st.session_state.tree[gen + 1] = children

# -------------------------------------------------------
# Family Tree Display
# -------------------------------------------------------
st.header("3️⃣ Family Tree")

for gen, imgs in st.session_state.tree.items():
    st.subheader(f"Generation {gen}")
    cols = st.columns(min(4, len(imgs)))
    for idx, img in enumerate(imgs):
        with cols[idx % len(cols)]:
            st.image(img, caption=f"G{gen}-{idx + 1}")
            if st.button(f"🔍 Zoom G{gen}-{idx + 1}", key=f"zoom_{gen}_{idx}"):
                st.image(img, caption=f"Zoomed G{gen}-{idx + 1}", width=800)
