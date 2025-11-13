'use client'
import { useState } from 'react';
import { Zap, RotateCcw, AlertCircle, CheckCircle } from 'lucide-react';
import SolverActions from '@/components/SolverActions';

interface Assignment {
  worker: number;
  task: number;
  cost: number;
}

interface Solution {
  assignments: Assignment[];
  total_cost: number;
  problem_type: 'min' | 'max';
}
export default function AssignmentPage() {
  // Form State
  const [isSquare, setIsSquare] = useState(true);
  const [rows, setRows] = useState(3);
  const [cols, setCols] = useState(3);
  const [problemType, setProblemType] = useState<'min' | 'max'>('min');
  const [tableData, setTableData] = useState<number[][]>(
    Array(3).fill(0).map(() => Array(3).fill(0))
  );
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [solution, setSolution] = useState<Solution | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // State for video

  // --- All your other functions (updateDimensions, handleSquareChange, etc.) are unchanged ---
  const updateDimensions = (newRows: number, newCols: number) => {
    setRows(newRows);
    setCols(newCols);
    const newTable = Array(newRows).fill(0).map((_, i) => 
      Array(newCols).fill(0).map((_, j) => 
        tableData[i]?.[j] ?? 0
      )
    );
    setTableData(newTable);
  };
  const handleSquareChange = (checked: boolean) => {
    setIsSquare(checked);
    if (checked) {
      updateDimensions(rows, rows);
    }
  };
  const updateCell = (row: number, col: number, value: string) => {
    const numValue = value === '' ? 0 : parseFloat(value);
    if (isNaN(numValue)) return;
    const newData = [...tableData];
    newData[row][col] = numValue;
    setTableData(newData);
  };
  const generateRandom = () => {
    const newData = Array(rows).fill(0).map(() => 
      Array(cols).fill(0).map(() => Math.floor(Math.random() * 100))
    );
    setTableData(newData);
    setSuccess('Random table generated!');
    setSolution(null);
    setTimeout(() => setSuccess(null), 2000);
  };
  const clearTable = () => {
    setTableData(Array(rows).fill(0).map(() => Array(cols).fill(0)));
    setSolution(null);
  };
  // --- END of unchanged functions ---


  // --- NEW POLLING LOGIC ---
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
          // Direct solution
          setSolution(resultData.solution); // This should match your JSON structure
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
  const startJob = async (outputType: 'direct' | 'video' | 'pdf') => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setSolution(null);
    setVideoUrl(null);

    try {
      const payload = {
        isSquare,
        rows,
        cols,
        problemType,
        tableData,
        outputType
      };

      const response = await fetch('http://localhost:8000/api/assignment/solve', { // <-- New FastAPI URL
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
  
  const isInputEmpty = tableData.flat().every(cell => cell === 0);

  return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header (unchanged) */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Assignment Problem Solver
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Solve assignment problems using the Hungarian Algorithm. Enter your cost matrix and get instant solutions with beautiful animations.
          </p>
        </div>

        {/* Main Form Container (unchanged) */}
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-8 mb-8">
          
          {/* Configuration Section (unchanged) */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* ... (all your config JSX is unchanged) ... */}
            {/* Left Column - Problem Settings */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-white mb-4">Problem Configuration</h3>
              
              {/* Square Matrix Toggle */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isSquare}
                    onChange={(e) => handleSquareChange(e.target.checked)}
                    className="w-5 h-5 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <div>
                    <span className="text-white font-medium">Square Matrix</span>
                    <p className="text-sm text-gray-400">Equal number of rows and columns</p>
                  </div>
                </label>
              </div>

              {/* Dimensions */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Rows (Workers)
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={rows}
                    onChange={(e) => {
                      const newRows = parseInt(e.target.value) || 2;
                      updateDimensions(newRows, isSquare ? newRows : cols);
                    }}
                    className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Columns (Tasks)
                  </label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={cols}
                    disabled={isSquare}
                    onChange={(e) => {
                      const newCols = parseInt(e.target.value) || 2;
                      updateDimensions(rows, newCols);
                    }}
                    className={`w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 ${
                      isSquare ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
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

            {/* Right Column - Quick Actions (Unchanged) */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
              
              <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg p-6 border border-purple-500/30">
                <h4 className="text-white font-semibold mb-3">Need sample data?</h4>
                <p className="text-gray-300 text-sm mb-4">
                  Generate a random cost matrix to test the solver
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

              {/* Info Box */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <div className="flex gap-2">
                  <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-blue-300">
                    <strong>Tip:</strong> For non-square matrices, dummy rows/columns will be added automatically.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Cost Matrix Input (Unchanged) */}
          <div className="mb-8">
            {/* ... (all your table JSX is unchanged) ... */}
            <h3 className="text-xl font-semibold text-white mb-4">
              Cost Matrix
              <span className="text-sm text-gray-400 ml-2 font-normal">
                ({rows} × {cols})
              </span>
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="bg-slate-800/50 border border-white/10 p-2 text-gray-400 text-sm font-medium"></th>
                    {Array.from({ length: cols }, (_, i) => (
                      <th key={i} className="bg-slate-800/50 border border-white/10 p-2 text-purple-400 text-sm font-medium">
                        Task {i + 1}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: rows }, (_, i) => (
                    <tr key={i}>
                      <td className="bg-slate-800/50 border border-white/10 p-2 text-blue-400 text-sm font-medium text-center">
                        Worker {i + 1}
                      </td>
                      {Array.from({ length: cols }, (_, j) => (
                        <td key={j} className="border border-white/10 p-1">
                          <input
                            type="number"
                            value={tableData[i][j] || ''}
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

          {/* Status Messages (Unchanged) */}
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
            isInputDisabled={isInputEmpty} // Disable if all cells are 0
            onSolveVideo={() => startJob('video')}
            onSolveDirect={() => startJob('direct')}
            onSolvePdf={() => startJob('pdf')}
          />
        </div>
        
        {/* --- NEW VIDEO SECTION --- */}
        {videoUrl && (
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-500/10 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-6 my-8">
            <h3 className="text-2xl font-bold text-white mb-4 text-center">
              Video Solution
            </h3>
            <div className="aspect-video rounded-lg overflow-hidden border border-white/20 bg-black">
              <video
                key={videoUrl}
                width="100%"
                controls
                autoPlay
                playsInline
              >
                <source src={videoUrl} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        )}

        {/* Solution Display (Unchanged) */}
        {solution && (
          <div className="bg-gradient-to-br from-green-500/20 to-green-500/10 backdrop-blur-sm border border-green-500/30 rounded-2xl p-8 my-8">
            {/* ... (all your solution display JSX is unchanged) ... */}
            <h3 className="text-2xl font-bold text-white mb-6 text-center">
              Optimal Solution Found!
            </h3>
            <div className="text-center mb-6">
              <p className="text-lg text-gray-300">
                Total {solution.problem_type === 'min' ? 'Cost' : 'Profit'}:
              </p>
              <p className="text-5xl font-bold text-green-400">
                {solution.total_cost}
              </p>
            </div>
            <div className="max-w-md mx-auto">
              <h4 className="text-lg font-semibold text-white mb-3 text-center">
                Optimal Assignments:
              </h4>
              <ul className="space-y-2">
                {solution.assignments.map((assign, index) => (
                  <li 
                    key={index}
                    className="bg-white/5 border border-white/10 rounded-lg p-3 flex justify-between items-center"
                  >
                    <span className="text-blue-300 font-medium">Worker {assign.worker}</span>
                    <Zap className="w-5 h-5 text-purple-400" />
                    <span className="text-purple-300 font-medium">Task {assign.task}</span>
                    <span className="text-gray-400">(Cost: {assign.cost})</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {/* How It Works Section (Unchanged) */}
        <div className="bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
          {/* ... (all your "How it works" JSX is unchanged) ... */}
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            How the Hungarian Algorithm Works
          </h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-purple-400">1</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Row Reduction</h4>
              <p className="text-gray-400 text-sm">Subtract minimum value from each row</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-blue-400">2</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Column Reduction</h4>
              <p className="text-gray-400 text-sm">Subtract minimum value from each column</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-green-400">3</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Cover Zeros</h4>
              <p className="text-gray-400 text-sm">Draw minimum lines to cover all zeros</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-xl font-bold text-yellow-400">4</span>
              </div>
              <h4 className="text-white font-semibold mb-2">Optimal Assignment</h4>
              <p className="text-gray-400 text-sm">Find the optimal worker-task pairing</p>
            </div>
          </div>
        </div>
      </div>
  );
}