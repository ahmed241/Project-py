'use client';

import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Support, Load } from '@/app/strength-of-materials/sfd-bmd/type';

// Define the structure of the solver's output
interface SolverSolution {
  analysis_results: {
    reactions: Array<{
      position: number;
      type: string;
      vertical_reaction: number;
      moment_reaction: number;
    }>;
    // ... other FEM data
  };
  element_forces: Array<{
    x1: number;
    x2: number;
    V1: number; // Shear at start
    V2: number; // Shear at end
    M1: number; // Moment at start
    M2: number; // Moment at end
  }>;
}

interface ResultsDisplayProps {
  // This 'solution' is the object from your FastAPI
  solution: SolverSolution;
  // We pass these in for context
  supports: Support[];
  loads: Load[];
}

export default function ResultsDisplay({ solution, supports, loads }: ResultsDisplayProps) {

  // --- 1. Process Data for Charts & Cards ---
  const processedData = useMemo(() => {
    const sfdData: { x: number; V: number }[] = [];
    const bmdData: { x: number; M: number }[] = [];

    // Unroll the element_forces data into plot-able (x, y) points
    solution.element_forces.forEach((el, index) => {
      // Add the start point for this element
      sfdData.push({ x: el.x1, V: el.V1 });
      bmdData.push({ x: el.x1, M: el.M1 });

      // Add the end point for this element
      sfdData.push({ x: el.x2, V: el.V2 });
      bmdData.push({ x: el.x2, M: el.M2 });
    });

    // Get all shear and moment values to find max/min
    const allV = solution.element_forces.flatMap(el => [el.V1, el.V2]);
    const allM = solution.element_forces.flatMap(el => [el.M1, el.M2]);

    return {
      sfdData,
      bmdData,
      maxShear: Math.max(...allV),
      minShear: Math.min(...allV),
      maxMoment: Math.max(...allM),
      minMoment: Math.min(...allM),
      reactions: solution.analysis_results.reactions,
    };
  }, [solution]);

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 rounded-2xl shadow-lg border border-white/10 p-6 space-y-8">
      
      {/* --- 2. Key Metrics Section --- */}
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">
          Analysis Summary
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <ResultCard 
            label="Max Bending Moment (M_max)" 
            value={`${processedData.maxMoment.toFixed(2)} kN-m`} 
            color="blue"
          />
          <ResultCard 
            label="Min Bending Moment (M_min)" 
            value={`${processedData.minMoment.toFixed(2)} kN-m`} 
            color="blue"
          />
          <ResultCard 
            label="Max Shear Force (V_max)" 
            value={`${processedData.maxShear.toFixed(2)} kN`} 
            color="green"
          />
          <ResultCard 
            label="Min Shear Force (V_min)" 
            value={`${processedData.minShear.toFixed(2)} kN`} 
            color="green"
          />
        </div>
      </div>

      {/* --- 3. Reactions Section --- */}
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">
          Support Reactions
        </h3>
        <div className="bg-gray-800/50 border border-white/10 rounded-lg p-4 space-y-2">
          {processedData.reactions.map((reaction, idx) => (
            <div key={idx} className="flex justify-between items-center text-gray-300">
              <span className="font-medium capitalize">
                {reaction.type} @ {reaction.position}m:
              </span>
              <div className="flex gap-4">
                <span className="text-white font-bold">{reaction.vertical_reaction.toFixed(2)} kN</span>
                {reaction.moment_reaction !== 0 && (
                  <span className="text-white font-bold">{reaction.moment_reaction.toFixed(2)} kN-m</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* --- 4. Shear Force Diagram (SFD) --- */}
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">
          Shear Force Diagram (SFD)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={processedData.sfdData} margin={{ top: 5, right: 20, left: -20, bottom: 20 }}>
            <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              type="number"
              label={{ value: 'Position (m)', position: 'insideBottom', dy: 20, fill: '#9CA3AF' }}
              stroke="#9CA3AF" 
              domain={['dataMin', 'dataMax']}
            />
            <YAxis 
              label={{ value: 'Shear (kN)', angle: -90, position: 'insideLeft', dx: -10, fill: '#9CA3AF' }}
              stroke="#9CA3AF"
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem' }}
              labelStyle={{ color: '#E5E7EB', fontWeight: 'bold' }}
              itemStyle={{ color: '#818CF8' }}
              formatter={(value: number) => [value.toFixed(2), 'Shear']}
            />
            <Legend />
            <ReferenceLine y={0} stroke="#E5E7EB" strokeWidth={2} />
            <Line 
              type="stepAfter" // This creates the classic SFD "step" look
              dataKey="V" 
              name="Shear Force"
              stroke="#818CF8" 
              strokeWidth={3} 
              dot={false} 
              activeDot={{ r: 6, fill: '#818CF8', stroke: 'rgba(255, 255, 255, 1)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* --- 5. Bending Moment Diagram (BMD) --- */}
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">
          Bending Moment Diagram (BMD)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={processedData.bmdData} margin={{ top: 5, right: 20, left: -20, bottom: 20 }}>
            <CartesianGrid stroke="#374151" strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              type="number"
              label={{ value: 'Position (m)', position: 'insideBottom', dy: 20, fill: '#9CA3AF' }}
              stroke="#9CA3AF" 
              domain={['dataMin', 'dataMax']}
            />
            <YAxis 
              label={{ value: 'Moment (kN-m)', angle: -90, position: 'insideLeft', dx: -10, fill: '#9CA3AF' }}
              stroke="#9CA3AF"
              // Invert Y-axis (common for BMD)
              reversed={true} 
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem' }}
              labelStyle={{ color: '#E5E7EB', fontWeight: 'bold' }}
              itemStyle={{ color: '#F472B6' }}
              formatter={(value: number) => [value.toFixed(2), 'Moment']}
            />
            <Legend />
            <ReferenceLine y={0} stroke="#E5E7EB" strokeWidth={2} />
            <Line 
              type="monotone" // 'monotone' creates smooth curves
              dataKey="M" 
              name="Bending Moment"
              stroke="#F472B6" 
              strokeWidth={3} 
              dot={false} 
              activeDot={{ r: 6, fill: '#F472B6', stroke: '#fff' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}

// Reusable Result Card (themed for our page)
function ResultCard({ label, value, color }: { label: string; value: string; color: 'blue' | 'green' }) {
  const colorClasses = {
    blue: 'from-blue-500/10 to-blue-500/20 border-blue-500/30 text-blue-300',
    green: 'from-green-500/10 to-green-500/20 border-green-500/30 text-green-300',
  };
  
  return (
    <div className={`p-4 bg-gradient-to-br border rounded-lg ${colorClasses[color]}`}>
      <div className="text-sm mb-1">{label}</div>
      <div className="text-2xl font-bold text-white mt-1">{value}</div>
    </div>
  );
}