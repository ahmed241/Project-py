'use client'
import { useState, useRef, useEffect } from 'react';
import { RotateCcw, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';
import SolverActions from '@/components/SolverActions';

// Define the response type
interface LaplaceResponse {
  result: string;
  steps?: string[];
  videoUrl?: string;
  pdfUrl?: string;
}

export default function LaplacePage() {
  // Form State
  const [latexInput, setLatexInput] = useState<string>('f(t) = t^2');
  const [operation, setOperation] = useState<'laplace' | 'inverse'>('laplace');
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<LaplaceResponse | null>(null);
  const [mathLiveLoaded, setMathLiveLoaded] = useState(false);

  const mathfieldRef = useRef<HTMLDivElement>(null);

// Initialize MathLive with current API
  useEffect(() => {
    const initializeMathLive = async () => {
      try {
        // Dynamically import MathLive
        const MathLive = await import('mathlive');
        console.log('MathLive loaded:', MathLive);
        
        if (mathfieldRef.current && MathLive.MathfieldElement) {
          
          // 1. Create the element with correct, flat options
          const mfe = new MathLive.MathfieldElement({
            // --- THIS IS THE FIX ---
            // 'mathVirtualKeyboardPolicy' controls the mode
            mathVirtualKeyboardPolicy: 'auto' 
            // 'virtualKeyboards' controls the layouts
          });

          // 2. Set the .value property (this is not an option)
          mfe.value = latexInput; 
          
          // 3. Add event listener
          mfe.addEventListener('input', () => {
            setLatexInput(mfe.value);
          });

          // 4. Set styles
          mfe.style.width = '100%';
          mfe.style.minHeight = '80px';
          mfe.style.fontSize = '1.25rem';
          
          // 5. Append to the DOM
          mathfieldRef.current.innerHTML = '';
          mathfieldRef.current.appendChild(mfe);
          
          // 6. Focus
          mfe.focus();
          
          setMathLiveLoaded(true);
        }
      } catch (err) {
        console.error('Failed to load MathLive:', err);
        setError('Math editor failed to load. Please refresh the page.');
      }
    };

    initializeMathLive();
  }, []); // Empty array ensures this runs once on mount
  
  // Fallback to textarea if MathLive fails
  const handleManualLatexChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setLatexInput(e.target.value);
  };

  // Common math templates
  const mathTemplates = [
    { name: 'Polynomial', latex: 't^2' },
    { name: 'Exponential', latex: 'e^{-t}' },
    { name: 'Sine', latex: '\\sin(\\omega t)' },
    { name: 'Cosine', latex: '\\cos(2t)' },
    { name: 'Damped Oscillator', latex: 'e^{-t}\\sin(t)' },
    { name: 'Step Function', latex: 'u(t)' },
    { name: 'Delta Function', latex: '\\delta(t)' },
    { name: 'Rational Function', latex: '\\frac{1}{s^2 + 1}' },
    { name: 'Partial Fractions', latex: '\\frac{1}{s(s+1)}' },
  ];

  // Insert template using current MathLive API
  const insertTemplate = (latex: string) => {
    if (mathfieldRef.current?.querySelector('math-field')) {
      const mf = mathfieldRef.current.querySelector('math-field') as any;
      if (mf) {
        // Use insert command for MathLive
        mf.insert(latex, { 
          insertionMode: 'replaceAll',
          focus: true,
          scrollIntoView: true
        });
      }
    } else {
      // Fallback: append to textarea
      setLatexInput(prev => prev + latex);
    }
  };

  // Show virtual keyboard using current API
  const showVirtualKeyboard = () => {
    if (mathfieldRef.current?.querySelector('math-field')) {
      const mf = mathfieldRef.current.querySelector('math-field') as any;
      if (mf) {
        mf.focus();
        mf.executeCommand('toggleVirtualKeyboard');
      }
    }
  };

  // Clear input
  const clearInput = () => {
    if (mathfieldRef.current?.querySelector('math-field')) {
      const mf = mathfieldRef.current.querySelector('math-field') as any;
      if (mf) {
        mf.value = '';
      }
    }
    setLatexInput('');
    setResult(null);
    setError(null);
    setSuccess(null);
  };

  // Generate random example
  const generateRandomExample = () => {
    const examples = operation === 'laplace' ? [
      't^2',
      'e^{-t}',
      '\\sin(\\omega t)',
      '\\cos(2t)',
      't e^{-3t}',
      '\\delta(t)',
      'u(t-1)',
    ] : [
      '\\frac{1}{s}',
      '\\frac{1}{s^2 + 1}',
      '\\frac{s}{s^2 + 4}',
      '\\frac{1}{(s+1)^2}',
      '\\frac{1}{s(s+1)}',
      '\\frac{e^{-s}}{s}',
    ];
    
    const randomExample = examples[Math.floor(Math.random() * examples.length)];
    const prefix = operation === 'laplace' ? 'f(t) = ' : 'F(s) = ';
    
    if (mathfieldRef.current?.querySelector('math-field')) {
      const mf = mathfieldRef.current.querySelector('math-field') as any;
      if (mf) {
        mf.value = prefix + randomExample;
      }
    } else {
      setLatexInput(prefix + randomExample);
    }
  };

 // --- API Call Function ---
  const solveProblem = async (outputType: 'direct' | 'video' | 'pdf') => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setResult(null); // Clear previous results

    try {
      const payload = {
        latex: latexInput,
        operation,
        outputType,
      };

      console.log('Sending to API:', payload);

      // --- STEP 1: Start the job ---
      const response = await fetch('http://localhost:8000/api/laplace/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        // This catches errors from FastAPI itself (e.g., 500 server error)
        throw new Error(`API Error: ${response.statusText}`);
      }

      const { job_id } = await response.json();
      if (!job_id) {
        throw new Error("Failed to get Job ID from server.");
      }
      
      setSuccess("Job started! Waiting for server to finish...");

      // --- STEP 2: Poll for the result ---
      const poll = async () => {
        
        // --- FIX: Add try...catch INSIDE the poll function ---
        try {
          const statusResponse = await fetch(`http://localhost:8000/api/status/${job_id}`);
          if (!statusResponse.ok) {
            throw new Error("Polling request failed.");
          }
          
          const result = await statusResponse.json();

          if (result.status === 'pending') {
            // Not done, poll again in 2 seconds
            setTimeout(poll, 2000);

          } else if (result.status === 'complete' || result.status === 'success') {
            // --- Job is DONE! ---
            setLoading(false);
            setSuccess('Solution calculated successfully!');
            
            if (result.videoUrl) {
              setResult({ result: 'Video Generated', videoUrl: result.videoUrl });
              window.open(result.videoUrl, '_blank'); // Open the video
            } else if (result.pdfUrl) {
              setResult({ result: 'PDF Generated', pdfUrl: result.pdfUrl });
              window.open(result.pdfUrl, '_blank'); // Open the PDF
            } else {
              // Direct solution
              setResult(result); // This is the {status: 'success', result: '...', steps: [...]}
            }
            
          } else if (result.status === 'error') {
            // --- The job failed on the backend ---
            // This now correctly sets the error state and stops loading
            throw new Error(result.message || 'The script failed to run.');
          }
        } catch (pollError: any) {
          // --- FIX: This catch block now handles polling errors ---
          console.error('Polling Error:', pollError);
          setError(pollError.message || 'Failed to get job status.');
          setLoading(false); // Stop the loading spinner
        }
      };
      
      // Start the first poll
      setTimeout(poll, 2000);

    } catch (err) {
      // This catch block only handles the INITIAL job request
      setError(err instanceof Error ? err.message : 'Failed to solve problem');
      console.error('Error:', err);
      setLoading(false); // Stop loading on initial error
    }
  };
  
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Laplace Transform Calculator
        </h1>
        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
          Compute Laplace transforms and inverse Laplace transforms with WYSIWYG math editing
        </p>
      </div>

      {/* Main Form Container */}
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-8 mb-8">
        
        {/* Configuration Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          
          {/* Left Column - Problem Settings */}
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Problem Configuration</h3>
            
            {/* Operation Type */}
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Operation Type
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setOperation('laplace')}
                  className={`py-3 px-4 rounded-lg font-medium transition-all ${
                    operation === 'laplace'
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                      : 'bg-white/5 text-gray-300 hover:bg-white/10'
                  }`}
                >
                  Laplace Transform
                </button>
                <button
                  onClick={() => setOperation('inverse')}
                  className={`py-3 px-4 rounded-lg font-medium transition-all ${
                    operation === 'inverse'
                      ? 'bg-green-600 text-white shadow-lg shadow-green-500/50'
                      : 'bg-white/5 text-gray-300 hover:bg-white/10'
                  }`}
                >
                  Inverse Laplace
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Quick Actions */}
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-white mb-4">Quick Actions</h3>
            
            <div className="bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg p-6 border border-purple-500/30">
              <h4 className="text-white font-semibold mb-3">Need an example?</h4>
              <p className="text-gray-300 text-sm mb-4">
                Generate a random Laplace transform problem
              </p>
              <button
                onClick={generateRandomExample}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Generate Random Example
              </button>
            </div>

            <div className="bg-white/5 rounded-lg p-6 border border-white/10">
              <h4 className="text-white font-semibold mb-3">Reset Input</h4>
              <p className="text-gray-300 text-sm mb-4">
                Clear the input field and start fresh
              </p>
              <button
                onClick={clearInput}
                className="w-full bg-red-600/20 hover:bg-red-600/30 text-red-300 py-2 rounded-lg transition-colors border border-red-500/30"
              >
                Clear Input
              </button>
            </div>
          </div>
        </div>

        {/* Math Input Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">
              Math Input
            </h3>
            {mathLiveLoaded && (
              <button
                onClick={showVirtualKeyboard}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors bg-white/5 text-gray-300 hover:bg-white/10"
              >
                Show Math Keyboard
              </button>
            )}
          </div>

          {/* MathLive Editor */}
          <div className="bg-white border border-gray-300 rounded-lg p-4 mb-4 min-h-[120px]">
            <div 
              ref={mathfieldRef}
              className="min-h-[80px] w-full focus:outline-none"
            />
            
            {/* Fallback textarea if MathLive fails */}
            {!mathLiveLoaded && (
              <textarea
                value={latexInput}
                onChange={handleManualLatexChange}
                className="w-full bg-transparent text-black text-lg min-h-[100px] resize-none focus:outline-none font-mono"
                placeholder="Enter your function in LaTeX (e.g., f(t) = t^2 or F(s) = 1/(s^2+1))"
              />
            )}
          </div>

          {/* LaTeX output display */}
          <div className="bg-slate-800/50 border border-white/10 rounded-lg p-3 mb-4">
            <h4 className="text-gray-400 text-sm font-medium mb-2">LaTeX Output:</h4>
            <code className="text-sm text-green-300 font-mono break-all">
              {latexInput || 'Enter math to see LaTeX output...'}
            </code>
          </div>

          {/* Math Templates */}
          <div className="bg-slate-800/50 border border-white/10 rounded-lg p-6">
            <h4 className="text-white font-semibold mb-4">Common Templates</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {mathTemplates.map((template, index) => (
                <button
                  key={index}
                  onClick={() => insertTemplate(template.latex)}
                  className="bg-white/5 hover:bg-white/10 text-white p-3 rounded-lg transition-colors border border-white/10 text-sm text-center"
                >
                  {template.name}
                </button>
              ))}
            </div>
          </div>
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

        {/* Action Buttons */}
     {/* Action Buttons */}
        <SolverActions
          isLoading={loading}
          isInputDisabled={!latexInput.trim()}
          onSolveVideo={() => solveProblem('video')}
          onSolveDirect={() => solveProblem('direct')}
          onSolvePdf={() => solveProblem('pdf')}
        />
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-gradient-to-br from-green-500/20 to-green-500/10 backdrop-blur-sm border border-green-500/30 rounded-2xl p-8 my-8">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">
            Solution Result
          </h3>
          
          {/* Main Result */}
          <div className="text-center mb-8">
            <p className="text-lg text-gray-300 mb-2">
              {operation === 'laplace' ? 'Laplace Transform:' : 'Inverse Laplace Transform:'}
            </p>
            
            {/* --- THIS IS THE FIX --- */}
            <div className="text-3xl p-4">
              <BlockMath math={result.result} />
            </div>
            {/* --- END FIX --- */}
          </div>

          {/* Steps */}
          {result.steps && result.steps.length > 0 && (
            <div className="max-w-4xl mx-auto">
              <h4 className="text-lg font-semibold text-white mb-4 text-center">
                Step-by-Step Solution
              </h4>
              <div className="space-y-4">
                {result.steps.map((step, index) => (
                  <div
                    key={index}
                    className="bg-slate-800/50 border border-white/10 rounded-lg p-4"
                  >
                    <div className="flex items-start gap-3">
                      <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0 mt-1">
                        {index + 1}
                      </span>
                      
                      {/* --- THIS IS THE FIX --- */}
                      {/* We use InlineMath here so it flows with the text */}
                      <div className="text-white text-lg pt-1">
                        <InlineMath math={step} />
                      </div>
                      {/* --- END FIX --- */}

                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* How It Works Section */}
      <div className="bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
        <h3 className="text-2xl font-bold text-white mb-6 text-center">
          How Laplace Transforms Work
        </h3>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl font-bold text-purple-400">∫</span>
            </div>
            <h4 className="text-white font-semibold mb-2">Definition</h4>
            <p className="text-gray-400 text-sm">
              Laplace transform converts time-domain functions to complex frequency-domain
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl font-bold text-blue-400">ℒ</span>
            </div>
            <h4 className="text-white font-semibold mb-2">Forward Transform</h4>
            <p className="text-gray-400 text-sm">
              ℒaplace
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-xl font-bold text-green-400">ℒ⁻¹</span>
            </div>
            <h4 className="text-white font-semibold mb-2">Inverse Transform</h4>
            <p className="text-gray-400 text-sm">
              Converts frequency-domain back to time-domain functions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}