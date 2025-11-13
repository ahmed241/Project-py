'use client'
import { Clock, Video, Zap, FileText, Scaling, Baseline, RefreshCw, ArrowDownToLine, Disc } from 'lucide-react';

export default function StrengthOfMaterialsPage() {
  
  // --- Topics for Strength of Materials ---
  const topics = [
    {
      id: 1,
      title: "SFD & BMD Calculator",
      description: "Visualize Shear Force and Bending Moment Diagrams. Supports point loads, UDLs, and various supports.",
      available: true,
      icon: <Baseline className="w-12 h-12 text-blue-400" />,
      link: "/strength-of-materials/sfd-bmd",
      color: "blue"
    },
    {
      id: 2,
      title: "Torsion of Shafts",
      description: "Calculate shear stress, angle of twist, and power transmission in solid or hollow circular shafts.",
      available: false,
      icon: <RefreshCw className="w-12 h-12 text-green-400" />,
      link: "#",
      color: "green"
    },
    {
      id: 3,
      title: "Mohr's Circle",
      description: "Find principal stresses, max shear stress, and plane orientation by visualizing stress transformation.",
      available: false,
      icon: <Disc className="w-12 h-12 text-yellow-400" />,
      link: "#",
      color: "yellow"
    },
    {
      id: 4,
      title: "Columns & Buckling",
      description: "Analyze critical loads for columns using Euler's formula and Rankine's formula for different end conditions.",
      available: false,
      icon: <ArrowDownToLine className="w-12 h-12 text-red-400" />,
      link: "#",
      color: "red"
    },
  ];

  return (
    
    <div>
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 rounded-full border border-blue-500/30 mb-6">
          <Scaling className="w-4 h-4 text-blue-300" />
          <span className="text-blue-300 text-sm font-medium">Structural & Stress Analysis</span>
        </div>

        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
          Analyze
          <br />
          <span className="bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            Strength of Materials
          </span>
        </h2>
        
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Visualize stress, strain, bending, and torsion. Solve complex structural problems with animated diagrams and step-by-step solutions.
        </p>
        
        <div className="flex flex-wrap gap-4 justify-center">
          <a href="#topics" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition transform hover:scale-105 shadow-lg shadow-blue-500/50">
            Choose a Module
          </a>
          <a href="#about" className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition border border-white/20">
            Learn More
          </a>
        </div>
      </section>

      {/* Topics Grid */}
      <section id="topics" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h3 className="text-3xl font-bold text-white mb-4 text-center">Analysis Modules</h3>
        <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
          Select a module to analyze common SOM problems with step-by-step animations
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((topic, index) => (
            <a
              key={topic.id}
              href={topic.available ? topic.link : '#'}
              style={{ animationDelay: `${index * 100}ms` }}
              className={`relative group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl animate-slide-up ${
                !topic.available ? 'opacity-60 cursor-not-allowed' : `cursor-pointer hover:shadow-${topic.color}-500/20`
              }`}
            >
              {!topic.available && (
                <div className="absolute top-4 right-4 flex items-center gap-1 bg-yellow-500/20 border border-yellow-500/30 px-3 py-1 rounded-full">
                  <Clock className="w-3 h-3 text-yellow-300" />
                  <span className="text-xs font-medium text-yellow-300">Coming Soon</span>
                </div>
              )}

              {/* Icon */}
              <div className="mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3">
                {topic.icon}
              </div>

              {/* Title */}
              <h4 className="text-xl font-bold text-white mb-2">{topic.title}</h4>

              {/* Description */}
              <p className="text-gray-300 text-sm mb-4 line-clamp-3">{topic.description}</p>

              {/* Feature Pills */}
              {topic.available && (
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full flex items-center gap-1">
                    <Video className="w-3 h-3" />
                    Manim
                  </span>
                  <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded-full flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    Symbolic
                  </span>
                  <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    PDF
                  </span>
                </div>
              )}

              {/* Action Button */}
              <div className={`text-center py-2 rounded-lg font-medium transition-all ${
                topic.available
                  ? `bg-${topic.color}-600/20 text-${topic.color}-300 group-hover:bg-${topic.color}-600 group-hover:text-white`
                  : 'bg-gray-700/50 text-gray-500'
              }`}>
                {topic.available ? 'Start Analysis →' : 'Coming Soon'}
              </div>

              {/* Hover Gradient Overlay */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br transition-all duration-300 pointer-events-none from-${topic.color}-500/0 to-${topic.color}-500/0 group-hover:from-${topic.color}-500/10 group-hover:to-${topic.color}-500/10`} />
            </a>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-12">
          <h3 className="text-3xl font-bold text-white mb-6 text-center">About Strength of Materials (SOM)</h3>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">What is SOM?</h4>
              <p className="text-gray-300">
                Strength of Materials, also known as Mechanics of Materials, is a fundamental engineering subject. It studies the behavior of solid objects subjected to stresses and strains.
              </p>
              <p className="text-gray-300">
                Understanding SOM is critical for designing safe and reliable structures, from bridges and buildings to machine parts and aerospace components.
              </p>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">Why Use This Tool?</h4>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Visual Learning:</strong> See SFD/BMD and Mohr's Circle drawn step-by-step.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Complex Problems:</strong> Handle multiple load types on beams or shafts.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Instant Results:</strong> Get quick symbolic solutions for your calculations.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Export PDFs:</strong> Download detailed reports for your notes.</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 text-center">
            <p className="text-blue-300 text-lg">
              <strong>Pro Tip:</strong> Start with the SFD & BMD Calculator to see how a beam's internal forces are visualized with Manim!
            </p>
          </div>
        </div>
      </section>

      {/* --- This CSS allows the dynamic color hovers to work --- */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fadeIn 0.6s ease-out; }
        .animate-slide-up { animation: slideUp 0.5s ease-out forwards; opacity: 0; }
        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        /* JIT-safe dynamic colors */
        .from-blue-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(59 130 246 / 0); --tw-gradient-to: rgb(59 130 246 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-blue-500\/0 { --tw-gradient-to: rgb(59 130 246 / 0); }
        .group-hover\:from-blue-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(59 130 246 / 0.1); --tw-gradient-to: rgb(59 130 246 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-blue-500\/10:hover { --tw-gradient-to: rgb(59 130 246 / 0.1); }
        
        .from-green-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(34 197 94 / 0); --tw-gradient-to: rgb(34 197 94 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-green-500\/0 { --tw-gradient-to: rgb(34 197 94 / 0); }
        .group-hover\:from-green-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(34 197 94 / 0.1); --tw-gradient-to: rgb(34 197 94 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-green-500\/10:hover { --tw-gradient-to: rgb(34 197 94 / 0.1); }

        .from-yellow-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(234 179 8 / 0); --tw-gradient-to: rgb(234 179 8 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-yellow-500\/0 { --tw-gradient-to: rgb(234 179 8 / 0); }
        .group-hover\:from-yellow-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(234 179 8 / 0.1); --tw-gradient-to: rgb(234 179 8 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-yellow-500\/10:hover { --tw-gradient-to: rgb(234 179 8 / 0.1); }

        .from-red-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(239 68 68 / 0); --tw-gradient-to: rgb(239 68 68 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-red-500\/0 { --tw-gradient-to: rgb(239 68 68 / 0); }
        .group-hover\:from-red-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(239 68 68 / 0.1); --tw-gradient-to: rgb(239 68 68 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-red-500\/10:hover { --tw-gradient-to: rgb(239 68 68 / 0.1); }
      `}</style>
    </div>
    
  );
}