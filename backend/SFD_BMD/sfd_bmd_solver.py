from numpyencoder import NumpyEncoder
import numpy as np
from typing import List, Dict, Any, Tuple

# ---------- Utilities ----------
def ensure_float(x):
    return float(x) if x is not None else 0.0

# ---------- Beam element stiffness (Euler-Bernoulli) ----------
# Local element stiffness (4x4) for two-node beam element (v1, th1, v2, th2)
# k_e = (EI / L^3) * [ [12, 6L, -12, 6L],
#                      [6L, 4L^2, -6L, 2L^2],
#                      [-12, -6L, 12, -6L],
#                      [6L, 2L^2, -6L, 4L^2] ]
def element_stiffness(EI: float, L: float) -> np.ndarray:
    L2 = L * L
    L3 = L2 * L
    k = (EI / L3) * np.array([
        [12.0, 6.0 * L, -12.0, 6.0 * L],
        [6.0 * L, 4.0 * L2, -6.0 * L, 2.0 * L2],
        [-12.0, -6.0 * L, 12.0, -6.0 * L],
        [6.0 * L, 2.0 * L2, -6.0 * L, 4.0 * L2]
    ], dtype=float)
    return k

# ---------- Equivalent nodal loads ----------
# Point load at node (vertical): simply add to the corresponding DOF (v DOF)
# Point moment at node: added to rotational DOF
# UDL over an element [startNode--endNode] with intensity q (N/m) -> equivalent nodal loads:
# Fe = q * L / 2 * [1, L/6, 1, -L/6] (vertical, moment signs: check sign conv)
def udl_equivalent(q: float, L: float) -> np.ndarray:
    # q positive = downward (consistent with magnitude sign used)
    # returns array [Fy1, M1, Fy2, M2]
    # For a uniformly distributed load acting downward (positive q), equivalent nodal values:
    # Fy1 = qL/2, M1 = qL^2/12 (signs depend on sign convention). We'll use
    # M nodal contribution positive as per internal sign convention; calling code must be consistent.
    fy = q * L / 2.0
    m = q * L * L / 12.0
    return np.array([fy, m, fy, -m], dtype=float)

# ---------- Assembly ----------
def assemble_global(nodes: List[float], EI: float) -> Tuple[np.ndarray, int]:
    n_nodes = len(nodes)
    ndof = 2 * n_nodes
    K = np.zeros((ndof, ndof), dtype=float)

    # elements between consecutive nodes i--i+1
    for i in range(n_nodes - 1):
        L = nodes[i+1] - nodes[i]
        if L <= 0:
            raise ValueError("Node coordinates must be strictly increasing.")
        ke = element_stiffness(EI, L)
        # global DOF indices for nodes i and i+1
        gd = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
        # assemble
        for a in range(4):
            for b in range(4):
                K[gd[a], gd[b]] += ke[a, b]
    return K, ndof

# ---------- Apply loads (build global F) ----------
def build_global_load_vector(nodes: List[float], loads: List[Dict[str, Any]]) -> np.ndarray:
    n_nodes = len(nodes)
    F = np.zeros((2 * n_nodes,), dtype=float)  # [v0, th0, v1, th1, ...] but we'll use v indices 0,2,4...
    # Map position -> node index (nodes list must include all load positions)
    pos_to_index = {pos: idx for idx, pos in enumerate(nodes)}

    for ld in loads:
        typ = ld.get("type")
        if typ == "point":
            pos = float(ld["position"])
            mag = float(ld["magnitude"])  # positive up or down depending on convention (we'll take +ve upward)
            # find node
            if pos not in pos_to_index:
                # shouldn't happen if nodes include loads
                idx = min(range(len(nodes)), key=lambda i: abs(nodes[i] - pos))
            else:
                idx = pos_to_index[pos]
            # vertical DOF index:
            dof_v = 2 * idx
            dof_m = 2 * idx + 1
            # Convention: we treat positive magnitude as upward. In our FEM sign convention
            # choose positive upward -> so add (+) to F
            F[dof_v] += mag
        elif typ == "moment":
            pos = float(ld["position"])
            mag = float(ld["magnitude"])  # kN·m or N·m (units must match EI)
            if pos not in pos_to_index:
                idx = min(range(len(nodes)), key=lambda i: abs(nodes[i] - pos))
            else:
                idx = pos_to_index[pos]
            dof_m = 2 * idx + 1
            F[dof_m] += mag
        elif typ == "udl":
            # UDL defined by start, end, intensity (q) in N/m (positive downward by our earlier convention).
            a = float(ld["start"])
            b = float(ld["end"])
            q = float(ld["intensity"])
            # find element that exactly matches [a,b] (we constructed nodes to include start/end)
            # iterate elements and add equivalent nodal loads
            for i in range(len(nodes) - 1):
                x0, x1 = nodes[i], nodes[i+1]
                if abs(x0 - a) < 1e-9 and abs(x1 - b) < 1e-9:
                    L = x1 - x0
                    Fe = udl_equivalent(q, L)
                    gd = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
                    for k in range(4):
                        F[gd[k]] += Fe[k]
                    break
            else:
                # if no exact matching element, try accumulating across multiple elements overlapping [a,b]
                # simpler: loop elements that lie within [a,b] and accumulate q*Le on nodes (approx)
                for i in range(len(nodes) - 1):
                    x0, x1 = nodes[i], nodes[i+1]
                    L = x1 - x0
                    if x1 <= a + 1e-9 or x0 >= b - 1e-9:
                        continue
                    # overlap length
                    left = max(x0, a)
                    right = min(x1, b)
                    Le = right - left
                    if Le <= 0: 
                        continue
                    # scale equivalent nodal loads for this partial element
                    Fe = udl_equivalent(q, Le) * (Le / L)  # approximate
                    gd = [2*i, 2*i+1, 2*(i+1), 2*(i+1)+1]
                    for k in range(4):
                        F[gd[k]] += Fe[k]
        else:
            # ignore unknown load types for now
            pass

    return F

# ---------- Apply boundary conditions & solve ----------
def apply_supports_and_solve(K_full: np.ndarray, F_full: np.ndarray, nodes: List[float], supports: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
    ndof = K_full.shape[0]
    u_full = np.zeros((ndof,), dtype=float)

    # determine constrained DOFs
    constrained = np.zeros((ndof,), dtype=bool)

    # map support positions to node indices
    pos_to_index = {pos: idx for idx, pos in enumerate(nodes)}
    for s in supports:
        pos = float(s["position"])
        typ = s["type"]
        # find closest node
        if pos not in pos_to_index:
            idx = min(range(len(nodes)), key=lambda i: abs(nodes[i] - pos))
        else:
            idx = pos_to_index[pos]
        v_dof = 2 * idx
        th_dof = 2 * idx + 1
        if typ == "pin":
            constrained[v_dof] = True
            # rotation free
        elif typ == "roller":
            constrained[v_dof] = True
        elif typ == "fixed":
            constrained[v_dof] = True
            constrained[th_dof] = True
        elif typ == "spring":
            # spring support: for simplicity treat as vertical spring with stiffness k_s (user must provide)
            k_s = float(s.get("stiffness", 1e6))
            # add spring stiffness to diagonal of K_full at v_dof
            K_full[v_dof, v_dof] += k_s
            constrained[v_dof] = False
        else:
            # default: pin-like
            constrained[v_dof] = True

    free_dofs = [i for i in range(ndof) if not constrained[i]]
    fixed_dofs = [i for i in range(ndof) if constrained[i]]

    # Partition matrices
    Kff = K_full[np.ix_(free_dofs, free_dofs)]
    Kfc = K_full[np.ix_(free_dofs, fixed_dofs)]
    Kcf = K_full[np.ix_(fixed_dofs, free_dofs)]
    Kcc = K_full[np.ix_(fixed_dofs, fixed_dofs)]

    Ff = F_full[free_dofs]
    Fc = F_full[fixed_dofs]

    # Solve Kff * uf = Ff - Kfc * uc  (uc = 0 for prescribed zero displacements)
    if Kff.size == 0:
        uf = np.array([], dtype=float)
    else:
        uf = np.linalg.solve(Kff, Ff)

    # Build full displacement vector
    u_full = np.zeros((ndof,), dtype=float)
    for i, dof in enumerate(free_dofs):
        u_full[dof] = uf[i]
    for dof in fixed_dofs:
        u_full[dof] = 0.0

    # Compute reactions: R = K_full * u_full - F_full
    R_full = K_full.dot(u_full) - F_full
    return u_full, R_full

def element_internal_forces(nodes, u, E, I):
    """Return list of element end forces (shear, moment) for plotting SFD/BMD."""
    EI = E * I
    n_nodes = len(nodes)
    results = []
    for i in range(n_nodes - 1):
        L = nodes[i+1] - nodes[i]
        ue = u[2*i:2*i+4]  # [v1, th1, v2, th2]
        ke = element_stiffness(EI, L)
        fe_int = ke.dot(ue)  # element end forces (shear/moment)
        results.append({
            "x1": nodes[i],
            "x2": nodes[i+1],
            "V1": fe_int[0],
            "M1": fe_int[1],
            "V2": -fe_int[2],  # opposite sign convention for far end
            "M2": fe_int[3]
        })
    return results

# ---------- Top-level solver ----------
def solve_beam_by_stiffness(beam_length: float,
                            supports: List[Dict[str, Any]],
                            loads: List[Dict[str, Any]],
                            E: float = 210e9,
                            I: float = 8.333e-6) -> Dict[str, Any]:
    # 1) Build nodes: include 0 and beam_length, plus all support positions and load positions (unique sorted)
    pts = {0.0, float(beam_length)}
    for s in supports:
        pts.add(float(s["position"]))
    for ld in loads:
        if ld["type"] == "udl":
            pts.add(float(ld["start"]))
            pts.add(float(ld["end"]))
        else:
            pts.add(float(ld["position"]))
    nodes = sorted(list(pts))

    EI = E * I

    # 2) Assemble global stiffness
    K, ndof = assemble_global(nodes, EI)

    # 3) Build global load vector
    F = build_global_load_vector(nodes, loads)

    # 4) Apply BCs and solve
    u, R = apply_supports_and_solve(K, F, nodes, supports)

    # 5) extract reactions at supports
    reactions = []
    pos_to_index = {pos: idx for idx, pos in enumerate(nodes)}
    for s in supports:
        pos = float(s["position"])
        if pos not in pos_to_index:
            idx = min(range(len(nodes)), key=lambda i: abs(nodes[i] - pos))
        else:
            idx = pos_to_index[pos]
        v_dof = 2 * idx
        th_dof = 2 * idx + 1
        reactions.append({
            "support_id": s.get("id"),
            "position": pos,
            "type": s.get("type"),
            "vertical_reaction": R[v_dof],
            "moment_reaction": R[th_dof] if s.get("type") == "fixed" else 0.0
        })

    # 6) Return some state useful for SFD/BMD construction: nodes, displacements, reactions
    result = {
        "nodes": nodes,
        "displacements": u.reshape(-1, 2).tolist(),  # [[v0, th0], [v1, th1], ...]
        "reactions": reactions,
        "K": K,
        "F": F.tolist(),
        "R_full": R.tolist()
    }
    ele_forces = element_internal_forces(result["nodes"], np.array(result["displacements"]).flatten(), E, I)
    return result, ele_forces

# ---------- Example CLI run  ----------
if __name__ == "__main__":
    # example using your JSON
    data = {
      "beamLength": 10.0,
      "supports": [
        {"id": "support-1762958934939", "type": "pin", "position": 0},
        {"id": "support-1762958934939", "type": "pin", "position": 7.5},
        {"id": "support-1762958939645", "type": "pin", "position": 10}
      ],
      "loads": [
        {"id": "load-1762958817467", "type": "moment", "position": 5, "magnitude": -1}
      ]
    }
    res, forces = solve_beam_by_stiffness(
        beam_length=data["beamLength"],
        supports=data["supports"],
        loads=data["loads"],
        E=210e9,
        I=8.333e-6
    )
    import json
    print(json.dumps(res, indent=2, cls=NumpyEncoder))
    print(json.dumps(forces, indent=2, cls=NumpyEncoder))
