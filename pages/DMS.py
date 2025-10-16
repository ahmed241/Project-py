import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Mechanical Design Solver",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .card {
        padding: 2rem;
        border-radius: 10px;
        background: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
    }
    .card-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #f5576c;
    }
    .card-description {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .feature-list {
        margin: 1rem 0;
    }
    .feature-item {
        padding: 0.5rem 0;
        font-size: 1rem;
    }
    .stButton>button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 5px;
    }
    .coming-soon-badge {
        background: #ffc107;
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)



st.markdown("<br>", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div class="main-header">
        <h1>⚙️ Design of Mechanical Systems</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Comprehensive design and analysis tools for mechanical components
        </p>
    </div>
""", unsafe_allow_html=True)

# Introduction section
st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h3>Design and analyze mechanical components with precision!</h3>
        <p style="font-size: 1.1rem; color: #666;">
            Choose a component type below to perform detailed calculations and analysis.
        </p>
    </div>
""", unsafe_allow_html=True)

# Create two rows of cards
row1_col1, row1_col2, row1_col3 = st.columns(3, gap="large")

with row1_col1:
    st.markdown("""
        <div class="card">
            <div class="card-title">🏗️ EOT Crane</div>
            <div class="card-description">
                Design of all components of an EOT Crane (Hoisting Mechanism) using PSG Design Data book.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Rope</div>
                <div class="feature-item">✓ Pulley and Axle</div>
                <div class="feature-item">✓ Bearings and Cross Piece</div>
                <div class="feature-item">✓ Motor Selection</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Design EOT Crane", key="spring", use_container_width=True):
        st.switch_page("pages/EOT.py")

with row1_col2:
    st.markdown("""
        <div class="card">
            <div class="card-title">⚡ Shaft Design & Analysis</div>
            <div class="card-description">
                Analyze shafts for torsion, bending, and combined loading.
                Calculate critical speeds and design for fatigue.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Torsional Analysis</div>
                <div class="feature-item">✓ Bending Stress</div>
                <div class="feature-item">✓ Critical Speed</div>
                <div class="feature-item">✓ Fatigue Design</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Analyze Shafts", key="shaft", use_container_width=True, disabled=True):
        st.info("Coming soon!")

with row1_col3:
    st.markdown("""
        <div class="card">
            <div class="card-title">🎡 Bearing Selection</div>
            <div class="card-description">
                Select appropriate bearings based on load, speed, and life requirements.
                Calculate bearing life and capacity.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Ball Bearings</div>
                <div class="feature-item">✓ Roller Bearings</div>
                <div class="feature-item">✓ Life Calculation</div>
                <div class="feature-item">✓ Load Analysis</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Select Bearings", key="bearing", use_container_width=True, disabled=True):
        st.info("Coming soon!")

st.markdown("<br>", unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3 = st.columns(3, gap="large")

with row2_col1:
    st.markdown("""
        <div class="card">
            <div class="card-title">⚙️ Gear Design</div>
            <div class="card-description">
                Design spur, helical, and bevel gears with complete tooth geometry
                and strength calculations.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Spur Gears</div>
                <div class="feature-item">✓ Helical Gears</div>
                <div class="feature-item">✓ Bevel Gears</div>
                <div class="feature-item">✓ Strength Analysis</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Design Gears", key="gear", use_container_width=True, disabled=True):
        st.info("Coming soon!")

with row2_col2:
    st.markdown("""
        <div class="card">
            <div class="card-title">🔗 Belt & Chain Drives</div>
            <div class="card-description">
                Design belt and chain power transmission systems with proper
                tension, sizing, and selection calculations.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Flat Belts</div>
                <div class="feature-item">✓ V-Belts</div>
                <div class="feature-item">✓ Chain Drives</div>
                <div class="feature-item">✓ Power Transmission</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Design Drives", key="drive", use_container_width=True, disabled=True):
        st.info("Coming soon!")

with row2_col3:
    st.markdown("""
        <div class="card">
            <div class="card-title">🔩 Fastener Design</div>
            <div class="card-description">
                Design bolted joints, welded connections, and riveted assemblies
                with complete stress and failure analysis.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Bolted Joints</div>
                <div class="feature-item">✓ Welded Joints</div>
                <div class="feature-item">✓ Riveted Joints</div>
                <div class="feature-item">✓ Failure Analysis</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Design Fasteners", key="fastener", use_container_width=True, disabled=True):
        st.info("Coming soon!")

# Footer section
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h3>📚 Design Standards & References</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("📖 Design Methodology"):
        st.markdown("""
        All design tools follow standard mechanical engineering practices:
        
        - **Safety Factors**: Appropriate factors of safety for different applications
        - **Material Properties**: Comprehensive material database
        - **Industry Standards**: AGMA, ANSI, ISO standards compliance
        - **Failure Theories**: Von Mises, Tresca, maximum shear stress
        """)

with col2:
    with st.expander("📖 Analysis Features"):
        st.markdown("""
        Each solver provides comprehensive analysis:
        
        - **Stress Analysis**: Normal, shear, and combined stresses
        - **Deflection**: Elastic deformation calculations
        - **Fatigue**: Endurance limit and fatigue life
        - **Visualization**: 3D models and stress distributions
        """)

with col3:
    with st.expander("📖 Output & Reports"):
        st.markdown("""
        Generate detailed engineering reports:
        
        - **Design Calculations**: Step-by-step methodology
        - **Safety Checks**: Factor of safety verification
        - **Material Specs**: Complete material specifications
        - **CAD Export**: Compatible with standard formats
        - **PDF Reports**: Professional documentation
        """)

# Additional info
st.markdown("---")
st.warning("⚠️ **Note:** Mechanical Design solvers are currently under development. Check back soon for updates!")

# Statistics section
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3>📊 Development Status</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔧 Solvers Planned", "6", delta="Coming Soon")
with col2:
    st.metric("📐 Design Standards", "AGMA/ANSI/ISO", delta=None)
with col3:
    st.metric("🎬 Visualization", "3D Models", delta="Planned")

# Roadmap
st.markdown("---")
with st.expander("🗺️ Development Roadmap"):
    st.markdown("""
        ### Phase 1 (Q1 2025)
        - ✅ Spring Design Calculator
        - ✅ Basic Shaft Analysis
        - 🔄 Bearing Selection Tool
        
        ### Phase 2 (Q2 2025)
        - 📅 Gear Design Module
        - 📅 Belt & Chain Drives
        - 📅 Fastener Design
        
        ### Phase 3 (Q3 2025)
        - 📅 3D Visualization
        - 📅 CAD Integration
        - 📅 Automated Reports
        
        ### Phase 4 (Q4 2025)
        - 📅 FEA Integration
        - 📅 Optimization Algorithms
        - 📅 Material Database Expansion
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666;">
        <p style="font-size: 1rem;">
            💡 <strong>Tip:</strong> These tools will integrate with CAD software for seamless workflow
        </p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            Stay tuned for updates!
        </p>
    </div>
""", unsafe_allow_html=True)