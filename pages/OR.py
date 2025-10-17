import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Operations Research Solver",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
        color: #667eea;
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
    </style>
""", unsafe_allow_html=True)

# Main header
# Back to main button
if st.button("⬅️ Back to Main Menu", use_container_width=False):
    st.switch_page("home.py")
st.markdown("""
    <div class="main-header">
        <h1>🎯 Operations Research Solver Suite</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Solve complex optimization problems with animated visualizations
        </p>
    </div>
""", unsafe_allow_html=True)

# Introduction section
st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h3>Welcome to your comprehensive OR problem solver!</h3>
        <p style="font-size: 1.1rem; color: #666;">
            Choose a problem type below to get started with step-by-step solutions and beautiful animations.
        </p>
    </div>
""", unsafe_allow_html=True)

# Create three columns for the problem cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
        <div class="card">
            <div class="card-title">📊 Assignment Problem</div>
            <div class="card-description">
                Solve optimal assignment problems using the Hungarian Method.
                Perfect for resource allocation, job scheduling, and cost minimization.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Maximization & Minimization</div>
                <div class="feature-item">✓ Restricted Cell Handling</div>
                <div class="feature-item">✓ Step-by-step Animation</div>
                <div class="feature-item">✓ Interactive Matrix Editor</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Solve Assignment Problem", key="assignment", use_container_width=True):
        st.switch_page("pages/Assignment.py")

with col2:
    st.markdown("""
        <div class="card">
            <div class="card-title">🚚 Transportation Problem</div>
            <div class="card-description">
                Optimize transportation routes using Vogel's Approximation Method (VAM).
                Ideal for supply chain, logistics, and distribution planning.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ VAM Method Implementation</div>
                <div class="feature-item">✓ Unbalanced Problem Handling</div>
                <div class="feature-item">✓ Automated Dummy Addition</div>
                <div class="feature-item">✓ Visual Route Optimization</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Solve Transportation Problem", key="transportation", use_container_width=True):
        st.switch_page("pages/Transportation.py")

with col3:
    st.markdown("""
        <div class="card">
            <div class="card-title">📈 Simplex Method</div>
            <div class="card-description">
                Solve linear programming problems using the Simplex Algorithm.
                Essential for optimization, resource allocation, and decision making.
            </div>
            <div class="feature-list">
                <div class="feature-item">✓ Maximization & Minimization</div>
                <div class="feature-item">✓ Multiple Constraints</div>
                <div class="feature-item">✓ Tableau Visualization</div>
                <div class="feature-item">✓ Sample Problem Loading</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Solve Simplex Problem", key="simplex", use_container_width=True):
        st.switch_page("pages/Simplex_Problem.py")

# Footer section
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h3>🎓 About These Methods</h3>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("📖 What is the Assignment Problem?"):
        st.markdown("""
        The **Assignment Problem** is a fundamental combinatorial optimization problem where the goal is to assign a set of tasks to a set of agents in the most efficient way possible.
        
        **Common Applications:**
        - Assigning workers to jobs
        - Scheduling tasks to machines
        - Allocating resources to projects
        - Matching students to schools
        
        **Hungarian Method:** An efficient algorithm that guarantees optimal assignment in polynomial time.
        """)

with col2:
    with st.expander("📖 What is the Transportation Problem?"):
        st.markdown("""
        The **Transportation Problem** is a special type of linear programming problem where the objective is to minimize the cost of distributing goods from multiple sources to multiple destinations.
        
        **Common Applications:**
        - Supply chain optimization
        - Warehouse distribution
        - Logistics planning
        - Resource allocation
        
        **VAM Method:** Vogel's Approximation Method provides near-optimal solutions quickly and handles unbalanced problems efficiently.
        """)

# Additional info
st.markdown("---")
st.info("💡 **Tip:** All three solvers generate animated videos showing the step-by-step solution process using Manim!")

# Statistics section
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Methods Available", "3", delta="Simplex Added!")
with col2:
    st.metric("🎬 Animation Support", "100%", delta="All Methods")
with col3:
    st.metric("⚡ Average Solve Time", "< 1s", delta=None)