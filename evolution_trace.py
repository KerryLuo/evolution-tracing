import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Interactive Drawing Evolution", layout="wide")

# Initialize session state
if 'family_tree' not in st.session_state:
    st.session_state.family_tree = []
if 'current_generation' not in st.session_state:
    st.session_state.current_generation = 0
if 'current_parent_index' not in st.session_state:
    st.session_state.current_parent_index = 0
if 'current_child' not in st.session_state:
    st.session_state.current_child = 1  # 1 or 2
if 'original_img' not in st.session_state:
    st.session_state.original_img = None
if 'started' not in st.session_state:
    st.session_state.started = False

def load_image_from_url(url):
    """Load image from URL"""
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img.convert('RGBA')
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def make_semi_transparent(img, opacity=0.5):
    """Make image semi-transparent for tracing"""
    img = img.copy()
    alpha = img.split()[3] if img.mode == 'RGBA' else Image.new('L', img.size, 255)
    alpha = alpha.point(lambda p: int(p * opacity))
    img.putalpha(alpha)
    return img

def start_evolution():
    """Initialize evolution with original image"""
    st.session_state.started = True
    st.session_state.family_tree = [[st.session_state.original_img]]
    st.session_state.current_generation = 0
    st.session_state.current_parent_index = 0
    st.session_state.current_child = 1

def save_traced_child(canvas_result, parent_img):
    """Save the traced drawing as a child"""
    if canvas_result.image_data is not None:
        # Get the drawing from canvas (RGB from RGBA)
        traced_array = canvas_result.image_data[:, :, :3]
        traced_img = Image.fromarray(traced_array.astype('uint8'), 'RGB')
        
        return traced_img
    return None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    if not st.session_state.started:
        image_url = st.text_input(
            "Image URL", 
            value="https://cataas.com/cat?width=400",
            help="Paste a direct link to an image"
        )
        
        st.caption("💡 Try these URLs:")
        st.caption("• https://cataas.com/cat?width=400")
        st.caption("• https://picsum.photos/400")
        st.caption("• https://loremflickr.com/400/400/cat")
        
        num_generations = st.slider(
            "Number of Generations", 
            min_value=1, 
            max_value=4, 
            value=2,
            help="Each generation requires manual tracing"
        )
        
        drawing_mode = st.selectbox(
            "Drawing Tool",
            ["freedraw", "line", "rect", "circle"]
        )
        
        stroke_width = st.slider("Brush Size", 1, 25, 3)
        stroke_color = st.color_picker("Brush Color", "#000000")
        
        canvas_width = 400
        canvas_height = 400
        
        if st.button("🎨 Load Image & Start", type="primary"):
            img = load_image_from_url(image_url)
            if img:
                # Resize to canvas size
                img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                st.session_state.original_img = img
                st.session_state.num_generations = num_generations
                st.session_state.drawing_mode = drawing_mode
                st.session_state.stroke_width = stroke_width
                st.session_state.stroke_color = stroke_color
                st.session_state.canvas_width = canvas_width
                st.session_state.canvas_height = canvas_height
                start_evolution()
                st.rerun()
    else:
        st.success("✅ Evolution in progress!")
        st.metric("Generation", st.session_state.current_generation)
        
        total_in_gen = 2 ** st.session_state.current_generation
        st.metric("Parent", f"{st.session_state.current_parent_index + 1} of {total_in_gen}")
        st.metric("Child", f"{st.session_state.current_child} of 2")
        
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Main App
st.title("🎨 Interactive Drawing Evolution Simulator")

if not st.session_state.started:
    st.markdown("""
    ## How It Works:
    1. Load an image from a URL
    2. The image appears at **50% opacity** for you to trace over
    3. Trace the image **twice** to create 2 children
    4. Each child becomes a parent for the next generation
    5. Watch how small differences accumulate over generations!
    
    **Your hand tremors and imperfections create the evolution!**
    """)
    st.info("👈 Configure settings in the sidebar and click 'Load Image & Start'")

else:
    # Check if we're done with all generations
    if st.session_state.current_generation >= st.session_state.num_generations:
        st.success("🎉 Evolution Complete!")
        
        # Display all generations
        st.header("📊 Family Tree")
        for gen_num, generation in enumerate(st.session_state.family_tree):
            st.subheader(f"Generation {gen_num} ({len(generation)} individuals)")
            cols = st.columns(min(4, len(generation)))
            for idx, img in enumerate(generation):
                with cols[idx % len(cols)]:
                    st.image(img, caption=f"Individual {idx + 1}", use_container_width=True)
            st.markdown("---")
        
        # Comparison
        st.header("🔍 Compare Original vs Final Generation")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(st.session_state.family_tree[0][0], use_container_width=True)
        with col2:
            st.subheader("Final Generation Sample")
            st.image(st.session_state.family_tree[-1][0], use_container_width=True)
    
    else:
        # Get current parent to trace
        current_gen = st.session_state.family_tree[st.session_state.current_generation]
        parent_img = current_gen[st.session_state.current_parent_index]
        
        st.header(f"🖌️ Generation {st.session_state.current_generation + 1}")
        st.subheader(f"Trace Parent {st.session_state.current_parent_index + 1} - Child {st.session_state.current_child}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("👇 The parent image is shown at 50% opacity. Trace over it with your mouse/stylus!")
            
            # Make parent semi-transparent for tracing
            bg_img = make_semi_transparent(parent_img, opacity=0.5)
            
            # Create canvas with semi-transparent background
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=st.session_state.stroke_width,
                stroke_color=st.session_state.stroke_color,
                background_image=bg_img,
                update_streamlit=True,
                height=st.session_state.canvas_height,
                width=st.session_state.canvas_width,
                drawing_mode=st.session_state.drawing_mode,
                key=f"canvas_gen{st.session_state.current_generation}_parent{st.session_state.current_parent_index}_child{st.session_state.current_child}",
            )
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("✅ Save This Child", type="primary"):
                    traced_img = save_traced_child(canvas_result, parent_img)
                    if traced_img:
                        # Initialize new generation if needed
                        if len(st.session_state.family_tree) <= st.session_state.current_generation + 1:
                            st.session_state.family_tree.append([])
                        
                        # Add child to next generation
                        st.session_state.family_tree[st.session_state.current_generation + 1].append(traced_img)
                        
                        # Move to next child or parent
                        if st.session_state.current_child == 1:
                            st.session_state.current_child = 2
                        else:
                            st.session_state.current_child = 1
                            st.session_state.current_parent_index += 1
                            
                            # Check if we're done with this generation
                            if st.session_state.current_parent_index >= len(current_gen):
                                st.session_state.current_generation += 1
                                st.session_state.current_parent_index = 0
                        
                        st.rerun()
                    else:
                        st.error("Please draw something first!")
            
            with col_b:
                if st.button("🗑️ Clear Canvas"):
                    st.rerun()
        
        with col2:
            st.write("**Original Parent (100% opacity):**")
            st.image(parent_img, use_container_width=True)
            
            st.write("**Progress:**")
            total_traces_needed = sum([2 ** i * 2 for i in range(st.session_state.num_generations)])
            traces_completed = sum([len(gen) for gen in st.session_state.family_tree[1:]])
            st.progress(traces_completed / total_traces_needed)
            st.caption(f"{traces_completed} of {total_traces_needed} traces completed")

st.markdown("---")
st.markdown("""
**Tip:** Your natural hand movements create unique variations! Try tracing quickly vs slowly, 
or with different levels of detail to see how it affects evolution.
""")