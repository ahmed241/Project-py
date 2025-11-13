import { Loader2, Video, Zap, FileText } from 'lucide-react';

// Define the props the component will accept
type SolverActionsProps = {
  isLoading: boolean;
  isInputDisabled: boolean;
  onSolveVideo: () => void;
  onSolveDirect: () => void;
  onSolvePdf: () => void;
};

export default function SolverActions({
  isLoading,
  isInputDisabled,
  onSolveVideo,
  onSolveDirect,
  onSolvePdf,
}: SolverActionsProps) {
  
  return (
    <div className="grid md:grid-cols-3 gap-4">
      {/* Video Solution */}
      <button
        onClick={onSolveVideo} // Use the prop
        disabled={isLoading || isInputDisabled}
        className="group relative bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-xl p-6 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex flex-col items-center gap-3">
          {isLoading ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <Video className="w-8 h-8 group-hover:scale-110 transition-transform" />
          )}
          <div>
            <h4 className="font-semibold text-lg">Video Solution</h4>
            <p className="text-sm text-blue-100 mt-1">
              Animated step-by-step with Manim
            </p>
          </div>
        </div>
      </button>

      {/* Instant Solution */}
      <button
        onClick={onSolveDirect} // Use the prop
        disabled={isLoading || isInputDisabled}
        className="group relative bg-gradient-to-br from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white rounded-xl p-6 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex flex-col items-center gap-3">
          {isLoading ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <Zap className="w-8 h-8 group-hover:scale-110 transition-transform" />
          )}
          <div>
            <h4 className="font-semibold text-lg">Instant Solution</h4>
            <p className="text-sm text-green-100 mt-1">
              Get results immediately
            </p>
          </div>
        </div>
      </button>

      {/* PDF Solution */}
      <button
        onClick={onSolvePdf} // Use the prop
        disabled={isLoading || isInputDisabled}
        className="group relative bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white rounded-xl p-6 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex flex-col items-center gap-3">
          {isLoading ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <FileText className="w-8 h-8 group-hover:scale-110 transition-transform" />
          )}
          <div>
            <h4 className="font-semibold text-lg">PDF Report</h4>
            <p className="text-sm text-purple-100 mt-1">
              Detailed step-by-step document
            </p>
          </div>
        </div>
      </button>
    </div>
  );
}