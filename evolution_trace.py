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
st.markdown("### *Experience how tiny imperfections compound into radical transformation*")

# Educational banner
with st.expander("🧬 What You'll Discover About Evolution", expanded=False):
    st.markdown("""
    **This isn't just a drawing game—it's a visceral demonstration of evolutionary principles.**
    
    Evolution doesn't happen through dramatic leaps. It happens through the accumulation of tiny, 
    almost imperceptible changes. A hand tremor here. A slight misalignment there. Over generations, 
    these microscopic variations compound into something unrecognizable from the original.
    
    **By tracing these images with your own hand, you become evolution itself.** Your natural imperfections—
    the slight wobble in your line, the way you interpret a curve, the unconscious choices you make—
    mirror the random mutations that drive biological change. You'll feel, in real-time, how 
    small errors aren't failures. They're the engine of transformation.
    
    *This is how new species emerge. This is how languages drift. This is how you became you.*
    """)

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
    ## 🌱 What is Evolution, Really?
    
    We often think of evolution as something that happened long ago to dinosaurs and ancient humans. 
    But evolution is happening *right now*—in viruses, in bacteria, in the way languages change, 
    even in how ideas spread through culture.
    
    **The key insight:** Evolution doesn't require intelligence or intention. It only requires:
    1. **Variation** - Small differences between copies
    2. **Inheritance** - Those differences get passed down
    3. **Time** - Many generations for changes to accumulate
    
    ---
    
    ## 🖐️ You Are The Evolutionary Force
    
    In this experience, **you embody the mechanisms of natural selection.** When you trace an image:
    
    - **Your hand tremor** = Random genetic mutations
    - **Your interpretation** = Environmental pressures shaping traits
    - **Your fatigue or hurry** = Selection pressures that favor certain outcomes
    - **Each generation** = Hundreds of thousands of years compressed into minutes
    
    **You'll discover something profound:** Even with the "goal" of copying perfectly, you can't. 
    Your humanity—your imperfection—*is* the creative force. Just as DNA replication isn't perfect, 
    neither is your hand. And that's not a bug. It's the feature that makes all life possible.
    
    ---
    
    ## 📖 How This Works:
    
    1. **Load an image** - This is your "common ancestor"
    2. **Trace it twice** - Creating 2 "offspring" (like cell division)
    3. **Each offspring becomes a parent** - The family tree branches exponentially
    4. **Compare the final generation to the first** - See evolution in action
    
    **The revelation:** By Generation 3, your drawing will look *nothing* like the original. 
    Not because you tried to change it, but because tiny errors compound. This is exactly how 
    a single-celled organism became you, me, and every living thing on Earth.
    
    ---
    
    ## 🤔 The Human Question
    
    This raises something haunting about our own existence: **We are the result of countless 
    imperfect copies.** Every human alive today descended from beings who made "errors" in 
    reproducing their parents' traits. 
    
    What does it mean that our existence depends entirely on imperfection? That perfection 
    would have meant no change, no adaptation, no *us*? 
    
    **You'll feel this truth in your hands as you trace.** The harder you try to be perfect, 
    the more you'll notice your inevitable deviations. And those deviations—your unique way 
    of seeing and recreating—are what make the final result *yours*. Just as genetic mutations 
    made you *you*.
    
    ---
    
    ### ⏱️ Time Commitment: ~10 minutes
    
    - 2 generations = ~5 minutes (6 tracings)
    - 3 generations = ~10 minutes (14 tracings)
    - Each tracing takes about 30-60 seconds
    
    **Ready to become evolution?**
    
    👈 **Configure your experiment in the sidebar and click 'Load Image & Start'**
    """)

else:
            # Check if we're done
    if st.session_state.current_generation >= st.session_state.num_generations:
        st.success("🎉 Evolution Complete!")
        
        st.markdown("""
        ## 🔬 What You Just Witnessed
        
        **You've compressed millions of years of evolution into minutes.** Look at what happened:
        
        - **Generation 0:** Your "common ancestor"—perfectly clear and defined
        - **Each generation:** Small deviations accumulated
        - **Final generation:** Barely recognizable transformations
        
        ### The Profound Truth
        
        **Nothing tried to change.** You attempted to copy faithfully each time. Yet change happened anyway, 
        inevitably, because *perfect replication is impossible*. This is the most fundamental insight of evolution:
        
        > **Imperfection isn't a bug in the system. Imperfection IS the system.**
        
        Every living thing on Earth—from bacteria to blue whales to you—exists because DNA replication 
        isn't perfect. If it were, the first single-celled organism would have just made perfect copies 
        forever. No plants. No animals. No consciousness. No art. No love.
        
        **Your drawings below are a mirror of your own ancestry.** Trace backward through your family tree—
        through your parents, grandparents, back thousands of generations—and eventually you reach something 
        that doesn't even look human. Just like these drawings.
        
        ---
        """)
        
        # Display family tree
        st.header("📊 Your Evolutionary Family Tree")
        for gen_num, generation in enumerate(st.session_state.family_tree):
            st.subheader(f"Generation {gen_num} ({len(generation)} individuals)")
            cols = st.columns(min(4, len(generation)))
            for idx, img in enumerate(generation):
                with cols[idx % len(cols)]:
                    st.image(img, caption=f"Individual {idx + 1}", width=200)
            st.markdown("---")
        
        # Comparison
        st.header("🔍 The Evolutionary Journey: First vs. Last")
        st.markdown("""
        **This is the moment of revelation.** Place your hand over each image. One is your starting point—
        your primordial ancestor. One is the descendant after generations of imperfect copying.
        
        Ask yourself: *If I hadn't watched this process unfold, would I believe these came from the same source?*
        
        That's the question paleontologists face when comparing fossils. That's the question that made 
        Darwin realize humans and apes share ancestry. The evidence is in the gradual accumulation of 
        tiny changes you just created with your own hand.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌱 Generation 0: The Ancestor")
            st.image(st.session_state.family_tree[0][0], width=300)
            st.caption("This is where it all began. Clear. Defined. Unchanged for now.")
        with col2:
            st.subheader(f"🦋 Generation {st.session_state.num_generations}: The Descendant")
            st.image(st.session_state.family_tree[-1][0], width=300)
            st.caption("After generations of imperfect copying, something new emerges.")
        
        st.markdown("---")
        
        # Reflection prompts
        with st.expander("💭 Reflect on What You've Learned"):
            st.markdown("""
            ### Questions to Consider:
            
            1. **About Process:**
               - At what generation did you first notice significant drift from the original?
               - Did you try to copy perfectly? What made that impossible?
               - How did your own fatigue or attention affect later generations?
            
            2. **About Evolution:**
               - If this happened with drawings, what does it mean for DNA replication over millions of years?
               - How many generations would it take for your drawing to become completely unrecognizable?
               - What if some "mutations" made the next tracing easier? (That's natural selection!)
            
            3. **About Being Human:**
               - You are the product of imperfect copies going back 4 billion years. How does that feel?
               - What makes you "you" vs. your parents? (Hint: imperfect copying)
               - If perfection means no change, is imperfection actually... perfect?
            
            ### The Takeaway
            
            **Creativity, diversity, and life itself emerge not from perfection, but from beautiful, 
            inevitable imperfection.** Every time a cell divides in your body right now, there's a 
            tiny chance of mutation. Most do nothing. Some are harmful. But occasionally, one changes 
            everything.
            
            You just experienced, viscerally, what Darwin spent decades trying to explain: 
            *descent with modification*. The power isn't in staying the same. The power is in the 
            capacity to change, one tiny imperfection at a time.
            """)
        
        st.markdown("---")
        st.markdown("**Want to see how different choices create different evolutionary paths?** Try again with a different image or tracing style!")
    
    else:
        # Current tracing step
        current_gen = st.session_state.family_tree[st.session_state.current_generation]
        parent_img = current_gen[st.session_state.current_parent_index]
        
        st.header(f"🖌️ Generation {st.session_state.current_generation + 1}")
        st.subheader(f"Trace Parent {st.session_state.current_parent_index + 1}, Child {st.session_state.current_child}")
        
        # Evolutionary context
        st.info(f"""
        **🧬 What's happening evolutionarily:** You are creating a new generation through imperfect 
        replication. Notice how your hand naturally deviates from the original—that's exactly how 
        DNA mutations work. No copy is perfect. Evolution depends on these tiny "errors."
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 👇 Parent Image (50% opacity)")
            st.info("Right-click and 'Save Image As...' to download. Trace it in your drawing app, then upload below!")
            
            st.markdown("""
            **💭 Reflect as you trace:** 
            - Notice your hand's natural tremor—that's like random mutations
            - Feel how fatigue changes your lines—that's like environmental pressure
            - See how you interpret curves differently—that's like genetic drift
            
            *Your imperfection is not a flaw. It's the engine of change.*
            """)
            
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
## 🎨 About This Experience

**STEM Concept:** Evolution through accumulated variation  
**Time:** ~10 minutes for 2-3 generations  
**What Makes This Different:** You don't just *learn about* evolution—you *become* the evolutionary process

### Why This Matters

Traditional evolution education shows us charts and timelines. But evolution isn't something you *understand* 
intellectually—it's something you *feel* when you realize that change is inevitable, that perfection is 
impossible, and that beauty emerges from imperfection.

By putting the process in your hands—literally—you experience the truth that no copy is perfect, 
that small changes compound exponentially, and that you yourself are the product of billions of 
"imperfect" replications.

**This is evolution made visceral. Made human. Made real.**

---

**💡 Tracing Tips:**
- Use any drawing app you like (Procreate, Paint, Photoshop, etc.)
- Place the 50% opacity image as a background layer
- Trace loosely for dramatic evolution, carefully for subtle changes
- Each child should be slightly different - don't copy-paste!
- Your natural hand variations create the evolution

*"Nothing in biology makes sense except in the light of evolution."* — Theodosius Dobzhansky
""")