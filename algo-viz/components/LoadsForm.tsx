import { useState } from "react";
import { MoveUp, RotateCcw, RotateCw, Trash2, MoveDownLeft, MoveDown } from "lucide-react";
// Import your shared types
import { Load, LoadType, PointLoad, MomentLoad, DistributedLoad } from "@/app/strength-of-materials/sfd-bmd/type";

interface LoadsFormProps {
    loads: Load[];
    setLoads: (loads: Load[]) => void;
    beamLength: number;
}

// --- Main Component ---
export default function LoadsForm({ loads, setLoads, beamLength }: LoadsFormProps) {
    const [selectedType, setSelectedType] = useState<LoadType>("point");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const onAddLoad = (newLoad: Load) => {
        setLoads([...loads, newLoad].sort((a, b) => {
            const posA = 'position' in a ? a.position : a.startPosition;
            const posB = 'position' in b ? b.position : b.startPosition;
            return posA - posB;
        }));
    };

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-semibold text-white mb-4">3. Add Loads</h3>
                <p className="text-sm text-gray-400 mb-4">
                    Add point loads, distributed loads (UDL/UVL), or moments.
                </p>
            </div>

            {/* Load Type Buttons */}
            <div className="grid grid-cols-3 gap-3">
                <LoadTypeButton
                    label="Point Load"
                    type="point"
                    selectedType={selectedType}
                    onClick={setSelectedType}
                />
                <LoadTypeButton
                    label="Moment"
                    type="moment"
                    selectedType={selectedType}
                    onClick={setSelectedType}
                />
                <LoadTypeButton
                    label="Distributed"
                    type="distributed"
                    selectedType={selectedType}
                    onClick={setSelectedType}
                />
            </div>

            {/* --- Conditional Input Forms --- */}
            <div className="border-t border-white/10 pt-6">
                {selectedType === "point" && (
                    <PointLoadForm beamLength={beamLength} onAdd={onAddLoad} setError={setErrorMsg} />
                )}
                {selectedType === "moment" && (
                    <MomentForm beamLength={beamLength} onAdd={onAddLoad} setError={setErrorMsg} />
                )}
                {selectedType === "distributed" && (
                    <DistributedLoadForm beamLength={beamLength} onAdd={onAddLoad} setError={setErrorMsg} />
                )}
            </div>

            {/* Error Message */}
            {errorMsg && (
                <p className="text-sm text-red-400 bg-red-900/20 border border-red-600/30 p-2 rounded-md">
                    {errorMsg}
                </p>
            )}

            {/* Current Loads List */}
            {loads.length > 0 && (
                <div className="pt-4 border-t border-gray-600">
                    <h4 className="text-sm text-gray-300 mb-2">Current Loads</h4>
                    <ul className="space-y-2">
                        {loads.map((load) => (
                            <li
                                key={load.id}
                                className="flex justify-between items-center bg-gray-800 rounded-md px-3 py-2"
                            >
                                <span className="text-gray-200 text-sm">
                                    {/* Updated text for PointLoad to show angle */}
                                    {load.type === 'point' && `Point: ${load.magnitude} kN at ${load.position}m (${load.angle ?? (load.magnitude < 0 ? 270 : 90)}°) `}
                                    {load.type === 'moment' && `Moment: ${load.magnitude} kN-m at ${load.position}m`}
                                    {load.type === 'distributed' && `Dist.: ${load.startMagnitude} to ${load.endMagnitude} kN/m (${load.startPosition}m to ${load.endPosition}m)`}
                                </span>
                                <button
                                    onClick={() => setLoads(loads.filter((l) => l.id !== load.id))}
                                    className="text-red-400 hover:text-red-300"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// --- Sub-Component for Load Type Button ---
function LoadTypeButton({ label, type, selectedType, onClick }: {
    label: string;
    type: LoadType;
    selectedType: LoadType;
    onClick: (type: LoadType) => void;
}) {
    return (
        <button
            onClick={() => onClick(type)}
            className={`py-3 px-2 rounded-lg border-2 transition-all ${selectedType === type
                    ? "bg-blue-600/30 border-blue-500 text-white"
                    : "bg-gray-800/50 border-gray-600 text-gray-300 hover:bg-gray-700/50"
                }`}
        >
            {label}
        </button>
    );
}

// --- (CORRECTED) Sub-Component for Point Load Form ---
function PointLoadForm({ beamLength, onAdd, setError }: {
    beamLength: number;
    onAdd: (load: PointLoad) => void;
    setError: (msg: string | null) => void;
}) {
    const [position, setPosition] = useState("");
    const [magnitude, setMagnitude] = useState("10"); // Always positive
    const [direction, setDirection] = useState<"down" | "up" | "angled">("down");
    const [angle, setAngle] = useState("45"); // Angle (only for 'angled' direction)

    const handleAdd = () => {
        setError(null);
        const pos = Number(position);
        const mag = Number(magnitude); // This is the absolute magnitude
        const ang = Number(angle);

        // --- Validation ---
        if (isNaN(pos) || pos < 0 || pos > beamLength) {
            setError(`Position must be between 0 and ${beamLength} m.`);
            return;
        }
        if (isNaN(mag) || mag <= 0) {
            setError("Magnitude must be a positive number.");
            return;
        }
        if (direction === "angled" && isNaN(ang)) {
            setError("Enter a valid angle for the angled load.");
            return;
        }

        // --- Create Payload (FIXED) ---
        let payload: PointLoad;

        if (direction === "down") {
            payload = {
                id: `load-${Date.now()}`,
                type: "point",
                position: pos,
                magnitude: -mag, // Negative for downward
                angle: 270,      // **THIS WAS MISSING**
            };
        } else if (direction === "up") {
            payload = {
                id: `load-${Date.now()}`,
                type: "point",
                position: pos,
                magnitude: mag, // Positive for upward
                angle: 90,     // **THIS WAS MISSING**
            };
        } else { // 'angled'
            payload = {
                id: `load-${Date.now()}`,
                type: "point",
                position: pos,
                magnitude: mag, // Magnitude is just its size
                angle: ang,      // Use the user's angle
            };
        }

        onAdd(payload); // This is now a valid PointLoad object

        // Reset form
        setPosition("");
        setMagnitude("10");
        // We can keep the direction and angle for the next input
    };

    return (
        <div className="space-y-4">
            <p className="text-sm text-gray-400">Add a concentrated force. Magnitude is always positive; use buttons to set direction.</p>

            {/* direction buttons */}
            <div className="flex gap-3">
                <DirButton icon={<MoveDown />} label="Down" active={direction === "down"} onClick={() => setDirection("down")} />
                <DirButton icon={<MoveUp />} label="Up" active={direction === "up"} onClick={() => setDirection("up")} />
                <DirButton icon={<MoveDownLeft />} label="Angled" active={direction === "angled"} onClick={() => setDirection("angled")} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                <FormInput
                    label="Position (m)"
                    value={position}
                    onChange={setPosition}
                    placeholder={`0 - ${beamLength}`}
                    max={beamLength}
                    min={0}
                />
                <FormInput
                    label="Magnitude (kN)"
                    value={magnitude}
                    onChange={setMagnitude}
                    placeholder="10"
                    min = {0.01}
                />

                {/* Angle input only visible for angled loads */}
                {direction === "angled" ? (
                    <FormInput
                        label="Angle (deg)"
                        value={angle}
                        onChange={setAngle}
                        placeholder="45"
                    />
                ) : (
                    <div /> // Empty div to keep grid layout
                )}
            </div>
            
            <button onClick={handleAdd} className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                Add Point Load
            </button>
        </div>
    );
}

// --- Sub-Component for Moment Form ---
function MomentForm({ beamLength, onAdd, setError }: {
    beamLength: number;
    onAdd: (load: MomentLoad) => void;
    setError: (msg: string | null) => void;
}) {
    const [position, setPosition] = useState("");
    const [magnitude, setMagnitude] = useState("10"); // Default 10 kNm
    const [rotation, setRotation] = useState<"ccw" | "cw">("cw");

    const handleAdd = () => {
        setError(null);
        const pos = Number(position);
        const mag = Number(magnitude);
        const rot = rotation;

        if (isNaN(pos) || pos < 0 || pos > beamLength) {
            setError(`Position must be between 0 and ${beamLength} m.`);
            return;
        }
        if (isNaN(mag) || mag === 0) {
            setError("Magnitude cannot be zero.");
            return;
        }

        // Ensure magnitude sign matches rotation: CCW => positive, CW => negative
        const signedMag = rot === "cw" ? -Math.abs(mag) : Math.abs(mag);

        const payload: MomentLoad = {
            id: `load-${Date.now()}`,
            type: "moment",
            position: pos,
            magnitude: signedMag,
            rotation: rot,
        };

        onAdd(payload);
        setPosition("");
        setMagnitude("10");
    };

    return (
        <div className="space-y-4">
            <p className="text-sm text-gray-400">Add a moment. Selecting CW will create a clockwise moment (negative magnitude) and CCW a counter-clockwise moment (positive magnitude).</p>
            <div className="flex gap-2">
                <DirButton
                    icon={<RotateCcw />}
                    label="CCW" active={rotation === "ccw"}
                    onClick={() => setRotation("ccw")}
                />
                <DirButton
                    icon={<RotateCw />}
                    label="CW"
                    active={rotation === "cw"}
                    onClick={() => setRotation("cw")} />
            </div>

            <FormInput label="Position (m)" value={position} onChange={setPosition} placeholder={`0 - ${beamLength}`} />
            <FormInput label="Magnitude (kN-m)" value={magnitude} onChange={setMagnitude} placeholder="10" />
            <button onClick={handleAdd} className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                Add Moment
            </button>
        </div>
    );
}

// --- Sub-Component for Distributed Load Form (UDL/UVL) ---
function DistributedLoadForm({ beamLength, onAdd, setError }: {
    beamLength: number;
    onAdd: (load: DistributedLoad) => void;
    setError: (msg: string | null) => void;
}) {
    const [startPos, setStartPos] = useState("");
    const [endPos, setEndPos] = useState("");
    const [startMag, setStartMag] = useState("-10");
    const [endMag, setEndMag] = useState("-10"); // Default UDL

    const handleAdd = () => {
        setError(null);
        const startP = Number(startPos);
        const endP = Number(endPos);
        const startM = Number(startMag);
        const endM = Number(endMag);

        if (isNaN(startP) || startP < 0 || startP > beamLength) {
            setError(`Start Position must be between 0 and ${beamLength} m.`);
            return;
        }
        if (isNaN(endP) || endP < 0 || endP > beamLength) {
            setError(`End Position must be between 0 and ${beamLength} m.`);
            return;
        }
        if (startP >= endP) {
            setError("End Position must be greater than Start Position.");
            return;
        }
        if (isNaN(startM)) {
            setError("Start Magnitude must be a number.");
            return;
        }
        if (isNaN(endM)) {
            setError("End Magnitude must be a number.");
            return;
        }

        onAdd({
            id: `load-${Date.now()}`,
            type: "distributed",
            startPosition: startP,
            endPosition: endP,
            startMagnitude: startM,
            endMagnitude: endM,
        });
        setStartPos("");
        setEndPos("");
        setStartMag("-10");
        setEndMag("-10");
    };

    return (
        <div className="space-y-4">
            <p className="text-sm text-gray-400">Add a distributed load (UDL or UVL). For a UDL, make Start and End Magnitude the same.</p>
            <div className="grid grid-cols-2 gap-4">
                <FormInput label="Start Position (m)" value={startPos} onChange={setStartPos} placeholder="0" />
                <FormInput label="End Position (m)" value={endPos} onChange={setEndPos} placeholder={`${beamLength}`} />
            </div>
            <div className="grid grid-cols-2 gap-4">
                <FormInput label="Start Magnitude (kN/m)" value={startMag} onChange={setStartMag} placeholder="-10" />
                <FormInput label="End Magnitude (kN/m)" value={endMag} onChange={setEndMag} placeholder="-10" />
            </div>
            <button onClick={handleAdd} className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                Add Distributed Load
            </button>
        </div>
    );
}

// --- Reusable Form Input Component ---
function FormInput({ label, value, onChange, placeholder, type = "number", min, max }: {
    label: string;
    value: string;
    onChange: (val: string) => void;
    placeholder?: string;
    type?: string;
    min?: number;
    max?: number;
}) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{label}</label>
            <input
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                min={min}
                max={max}
                step="0.1"
                className="w-full px-3 py-2 rounded-md bg-gray-800 border border-gray-600 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
        </div>
    );
}

// --- Reusable Direction Button ---
function DirButton({ icon, label, active, onClick }: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-lg border-2 transition-all ${
        active
          ? "bg-blue-600/30 border-blue-500 text-white"
          : "bg-gray-800/50 border-gray-600 text-gray-300 hover:bg-gray-700/50"
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}