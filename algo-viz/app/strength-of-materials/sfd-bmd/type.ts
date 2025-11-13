export type SupportType = "pin" | "roller" | "fixed" | "spring";

export interface Support {
  id: string;
  type: SupportType;
  position: number;
}

// --- NEW, MORE DETAILED LOAD TYPES ---

export type LoadType = "point" | "distributed" | "moment";

export interface PointLoad {
  id: string;
  type: "point";
  position: number;
  magnitude: number;
  angle?: number; // <-- FIX: Made angle optional
}

export interface MomentLoad {
  id: string;
  type: "moment";
  position: number;
  magnitude: number;
  rotation: "cw" | "ccw"
}

export interface DistributedLoad {
  id: string;
  type: "distributed";
  startPosition: number;
  endPosition: number;
  startMagnitude: number;
  endMagnitude: number; // If startMag === endMag, it's a UDL
}

// The main Load type is a union of all possible loads
export type Load = PointLoad | MomentLoad | DistributedLoad;