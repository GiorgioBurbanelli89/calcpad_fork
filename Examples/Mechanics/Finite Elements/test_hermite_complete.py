"""
Complete Hermite Element Test (2x3 mesh)
Computes element matrices and solves the full system
"""
import numpy as np
from scipy.integrate import dblquad
from scipy.linalg import solve

# Parameters matching Calcpad
a = 6.0  # m
b = 4.0  # m
t = 0.1  # m
q = 10.0  # kN/m2
E = 35000e3  # kN/m2 (35000 MPa)
nu = 0.15

n_a = 2  # elements in x
n_b = 3  # elements in y
n_dof = 16  # DOF per element (Hermite)

a_e = a / n_a  # 3.0 m
b_e = b / n_b  # 1.333... m

print("="*60)
print("HERMITE ELEMENT - COMPLETE TEST (2x3)")
print("="*60)
print(f"Slab: {a}m x {b}m, t={t}m")
print(f"Load: q={q} kN/m2")
print(f"Material: E={E/1e3} MPa, nu={nu}")
print(f"Mesh: {n_a} x {n_b} elements")
print(f"Element size: {a_e:.4f} x {b_e:.4f} m")

# Number of joints
n_j = (n_a + 1) * (n_b + 1)  # 3 * 4 = 12 joints
print(f"Joints: {n_j}")

# Joint coordinates (same order as Calcpad)
x_j = np.zeros(n_j)
y_j = np.zeros(n_j)
j = 0
for i_x in range(n_a + 1):
    for i_y in range(n_b + 1):
        x_j[j] = i_x * a_e
        y_j[j] = i_y * b_e
        j += 1

print("\nJoint coordinates:")
print("j    x      y")
for j in range(n_j):
    print(f"{j+1:2d}  {x_j[j]:5.2f}  {y_j[j]:5.2f}")

# Element connectivity (1-based like Calcpad)
n_e = n_a * n_b  # 6 elements
e_j = np.zeros((n_e, 4), dtype=int)
for i_a in range(n_a):
    for i_b in range(n_b):
        e = i_b + n_b * i_a
        j_base = e + i_a
        e_j[e, 0] = j_base + 1      # node 1
        e_j[e, 1] = j_base + n_b + 2  # node 2
        e_j[e, 2] = j_base + n_b + 3  # node 3
        e_j[e, 3] = j_base + 2      # node 4

print("\nElement connectivity (1-based):")
print("e   j1  j2  j3  j4")
for e in range(n_e):
    print(f"{e+1:2d}  {e_j[e,0]:2d}  {e_j[e,1]:2d}  {e_j[e,2]:2d}  {e_j[e,3]:2d}")

# Supported joints (all boundary joints)
s_j = []
for i in range(n_a + 1):
    s_j.append((n_b + 1) * i + 1)  # y=0 edge
    s_j.append((n_b + 1) * (i + 1))  # y=b edge
for i in range(1, n_b):
    s_j.append(i + 1)  # x=0 edge (excluding corners)
    s_j.append(n_a * (n_b + 1) + i + 1)  # x=a edge (excluding corners)

s_j = sorted(set(s_j))
print(f"\nSupported joints (all edges): {s_j}")
print(f"Number of supported joints: {len(s_j)}")

# Constitutive matrix D
D = E * t**3 / (12 * (1 - nu**2)) * np.array([
    [1, nu, 0],
    [nu, 1, 0],
    [0, 0, (1-nu)/2]
])

print(f"\nConstitutive matrix D:")
print(f"  D[0,0] = {D[0,0]:.6f}")
print(f"  D[0,1] = {D[0,1]:.6f}")
print(f"  D[2,2] = {D[2,2]:.6f}")

# Hermite shape functions
def Phi_1a(xi): return 1 - xi**2 * (3 - 2*xi)
def Phi_2a(xi): return xi * a_e * (1 - xi*(2 - xi))
def Phi_3a(xi): return xi**2 * (3 - 2*xi)
def Phi_4a(xi): return xi**2 * a_e * (-1 + xi)

def Phi_1b(eta): return 1 - eta**2 * (3 - 2*eta)
def Phi_2b(eta): return eta * b_e * (1 - eta*(2 - eta))
def Phi_3b(eta): return eta**2 * (3 - 2*eta)
def Phi_4b(eta): return eta**2 * b_e * (-1 + eta)

# Second derivatives
def ddPhi_1a(xi): return -(6/a_e**2) * (1 - 2*xi)
def ddPhi_2a(xi): return -(2/a_e) * (2 - 3*xi)
def ddPhi_3a(xi): return (6/a_e**2) * (1 - 2*xi)
def ddPhi_4a(xi): return -(2/a_e) * (1 - 3*xi)

def ddPhi_1b(eta): return -(6/b_e**2) * (1 - 2*eta)
def ddPhi_2b(eta): return -(2/b_e) * (2 - 3*eta)
def ddPhi_3b(eta): return (6/b_e**2) * (1 - 2*eta)
def ddPhi_4b(eta): return -(2/b_e) * (1 - 3*eta)

# First derivatives
def dPhi_1a(xi): return -6 * (xi/a_e) * (1 - xi)
def dPhi_2a(xi): return 1 - xi*(4 - 3*xi)
def dPhi_3a(xi): return 6 * (xi/a_e) * (1 - xi)
def dPhi_4a(xi): return -xi * (2 - 3*xi)

def dPhi_1b(eta): return -6 * (eta/b_e) * (1 - eta)
def dPhi_2b(eta): return 1 - eta*(4 - 3*eta)
def dPhi_3b(eta): return 6 * (eta/b_e) * (1 - eta)
def dPhi_4b(eta): return -eta * (2 - 3*eta)

# Shape functions for displacement w
# DOF order: [w1, tx1, ty1, psi1, w2, tx2, ty2, psi2, w3, tx3, ty3, psi3, w4, tx4, ty4, psi4]
def get_N(i, xi, eta):
    """Get shape function N_i for w interpolation"""
    if i == 0: return Phi_1a(xi) * Phi_1b(eta)  # w1
    if i == 1: return Phi_2a(xi) * Phi_1b(eta)  # tx1
    if i == 2: return Phi_1a(xi) * Phi_2b(eta)  # ty1
    if i == 3: return Phi_2a(xi) * Phi_2b(eta)  # psi1
    if i == 4: return Phi_3a(xi) * Phi_1b(eta)  # w2
    if i == 5: return Phi_4a(xi) * Phi_1b(eta)  # tx2
    if i == 6: return Phi_3a(xi) * Phi_2b(eta)  # ty2
    if i == 7: return Phi_4a(xi) * Phi_2b(eta)  # psi2
    if i == 8: return Phi_3a(xi) * Phi_3b(eta)  # w3
    if i == 9: return Phi_4a(xi) * Phi_3b(eta)  # tx3
    if i == 10: return Phi_3a(xi) * Phi_4b(eta)  # ty3
    if i == 11: return Phi_4a(xi) * Phi_4b(eta)  # psi3
    if i == 12: return Phi_1a(xi) * Phi_3b(eta)  # w4
    if i == 13: return Phi_2a(xi) * Phi_3b(eta)  # tx4
    if i == 14: return Phi_1a(xi) * Phi_4b(eta)  # ty4
    if i == 15: return Phi_2a(xi) * Phi_4b(eta)  # psi4

# B matrix components
def get_B(xi, eta):
    """Full B matrix at point (xi, eta)"""
    B = np.zeros((3, 16))

    ddPhi_a = [ddPhi_1a, ddPhi_2a, ddPhi_1a, ddPhi_2a,
               ddPhi_3a, ddPhi_4a, ddPhi_3a, ddPhi_4a,
               ddPhi_3a, ddPhi_4a, ddPhi_3a, ddPhi_4a,
               ddPhi_1a, ddPhi_2a, ddPhi_1a, ddPhi_2a]
    Phi_b_list = [Phi_1b, Phi_1b, Phi_2b, Phi_2b,
                  Phi_1b, Phi_1b, Phi_2b, Phi_2b,
                  Phi_3b, Phi_3b, Phi_4b, Phi_4b,
                  Phi_3b, Phi_3b, Phi_4b, Phi_4b]

    Phi_a_list = [Phi_1a, Phi_2a, Phi_1a, Phi_2a,
                  Phi_3a, Phi_4a, Phi_3a, Phi_4a,
                  Phi_3a, Phi_4a, Phi_3a, Phi_4a,
                  Phi_1a, Phi_2a, Phi_1a, Phi_2a]
    ddPhi_b = [ddPhi_1b, ddPhi_1b, ddPhi_2b, ddPhi_2b,
               ddPhi_1b, ddPhi_1b, ddPhi_2b, ddPhi_2b,
               ddPhi_3b, ddPhi_3b, ddPhi_4b, ddPhi_4b,
               ddPhi_3b, ddPhi_3b, ddPhi_4b, ddPhi_4b]

    dPhi_a = [dPhi_1a, dPhi_2a, dPhi_1a, dPhi_2a,
              dPhi_3a, dPhi_4a, dPhi_3a, dPhi_4a,
              dPhi_3a, dPhi_4a, dPhi_3a, dPhi_4a,
              dPhi_1a, dPhi_2a, dPhi_1a, dPhi_2a]
    dPhi_b = [dPhi_1b, dPhi_1b, dPhi_2b, dPhi_2b,
              dPhi_1b, dPhi_1b, dPhi_2b, dPhi_2b,
              dPhi_3b, dPhi_3b, dPhi_4b, dPhi_4b,
              dPhi_3b, dPhi_3b, dPhi_4b, dPhi_4b]

    for j in range(16):
        B[0, j] = ddPhi_a[j](xi) * Phi_b_list[j](eta)  # d2w/dx2
        B[1, j] = Phi_a_list[j](xi) * ddPhi_b[j](eta)  # d2w/dy2
        B[2, j] = 2 * dPhi_a[j](xi) * dPhi_b[j](eta)   # 2*d2w/dxdy
    return B

# Element stiffness matrix using Gauss quadrature
from numpy.polynomial.legendre import leggauss

def compute_K_element_gauss(n_points=4):
    """Compute element stiffness matrix using Gauss quadrature"""
    K = np.zeros((16, 16))

    # Get Gauss points and weights for [0,1] interval
    xi_g, w_xi = leggauss(n_points)
    eta_g, w_eta = leggauss(n_points)

    # Transform from [-1,1] to [0,1]
    xi_g = (xi_g + 1) / 2
    w_xi = w_xi / 2
    eta_g = (eta_g + 1) / 2
    w_eta = w_eta / 2

    for i_xi, xi in enumerate(xi_g):
        for i_eta, eta in enumerate(eta_g):
            B = get_B(xi, eta)
            K += w_xi[i_xi] * w_eta[i_eta] * a_e * b_e * B.T @ D @ B

    return K

# Element load vector using Gauss quadrature
def compute_F_element_gauss(n_points=4):
    """Compute element load vector using Gauss quadrature"""
    F = np.zeros(16)

    xi_g, w_xi = leggauss(n_points)
    eta_g, w_eta = leggauss(n_points)

    xi_g = (xi_g + 1) / 2
    w_xi = w_xi / 2
    eta_g = (eta_g + 1) / 2
    w_eta = w_eta / 2

    for i_xi, xi in enumerate(xi_g):
        for i_eta, eta in enumerate(eta_g):
            for i in range(16):
                F[i] += w_xi[i_xi] * w_eta[i_eta] * a_e * b_e * get_N(i, xi, eta) * q

    return F

print("\nComputing element stiffness matrix K_e (Gauss quadrature)...")
K_e = compute_K_element_gauss(6)

print("\nK_e diagonal (first 8):")
for i in range(8):
    print(f"  K_e[{i},{i}] = {K_e[i,i]:.6e}")

print("\nComputing element load vector F_e (Gauss quadrature)...")
F_e = compute_F_element_gauss(6)

print("\nF_e (first 8 components):")
for i in range(8):
    print(f"  F_e[{i}] = {F_e[i]:.6f}")

# Global assembly
print("\n" + "="*60)
print("GLOBAL ASSEMBLY")
print("="*60)

n_dof_global = 4 * n_j  # 4 DOF per joint
print(f"Global DOF: {n_dof_global}")

K_global = np.zeros((n_dof_global, n_dof_global))
F_global = np.zeros(n_dof_global)

# Assembly
for e in range(n_e):
    # Global DOF indices for this element
    dof_map = []
    for node_local in range(4):
        node_global = e_j[e, node_local] - 1  # Convert to 0-based
        for dof in range(4):
            dof_map.append(4 * node_global + dof)

    # Add element contributions
    for i_local in range(16):
        i_global = dof_map[i_local]
        F_global[i_global] += F_e[i_local]
        for j_local in range(16):
            j_global = dof_map[j_local]
            K_global[i_global, j_global] += K_e[i_local, j_local]

print(f"K_global assembled, shape: {K_global.shape}")

# Apply boundary conditions (penalty method)
k_s = 1e20

# For each supported joint, fix w (vertical displacement)
# Also fix rotations at edges
for j in s_j:
    j_idx = j - 1  # Convert to 0-based
    dof_w = 4 * j_idx  # w DOF
    K_global[dof_w, dof_w] += k_s  # Fix w

    # Fix theta_x at y=0 and y=b edges
    if abs(y_j[j_idx]) < 1e-10 or abs(y_j[j_idx] - b) < 1e-10:
        dof_tx = 4 * j_idx + 1
        K_global[dof_tx, dof_tx] += k_s

    # Fix theta_y at x=0 and x=a edges
    if abs(x_j[j_idx]) < 1e-10 or abs(x_j[j_idx] - a) < 1e-10:
        dof_ty = 4 * j_idx + 2
        K_global[dof_ty, dof_ty] += k_s

print("Boundary conditions applied (penalty method)")

# Solve
print("\nSolving system...")
Z = solve(K_global, F_global)

print("\n" + "="*60)
print("RESULTS")
print("="*60)

# Extract displacements
print("\nVertical displacements w at joints (mm):")
W_z = np.zeros((n_a + 1, n_b + 1))
for i_x in range(n_a + 1):
    for i_y in range(n_b + 1):
        j = i_x * (n_b + 1) + i_y
        W_z[i_x, i_y] = Z[4*j] * 1000  # Convert to mm

# Print as matrix (transposed for y along rows)
print("    y=0     y=b/3   y=2b/3  y=b")
for i_x in range(n_a + 1):
    row = f"x={i_x*a_e:4.1f}m "
    for i_y in range(n_b + 1):
        row += f"{W_z[i_x, i_y]:8.4f} "
    print(row)

# Maximum displacement at center
j_center = (n_a // 2) * (n_b + 1) + n_b // 2
if n_a % 2 == 0 and n_b % 2 == 1:
    # For 2x3 mesh, center is between joints
    # Interpolate or use nearest
    pass
w_center = Z[4 * ((n_a//2) * (n_b+1) + (n_b)//2)] * 1000

# Find max displacement
w_max = np.max(np.abs(Z[::4])) * 1000
j_max = np.argmax(np.abs(Z[::4]))

print(f"\nMax displacement: {w_max:.4f} mm at joint {j_max+1}")

# Compute bending moments at center of element 1
print("\n" + "="*60)
print("BENDING MOMENTS (at center of element 1)")
print("="*60)

# Get element 1 displacements
e = 0
dof_map = []
for node_local in range(4):
    node_global = e_j[e, node_local] - 1
    for dof in range(4):
        dof_map.append(4 * node_global + dof)

Z_e = Z[dof_map]

# Moments at center (xi=0.5, eta=0.5)
B_center = get_B(0.5, 0.5)
curvatures = B_center @ Z_e
M = -D @ curvatures

print(f"Mx  = {M[0]:.4f} kNm/m")
print(f"My  = {M[1]:.4f} kNm/m")
print(f"Mxy = {M[2]:.4f} kNm/m")

# Also compute at element centers for all elements
print("\nMoments at element centers:")
print("e    Mx       My       Mxy")
for e in range(n_e):
    dof_map = []
    for node_local in range(4):
        node_global = e_j[e, node_local] - 1
        for dof in range(4):
            dof_map.append(4 * node_global + dof)
    Z_e = Z[dof_map]
    B_center = get_B(0.5, 0.5)
    curvatures = B_center @ Z_e
    M = -D @ curvatures
    print(f"{e+1:2d}  {M[0]:8.4f} {M[1]:8.4f} {M[2]:8.4f}")
