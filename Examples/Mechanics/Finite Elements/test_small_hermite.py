"""
Small Hermite Element Test (2x3 mesh)
Compare with Calcpad Rectangular Slab FEA.cpd
"""
import numpy as np

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
print("HERMITE ELEMENT TEST - Small mesh (2x3)")
print("="*60)
print(f"Slab: {a}m x {b}m, t={t}m")
print(f"Load: q={q} kN/m2")
print(f"Material: E={E/1e3} MPa, nu={nu}")
print(f"Mesh: {n_a} x {n_b} elements")
print(f"Element size: {a_e:.4f} x {b_e:.4f} m")

# Number of joints
n_j = (n_a + 1) * (n_b + 1)  # 3 * 4 = 12 joints
print(f"Joints: {n_j}")

# Joint coordinates
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
print(f"\nSupported joints: {s_j}")

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

# Hermite shape functions (Calcpad notation)
# xi = x/a_e, eta = y/b_e in [0,1]

def Phi_1a(xi): return 1 - xi**2 * (3 - 2*xi)
def Phi_2a(xi): return xi * a_e * (1 - xi*(2 - xi))
def Phi_3a(xi): return xi**2 * (3 - 2*xi)
def Phi_4a(xi): return xi**2 * a_e * (-1 + xi)

def Phi_1b(eta): return 1 - eta**2 * (3 - 2*eta)
def Phi_2b(eta): return eta * b_e * (1 - eta*(2 - eta))
def Phi_3b(eta): return eta**2 * (3 - 2*eta)
def Phi_4b(eta): return eta**2 * b_e * (-1 + eta)

# First derivatives
def dPhi_1a(xi): return -6 * (xi/a_e) * (1 - xi)
def dPhi_2a(xi): return 1 - xi*(4 - 3*xi)
def dPhi_3a(xi): return 6 * (xi/a_e) * (1 - xi)
def dPhi_4a(xi): return -xi * (2 - 3*xi)

def dPhi_1b(eta): return -6 * (eta/b_e) * (1 - eta)
def dPhi_2b(eta): return 1 - eta*(4 - 3*eta)
def dPhi_3b(eta): return 6 * (eta/b_e) * (1 - eta)
def dPhi_4b(eta): return -eta * (2 - 3*eta)

# Second derivatives
def ddPhi_1a(xi): return -(6/a_e**2) * (1 - 2*xi)
def ddPhi_2a(xi): return -(2/a_e) * (2 - 3*xi)
def ddPhi_3a(xi): return (6/a_e**2) * (1 - 2*xi)
def ddPhi_4a(xi): return -(2/a_e) * (1 - 3*xi)

def ddPhi_1b(eta): return -(6/b_e**2) * (1 - 2*eta)
def ddPhi_2b(eta): return -(2/b_e) * (2 - 3*eta)
def ddPhi_3b(eta): return (6/b_e**2) * (1 - 2*eta)
def ddPhi_4b(eta): return -(2/b_e) * (1 - 3*eta)

# Shape functions N for displacement w
# DOF order per node: w, theta_x, theta_y, psi (twist)
# For node i: N_i,w, N_i,tx, N_i,ty, N_i,psi

def get_N(i, xi, eta):
    """Get shape function N_i for w interpolation"""
    if i == 0: return Phi_1a(xi) * Phi_1b(eta)
    if i == 1: return Phi_2a(xi) * Phi_1b(eta)
    if i == 2: return Phi_1a(xi) * Phi_2b(eta)
    if i == 3: return Phi_2a(xi) * Phi_2b(eta)
    if i == 4: return Phi_3a(xi) * Phi_1b(eta)
    if i == 5: return Phi_4a(xi) * Phi_1b(eta)
    if i == 6: return Phi_3a(xi) * Phi_2b(eta)
    if i == 7: return Phi_4a(xi) * Phi_2b(eta)
    if i == 8: return Phi_3a(xi) * Phi_3b(eta)
    if i == 9: return Phi_4a(xi) * Phi_3b(eta)
    if i == 10: return Phi_3a(xi) * Phi_4b(eta)
    if i == 11: return Phi_4a(xi) * Phi_4b(eta)
    if i == 12: return Phi_1a(xi) * Phi_3b(eta)
    if i == 13: return Phi_2a(xi) * Phi_3b(eta)
    if i == 14: return Phi_1a(xi) * Phi_4b(eta)
    if i == 15: return Phi_2a(xi) * Phi_4b(eta)

# B matrix components (curvature-displacement)
def get_B1(j, xi, eta):
    """Row 1 of B: d2w/dx2"""
    ddPhi_a = [ddPhi_1a, ddPhi_2a, ddPhi_1a, ddPhi_2a,
               ddPhi_3a, ddPhi_4a, ddPhi_3a, ddPhi_4a,
               ddPhi_3a, ddPhi_4a, ddPhi_3a, ddPhi_4a,
               ddPhi_1a, ddPhi_2a, ddPhi_1a, ddPhi_2a]
    Phi_b = [Phi_1b, Phi_1b, Phi_2b, Phi_2b,
             Phi_1b, Phi_1b, Phi_2b, Phi_2b,
             Phi_3b, Phi_3b, Phi_4b, Phi_4b,
             Phi_3b, Phi_3b, Phi_4b, Phi_4b]
    return ddPhi_a[j](xi) * Phi_b[j](eta)

def get_B2(j, xi, eta):
    """Row 2 of B: d2w/dy2"""
    Phi_a = [Phi_1a, Phi_2a, Phi_1a, Phi_2a,
             Phi_3a, Phi_4a, Phi_3a, Phi_4a,
             Phi_3a, Phi_4a, Phi_3a, Phi_4a,
             Phi_1a, Phi_2a, Phi_1a, Phi_2a]
    ddPhi_b = [ddPhi_1b, ddPhi_1b, ddPhi_2b, ddPhi_2b,
               ddPhi_1b, ddPhi_1b, ddPhi_2b, ddPhi_2b,
               ddPhi_3b, ddPhi_3b, ddPhi_4b, ddPhi_4b,
               ddPhi_3b, ddPhi_3b, ddPhi_4b, ddPhi_4b]
    return Phi_a[j](xi) * ddPhi_b[j](eta)

def get_B3(j, xi, eta):
    """Row 3 of B: 2*d2w/dxdy"""
    dPhi_a = [dPhi_1a, dPhi_2a, dPhi_1a, dPhi_2a,
              dPhi_3a, dPhi_4a, dPhi_3a, dPhi_4a,
              dPhi_3a, dPhi_4a, dPhi_3a, dPhi_4a,
              dPhi_1a, dPhi_2a, dPhi_1a, dPhi_2a]
    dPhi_b = [dPhi_1b, dPhi_1b, dPhi_2b, dPhi_2b,
              dPhi_1b, dPhi_1b, dPhi_2b, dPhi_2b,
              dPhi_3b, dPhi_3b, dPhi_4b, dPhi_4b,
              dPhi_3b, dPhi_3b, dPhi_4b, dPhi_4b]
    return 2 * dPhi_a[j](xi) * dPhi_b[j](eta)

def get_B(xi, eta):
    """Full B matrix at point (xi, eta)"""
    B = np.zeros((3, 16))
    for j in range(16):
        B[0, j] = get_B1(j, xi, eta)
        B[1, j] = get_B2(j, xi, eta)
        B[2, j] = get_B3(j, xi, eta)
    return B

# Element stiffness matrix using numerical integration
from scipy.integrate import dblquad

def compute_K_element():
    """Compute element stiffness matrix"""
    K = np.zeros((16, 16))

    def integrand(eta, xi, i, j):
        B = get_B(xi, eta)
        return a_e * b_e * B[:, i].T @ D @ B[:, j]

    for i in range(16):
        for j in range(i, 16):
            val, _ = dblquad(lambda eta, xi: integrand(eta, xi, i, j),
                            0, 1, 0, 1, epsabs=1e-6)
            K[i, j] = val
            K[j, i] = val

    return K

print("\nComputing element stiffness matrix K_e...")
K_e = compute_K_element()

print("\nK_e diagonal (first 8):")
for i in range(8):
    print(f"  K_e[{i},{i}] = {K_e[i,i]:.6e}")

print("\nK_e[0,:4] (first row, first 4 columns):")
print(f"  {K_e[0,0]:.6e}  {K_e[0,1]:.6e}  {K_e[0,2]:.6e}  {K_e[0,3]:.6e}")

# Element load vector
def compute_F_element():
    """Compute element load vector"""
    F = np.zeros(16)

    for i in range(16):
        def integrand(eta, xi):
            return a_e * b_e * get_N(i, xi, eta) * q
        val, _ = dblquad(integrand, 0, 1, 0, 1, epsabs=1e-6)
        F[i] = val

    return F

print("\nComputing element load vector F_e...")
F_e = compute_F_element()

print("\nF_e (element load vector):")
for i in range(16):
    print(f"  F_e[{i}] = {F_e[i]:.6f}")

print("\n" + "="*60)
print("Values to compare with Calcpad:")
print("="*60)
print(f"K_e[0,0] = {K_e[0,0]:.6e}")
print(f"K_e[1,1] = {K_e[1,1]:.6e}")
print(f"F_e[0] = {F_e[0]:.6f}")
print(f"F_e[1] = {F_e[1]:.6f}")
