'use client'
import { useState } from 'react';
import { RotateCcw, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import SolverActions from '@/components/SolverActions';

// --- Define the Solution Type ---
interface Solution {
  assignments: number[][]; // e.g., [[0, 30, 0], [0, 0, 70]]
  total_cost: number;
  problem_type: 'min' | 'max';
}

// --- Reusable Solution Display Component ---
function SolutionDisplay({ title, subtitle, solution }: { title: string, subtitle: string, solution: Solution }) {
  
  return (
    <div className="bg-gradient-to-br from-green-500/20 to-green-500/10 backdrop-blur-sm border border-green-500/30 rounded-2xl p-8 my-8">
      <h3 className="text-2xl font-bold text-white mb-6 text-center">
        {title}
      </h3>
      
      {/* Total Cost */}
      <div className="text-center mb-6">
        <p className="text-lg text-gray-300">
          Total {solution.problem_type === 'min' ? 'Cost' : 'Profit'}:
        </p>
        <p className="text-5xl font-bold text-green-400">
          {solution.total_cost}
        </p>
      </div>
      
      {/* Allocation Matrix */}
      <div className="max-w-2xl mx-auto">
        <h4 className="text-lg font-semibold text-white mb-3 text-center">
          {subtitle}
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="bg-slate-800/50 border border-white/10 p-2 text-gray-400 text-sm font-medium"></th>
                {Array.from({ length: solution.assignments[0].length }, (_, j) => (
                  <th key={j} className="bg-slate-800/50 border border-white/10 p-2 text-purple-400 text-sm font-medium">
                    Dest. {j + 1}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {solution.assignments.map((row, i) => (
                <tr key={i}>
                  <td className="bg-slate-800/50 border border-white/10 p-2 text-blue-400 text-sm font-medium text-center">
                    Source {i + 1}
                  </td>
                  {row.map((quantity, j) => (
                    <td key={j} className="border border-white/10 p-3 text-center">
                      {quantity > 0 ? (
                        <span className="text-green-300 font-bold text-lg">{quantity}</span>
                      ) : (
                        <span className="text-gray-500">0</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


export default function TransportationPage() {
  // Form State
  const [numSources, setNumSources] = useState(3);
  const [numDestinations, setNumDestinations] = useState(3);
  const [problemType, setProblemType] = useState<'min' | 'max'>('min');
  const [costMatrix, setCostMatrix] = useState<number[][]>(
    Array(3).fill(0).map(() => Array(3).fill(0))
  );
  const [supplyData, setSupplyData] = useState<number[]>(Array(3).fill(0));
  const [demandData, setDemandData] = useState<number[]>(Array(3).fill(0));
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [solutionType, setSolutionType] = useState<'initial'|'final'|'both'>('final'); // <-- Changed default to 'final'

  // --- Split solution state ---
  const [initialSolution, setInitialSolution] = useState<Solution | null>(null);
  const [finalSolution, setFinalSolution] = useState<Solution | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  // --- Helper Functions ---
  const updateSources = (newSources: number) => {
    setNumSources(newSources);
    const newSupply = Array(newSources).fill(0).map((_, i) => supplyData[i] ?? 0);
    setSupplyData(newSupply);
    const newMatrix = Array(newSources).fill(0).map((_, i) => 
      Array(numDestinations).fill(0).map((_, j) => 
        costMatrix[i]?.[j] ?? 0
      )
    );
    setCostMatrix(newMatrix);
  };
  const updateDestinations = (newDests: number) => {
    setNumDestinations(newDests);
    const newDemand = Array(newDests).fill(0).map((_, i) => demandData[i] ?? 0);
    setDemandData(newDemand);
    const newMatrix = Array(numSources).fill(0).map((_, i) => 
      Array(newDests).fill(0).map((_, j) => 
        costMatrix[i]?.[j] ?? 0
      )
    );
    setCostMatrix(newMatrix);
  };
  const updateCell = (row: number, col: number, value: string) => {
    const numValue = value === '' ? 0 : parseFloat(value);
    if (isNaN(numValue)) return;
    const newData = [...costMatrix];
    newData[row][col] = numValue;
    setCostMatrix(newData);
  };
  const updateSupply = (index: number, value: string) => {
    const numValue = value === '' ? 0 : parseFloat(value);
    if (isNaN(numValue)) return;
    const newSupply = [...supplyData];
    newSupply[index] = numValue;
    setSupplyData(newSupply);
  };
  const updateDemand = (index: number, value: string) => {
    const numValue = value === '' ? 0 : parseFloat(value);
    if (isNaN(numValue)) return;
    const newDemand = [...demandData];
    newDemand[index] = numValue;
    setDemandData(newDemand);
  };
    // Generate random data
  const generateRandom = () => {
    const newMatrix = Array(numSources).fill(0).map(() => 
      Array(numDestinations).fill(0).map(() => Math.floor(Math.random() * 100))
    );
    const newSupply = Array(numSources).fill(0).map(() => Math.floor(Math.random() * 50) + 10);
    const newDemand = Array(numDestinations).fill(0).map(() => Math.floor(Math.random() * 50) + 10);
    
    setCostMatrix(newMatrix);
    setSupplyData(newSupply);
    setDemandData(newDemand);
    setSuccess('Random table generated!');
    setInitialSolution(null);
    setFinalSolution(null);
    setError(null);
    setVideoUrl(null);

    setTimeout(() => setSuccess(null), 2000);
  };

  // Clear all data
  const clearTable = () => {
    setCostMatrix(Array(numSources).fill(0).map(() => Array(numDestinations).fill(0)));
    setSupplyData(Array(numSources).fill(0));
    setDemandData(Array(numDestinations).fill(0));
    setInitialSolution(null);
    setFinalSolution(null);
    setError(null);
    setVideoUrl(null);
  };

    // --- NEW POLLING LOGIC ---
  // This function will be called every few seconds to check if the job is done
  const pollForJobResult = async (job_id: string) => {
    try {
      const statusResponse = await fetch(`http://localhost:8000/api/status/${job_id}`);
      if (!statusResponse.ok) throw new Error("Polling request failed.");
      
      const resultData = await statusResponse.json();

      if (resultData.status === 'pending') {
        // Not done, poll again in 3 seconds
        setTimeout(() => pollForJobResult(job_id), 3000);
      } else if (resultData.status === 'complete' || resultData.status === 'success') {
        // --- Job is DONE! ---
        setLoading(false);
        setSuccess('Solution calculated successfully!');
        
        if (resultData.videoUrl) {
          setVideoUrl(resultData.videoUrl); // Set the video URL
        } else if (resultData.pdfUrl) {
          window.open(resultData.pdfUrl, '_blank'); // Open the PDF
        } else {
          // Direct solution. Your backend returns {status: 'success', solution: {...}}
          // The solution object contains 'initial' and/or 'final'
          if (resultData.solution.initial) {
            setInitialSolution(resultData.solution.initial);
          }
          if (resultData.solution.final) {
            setFinalSolution(resultData.solution.final);
          }
        }
      } else if (resultData.status === 'error') {
        // The job failed on the backend
        throw new Error(resultData.message || 'The script failed to run.');
      }
    } catch (pollError: any) {
      console.error('Polling Error:', pollError);
      setError(pollError.message || 'Failed to get job status.');
      setLoading(false); // Stop the loading spinner
    }
  };

  // --- NEW 'startJob' function (replaces old 'solveProblem') ---
  // This function is called by the buttons. It only *starts* the job.
  const startJob = async (outputType: 'direct' | 'video' | 'pdf') => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setInitialSolution(null);
    setFinalSolution(null);
    setVideoUrl(null);
    
    // Check for unbalanced problem
    const totalSupply = supplyData.reduce((a, b) => a + b, 0);
    const totalDemand = demandData.reduce((a, b) => a + b, 0);
    if (totalSupply !== totalDemand) {
      setSuccess('Note: Problem is unbalanced. A dummy source/destination will be added.');
    }

    try {
      // 'direct' uses the user's choice. 'video' or 'pdf' always requests 'both'.
      let finalSolutionType = solutionType;
      if (outputType === 'video' || outputType === 'pdf') {
        finalSolutionType = 'both';
      }

      const payload = {
        costMatrix: costMatrix,
        supply: supplyData,
        demand: demandData,
        problemType,
        outputType,
        solutionType: finalSolutionType
      };

      // Call the FastAPI endpoint
      const response = await fetch('http://localhost:8000/api/transportation/solve', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

      const { job_id } = await response.json();
      if (!job_id) throw new Error("Failed to get Job ID from server.");
      
      setSuccess("Job started! This may take a minute...");
      
      // Start polling
      setTimeout(() => pollForJobResult(job_id), 3000); // Start polling after 3s

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start job');
      setLoading(false); // Stop loading on initial error
    }
  };

  return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Transportation Problem Solver
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Solve transportation problems using VAM & MODI. Enter your cost matrix, supply, and demand to get optimized solutions.
          </p>
        </div>

        {/* Main Form Container */}
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-8 mb-8">
          
          {/* Configuration Section */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            
            {/* Left Column - Problem Settings */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-white mb-4">Problem Configuration</h3>
              
              {/* Dimensions */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Sources (e.g., Plants)
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={numSources}
                    onChange={(e) => {
                      const newSources = parseInt(e.target.value) || 2;
                      updateSources(newSources);
                    }}
                    className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Destinations (e.g., Warehouses)
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={numDestinations}
                    onChange={(e) => {
                      const newDests = parseInt(e.target.value) || 2;
                      updateDestinations(newDests);
                    }}
                    className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Problem Type */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Optimization Type
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setProblemType('min')}
                    className={`py-3 px-4 rounded-lg font-medium transition-all ${
                      problemType === 'min'
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    Minimization
                  </button>
                  <button
                    onClick={() => setProblemType('max')}
                    className={`py-3 px-4 rounded-lg font-medium transition-all ${
                      problemType === 'max'
                        ? 'bg-green-600 text-white shadow-lg shadow-green-500/50'
                        : 'bg-white/5 text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    Maximization
                  </button>
                </div>
              </div>
            </div>

            {/* Right Column - Quick Actions */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
              
              <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg p-6 border border-purple-500/30">
                <h4 className="text-white font-semibold mb-3">Need sample data?</h4>
                <p className="text-gray-300 text-sm mb-4">
                  Generate a random cost matrix, supply, and demand
                </p>
                <button
                  onClick={generateRandom}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Generate Random Table
                </button>
              </div>

              <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-semibold mb-3">Reset Data</h4>
                <p className="text-gray-300 text-sm mb-4">
                  Clear all values and start fresh
                </p>
                <button
                  onClick={clearTable}
                  className="w-full bg-red-600/20 hover:bg-red-600/30 text-red-300 py-2 rounded-lg transition-colors border border-red-500/30"
                >
                  Clear Table
                </button>
              </div>
            </div>
          </div>

          {/* Cost Matrix Input */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-white mb-4">
              Cost Matrix
              <span className="text-sm text-gray-400 ml-2 font-normal">
                ({numSources} × {numDestinations})
              </span>
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="bg-slate-800/50 border border-white/10 p-2 text-gray-400 text-sm font-medium"></th>
                    {Array.from({ length: numDestinations }, (_, i) => (
                      <th key={i} className="bg-slate-800/50 border border-white/10 p-2 text-purple-400 text-sm font-medium">
                        Destination {i + 1}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: numSources }, (_, i) => (
                    <tr key={i}>
                      <td className="bg-slate-800/50 border border-white/10 p-2 text-blue-400 text-sm font-medium text-center">
                        Source {i + 1}
                      </td>
                      {Array.from({ length: numDestinations }, (_, j) => (
                        <td key={j} className="border border-white/10 p-1">
                          <input
                            type="number"
                            value={costMatrix[i][j] || ''}
                            onChange={(e) => updateCell(i, j, e.target.value)}
                            className="w-full bg-slate-800/80 text-white text-center px-2 py-2 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 hover:bg-slate-700/80 transition-colors"
                            placeholder="0"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* --- Supply and Demand --- */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Supply */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">Supply</h3>
              <div className="grid grid-cols-1 gap-2">
                {Array.from({ length: numSources }, (_, i) => (
                  <div key={i} className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-lg p-2">
                    <label className="text-sm font-medium text-blue-300 w-24">
                      Source {i + 1}
                    </label>
                    <input
                      type="number"
                      value={supplyData[i] || ''}
                      onChange={(e) => updateSupply(i, e.target.value)}
                      className="w-full bg-slate-800/80 text-white text-center px-2 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0"
                    />
                  </div>
                ))}
              </div>
            </div>
            {/* Demand */}
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">Demand</h3>
              <div className="grid grid-cols-1 gap-2">
                {Array.from({ length: numDestinations }, (_, j) => (
                  <div key={j} className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-lg p-2">
                    <label className="text-sm font-medium text-purple-300 w-28">
                      Destination {j + 1}
                    </label>
                    <input
                      type="number"
                      value={demandData[j] || ''}
                      onChange={(e) => updateDemand(j, e.target.value)}
                      className="w-full bg-slate-800/80 text-white text-center px-2 py-2 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="0"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
          {/* --- END SECTION --- */}
          {/* Solution Type selector */}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10 my-4">
            <label className="block text-sm font-medium text-gray-300 mb-3">Solution to compute</label>
            <div className="flex gap-3">
              <button
                onClick={() => setSolutionType('initial')}
                className={`py-2 px-3 rounded-lg text-sm ${
                  solutionType === 'initial' ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-300'
                }`}
              >
                Initial (VAM)
              </button>
              <button
                onClick={() => setSolutionType('final')}
                className={`py-2 px-3 rounded-lg text-sm ${
                  solutionType === 'final' ? 'bg-green-600 text-white' : 'bg-white/5 text-gray-300'
                }`}
              >
                Final (MODI)
              </button>
              <button
                onClick={() => setSolutionType('both')}
                className={`py-2 px-3 rounded-lg text-sm ${
                  solutionType === 'both' ? 'bg-purple-600 text-white' : 'bg-white/5 text-gray-300'
                }`}
              >
                Both
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              Note: Video and PDF reports will always compute both.
            </p>
          </div>

          {/* Status Messages */}
          {error && (
            <div className="mb-6 bg-red-500/20 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 bg-green-500/20 border border-green-500/50 rounded-lg p-4 flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
              <p className="text-green-300">{success}</p>
            </div>
          )}

          {/* Action Buttons are replaced with the component */}
              <SolverActions
                isLoading={loading}
                isInputDisabled={
                  costMatrix.flat().every(cell => cell === 0) ||
                  supplyData.every(s => s === 0) ||
                  demandData.every(d => d === 0)
                }
                onSolveVideo={() => startJob('video')}
                onSolveDirect={() => startJob('direct')}
                onSolvePdf={() => startJob('pdf')}
              />
                  </div>

        {/* --- Results Section --- */}
        {/* --- Video Player Section --- */}
        {videoUrl && (
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-500/10 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-6 my-8">
            <h3 className="text-2xl font-bold text-white mb-4 text-center">
              Video Solution
            </h3>
            <div className="aspect-video rounded-lg overflow-hidden border border-white/20 bg-black">
              <video
                key={videoUrl} // Using key to force re-render if URL changes
                width="100%"
                controls
                autoPlay
                playsInline
                preload="metadata"
              >
                <source src={videoUrl} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        )}
        {/* --- END OF VIDEO DISPLAY SECTION --- */}

        {/* Show Initial Solution if it exists */}
        {initialSolution && (
          <SolutionDisplay
            title="Initial Feasible Solution"
            subtitle="Initial Allocation Matrix (VAM)"
            solution={initialSolution}
          />
        )}
        
        {/* Show Final Solution if it exists */}
        {finalSolution && (
          <SolutionDisplay
            title="Optimal Solution Found!"
            subtitle="Optimal Allocation Matrix (MODI)"
            solution={finalSolution}
          />
        )}
        {/* --- END OF MODIFIED SECTION --- */}

        {/* How It Works Section */}
        <div className="bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            How the VAM & MODI Method Works
          </h3>
          
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-purple-400">1</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Initial Solution (VAM)</h4>
              <p className="text-gray-400 text-sm">Find a good starting solution using penalties</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-400">2</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Calculate U/V Values</h4>
              <p className="text-gray-400 text-sm">Find row/column values for allocated cells</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-green-400">3</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Check Optimality</h4>
              <p className="text-gray-400 text-sm">Calculate opportunity costs for empty cells</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-yellow-400">4</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Adjust Allocations</h4>
              <p className="text-gray-400 text-sm">Create a closed loop to improve the solution</p>
            </div>
          </div>
        </div>
      </div>
  );
}