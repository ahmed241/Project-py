'use client'
import { Clock, Cpu, Ship, Workflow, Video, Zap, FileText } from 'lucide-react';

export default function OperationalResearchPage() {
  const topics = [
    {
      id: 1,
      title: "Transportation Problem",
      description: "Solve transportation problems using VAM (Vogel's Approximation Method) and MODI (Modified Distribution) methods with animated visualizations.",
      available: true,
      icon: <Ship className="w-12 h-12 text-blue-400" />,
      link: "/operational-research/transportation",
      color: "blue"
    },
    {
      id: 2,
      title: "Assignment Problem",
      description: "Optimize task assignments with the Hungarian algorithm. Watch step-by-step matrix reductions and optimal assignments.",
      available: true,
      icon: <Workflow className="w-12 h-12 text-green-400" />,
      link: "/operational-research/assignment",
      color: "green"
    },
    {
      id: 3,
      title: "Simulation",
      description: "Model and analyze complex systems using Monte Carlo simulation and discrete event simulation techniques.",
      available: false,
      icon: <Cpu className="w-12 h-12 text-yellow-400" />,
      link: "/operational-research/simulation",
      color: "yellow"
    },
  ];

  return (
    
    <div>
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 rounded-full border border-blue-500/30 mb-6">
          <Video className="w-4 h-4 text-blue-300" />
          <span className="text-blue-300 text-sm font-medium">Animated Step-by-Step Solutions</span>
        </div>

        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
          Master
          <br />
          <span className="bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            Operational Research
          </span>
        </h2>
        
        <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          Explore OR topics with interactive Manim animations, instant solutions, and downloadable PDFs. Enter your problem parameters and watch the magic happen!
        </p>
        
        <div className="flex flex-wrap gap-4 justify-center">
          <a href="#topics" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition transform hover:scale-105 shadow-lg shadow-blue-500/50">
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
          Select a topic to start solving problems with beautiful animations
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((topic, index) => (
            <a
              key={topic.id}
              href={topic.available ? topic.link : '#'}
              style={{ animationDelay: `${index * 100}ms` }}
              className={`relative group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl animate-slide-up ${
                !topic.available ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:shadow-blue-500/20'
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
                    Instant
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

              {/* Hover Gradient Overlay */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br transition-all duration-300 pointer-events-none ${
                topic.color === 'blue' 
                  ? 'from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/10 group-hover:to-cyan-500/10'
                  : 'from-green-500/0 to-emerald-500/0 group-hover:from-green-500/10 group-hover:to-emerald-500/10'
              }`} />
            </a>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-12">
          <h3 className="text-3xl font-bold text-white mb-6 text-center">About Operational Research</h3>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">What is OR?</h4>
              <p className="text-gray-300">
                Operational Research (OR) is the discipline of applying advanced analytical methods to help make better decisions. It uses mathematical modeling, statistics, and algorithms to find optimal or near-optimal solutions to complex decision-making problems.
              </p>
              <p className="text-gray-300">
                OR is widely used in business, industry, government, and military to solve problems related to logistics, scheduling, resource allocation, and optimization.
              </p>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-xl font-semibold text-white">Why Use Algo-Viz?</h4>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Visual Learning:</strong> See algorithms in action with Manim animations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Step-by-Step:</strong> Understand every iteration and decision point</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Instant Results:</strong> Get quick solutions for practice problems</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span><strong className="text-white">Export PDFs:</strong> Download solutions for assignments and study</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 text-center">
            <p className="text-blue-300 text-lg">
              <strong>Pro Tip:</strong> Start with Transportation Problem to learn the basics, then move to Assignment for more advanced concepts!
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
      `}</style>
    </div>
    
  );
}