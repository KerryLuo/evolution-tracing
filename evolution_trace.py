import streamlit as st
import numpy as np
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="Drawing Evolution Simulator", layout="wide")

# Initialize session state
if 'family_tree' not in st.session_state:
    st.session_state.family_tree = []
if 'current_generation' not in st.session_state:
    st.session_state.current_generation = 0
if 'current_parent_index' not in st.session_state:
    st.session_state.current_parent_index = 0
if 'current_child' not in st.session_state:
    st.session_state.current_child = 1
if 'started' not in st.session_state:
    st.session_state.started = False

def load_image_from_url(url):
    """Load image from URL"""
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img.convert('RGB')
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def make_semi_transparent_overlay(img):
    """Create a semi-transparent version for display"""
    img_rgba = img.convert('RGBA')
    alpha = img_rgba.split()[3]
    alpha = alpha.point(lambda p: int(p * 0.5))
    img_rgba.putalpha(alpha)
    return img_rgba

def start_evolution(original_img, num_gen):
    """Initialize evolution with original image"""
    st.session_state.started = True
    st.session_state.family_tree = [[original_img]]
    st.session_state.num_generations = num_gen
    st.session_state.current_generation = 0
    st.session_state.current_parent_index = 0
    st.session_state.current_child = 1

# Main App
st.title("🎨 Drawing Evolution Simulator")
st.markdown("### Trace images by hand to watch evolution happen!")

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
        
        num_generations = st.slider(
            "Number of Generations", 
            min_value=1, 
            max_value=3, 
            value=2,
            help="Each generation requires manual tracing"
        )
        
        if st.button("🎨 Load Image & Start", type="primary"):
            img = load_image_from_url(image_url)
            if img:
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                start_evolution(img, num_generations)
                st.rerun()
    else:
        st.success("✅ Evolution in progress!")
        
        if st.session_state.current_generation < st.session_state.num_generations:
            total_in_gen = 2 ** st.session_state.current_generation
            st.metric("Current Generation", st.session_state.current_generation + 1)
            st.metric("Tracing Parent", f"{st.session_state.current_parent_index + 1} of {total_in_gen}")
            st.metric("Child Number", f"{st.session_state.current_child} of 2")
        
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Main content
if not st.session_state.started:
    st.markdown("""
    ## 📖 How It Works:
    
    1. **Load an image** from a URL
    2. **Download the parent image** (shown at 50% opacity)
    3. **Trace it by hand** using your drawing app (Procreate, Paint, etc.)
    4. **Upload your traced version** to create a child
    5. **Repeat twice** for each parent (2 children per parent)
    6. **Watch** how small differences accumulate over generations!
    
    ### Why Manual Tracing?
    Your hand naturally creates variations - tremors, style choices, positioning errors. 
    These small changes compound over generations, just like real evolution!
    
    ---
    
    👈 **Configure settings in the sidebar and click 'Load Image & Start'**
    """)

else:
    # Check if we're done
    if st.session_state.current_generation >= st.session_state.num_generations:
        st.success("🎉 Evolution Complete!")
        
        # Display family tree
        st.header("📊 Complete Family Tree")
        for gen_num, generation in enumerate(st.session_state.family_tree):
            st.subheader(f"Generation {gen_num} ({len(generation)} individuals)")
            cols = st.columns(min(4, len(generation)))
            for idx, img in enumerate(generation):
                with cols[idx % len(cols)]:
                    st.image(img, caption=f"Individual {idx + 1}", width=200)
            st.markdown("---")
        
        # Comparison
        st.header("🔍 Original vs Final Generation")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(st.session_state.family_tree[0][0], width=300)
        with col2:
            st.subheader("Final Generation Sample")
            st.image(st.session_state.family_tree[-1][0], width=300)
    
    else:
        # Current tracing step
        current_gen = st.session_state.family_tree[st.session_state.current_generation]
        parent_img = current_gen[st.session_state.current_parent_index]
        
        st.header(f"🖌️ Generation {st.session_state.current_generation + 1}")
        st.subheader(f"Trace Parent {st.session_state.current_parent_index + 1}, Child {st.session_state.current_child}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 👇 Parent Image (50% opacity)")
            st.info("Right-click and 'Save Image As...' to download. Trace it in your drawing app, then upload below!")
            
            # Show semi-transparent version
            semi_transparent = make_semi_transparent_overlay(parent_img)
            st.image(semi_transparent, caption="Parent at 50% opacity - Download this!", width=400)
            
            # Also show full opacity reference
            with st.expander("Show full opacity reference"):
                st.image(parent_img, caption="Full opacity reference", width=400)
        
        with col2:
            st.markdown("### 📤 Upload Your Traced Drawing")
            
            uploaded_file = st.file_uploader(
                "Upload your traced version (JPG, PNG)",
                type=['jpg', 'jpeg', 'png'],
                key=f"upload_gen{st.session_state.current_generation}_parent{st.session_state.current_parent_index}_child{st.session_state.current_child}"
            )
            
            if uploaded_file:
                try:
                    traced_img = Image.open(uploaded_file).convert('RGB')
                    traced_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                    
                    st.image(traced_img, caption="Your traced version", width=400)
                    
                    if st.button("✅ Accept This Child", type="primary"):
                        # Initialize new generation if needed
                        if len(st.session_state.family_tree) <= st.session_state.current_generation + 1:
                            st.session_state.family_tree.append([])
                        
                        # Add child to next generation
                        st.session_state.family_tree[st.session_state.current_generation + 1].append(traced_img)
                        
                        # Move to next step
                        if st.session_state.current_child == 1:
                            st.session_state.current_child = 2
                        else:
                            st.session_state.current_child = 1
                            st.session_state.current_parent_index += 1
                            
                            # Check if done with this generation
                            if st.session_state.current_parent_index >= len(current_gen):
                                st.session_state.current_generation += 1
                                st.session_state.current_parent_index = 0
                        
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error loading image: {e}")
        
        # Progress bar
        st.markdown("---")
        st.markdown("### 📊 Progress")
        total_traces_needed = sum([2 ** i * 2 for i in range(st.session_state.num_generations)])
        traces_completed = sum([len(gen) for gen in st.session_state.family_tree[1:]])
        progress = traces_completed / total_traces_needed
        st.progress(progress)
        st.caption(f"Completed {traces_completed} of {total_traces_needed} tracings ({progress*100:.1f}%)")

st.markdown("---")
st.markdown("""
**💡 Tracing Tips:**
- Use any drawing app you like (Procreate, Paint, Photoshop, etc.)
- Place the 50% opacity image as a background layer
- Trace loosely for dramatic evolution, carefully for subtle changes
- Each child should be slightly different - don't copy-paste!
- Your natural hand variations create the evolution
""")