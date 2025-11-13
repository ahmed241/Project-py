'use client';
import ResultsDisplay from '@/components/ResultsDisplay';
import { useState } from 'react';
import { ArrowLeft, Info, BookOpen, Settings, Shield, ArrowDownWideNarrow, List, CheckCircle, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import SolverActions from '@/components/SolverActions';
import SupportsForm from '@/components/SupportsForm';
import 'katex/dist/katex.min.css';
import { Support, Load } from './type';
import BeamCanvas from "@/components/BeamCanvas";
import LoadsForm from '@/components/LoadsForm';


export default function SFDBMDPage() {
  // State Management
  const [beamLength, setBeamLength] = useState<number>(10);
  const [supports, setSupports] = useState<Support[]>([]);
  const [loads, setLoads] = useState<Load[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null); // This will be your solution object
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Current step in the input process
  const [currentStep, setCurrentStep] = useState<
    'beam' | 'supports' | 'loads' | 'review'
  >('beam');

  // Validation
  const isInputComplete = beamLength > 0 && supports.length >= 2 && loads.length > 0;

  // --- API Call Functions (using FastAPI polling) ---
  const pollForJobResult = async (job_id: string) => {
    try {
      const statusResponse = await fetch(`http://localhost:8000/api/status/${job_id}`);
      if (!statusResponse.ok) throw new Error("Polling request failed.");

      const resultData = await statusResponse.json();

      if (resultData.status === 'pending') {
        setTimeout(() => pollForJobResult(job_id), 3000);
      } else if (resultData.status === 'complete' || resultData.status === 'success') {
        setIsLoading(false);
        setSuccess('Analysis Complete!');

        if (resultData.videoUrl) {
          setVideoUrl(resultData.videoUrl);
        } else if (resultData.pdfUrl) {
          window.open(resultData.pdfUrl, '_blank');
        } else {
          setResults(resultData.solution); // This will have the plot data, max values, etc.
        }
      } else if (resultData.status === 'error') {
        throw new Error(resultData.message || 'The script failed to run.');
      }
    } catch (pollError: any) {
      console.error('Polling Error:', pollError);
      setError(pollError.message || 'Failed to get job status.');
      setIsLoading(false);
    }
  };

  const startJob = async (outputType: 'direct' | 'video' | 'pdf') => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setResults(null);
    setVideoUrl(null);

    try {
      const payload = {
        beamLength,
        supports,
        loads,
        outputType,
      };

      const response = await fetch('http://localhost:8000/api/sfd-bmd/solve', { // <-- New Endpoint
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

      const { job_id } = await response.json();
      if (!job_id) throw new Error("Failed to get Job ID from server.");

      setSuccess("Job started! This may take a minute...");
      setTimeout(() => pollForJobResult(job_id), 3000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start job');
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setBeamLength(10);
    setSupports([]);
    setLoads([]);
    setResults(null);
    setVideoUrl(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <>
      {/* Header */}
      <header className="bg-gray-950/80 backdrop-blur border-b border-white/10 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Back Button & Title */}
            <div className="flex items-center gap-4">
              <Link
                href="/strength-of-materials"
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-300" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  SFD & BMD Calculator
                </h1>
                <p className="text-sm text-gray-400 mt-0.5">
                  Shear Force and Bending Moment Diagrams
                </p>
              </div>
            </div>

            {/* Info Button */}
            <button className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-500/20 text-blue-300 rounded-lg hover:bg-blue-500/30 transition-colors">
              <Info className="w-4 h-4" />
              <span>Help</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Input Steps */}
          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-gray-900 to-gray-950 rounded-2xl shadow-lg border border-white/10 overflow-hidden sticky top-24">
              {/* Step Navigation */}
              <div className="bg-gray-800/50 p-4 border-b border-white/10">
                <h2 className="text-white font-semibold text-lg">Input Steps</h2>
              </div>

              <nav className="p-4 space-y-2">
                {/* Step 1: Beam Properties */}
                <button
                  onClick={() => setCurrentStep('beam')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all ${currentStep === 'beam'
                    ? 'bg-blue-600/50 border-2 border-blue-500 text-blue-200'
                    : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">1. Beam Properties</div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        Length: {beamLength}m
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${beamLength > 0 ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300'
                      }`}>
                      {beamLength > 0 ? '✓' : '1'}
                    </div>
                  </div>
                </button>

                {/* Step 2: Supports */}
                <button
                  onClick={() => setCurrentStep('supports')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all ${currentStep === 'supports'
                    ? 'bg-blue-600/50 border-2 border-blue-500 text-blue-200'
                    : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">2. Add Supports</div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {supports.length} support(s) added
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${supports.length >= 2 ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300'
                      }`}>
                      {supports.length >= 2 ? '✓' : '2'}
                    </div>
                  </div>
                </button>

                {/* Step 3: Loads */}
                <button
                  onClick={() => setCurrentStep('loads')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all ${currentStep === 'loads'
                    ? 'bg-blue-600/50 border-2 border-blue-500 text-blue-200'
                    : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">3. Add Loads</div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {loads.length} load(s) added
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${loads.length > 0 ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300'
                      }`}>
                      {loads.length > 0 ? '✓' : '3'}
                    </div>
                  </div>
                </button>

                {/* Step 4: Review */}
                <button
                  onClick={() => setCurrentStep('review')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all ${currentStep === 'review'
                    ? 'bg-blue-600/50 border-2 border-blue-500 text-blue-200'
                    : 'bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10'
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">4. Review & Solve</div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {isInputComplete ? 'Ready to solve' : 'Complete all steps'}
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isInputComplete ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300'
                      }`}>
                      {isInputComplete ? '✓' : '4'}
                    </div>
                  </div>
                </button>
              </nav>

              {/* Quick Actions */}
              <div className="p-4 border-t border-white/10">
                <button
                  onClick={handleClear}
                  className="w-full px-4 py-2 text-sm text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>

          {/* Center & Right - Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Canvas Placeholder */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-950 rounded-2xl shadow-lg border border-white/10 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Beam Visualization</h3>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 text-sm border border-white/20 rounded-lg hover:bg-white/10 text-gray-300">
                    Zoom In
                  </button>
                  <button className="px-3 py-1.5 text-sm border border-white/20 rounded-lg hover:bg-white/10 text-gray-300">
                    Reset
                  </button>
                </div>
              </div>

              {/* Canvas will go here */}
              <div className="bg-gray-800/50 border-2 border-dashed border-gray-600 rounded-lg h-64 flex items-center justify-center">
                <div className="bg-black/40 p-4 rounded-lg">
                  {/* Replace the old stub with BeamCanvas */}
                  <BeamCanvas beamLength={beamLength} supports={supports} loads={loads} width={900} height={180} />
                </div>

              </div>
            </div>

            {/* Input Forms - Changes based on currentStep */}
            <div className="bg-gradient-to-br from-gray-900 to-gray-950 rounded-2xl shadow-lg border border-white/10 p-6">
              {currentStep === 'beam' && <BeamPropertiesForm beamLength={beamLength} setBeamLength={setBeamLength} />}
              {currentStep === 'supports' && <SupportsForm supports={supports} setSupports={setSupports} beamLength={beamLength} />}
              {currentStep === 'loads' && <LoadsForm loads={loads} setLoads={setLoads} beamLength={beamLength} />}
              {currentStep === 'review' && <ReviewSection beamLength={beamLength} supports={supports} loads={loads} />}

              {/* Status Messages */}
              {error && (

                <div className="mt-6 bg-red-500/20 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <p className="text-red-300">{error}</p>
                </div>
              )}
              {success && (
                <div className="mt-6 bg-green-500/20 border border-green-500/50 rounded-lg p-4 flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                  <p className="text-green-300">{success}</p>
                </div>
              )}
            </div>

            {/* Solver Actions */}
            {isInputComplete && (
              <div className="bg-gradient-to-br from-gray-900 to-gray-950 rounded-2xl shadow-lg border border-white/10 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Choose Solution Method
                </h3>
                <SolverActions
                  isLoading={isLoading}
                  isInputDisabled={!isInputComplete}
                  onSolveVideo={() => startJob('video')}
                  onSolveDirect={() => startJob('direct')}
                  onSolvePdf={() => startJob('pdf')}
                />
              </div>
            )}

            {/* Results Section */}
            {/* --- NEW Results Section --- */}
            {results && (
              <ResultsDisplay
                solution={results}
                supports={supports}
                loads={loads}
              />
            )}
          </div>
        </div>
      </main>
    </>
  );
}

// ============================================
// SUB-COMPONENTS FOR EACH STEP
// ============================================

// 1. Beam Properties Form
function BeamPropertiesForm({ beamLength, setBeamLength }: { beamLength: number; setBeamLength: (val: number) => void }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">
          1. Beam Properties
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Define the basic properties of your beam.
        </p>
      </div>

      {/* Beam Length */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Beam Length <span className="text-red-400">*</span>
        </label>
        <div className="flex gap-3">
          <input
            type="number"
            value={beamLength}
            onChange={(e) => setBeamLength(Number(e.target.value))}
            min="1"
            step="0.1"
            className="flex-1 px-4 py-2.5 bg-gray-800 border border-white/20 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="10"
          />
          <div className="flex items-center px-4 bg-gray-700/50 rounded-lg border border-white/20">
            <span className="text-gray-300 font-medium">m</span>
          </div>
        </div>
        <p className="mt-1.5 text-xs text-gray-400">
          Enter the total length of the beam in meters.
        </p>
      </div>

      {/* Optional: Material Properties */}
      <div className="border-t border-white/10 pt-4">
        <details className="group">
          <summary className="cursor-pointer text-sm font-medium text-gray-400 hover:text-blue-300">
            Advanced Properties (Optional)
          </summary>
          <div className="mt-4 space-y-4 pl-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Young's Modulus (E)
              </label>
              <div className="flex gap-3">
                <input
                  type="number"
                  className="flex-1 px-4 py-2.5 bg-gray-800 border border-white/20 text-white rounded-lg"
                  placeholder="200"
                />
                <div className="flex items-center px-4 bg-gray-700/50 rounded-lg border border-white/20">
                  <span className="text-gray-300">GPa</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Moment of Inertia (I)
              </label>
              <div className="flex gap-3">
                <input
                  type="number"
                  className="flex-1 px-4 py-2.5 bg-gray-800 border border-white/20 text-white rounded-lg"
                  placeholder="1000"
                />
                <div className="flex items-center px-4 bg-gray-700/50 rounded-lg border border-white/20">
                  <span className="text-gray-300">cm⁴</span>
                </div>
              </div>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}

// 4. Review Section (Placeholder)
function ReviewSection({ beamLength, supports, loads }: any) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">
          4. Review Your Problem
        </h3>
        <p className="text-sm text-gray-400 mb-4">
          Verify all inputs before generating the solution.
        </p>
      </div>

      <div className="space-y-4">
        <div className="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
          <h4 className="font-medium text-blue-200 mb-2">Beam Properties</h4>
          <p className="text-sm text-blue-300">Length: {beamLength}m</p>
        </div>

        <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
          <h4 className="font-medium text-green-200 mb-2">Supports</h4>
          <p className="text-sm text-green-300">{supports.length} support(s) added</p>
        </div>

        <div className="p-4 bg-purple-500/20 border border-purple-500/30 rounded-lg">
          <h4 className="font-medium text-purple-200 mb-2">Loads</h4>
          <p className="text-sm text-purple-300">{loads.length} load(s) added</p>
        </div>
      </div>
    </div>
  );
}

// Result Card Component
function ResultCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-4 bg-gradient-to-br from-blue-500/10 to-blue-500/20 border border-blue-500/30 rounded-lg">
      <div className="text-sm text-blue-300 mb-1">{label}</div>
      <div className="text-2xl font-bold text-white mt-1">{value}</div>
    </div>
  );
}