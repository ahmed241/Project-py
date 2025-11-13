'use client'
import { Clock, Video, Zap, FileText, Sigma, FunctionSquare, LucideWaves, AreaChart, LucideIceCream } from 'lucide-react';

export default function EngineeringMathematicsPage() {
  const topics = [
    {
      id: 1,
      title: "Laplace Transforms",
      description: "Solve and visualize the transformation of functions from the time domain to the s-domain. Handles linearity, shifting, and more.",
      available: true,
      icon: <FunctionSquare className="w-12 h-12 text-purple-400" />,
      link: "/engineering-mathematics/laplace-transform",
      color: "purple"
    },
    {
      id: 2,
      title: "Fourier Series",
      description: "Deconstruct periodic functions into a series of sines and cosines. Animate the convergence of the series.",
      available: false,
      icon: <LucideWaves className="w-12 h-12 text-teal-400" />,
      link: "#",
      color: "teal"
    },
    {
      id: 3,
      title: "Numerical Methods",
      description: "Find approximate solutions with methods like Runge-Kutta, Newton-Raphson, and numerical integration.",
      available: false,
      icon: <AreaChart className="w-12 h-12 text-orange-400" />,
      link: "#",
      color: "orange"
    },
  ];

  return (
    
    <div>
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/20 rounded-full border border-purple-500/30 mb-6">
          <Sigma className="w-4 h-4 text-purple-300" />
          <span className="text-purple-300 text-sm font-medium">Symbolic & Animated Solutions</span>
        </div>

        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
          Master
          <br />
          <span className="bg-gradient-to-r from-purple-400 to-teal-400 bg-clip-text text-transparent">
            Engineering Mathematics
          </span>
        </h2>
        
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Solve complex mathematical problems with interactive Manim animations, instant symbolic solutions, and step-by-step breakdowns.
        </p>
        
        <div className="flex flex-wrap gap-4 justify-center">
          <a href="#topics" className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition transform hover:scale-105 shadow-lg shadow-purple-500/50">
            Choose a Topic
          </a>
          <a href="#about" className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition border border-white/20">
            Learn More
          </a>
        </div>
      </section>

      {/* Topics Grid */}
      <section id="topics" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h3 className="text-3xl font-bold text-white mb-4 text-center">Available Topics</h3>
        <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
          Select a topic to start solving problems with step-by-step animations
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((topic, index) => (
            <a
              key={topic.id}
              href={topic.available ? topic.link : '#'}
              style={{ animationDelay: `${index * 100}ms` }}
              className={`relative group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl animate-slide-up ${
                !topic.available ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:shadow-purple-500/20'
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
                {topic.available ? 'Start Solving →' : 'Coming Soon'}
              </div>

              {/* Hover Gradient Overlay (simplified to use topic color) */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br transition-all duration-300 pointer-events-none from-${topic.color}-500/0 to-${topic.color}-500/0 group-hover:from-${topic.color}-500/10 group-hover:to-${topic.color}-500/10`} />
            </a>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-12">
          <h3 className="text-3xl font-bold text-white mb-6 text-center">About Engineering Mathematics</h3>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">What is Eng. Mathematics?</h4>
              <p className="text-gray-300">
                Engineering Mathematics is the backbone of all engineering disciplines. It uses mathematical principles and techniques to model, analyze, and solve complex real-world problems.
              </p>
              <p className="text-gray-300">
                From circuit analysis and control systems to fluid dynamics and structural analysis, a strong grasp of these mathematical concepts is essential for every engineer.
              </p>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">Why Use This Tool?</h4>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Visual Learning:</strong> See abstract concepts animated with Manim</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Symbolic Steps:</strong> Watch as properties like Linearity and Shifting are applied</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Instant Results:</strong> Get quick symbolic solutions for practice problems</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Export PDFs:</strong> Download step-by-step solutions for your notes</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6 text-center">
            <p className="text-purple-300 text-lg">
              <strong>Pro Tip:</strong> Start with Laplace Transforms to see how we turn a function string into a live, step-by-step animation!
            </p>
          </div>
        </div>
      </section>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.6s ease-out;
        }

        .animate-slide-up {
          animation: slideUp 0.5s ease-out forwards;
          opacity: 0;
        }

        .line-clamp-3 {
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        /* This is a JIT-safe way to get dynamic colors */
        .from-purple-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(168 85 247 / 0); --tw-gradient-to: rgb(168 85 247 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-purple-500\/0 { --tw-gradient-to: rgb(168 85 247 / 0); }
        .group-hover\:from-purple-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(168 85 247 / 0.1); --tw-gradient-to: rgb(168 85 247 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-purple-500\/10:hover { --tw-gradient-to: rgb(168 85 247 / 0.1); }
        
        .from-teal-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(20 184 166 / 0); --tw-gradient-to: rgb(20 184 166 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-teal-500\/0 { --tw-gradient-to: rgb(20 184 166 / 0); }
        .group-hover\:from-teal-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(20 184 166 / 0.1); --tw-gradient-to: rgb(20 184 166 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-teal-500\/10:hover { --tw-gradient-to: rgb(20 184 166 / 0.1); }

        .from-orange-500\/0 { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(249 115 22 / 0); --tw-gradient-to: rgb(249 115 22 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .to-orange-500\/0 { --tw-gradient-to: rgb(249 115 22 / 0); }
        .group-hover\:from-orange-500\/10:hover { --tw-gradient-from-position: 0%; --tw-gradient-from: rgb(249 115 22 / 0.1); --tw-gradient-to: rgb(249 115 22 / 0); --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to); }
        .group-hover\:to-orange-500\/10:hover { --tw-gradient-to: rgb(249 115 22 / 0.1); }
      `}</style>
    </div>
    
  );
}