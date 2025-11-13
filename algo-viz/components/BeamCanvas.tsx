import React, { useMemo } from "react";
import {
  Support,
  SupportType,
  Load,
  PointLoad,
  MomentLoad,
  DistributedLoad,
} from "@/app/strength-of-materials/sfd-bmd/type";

interface BeamCanvasProps {
  beamLength: number; // in meters ( > 0 )
  supports?: Support[];
  loads?: Load[]; // <-- 2. ADDED LOADS PROP
  width?: number; // px fallback width (optional)
  height?: number; // px fallback height (optional)
  showRuler?: boolean;
  padding?: number; // svg padding px
}

// --- 3. ADDED LOAD ICON PATHS ---
const supportIcons: Record<SupportType, string> = {
  pin: "/icons/pin.svg",
  roller: "/icons/roller.svg",
  fixed: "/icons/fixed.svg",
  spring: "/icons/spring.svg",
};

const loadIcons = {
  pointDown: "/icons/point-load-down.svg",
  pointUp: "/icons/point-load-up.svg",
  momentCCW: "/icons/moment-ccw.svg",
  momentCW: "/icons/moment-cw.svg",
  pointAngledDownRight: "/icons/point-load-down-right.svg",
  pointAngledDownLeft: "/icons/point-load-down-left.svg",
  pointAngledUpRight: "/icons/point-load-up-right.svg",
  pointAngledUpLeft: "/icons/point-load-up-left.svg",
};
// ---

export default function BeamCanvas({
  beamLength,
  supports = [],
  loads = [], // <-- Default loads to empty array
  width = 900,
  height = 300, // <-- Increased height to make room for loads
  showRuler = true,
  padding = 48, // <-- Increased padding
}: BeamCanvasProps) {
  // safety

  console.log('BeamCanvas - Loads:', loads);
  console.log('BeamCanvas - Supports:', supports);
  const safeLength = beamLength > 0 ? beamLength : 1;

  // virtual drawing area inside svg (width minus padding)
  const innerWidth = Math.max(100, width - padding * 2);
  const beamY = height / 2; // Center the beam vertically
  const beamHeight = 28;
  const beamRx = 6;

  // scale: meters -> px
  const scale = innerWidth / safeLength;

  const ticks = useMemo(() => {
    const meters = safeLength;
    const niceSteps = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100];
    let step = 1;
    for (let s of niceSteps) {
      const count = meters / s;
      if (count <= 12) {
        step = s;
        break;
      }
    }
    const arr: number[] = [];
    for (let m = 0; m <= meters + 1e-9; m += step) {
      arr.push(Number(m.toFixed(6)));
    }
    return { arr, step };
  }, [safeLength]);

  // utility: convert position meters -> svg x
  const xFromPos = (pos: number) => {
    return padding + Math.max(0, Math.min(pos, safeLength)) * scale;
  };

  return (
    <div className="w-full overflow-auto" style={{ maxWidth: "100%" }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height={height}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Beam drawing"
        className="rounded-md"
      >
        {/* background (using our dark theme colors) */}
        <rect x="0" y="0" width={width} height={height} rx="10" fill="#1f2937" />

        {/* beam (rounded rect) */}
        <g>
          <rect
            x={padding}
            y={beamY - beamHeight / 2}
            width={innerWidth}
            height={beamHeight}
            rx={beamRx}
            fill="#3B82F6"
            stroke="#9CA3AF"
            strokeOpacity={0.2}
          />
        </g>

        {/* --- 4. RENDER SUPPORTS (Updated Y positioning) --- */}
        <g className="supports">
          {supports &&
            supports.map((s, idx) => {
              const x = xFromPos(s.position);
              const iconSize = 36;
              const iconX = x - iconSize / 2;
              // Position support icon *below* the beam
              const iconY = beamY + beamHeight / 2 + 4;

              return (
                <g key={s.id ?? idx} className="support">
                  {/* icon (uses public folder path) */}
                  <image
                    href={supportIcons[s.type] ?? supportIcons["pin"]}
                    x={iconX}
                    y={iconY}
                    width={iconSize}
                    height={iconSize}
                    preserveAspectRatio="xMidYMid meet"
                  />

                  {/* position label */}
                  <text
                    x={x}
                    y={iconY + iconSize + 16}
                    fontSize={14}
                    textAnchor="middle"
                    fill="#9CA3AF"
                  >
                    {s.position} m
                  </text>
                </g>
              );
            })}
        </g>

        {/* --- 5. RENDER LOADS --- */}
        <g className="loads">
          {loads.map((load) => {
            // Use a switch to render the correct component based on load type
            switch (load.type) {
              case "point":
                return (
                  <RenderPointLoad
                    key={load.id}
                    load={load}
                    xFromPos={xFromPos}
                    beamY={beamY}
                    beamHeight={beamHeight}
                  />
                );
              case "moment":
                return (
                  <RenderMomentLoad
                    key={load.id}
                    load={load}
                    rotation={load.rotation}
                    xFromPos={xFromPos}
                    beamY={beamY}
                  />
                );
              case "distributed":
                return (
                  <RenderDistributedLoad
                    key={load.id}
                    load={load}
                    xFromPos={xFromPos}
                    beamY={beamY}
                    beamHeight={beamHeight}
                    scale={scale}
                  />
                );
              default:
                return null;
            }
          })}
        </g>
        {/* --- END LOADS --- */}

        {/* left & right end labels (Updated fill color) */}
        <g>
          <text
            x={padding}
            y={beamY - beamHeight / 2 - 12}
            fontSize={14}
            textAnchor="start"
            fill="#9CA3AF"
          >
            0 m
          </text>
          <text
            x={padding + innerWidth}
            y={beamY - beamHeight / 2 - 12}
            fontSize={14}
            textAnchor="end"
            fill="#9CA3AF"
          >
            {safeLength} m
          </text>
        </g>
      </svg>
    </div>
  );
}

// ===================================
// --- 6. NEW SUB-COMPONENTS ---
// ===================================

// --- Point Load Component ---
function RenderPointLoad({
  load,
  xFromPos,
  beamY,
  beamHeight,
}: {
  load: PointLoad;
  xFromPos: (pos: number) => number;
  beamY: number;
  beamHeight: number;
}) {
  const x = xFromPos(load.position);
  console.log('Rendering Point Load:', {
    position: load.position,
    magnitude: load.magnitude,
    angle: load.angle,
    x: x
  });
  const iconSize = 48;
  const magText = `${Math.abs(load.magnitude)} kN`;

  // --- NEW LOGIC FOR ANGLE ---
  // Default to 270 degrees (down) if angle isn't provided
  // or if magnitude is negative (for backward compatibility)
  const angle = load.angle ?? (load.magnitude < 0 ? 270 : 90);

  let iconHref: string;
  let iconY: number;
  let textY: number;
  let isAbove = true;

  // Normalize angle to 0-360 range
  const normAngle = ((angle % 360) + 360) % 360;

  if (normAngle > 180 && normAngle <= 360) {
    // --- DOWNWARD (or horizontal-right) ---
    // Includes 181-360 and 0
    isAbove = true;
    if (normAngle > 265 && normAngle < 275) { // Vertical Down
      iconHref = loadIcons.pointDown;
    } else if (normAngle > 180 && normAngle < 270) { // Down-Left
      iconHref = loadIcons.pointAngledDownLeft;
    } else { // Down-Right (includes 0/360)
      iconHref = loadIcons.pointAngledDownRight;
    }
  } else {
    // --- UPWARD (or horizontal-left) ---
    // Includes 1-180
    isAbove = false;
    if (normAngle > 85 && normAngle < 95) { // Vertical Up
      iconHref = loadIcons.pointUp;
    } else if (normAngle > 90 && normAngle <= 180) { // Up-Left (includes 180)
      iconHref = loadIcons.pointAngledUpLeft;
    } else { // Up-Right
      iconHref = loadIcons.pointAngledUpRight;
    }
  }

  // Set Y position based on direction
  if (isAbove) {
    // Sits on top of beam
    iconY = beamY - beamHeight / 2 - iconSize;
    textY = iconY - 8;
  } else {
    // Hangs below beam
    iconY = beamY + beamHeight / 2;
    textY = iconY + iconSize + 16;
  }
  // --- END NEW LOGIC ---

  return (
    <g className="point-load">
      <image
        href={iconHref}
        x={x - iconSize / 2}
        y={iconY}
        width={iconSize}
        height={iconSize}
      />
      <text x={x} y={textY} textAnchor="middle" fill="#E5E7EB" fontSize="14">
        {magText}
      </text>
    </g>
  );
}

// --- Moment Load Component ---
function RenderMomentLoad({
  load,
  rotation,
  xFromPos,
  beamY,
}: {
  load: MomentLoad;
  rotation : "cw" | "ccw"
  xFromPos: (pos: number) => number;
  beamY: number;
}) {
  const x = xFromPos(load.position);
  const isCCW = load.magnitude > 0; // Positive = CCW
  const iconSize = 36;

  const iconHref = isCCW ? loadIcons.momentCCW : loadIcons.momentCW;
  const iconY = beamY - iconSize / 2; // Center on the beam
  const textY = iconY - 8;
  const magText = `${Math.abs(load.magnitude)} kN-m`;

  return (
    <g className="moment-load">
      <image
        href={iconHref}
        x={x - iconSize / 2}
        y={iconY}
        width={iconSize}
        height={iconSize}
      />
      <text x={x} y={textY} textAnchor="middle" fill="#E5E7EB" fontSize="14">
        {magText}
      </text>
    </g>
  );
}

// --- Distributed Load Component (Placeholder) ---
function RenderDistributedLoad({
  load,
  xFromPos,
  beamY,
  beamHeight,
  scale,
}: {
  load: DistributedLoad;
  xFromPos: (pos: number) => number;
  beamY: number;
  beamHeight: number;
  scale: number;
}) {
  const x = xFromPos(load.startPosition);
  const loadWidth = (load.endPosition - load.startPosition) * scale;
  const isUDL = load.startMagnitude === load.endMagnitude;

  // This is just a placeholder box, you'll need to draw the
  // trapezoidal shape and arrows for a full implementation.
  const loadHeight = 30;
  const isDownward = load.startMagnitude < 0;
  const boxY = isDownward
    ? beamY - beamHeight / 2 - loadHeight - 5
    : beamY + beamHeight / 2 + 5;
  const magText = isUDL
    ? `${Math.abs(load.startMagnitude)} kN/m`
    : `${Math.abs(load.startMagnitude)} to ${Math.abs(load.endMagnitude)} kN/m`;

  return (
    <g className="distributed-load">
      <rect
        x={x}
        y={boxY}
        width={loadWidth}
        height={loadHeight}
        fill="#4B5563"
        opacity="0.5"
      />
      <text
        x={x + loadWidth / 2}
        y={boxY - 8}
        textAnchor="middle"
        fill="#9CA3AF"
        fontSize="14"
      >
        {magText} (Distributed)
      </text>
    </g>
  );
}