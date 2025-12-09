import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO
import random

st.set_page_config(page_title="Drawing Evolution Simulator", layout="wide")

def load_image_from_url(url):
    """Load image from URL"""
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img.convert('RGB')
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def trace_image(original_img, mutation_rate=0.15):
    """
    Simulate tracing an image with imperfections.
    This adds noise, slight shifts, and edge detection variations.
    """
    img_array = np.array(original_img)
    
    # Add random noise to simulate hand tremor
    noise = np.random.normal(0, mutation_rate * 30, img_array.shape)
    traced = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Apply slight blur (simulating imperfect tracing)
    traced_img = Image.fromarray(traced)
    traced_img = traced_img.filter(ImageFilter.GaussianBlur(radius=mutation_rate * 2))
    
    # Random shift (simulating positioning errors)
    shift_x = random.randint(-int(mutation_rate * 10), int(mutation_rate * 10))
    shift_y = random.randint(-int(mutation_rate * 10), int(mutation_rate * 10))
    traced_img = traced_img.transform(
        traced_img.size, 
        Image.AFFINE, 
        (1, 0, shift_x, 0, 1, shift_y)
    )
    
    # Adjust brightness randomly
    brightness_factor = 1 + random.uniform(-mutation_rate, mutation_rate)
    traced_array = np.array(traced_img)
    traced_array = np.clip(traced_array * brightness_factor, 0, 255).astype(np.uint8)
    
    return Image.fromarray(traced_array)

def create_generation(parents, mutation_rate):
    """Create next generation - each parent produces 2 children"""
    children = []
    for parent in parents:
        # Each parent has 2 children
        child1 = trace_image(parent, mutation_rate)
        child2 = trace_image(parent, mutation_rate)
        children.extend([child1, child2])
    return children

def create_family_tree(original_img, num_generations, mutation_rate):
    """Create complete family tree of traced images"""
    tree = [[original_img]]  # Generation 0
    
    for gen in range(num_generations):
        new_generation = create_generation(tree[-1], mutation_rate)
        tree.append(new_generation)
    
    return tree

def display_generation(generation, gen_num, cols_per_row=4):
    """Display a generation of images"""
    st.subheader(f"Generation {gen_num} ({len(generation)} individuals)")
    
    cols = st.columns(cols_per_row)
    for idx, img in enumerate(generation):
        with cols[idx % cols_per_row]:
            st.image(img, caption=f"Individual {idx + 1}", use_container_width=True)

# Main App
st.title("🎨 Drawing Evolution Simulator")
st.markdown("""
This app simulates how tracing a drawing repeatedly introduces small changes that accumulate over generations.
Each "parent" produces 2 "children" through imperfect tracing.
""")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    image_url = st.text_input(
        "Image URL", 
        value="https://cataas.com/cat?width=400",
        help="Paste a direct link to an image (JPG, PNG)"
    )
    
    st.caption("💡 Try these URLs:")
    st.caption("• https://cataas.com/cat?width=400")
    st.caption("• https://picsum.photos/400")
    st.caption("• https://loremflickr.com/400/400/cat")
    
    num_generations = st.slider(
        "Number of Generations", 
        min_value=1, 
        max_value=5, 
        value=3,
        help="Warning: Higher generations create exponentially more images (2^n)"
    )
    
    mutation_rate = st.slider(
        "Mutation Rate",
        min_value=0.05,
        max_value=0.5,
        value=0.15,
        step=0.05,
        help="Higher values = more dramatic changes per generation"
    )
    
    img_size = st.slider(
        "Image Size (px)",
        min_value=100,
        max_value=500,
        value=300,
        step=50
    )
    
    run_simulation = st.button("🧬 Start Evolution", type="primary")

# Display warning about exponential growth
total_images = sum([2**i for i in range(num_generations + 1)])
st.info(f"📊 This will generate **{total_images}** total images across {num_generations + 1} generations")

if run_simulation:
    with st.spinner("Loading original image..."):
        original_img = load_image_from_url(image_url)
    
    if original_img:
        # Resize image
        original_img.thumbnail((img_size, img_size), Image.Resampling.LANCZOS)
        
        with st.spinner(f"Evolving through {num_generations} generations..."):
            family_tree = create_family_tree(original_img, num_generations, mutation_rate)
        
        st.success(f"✅ Evolution complete! Generated {total_images} images")
        
        # Display all generations
        st.markdown("---")
        for gen_num, generation in enumerate(family_tree):
            if gen_num == 0:
                st.subheader("🌱 Original Image (Generation 0)")
                st.image(generation[0], width=img_size)
            else:
                display_generation(generation, gen_num, cols_per_row=min(4, len(generation)))
            st.markdown("---")
        
        # Comparison section
        st.header("📊 Compare First and Last Generation")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(family_tree[0][0], use_container_width=True)
        with col2:
            st.subheader(f"Final Generation Sample")
            # Show first individual from last generation
            st.image(family_tree[-1][0], use_container_width=True)

else:
    st.info("👆 Configure settings in the sidebar and click 'Start Evolution' to begin!")

# Footer
st.markdown("---")
st.markdown("""
**How it works:** Each generation, every parent produces 2 children through imperfect tracing. 
The tracing process adds noise, blur, positioning errors, and brightness variations that accumulate over generations.
""")