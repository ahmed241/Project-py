import Image from "next/image";
import { useState } from "react";
import { Support, SupportType } from "@/app/strength-of-materials/sfd-bmd/type";


interface SupportsFormProps {
  supports: Support[];
  setSupports: (supports: Support[]) => void;
  beamLength: number;
}

export default function SupportsForm({ supports, setSupports, beamLength }: SupportsFormProps) {
  const [selectedType, setSelectedType] = useState<SupportType>("pin");
  const [position, setPosition] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // --- UPDATED: Added a name property for the tooltip ---
  const icons = {
    pin: { src: "/icons/pin.svg", name: "Pin Support" },
    roller: { src: "/icons/roller.svg", name: "Roller Support" },
    fixed: { src: "/icons/fixed.svg", name: "Fixed Support" },
    spring: { src: "/icons/spring.svg", name: "Spring Support" },
  };
  // ---

  const handleTypeSelect = (type: SupportType) => {
    setSelectedType(type);
    setErrorMsg(null);
  };

  const handleAddSupport = () => {
    setErrorMsg(null);
    const pos = Number(position);

    if (isNaN(pos) || pos < 0 || pos > beamLength) {
      setErrorMsg(`Enter a valid position between 0 and ${beamLength} m.`);
      return;
    }

    const exists = supports.some((s) => Math.abs(s.position - pos) < 1e-3);
    if (exists) {
      setErrorMsg("A support already exists at this position.");
      return;
    }

    const newSupport: Support = {
      id: `support-${Date.now()}`,
      type: selectedType,
      position: pos,
    };

    setSupports([...supports, newSupport].sort((a, b) => a.position - b.position));
    setPosition("");
  };

  return (
    <div className="space-y-5">
      <h3 className="text-lg font-semibold text-white">2. Add Supports</h3>

      {/* Support Type Icons */}
      <div className="flex gap-3">
        {(Object.keys(icons) as SupportType[]).map((type) => (
          // --- FIX: 1. Wrap button in a relative 'group' div ---
          <div key={type} className="relative group">
            <button
              onClick={() => handleTypeSelect(type)}
              className={`w-16 h-16 flex items-center justify-center rounded-md border-2 transition-colors ${
                selectedType === type
                  ? "border-blue-500 bg-white"
                  : "border-gray-500 bg-gray-700/30 hover:bg-gray-700/60"
              }`}
            >
              <Image
                src={icons[type].src} // Use .src
                alt={type}
                width={40}
                height={40}
                className="object-contain"
              />
            </button>
            
            {/* --- FIX: 2. Add the tooltip span --- */}
            <span 
              className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1 
                         bg-gray-900 text-white text-sm rounded-md 
                         scale-0 group-hover:scale-100 transition-all 
                         duration-150 ease-in-out whitespace-nowrap z-10
                         pointer-events-none" // Prevents tooltip from blocking clicks
            >
              {icons[type].name} {/* Use .name */}
              {/* Arrow tip */}
              <svg 
                className="absolute left-1/2 -translate-x-1/2 top-full text-gray-900" 
                width="16" height="6" viewBox="0 0 16 6" fill="currentColor"
              >
                <path d="M0 0 L8 6 L16 0" />
              </svg>
            </span>
            {/* --- END FIX --- */}
          </div>
        ))}
      </div>

      {/* Position input */}
      <div className="flex gap-3 items-end">
        <div className="flex-1">
          <label className="block text-sm text-gray-300 mb-1">Position (m)</label>
          <input
            type="number"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-800 border border-gray-600 text-white"
            placeholder={`0 - ${beamLength}`}
          />
        </div>

        <button
          onClick={handleAddSupport}
          className="px-4 py-2 rounded-md bg-green-600 hover:bg-green-700 text-white"
        >
          Add
        </button>
      </div>

      {/* Error Message */}
      {errorMsg && (
        <p className="text-sm text-red-400 bg-red-900/20 border border-red-600/30 p-2 rounded-md">
          {errorMsg}
        </p>
      )}

      {/* Current supports list */}
      {supports.length > 0 && (
        <div className="pt-4 border-t border-gray-600">
          <h4 className="text-sm text-gray-300 mb-2">Current Supports</h4>
          <ul className="space-y-2">
            {supports.map((s) => (
              <li
                key={s.id}
                className="flex justify-between items-center bg-gray-800 rounded-md px-3 py-2"
              >
                <div className="flex items-center gap-3">
                  <Image
                    src={icons[s.type].src} // Use .src
                    alt={s.type}
                    width={28}
                    height={28}
                    className="object-contain"
                  />
                  <span className="text-gray-200 text-sm">
                    {s.type.toUpperCase()} — {s.position} m
                  </span>
                </div>
                <button
                  onClick={() => setSupports(supports.filter((sup) => sup.id !== s.id))}
                  className="text-sm text-red-400 hover:text-red-300"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}