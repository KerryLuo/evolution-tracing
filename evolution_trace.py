import streamlit as st
from streamlit_canvas import st_canvas
from PIL import Image, ImageEnhance

st.set_page_config(page_title="Evolution Tracing Simulator", layout="wide")

# ---------------------------------------------------------
# Load predetermined base image
# ---------------------------------------------------------
BASE_IMAGE_PATH = "base_image.png"
base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")

def dim_image(img, opacity=0.5):
    """Lower opacity for tracing reference."""
    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)
    return img

dimmed_base = dim_image(base_img.copy(), opacity=0.5)

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("✏️ Evolution Through Manual Tracing")
st.write("""
Trace an image to create children.  
Each child becomes a parent for the next generation.  
This produces a branching **evolution family tree** through drawing drift.
""")

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------
if "tree" not in st.session_state:
    st.session_state.tree = {0: [dimmed_base]}

if "generations" not in st.session_state:
    st.session_state.generations = 1


# ---------------------------------------------------------
# Draw a traced child
# ---------------------------------------------------------
def draw_trace(reference_img, label):
    w, h = reference_img.size

    st.markdown(f"#### {label}")

    canvas = st_canvas(
        stroke_width=4,
        stroke_color="black",
        background_image=reference_img,
        height=h,
        width=w,
        drawing_mode="freedraw",
        key=label
    )

    if canvas.image_data is not None:
        # Convert drawn image to PIL
        drawn = Image.fromarray(canvas.image_data.astype("uint8")).convert("L")
        return drawn

    return None


# ---------------------------------------------------------
# User selects generations
# ---------------------------------------------------------
st.header("1️⃣ Choose Number of Generations")
g = st.slider("Generations (binary branching)", 1, 6, st.session_state.generations)
if st.button("Start Over"):
    st.session_state.tree = {0: [dimmed_base]}
    st.session_state.generations = g
    st.experimental_rerun()


# ---------------------------------------------------------
# Build Generations
# ---------------------------------------------------------
st.header("2️⃣ Trace Each Generation")

for gen in range(st.session_state.generations):
    st.subheader(f"Generation {gen}")

    parents = st.session_state.tree.get(gen, [])
    children = []

    for i, parent_img in enumerate(parents):
        st.markdown(f"### Parent {i+1}")

        # Display parent reference
        st.image(parent_img, caption="Reference (50% opacity)")

        # Child 1 + Child 2
        child1 = draw_trace(parent_img, f"G{gen} Parent {i+1} → Child 1")
        child2 = draw_trace(parent_img, f"G{gen} Parent {i+1} → Child 2")

        if child1 is not None:
            children.append(child1)
        if child2 is not None:
            children.append(child2)

    # Save next generation
    if len(children) > 0:
        st.session_state.tree[gen + 1] = children


# ---------------------------------------------------------
# Display Family Tree
# ---------------------------------------------------------
st.header("3️⃣ Family Tree")

for gen, imgs in st.session_state.tree.items():
    st.subheader(f"Generation {gen}")
    columns = st.columns(min(len(imgs), 5))

    for idx, img in enumerate(imgs):
        with columns[idx % len(columns)]:
            st.image(img, caption=f"G{gen} — #{idx+1}")
            if st.button(f"🔍 Zoom G{gen}-{idx+1}", key=f"zoom_{gen}_{idx}"):
                st.image(img, caption="Zoomed View", width=800)
