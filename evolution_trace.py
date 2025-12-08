import streamlit as st
from PIL import Image, ImageEnhance
import base64
from io import BytesIO

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
# HTML CANVAS (works 100% on Streamlit Cloud)
# -------------------------------------------------------
def draw_canvas(reference_img, key):
    """Create an HTML5 drawing canvas with reference background."""
    w, h = reference_img.size

    # Convert reference image to base64 for embedding
    buffer = BytesIO()
    reference_img.save(buffer, format="PNG")
    bg_b64 = base64.b64encode(buffer.getvalue()).decode()

    # HTML
    html = f"""
    <style>
      canvas {{
        border: 1px solid #000;
        background-image: url('data:image/png;base64,{bg_b64}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        touch-action: none;
      }}
    </style>

    <canvas id="{key}" width="{w}" height="{h}"></canvas>

    <script>
    const canvas = document.getElementById("{key}");
    const ctx = canvas.getContext("2d");
    let drawing = false;

    canvas.addEventListener("pointerdown", () => drawing = true);
    canvas.addEventListener("pointerup", () => drawing = false);
    canvas.addEventListener("pointermove", function(e) {{
        if (!drawing) return;
        const rect = canvas.getBoundingClientRect();
        ctx.lineWidth = 4;
        ctx.lineCap = "round";
        ctx.strokeStyle = "black";
        ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    }});

    function saveImage() {{
        const data = canvas.toDataURL("image/png");
        const pyInput = document.getElementById("{key}_data");
        pyInput.value = data;
    }}
    </script>

    <button onclick="saveImage()">Save Drawing</button>
    <textarea id="{key}_data" name="{key}_data" style="display:none"></textarea>
    """

    st.components.v1.html(html, height=h + 80)

    # Get data saved via JS
    data = st.session_state.get(f"{key}_data", None)
    if data and data.startswith("data:image/png;base64,"):
        b64 = data.split(",", 1)[1]
        raw = base64.b64decode(b64)
        return Image.open(BytesIO(raw)).convert("L")

    return None


# Hook JavaScript values into Streamlit state
def sync_js(key):
    val = st.session_state.get(f"{key}_data", None)
    return val


# -------------------------------------------------------
# App UI
# -------------------------------------------------------
st.title("✏️ Evolution Through Manual Tracing")

if "tree" not in st.session_state:
    st.session_state.tree = {0: [dimmed_base]}

st.header("1️⃣ Select number of generations")
gens = st.slider("Generations", 1, 6, 3)

if st.button("Restart"):
    st.session_state.tree = {0: [dimmed_base]}
    st.experimental_rerun()

st.header("2️⃣ Trace each generation")

for gen in range(gens):
    st.subheader(f"Generation {gen}")
    parents = st.session_state.tree.get(gen, [])
    children = []

    for i, parent in enumerate(parents):
        st.image(parent, caption=f"Parent {i+1} (dimmed)")
        key1 = f"G{gen}_P{i}_C1"
        key2 = f"G{gen}_P{i}_C2"

        # Two children
        child1 = draw_canvas(parent, key1)
        child2 = draw_canvas(parent, key2)

        if child1: children.append(child1)
        if child2: children.append(child2)

    st.session_state.tree[gen + 1] = children

st.header("3️⃣ Family Tree")

for gen, images in st.session_state.tree.items():
    st.subheader(f"Generation {gen}")
    cols = st.columns(4)
    for i, img in enumerate(images):
        with cols[i % 4]:
            st.image(img, caption=f"G{gen}-{i+1}")
