'use client'
import { useState } from 'react';
import { AlertCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import SolverActions from '@/components/SolverActions'; // <-- 1. IMPORTED a new component

// Interface for the design result structure
interface DesignResult {
  Rope: any;
  Pulley: any;
  AxleAndBearing: any;
  Hook: any;
  Nut: any;
  ThrustBearing: any;
  CrossPiece: any;
  ShacklePlate: any;
  RopeDrum: any;
  DrumShaft: any;
}

export default function EOTCranePage() {
  // --- All your existing state is perfect ---
  const [load, setLoad] = useState(5);
  const [loadUnit, setLoadUnit] = useState<'tonnes' | 'kN'>('tonnes');
  const [speed, setSpeed] = useState(10);
  const [speedUnit, setSpeedUnit] = useState<'m/min' | 'm/s'>('m/min');
  const [liftHeight, setLiftHeight] = useState(15);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<DesignResult | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set([1]));
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  // --- This function is unchanged ---
  const toggleSection = (step: number) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(step)) {
      newExpanded.delete(step);
    } else {
      newExpanded.add(step);
    }
    setExpandedSections(newExpanded);
  };

  // --- 2. REPLACED 'solveProblem' with FastAPI polling logic ---

  // Helper function to poll for the job result
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
        setSuccess('Design completed successfully!');
        
        if (resultData.videoUrl) {
          setVideoUrl(resultData.videoUrl); // Set the video URL
        } else if (resultData.pdfUrl) {
          window.open(resultData.pdfUrl, '_blank'); // Open the PDF
        } else {
          // Direct solution
          setResult(resultData.results); // The EOT solver returns {status: 'success', results: {...}}
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

  // Main function to start the job
  const startJob = async (outputType: 'direct' | 'video' | 'pdf') => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setResult(null);
    setVideoUrl(null);

    try {
      const payload = {
        load,
        loadUnit: loadUnit === 'kN' ? 'kg' : 'tonnes', // Convert kN to kg for backend if needed, or adjust
        speed,
        speedUnit,
        liftHeight,
        outputType
      };
      
      // Convert kN to kg (assuming 1 kN = 100 kg, adjust if 1000/9.81 is better)
      // Note: Your FastAPI backend can also be built to handle 'kN'
      if (payload.loadUnit === 'kN') {
         payload.load = load * 100; // Example conversion: 5 kN -> 500 kg
         payload.loadUnit = 'kg';
      }

      const response = await fetch('http://localhost:8000/api/eot-crane/solve', { // <-- New FastAPI URL
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
      setError(err instanceof Error ? err.message : 'Failed to start design job');
      setLoading(false); // Stop loading on initial error
    }
  };
  
  // --- This data array is unchanged ---
  const designSteps = result ? [
    // ... (all your 8 designSteps objects are unchanged) ...
    { 
      id: 1, 
      title: "⛓️ Rope Design", 
      data: result.Rope,
      metrics: [
        { label: "Selected Rope Diameter", value: `${result.Rope.Diameter_mm?.toFixed(1)} mm` },
        { label: "Calculated Rope Life", value: `${result.Rope.Life_Months?.toFixed(1)} months` },
        { label: "Breaking Load", value: `${result.Rope.BreakingLoad_Tonnes?.toFixed(2)} Tonnes` }
      ],
      status: result.Rope.Status
    },
    { 
      id: 2, 
      title: "⚙️ Pulley & Axle Design", 
      data: { ...result.Pulley, ...result.AxleAndBearing },
      metrics: [
        { label: "Pulley Diameter (D)", value: `${result.Pulley.PulleyDiameter_mm?.toFixed(0)} mm` },
        { label: "Final Axle Diameter (d)", value: `${result.AxleAndBearing.FinalAxleDiameter_mm?.toFixed(0)} mm` }
      ]
    },
    { 
      id: 3, 
      title: "🔵 Bearing Selection", 
      data: result.AxleAndBearing,
      metrics: [
        { label: "Required Dynamic Load", value: `${result.AxleAndBearing.DynamicLoad_kgf?.toFixed(2)} kgf` },
        { label: "Selected Bearing", value: `No. ${result.AxleAndBearing.SelectedBearing?.BearingNo}` }
      ]
    },
    { 
      id: 4, 
      title: "⚓️ Hook Design", 
      data: result.Hook,
      metrics: [
        { label: "Resultant Stress", value: `${result.Hook.ResultantStress_N_mm2?.toFixed(2)} N/mm²` },
        { label: "Safe Load", value: `${result.Hook.ChosenHook?.SafeLoad} Tonnes` }
      ],
      status: result.Hook.Status
    },
    { 
      id: 5, 
      title: "🔩 Nut & Thrust Bearing", 
      data: { ...result.Nut, ...result.ThrustBearing },
      metrics: [
        { label: "Nut Height", value: `${result.Nut.NutHeight_mm?.toFixed(0)} mm` },
        { label: "Number of Threads", value: result.Nut.NumberOfThreads },
        { label: "Thrust Bearing", value: `No. ${result.ThrustBearing.ChosenBearing?.BearingNo}` }
      ]
    },
    { 
      id: 6, 
      title: "➕ Cross Piece & Shackle Plate", 
      data: { ...result.CrossPiece, ...result.ShacklePlate },
      metrics: [
        { label: "Cross Piece Height", value: `${result.CrossPiece.FinalHeight_mm?.toFixed(0)} mm` },
        { label: "Bearing Pressure", value: `${result.ShacklePlate.BearingPressure_N_mm2?.toFixed(2)} N/mm²` }
      ],
      status: result.ShacklePlate.Status
    },
    { 
      id: 7, 
      title: "🥁 Rope Drum Design", 
      data: result.RopeDrum,
      metrics: [
        { label: "Drum Length", value: `${result.RopeDrum.Length_mm?.toFixed(1)} mm` },
        { label: "Bending Stress", value: `${result.RopeDrum.BendingStress_N_mm2?.toFixed(2)} N/mm²` }
      ],
      status: result.RopeDrum.Status
    },
    { 
      id: 8, 
      title: "⚡ Drum Shaft Design", 
      data: result.DrumShaft,
      metrics: [
        { label: "Final Shaft Diameter", value: `${result.DrumShaft.Diameter_mm?.toFixed(0)} mm` },
        { label: "Equivalent Torque", value: `${result.DrumShaft.EquivalentTorque_N_mm?.toLocaleString()} N-mm` }
      ]
    }
  ] : [];

  return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header (unchanged) */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            EOT Crane Design
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Complete electric overhead traveling crane design with rope, pulley, hook, drum, and shaft calculations
          </p>
        </div>

        {/* Input Form (unchanged) */}
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-8 mb-8">
          <h3 className="text-2xl font-semibold text-white mb-6">Design Parameters</h3>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {/* Load (unchanged) */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-300">Load Capacity</label>
              <input
                type="number"
                value={load}
                onChange={(e) => setLoad(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter load"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => setLoadUnit('tonnes')}
                  className={`flex-1 py-2 rounded-lg transition-all ${loadUnit === 'tonnes' ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-300 hover:bg-white/10'}`}
                >
                  Tonnes
                </button>
                <button
                  onClick={() => setLoadUnit('kN')}
                  className={`flex-1 py-2 rounded-lg transition-all ${loadUnit === 'kN' ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-300 hover:bg-white/10'}`}
                >
                  kN
                </button>
              </div>
            </div>
            {/* Speed (unchanged) */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-300">Lifting Speed</label>
              <input
                type="number"
                value={speed}
                onChange={(e) => setSpeed(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter speed"
              />
              <div className="flex gap-2">
                <button
                  onClick={() => setSpeedUnit('m/min')}
                  className={`flex-1 py-2 rounded-lg transition-all ${speedUnit === 'm/min' ? 'bg-green-600 text-white' : 'bg-white/5 text-gray-300 hover:bg-white/10'}`}
                >
                  m/min
                </button>
                <button
                  onClick={() => setSpeedUnit('m/s')}
                  className={`flex-1 py-2 rounded-lg transition-all ${speedUnit === 'm/s' ? 'bg-green-600 text-white' : 'bg-white/5 text-gray-300 hover:bg-white/10'}`}
                >
                  m/s
                </button>
              </div>
            </div>
            {/* Lift Height (unchanged) */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-300">Lift Height (meters)</label>
              <input
                type="number"
                value={liftHeight}
                onChange={(e) => setLiftHeight(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-800 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter height"
              />
              <div className="text-sm text-gray-400 pt-2">
                Typical: 10-30 meters
              </div>
            </div>
          </div>


          {/* Status Messages (unchanged) */}
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

          {/* --- SolverActions component --- */}
          <SolverActions
            isLoading={loading}
            isInputDisabled={!load || !speed || !liftHeight} // Disable if any input is 0
            onSolveVideo={() => startJob('video')}
            onSolveDirect={() => startJob('direct')}
            onSolvePdf={() => startJob('pdf')}
          />
        </div>
        
        {/* Video Player Section */}
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
                preload="metadata"
              >
                <source src={videoUrl} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 backdrop-blur-sm border border-green-500/30 rounded-2xl p-8 mb-8">
            <h3 className="text-3xl font-bold text-white mb-6 text-center">Design Results</h3>
            <div className="space-y-4">
              {designSteps.map((step) => (
                <div key={step.id} className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                  <button
                    onClick={() => toggleSection(step.id)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{step.title.split(' ')[0]}</span>
                      <h4 className="text-lg font-semibold text-white">{step.title.substring(step.title.indexOf(' ') + 1)}</h4>
                      {step.status && (
                        <span className={`text-xs px-3 py-1 rounded-full ${step.status === 'Safe' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                          {step.status}
                        </span>
                      )}
                    </div>
                    {expandedSections.has(step.id) ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                  </button>

                  {expandedSections.has(step.id) && (
                    <div className="px-6 pb-6 pt-2">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {step.metrics.map((metric, idx) => (
                          <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                            <p className="text-sm text-gray-400 mb-1">{metric.label}</p>
                            <p className="text-lg font-bold text-white">{metric.value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Raw JSON */}
            <details className="mt-6">
              <summary className="cursor-pointer text-gray-400 hover:text-white transition-colors py-2">
                Show Full Design Data (JSON)
              </summary>
              <pre className="mt-4 bg-slate-900 rounded-lg p-4 overflow-auto text-xs text-gray-300">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        )}

        {/* Info Section (unchanged) */}
        <div className="bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Design Components</h3>
          <div className="grid md:grid-cols-4 gap-4">
            {['Rope', 'Pulley', 'Hook', 'Drum', 'Shaft', 'Bearings', 'Nut', 'Plates'].map((comp, idx) => (
              <div key={idx} className="text-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                <p className="text-gray-300 font-medium">{comp}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
  );
}