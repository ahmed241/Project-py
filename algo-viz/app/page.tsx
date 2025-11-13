'use client'
import { BookOpen, Clock, Sparkles, Video, Zap, FileText, PlayCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function LandingPage() {
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [matrixElements, setMatrixElements] = useState<any[]>([]);
  const [matrixColumns, setMatrixColumns] = useState<any[]>([]);

  useEffect(() => {
    setMatrixElements(Array.from({ length: 50 }, (_, i) => ({
      id: i,
      value: Math.floor(Math.random() * 100),
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5,
      duration: 8 + Math.random() * 12
    })));

    setMatrixColumns(Array.from({ length: 15 }, (_, i) => ({
      id: i,
      left: `${i * 7}%`,
      animationDelay: `${i * 0.3}s`,
      animationDuration: `${16 + Math.random() * 4}s`
    })));
  }, []);

  const subjects = [
    { id: 1, title: "Operational Research", description: "Master optimization techniques, linear programming, and decision-making strategies", available: true, icon: "📊", link: "/operational-research" },
    { id: 2, title: "Design of Mechanical Systems", description: "Learn mechanical design principles, CAD modeling, and system analysis", available: true, icon: "⚙️", link: "/mechanical-systems" },
{
  id: 3,
  title: "Engineering Mathematics",
  description: "Solve and animate problems like Laplace Transforms, Fourier Series, and more.",
  available: true,
  icon: "📈", 
  link: "/engineering-mathematics"
},
{
  id: 4,
  title: "Strength of Materials",
  description: "Stress, strain, shear force, bending moment, torsion, and columns",
  available: true, icon: "💪", link: "/strength-of-materials"
},
{
  id: 5,
  title: "Thermodynamics",
  description: "Understand heat transfer, energy systems, and thermodynamic cycles",
  available: false,
  icon: "🔥",
  link: "#" },
{ 
  id: 6, title: "Machine Learning",
  description: "Dive into neural networks, deep learning, and AI applications",
  available: false,
  icon: "🤖",
  link: "#"
}
  ];

  return (
      <div>
        <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 animate-gradient-shift" />
            <div className="absolute inset-0 opacity-20"><div className="animated-grid" /></div>
            
            <div className="absolute inset-0 overflow-hidden">
              {matrixElements.map((e) => (
                <div key={e.id} className="absolute text-purple-400/30 font-mono text-xl font-bold floating-element"
                  style={{ left: `${e.x}%`, top: `${e.y}%`, animationDelay: `${e.delay}s`, animationDuration: `${e.duration}s` }}>
                  {e.value}
                </div>
              ))}
            </div>

            <div className="absolute inset-0 overflow-hidden opacity-10">
              <div className="rotating-shape shape-1" />
              <div className="rotating-shape shape-2" />
              <div className="rotating-shape shape-3" />
            </div>

            <div className="absolute inset-0">
              {matrixColumns.map((c) => (
                <div key={c.id} className="matrix-column" style={{ left: c.left, animationDelay: c.animationDelay, animationDuration: c.animationDuration }}>
                  <div className="matrix-char">⎡</div>
                  <div className="matrix-char">⎢</div>
                  <div className="matrix-char">⎣</div>
                </div>
              ))}
            </div>

            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent z-28" />
            <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 via-transparent to-transparent z-28" />
          </div>

          <div className="relative z-29 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/30 backdrop-blur-md rounded-full border border-purple-500/50 mb-6 animate-float">
              <Sparkles className="w-4 h-4 text-purple-300" />
              <span className="text-purple-200 text-sm font-medium">Powered by Manim</span>
            </div>
            
            <h2 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight animate-fade-in-up">
              Master Engineering<br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent animate-gradient-text">
                Through Visual Animations
              </span>
            </h2>
            
            <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
              Watch algorithms come to life with stunning mathematical animations
            </p>
            
            <div className="flex flex-wrap gap-4 justify-center animate-fade-in-up animation-delay-400">
              <a href='#subjects' className="group bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 shadow-2xl shadow-purple-500/50 flex items-center gap-2">
                Explore Subjects<span className="group-hover:translate-x-1 transition-transform">→</span>
              </a>
              <button onClick={() => setShowVideoModal(true)} className="group bg-white/10 backdrop-blur-md hover:bg-white/20 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 border border-white/30 flex items-center gap-2">
                <PlayCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />Watch Demo
              </button>
            </div>

            <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {[{ label: "Matrix Operations", icon: "⎡⎣" }, { label: "Graph Algorithms", icon: "◉━◉" }, { label: "Optimization", icon: "↗↘" }, { label: "3D Visualizations", icon: "⬡⬢" }].map((item, idx) => (
                <div key={idx} style={{ animationDelay: `${idx * 0.1}s` }} className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-4 hover:bg-white/10 transition-all hover:scale-105 animate-slide-up-slow cursor-pointer group">
                  <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">{item.icon}</div>
                  <p className="text-sm text-gray-300 font-medium">{item.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-40 animate-bounce">
            <div className="w-6 h-10 rounded-full border-2 border-white/30 flex items-start justify-center p-2">
              <div className="w-1 h-3 bg-white/70 rounded-full animate-scroll" />
            </div>
          </div>
        </section>

        {showVideoModal && (
          <div className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-xl flex items-center justify-center p-4 animate-fade-in" onClick={() => setShowVideoModal(true)}>
            <div className="relative max-w-6xl w-full aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl" onClick={(e) => e.stopPropagation()}>
              <button onClick={() => setShowVideoModal(true)} className="absolute top-4 right-4 z-10 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
              <div className="w-full h-full bg-gradient-to-br from-purple-900 to-blue-900 flex items-center justify-center">
                <div className="text-center"><PlayCircle className="w-24 h-24 text-white/50 mx-auto mb-4" /><p className="text-white text-xl">Demo video coming soon!</p></div>
              </div>
            </div>
          </div>
        )}

        <section className="py-16 bg-gradient-to-r from-purple-900/20 via-blue-900/20 to-purple-900/20 border-y border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"><div className="grid md:grid-cols-3 gap-8 text-center">
            {[{ Icon: Video, title: "Manim Animations", desc: "Professional-grade mathematical animations" }, { Icon: Zap, title: "Instant Solutions", desc: "Get immediate answers with detailed breakdowns" }, { Icon: FileText, title: "PDF Reports", desc: "Download comprehensive solution reports" }].map(({ Icon, title, desc }, i) => (
              <div key={i} className="group"><div className="w-16 h-16 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform"><Icon className="w-8 h-8 text-blue-400" /></div><h3 className="text-xl font-semibold text-white mb-2">{title}</h3><p className="text-gray-400">{desc}</p></div>
            ))}
          </div></div>
        </section>

        <section id="subjects" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h3 className="text-3xl font-bold text-white mb-4 text-center">Available Subjects</h3>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">Enter your problem parameters and watch step-by-step animated solutions</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {subjects.map((s, i) => (
              <a key={s.id} href={s.available ? s.link : '#'} style={{ animationDelay: `${i * 100}ms` }} className={`relative group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 animate-card-appear ${!s.available ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}>
                {!s.available && <div className="absolute top-4 right-4 flex items-center gap-1 bg-yellow-500/20 border border-yellow-500/30 px-3 py-1 rounded-full"><Clock className="w-3 h-3 text-yellow-300" /><span className="text-xs font-medium text-yellow-300">Coming Soon</span></div>}
                <div className="text-5xl mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12">{s.icon}</div>
                <h4 className="text-xl font-bold text-white mb-2">{s.title}</h4>
                <p className="text-gray-300 text-sm mb-4">{s.description}</p>
                {s.available && <div className="flex flex-wrap gap-2 mb-4">{[{ Icon: Video, label: "Animation" }, { Icon: Zap, label: "Instant" }, { Icon: FileText, label: "PDF" }].map(({ Icon, label }, j) => <span key={j} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full flex items-center gap-1"><Icon className="w-3 h-3" />{label}</span>)}</div>}
                <div className={`text-center py-2 rounded-lg font-medium transition-all ${s.available ? 'bg-purple-600/20 text-purple-300 group-hover:bg-purple-600 group-hover:text-white' : 'bg-gray-700/50 text-gray-500'}`}>{s.available ? 'Start Learning →' : 'Coming Soon'}</div>
              </a>
            ))}
          </div>
        </section>

        <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-12">
            <h3 className="text-3xl font-bold text-white mb-6 text-center">How Algo-Viz Works</h3>
            <div className="grid md:grid-cols-3 gap-8 mb-8">
              {[{ step: "1", title: "Enter Parameters", desc: "Input your problem data" }, { Icon: Video, title: "Watch Animation", desc: "See step-by-step Manim visualizations" }, { Icon: Zap, title: "Get Solution", desc: "Download results or detailed PDF" }].map((item, i) => (
                <div key={i} className="text-center group"><div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">{item.Icon ? <item.Icon className="w-8 h-8 text-purple-400" /> : <span className="text-2xl font-bold text-purple-400">{item.step}</span>}</div><h4 className="text-xl font-semibold text-white mb-2">{item.title}</h4><p className="text-gray-300">{item.desc}</p></div>
              ))}
            </div>
            <p className="text-gray-300 text-center max-w-3xl mx-auto text-lg">Algo-Viz uses <span className="text-purple-400 font-semibold">Manim</span> to create stunning educational visualizations!</p>
          </div>
        </section>

        <footer className="border-t border-white/10 mt-20"><div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"><div className="flex flex-col md:flex-row justify-between items-center gap-4"><p className="text-gray-400">© 2025 Algo-Viz</p><div className="flex gap-6">{['Privacy', 'Terms', 'GitHub'].map(l => <a key={l} href="#" className="text-gray-400 hover:text-white transition-colors">{l}</a>)}</div></div></div></footer>

        <style jsx global>{`@keyframes gradientShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}@keyframes floatElement{0%,100%{transform:translateY(0) translateX(0);opacity:.2}25%{transform:translateY(-30px) translateX(10px);opacity:.4}50%{transform:translateY(-60px) translateX(-10px);opacity:.6}75%{transform:translateY(-30px) translateX(15px);opacity:.4}}@keyframes matrixFall{0%{transform:translateY(-100%);opacity:0}10%{opacity:.6}90%{opacity:.6}100%{transform:translateY(100vh);opacity:0}}@keyframes rotate{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@keyframes fadeInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}@keyframes cardAppear{from{opacity:0;transform:translateY(20px) scale(.95)}to{opacity:1;transform:translateY(0) scale(1)}}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}@keyframes gradientText{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}@keyframes scroll{0%{transform:translateY(0);opacity:1}100%{transform:translateY(12px);opacity:0}}@keyframes slideUpSlow{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:translateY(0)}}@keyframes fadeIn{from{opacity:0}to{opacity:1}}.animate-gradient-shift{background-size:200% 200%;animation:gradientShift 15s ease infinite}.floating-element{animation:floatElement 15s ease-in-out infinite}.matrix-column{position:absolute;top:-10%;display:flex;flex-direction:column;gap:1rem;animation:matrixFall 12s linear infinite}.matrix-char{color:rgba(139,92,246,.2);font-size:2rem;font-family:monospace}.rotating-shape{position:absolute;border:2px solid rgba(139,92,246,.2);animation:rotate 20s linear infinite}.shape-1{width:200px;height:200px;top:20%;left:10%;border-radius:30% 70% 70% 30%/30% 30% 70% 70%}.shape-2{width:300px;height:300px;top:50%;right:10%;border-radius:63% 37% 54% 46%/55% 48% 52% 45%;animation-duration:25s;animation-direction:reverse}.shape-3{width:150px;height:150px;bottom:20%;left:30%;border-radius:41% 59% 58% 42%/45% 65% 35% 55%;animation-duration:30s}.animated-grid{background-image:linear-gradient(rgba(139,92,246,.1) 2px,transparent 2px),linear-gradient(90deg,rgba(139,92,246,.1) 2px,transparent 2px);background-size:60px 60px;width:100%;height:100%;animation:fadeInUp 2s ease-out}.animate-fade-in-up{animation:fadeInUp .8s ease-out}.animate-card-appear{animation:cardAppear .6s ease-out forwards;opacity:0}.animate-float{animation:float 3s ease-in-out infinite}.animate-gradient-text{background-size:200% 200%;animation:gradientText 3s ease infinite}.animate-scroll{animation:scroll 1.5s ease-in-out infinite}.animate-slide-up-slow{animation:slideUpSlow .8s ease-out forwards;opacity:0}.animate-fade-in{animation:fadeIn .3s ease-out}.animation-delay-200{animation-delay:.2s}.animation-delay-400{animation-delay:.4s}`}</style>
      </div>
  );
}