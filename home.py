import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Engineering Problem Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Custom CSS for landing page
st.markdown("""
    <style>
    .main-hero {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.95;
    }
    .category-card {
        padding: 3rem 2rem;
        border-radius: 15px;
        background: white;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: all 0.4s ease;
        height: 100%;
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
    }
    .category-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .category-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    .category-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    .category-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #667eea;
    }
    .category-description {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #555;
        margin-bottom: 2rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feature-item {
        padding: 0.8rem;
        background: #f8f9fa;
        border-radius: 8px;
        font-size: 0.95rem;
        color: #333;
        border-left: 3px solid #764ba2;
    }
    .stButton>button {
        width: 100%;
        padding: 1rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    .stats-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 3rem 0;
    }
    .stat-box {
        text-align: center;
        padding: 1.5rem;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="main-hero">
        <div class="hero-title">🎓 Engineering Problem Solver Suite</div>
        <div class="hero-subtitle">
            Your comprehensive platform for solving complex engineering problems
        </div>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Choose your domain and start solving problems with step-by-step animated solutions
        </p>
    </div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2>Select Your Problem Domain</h2>
        <p style="font-size: 1.2rem; color: #666; margin-top: 1rem;">
            Explore different engineering disciplines with powerful solvers and visualizations
        </p>
    </div>
""", unsafe_allow_html=True)

# Main Categories
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
        <div class="category-card">
            <span class="category-icon">🎯</span>
            <div class="category-title">Operations Research</div>
            <div class="category-description">
                Solve optimization problems including Assignment, Transportation, 
                and Linear Programming using proven algorithms like Hungarian Method, 
                VAM, and Simplex Algorithm.
            </div>
            <div class="feature-grid">
                <div class="feature-item">📊 Assignment Problems</div>
                <div class="feature-item">🚚 Transportation Problems</div>
                <div class="feature-item">📈 Simplex Method</div>
                <div class="feature-item">🎬 Animated Solutions</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🚀 Explore Operations Research", key="or_btn", use_container_width=True):
        st.switch_page("pages/OR.py")

with col2:
    st.markdown("""
        <div class="category-card">
            <span class="category-icon">⚙️</span>
            <div class="category-title">Design of Mechanical Systems</div>
            <div class="category-description">
                Analyze and design mechanical components including springs, shafts, 
                bearings, and power transmission systems with comprehensive 
                calculations and visualizations.
            </div>
            <div class="feature-grid">
                <div class="feature-item">🔩 Spring Design</div>
                <div class="feature-item">⚡ Shaft Analysis</div>
                <div class="feature-item">🎡 Bearing Selection</div>
                <div class="feature-item">⚙️ Gear Design</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🚀 Explore Mechanical Design", key="mech_btn", use_container_width=True):
        st.switch_page("pages/DMS.py")

# Statistics Section
st.markdown("---")
st.markdown("""
    <div class="stats-container">
        <h3 style="text-align: center; margin-bottom: 2rem;">Platform Features</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">6+</div>
            <div class="stat-label">Problem Solvers</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">100%</div>
            <div class="stat-label">Visual Solutions</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">⚡</div>
            <div class="stat-label">Fast & Accurate</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">🎬</div>
            <div class="stat-label">Animated Steps</div>
        </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown("---")
st.markdown("## ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        ### 📊 Interactive Input
        Easy-to-use interfaces for entering problem data with sample data loading options
    """)

with col2:
    st.markdown("""
        ### 🎬 Step-by-Step Videos
        Watch animated solutions created with Manim showing every calculation step
    """)

with col3:
    st.markdown("""
        ### 💾 Export Solutions
        Save problem data to JSON for further analysis or documentation
    """)

# About Section
st.markdown("---")
with st.expander("ℹ️ About This Platform"):
    st.markdown("""
        ### Engineering Problem Solver Suite
        
        This comprehensive platform provides solutions to common engineering problems across multiple domains:
        
        **Operations Research:**
        - Optimization algorithms for resource allocation
        - Linear programming solutions
        - Cost minimization and profit maximization
        
        **Mechanical Design:**
        - Component design and analysis
        - Stress and deflection calculations
        - Material selection and safety factors
        
        All solvers include:
        - ✅ Sample data for quick testing
        - ✅ Step-by-step solution process
        - ✅ Animated visualizations (via Manim)
        - ✅ Final answer calculations
        - ✅ Export functionality
        
        **Built with:** Python, Streamlit, SciPy, NumPy, and Manim
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666;">
        <p style="font-size: 1rem;">
            💡 <strong>Tip:</strong> Start by selecting a domain above to explore available problem solvers
        </p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            Built for engineering students and professionals
        </p>
    </div>
""", unsafe_allow_html=True)