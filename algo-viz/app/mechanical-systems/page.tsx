'use client'
import { useState } from 'react';
import { Video, Zap, FileText, Eclipse, Cog, Wrench, Ruler, Box, Clock, Container, Settings } from 'lucide-react';

export default function MechanicalSystemsPage() {
  const topics = [
    {
    id: 1,
    title: "Design of EOT Crane",
    description: "Analyze and design key components of an EOT crane like the hook, hoist, bridge, and trolley.",
    available: true,
    icon: <Container className="w-12 h-12 text-yellow-400" />, // Using 'Construction' or similar icon
    link: "/mechanical-systems/eot-crane",
    color: "yellow"
},
    {
      id: 2,
      title: "Bearing Selection",
      description: "Calculate bearing life, load ratings, and select appropriate bearings for your application",
      available: true,
      icon: <Eclipse className="w-12 h-12 text-green-400" />,
      link: "/mechanical-systems/bearing",
      color: "green"
    },
    {
      id: 3,
      title: "Gear Design",
      description: "Design spur, helical, and bevel gears with Lewis equation and contact stress analysis",
      available: false,
      icon: <Cog className="w-12 h-12 text-purple-400" />,
      link: "#",
      color: "purple"
    },
    {
      id: 4,
      title: "Spring Design",
      description: "Design compression, extension, and torsion springs with stress and deflection analysis",
      available: false,
      icon: <Wrench className="w-12 h-12 text-orange-400" />,
      link: "#",
      color: "orange"
    },
    {
      id: 5,
      title: "Belt & Chain Drives",
      description: "Calculate belt tensions, power transmission, and select appropriate drive systems",
      available: false,
      icon: <Box className="w-12 h-12 text-cyan-400" />,
      link: "#",
      color: "cyan"
    },
    {
      id: 6,
      title: "Clutch & Brake Design",
      description: "Design friction clutches and brakes with torque capacity and heat dissipation analysis",
      available: false,
      icon: <Ruler className="w-12 h-12 text-red-400" />,
      link: "#",
      color: "red"
    },
  ];

  return (
      <div>
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 rounded-full border border-blue-500/30 mb-6">
            <Settings className="w-4 h-4 text-blue-300" />
            <span className="text-blue-300 text-sm font-medium">Engineering Design Made Visual</span>
          </div>

          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Master
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Mechanical System Design
            </span>
          </h2>
          
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Design shafts, bearings, gears, and more with animated visualizations. See stress distributions, deflection curves, and critical speeds come to life.
          </p>
          
          <div className="flex flex-wrap gap-4 justify-center">
            <a href="#topics" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition transform hover:scale-105 shadow-lg shadow-blue-500/50">
              Choose Component
            </a>
            <a href="#about" className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition border border-white/20">
              Learn More
            </a>
          </div>
        </section>

        {/* Topics Grid */}
        <section id="topics" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h3 className="text-3xl font-bold text-white mb-4 text-center">Available Components</h3>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Select a component to start designing with visual feedback and detailed calculations
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

                <div className="mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12">
                  {topic.icon}
                </div>

                <h4 className="text-xl font-bold text-white mb-2">{topic.title}</h4>
                <p className="text-gray-300 text-sm mb-4">{topic.description}</p>

                {topic.available && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full flex items-center gap-1">
                      <Video className="w-3 h-3" />
                      3D Visual
                    </span>
                    <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded-full flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      Instant
                    </span>
                    <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      Report
                    </span>
                  </div>
                )}

                <div className={`text-center py-2 rounded-lg font-medium transition-all ${
                  topic.available
                    ? `bg-${topic.color}-600/20 text-${topic.color}-300 group-hover:bg-${topic.color}-600 group-hover:text-white`
                    : 'bg-gray-700/50 text-gray-500'
                }`}>
                  {topic.available ? 'Start Design →' : 'Coming Soon'}
                </div>

                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br transition-all duration-300 pointer-events-none ${
                  topic.color === 'blue' 
                    ? 'from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/10 group-hover:to-cyan-500/10'
                    : 'from-green-500/0 to-emerald-500/0 group-hover:from-green-500/10 group-hover:to-emerald-500/10'
                }`} />
              </a>
            ))}
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-12">
            <h3 className="text-3xl font-bold text-white mb-6 text-center">Design Process</h3>
            
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-blue-400">1</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Input Parameters</h4>
                <p className="text-gray-400 text-sm">Power, speed, loads, materials, safety factors</p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-green-400">2</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Calculate Design</h4>
                <p className="text-gray-400 text-sm">Automatic sizing based on failure theories</p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-purple-400">3</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Visualize Results</h4>
                <p className="text-gray-400 text-sm">3D models, stress plots, deflection curves</p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-xl font-bold text-orange-400">4</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Export Design</h4>
                <p className="text-gray-400 text-sm">PDF reports with drawings and calculations</p>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h4 className="text-xl font-semibold text-white">What Makes It Unique?</h4>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span><strong className="text-white">Visual Design:</strong> See stress distributions and deflection in 3D</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span><strong className="text-white">Standard Compliance:</strong> Based on IS, ASME, DIN standards</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span><strong className="text-white">Interactive:</strong> Modify parameters and see instant updates</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-1">✓</span>
                    <span><strong className="text-white">Educational:</strong> Step-by-step explanations with formulas</span>
                  </li>
                </ul>
              </div>
              
              <div className="space-y-4">
                <h4 className="text-xl font-semibold text-white">Design Standards</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
                    <p className="text-blue-400 font-semibold">IS Standards</p>
                    <p className="text-gray-400 text-sm">Indian Standards</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
                    <p className="text-green-400 font-semibold">ASME</p>
                    <p className="text-gray-400 text-sm">American Society</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
                    <p className="text-purple-400 font-semibold">PSG Design Data Book</p>
                    <p className="text-gray-400 text-sm">PSG college of Technology, Coimbatore</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
                    <p className="text-orange-400 font-semibold">ISO</p>
                    <p className="text-gray-400 text-sm">International</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <style jsx>{`
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

          .animate-slide-up {
            animation: slideUp 0.5s ease-out forwards;
            opacity: 0;
          }
        `}</style>
      </div>
  );
}