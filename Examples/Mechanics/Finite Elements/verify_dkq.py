"""
DKQ Element Verification Script
Based on Batoz & Tahar (1982)
Compare with Calcpad implementation
"""

import numpy as np
from scipy.integrate import dblquad
import sympy as sp

# Element parameters
a_e = 1.0  # Element width (normalized)
b_e = 1.0  # Element height (for initial testing, use 1x1)

# For comparison with Calcpad: a=6, b=4, n_a=6, n_b=4
# a_e = 6/6 = 1.0, b_e = 4/4 = 1.0

# Edge geometry for rectangular element
# Node numbering: 1(-1,-1), 2(1,-1), 3(1,1), 4(-1,1) in natural coords
# Edge numbering: 5(1-2), 6(2-3), 7(3-4), 8(4-1)

# Edge vectors (in physical coordinates)
edges = {
    5: {'x': a_e, 'y': 0},      # 1->2: horizontal bottom
    6: {'x': 0, 'y': b_e},      # 2->3: vertical right
    7: {'x': -a_e, 'y': 0},     # 3->4: horizontal top
    8: {'x': 0, 'y': -b_e}      # 4->1: vertical left
}

# Calculate edge lengths
for k in edges:
    edges[k]['L'] = np.sqrt(edges[k]['x']**2 + edges[k]['y']**2)

print("Edge properties:")
for k in edges:
    x = edges[k]['x']
    y = edges[k]['y']
    L = edges[k]['L']
    print(f"  Edge {k}: x={x:6.3f}, y={y:6.3f}, L={L:6.3f}")

# DKQ coefficients (Batoz & Tahar 1982, Eq. 35)
def calc_coefficients(x, y, L):
    a = -6*x / L**2
    b = 3*x*y / L**2
    c = 3*y**2 / L**2 - 1
    d = -3*x**2 / L**2 + 1
    e = -3*x*y / L**2
    return {'a': a, 'b': b, 'c': c, 'd': d, 'e': e}

coefs = {}
print("\nDKQ Coefficients:")
for k in edges:
    coefs[k] = calc_coefficients(edges[k]['x'], edges[k]['y'], edges[k]['L'])
    print(f"  Edge {k}: a={coefs[k]['a']:7.3f}, b={coefs[k]['b']:7.3f}, "
          f"c={coefs[k]['c']:7.3f}, d={coefs[k]['d']:7.3f}, e={coefs[k]['e']:7.3f}")

# Quadratic edge functions P_k (bubble functions on edges)
def P5(xi, eta):
    return (1 - xi**2) * (1 - eta) / 4

def P6(xi, eta):
    return (1 + xi) * (1 - eta**2) / 4

def P7(xi, eta):
    return (1 - xi**2) * (1 + eta) / 4

def P8(xi, eta):
    return (1 - xi) * (1 - eta**2) / 4

# Derivatives of P_k
def dP5_dxi(xi, eta):
    return -xi * (1 - eta) / 2

def dP5_deta(xi, eta):
    return -(1 - xi**2) / 4

def dP6_dxi(xi, eta):
    return (1 - eta**2) / 4

def dP6_deta(xi, eta):
    return -eta * (1 + xi) / 2

def dP7_dxi(xi, eta):
    return -xi * (1 + eta) / 2

def dP7_deta(xi, eta):
    return (1 - xi**2) / 4

def dP8_dxi(xi, eta):
    return -(1 - eta**2) / 4

def dP8_deta(xi, eta):
    return -eta * (1 - xi) / 2

# Bilinear shape functions N_i
def N1(xi, eta):
    return (1 - xi) * (1 - eta) / 4

def N2(xi, eta):
    return (1 + xi) * (1 - eta) / 4

def N3(xi, eta):
    return (1 + xi) * (1 + eta) / 4

def N4(xi, eta):
    return (1 - xi) * (1 + eta) / 4

# Derivatives of N_i
def dN1_dxi(xi, eta):
    return -(1 - eta) / 4

def dN1_deta(xi, eta):
    return -(1 - xi) / 4

def dN2_dxi(xi, eta):
    return (1 - eta) / 4

def dN2_deta(xi, eta):
    return -(1 + xi) / 4

def dN3_dxi(xi, eta):
    return (1 + eta) / 4

def dN3_deta(xi, eta):
    return (1 + xi) / 4

def dN4_dxi(xi, eta):
    return -(1 + eta) / 4

def dN4_deta(xi, eta):
    return (1 - xi) / 4

# Test: verify P functions at Gauss points
print("\nP functions at Gauss points (+/-1/sqrt(3)):")
gp = 1/np.sqrt(3)
gauss_pts = [(-gp, -gp), (gp, -gp), (gp, gp), (-gp, gp)]
for xi, eta in gauss_pts:
    print(f"  (xi,eta)=({xi:6.4f},{eta:6.4f}): P5={P5(xi,eta):7.4f}, P6={P6(xi,eta):7.4f}, "
          f"P7={P7(xi,eta):7.4f}, P8={P8(xi,eta):7.4f}")

# DKQ interpolation functions for betax (Batoz & Tahar 1982, Eq. 34a)
# Node 1 uses edges 5 and 8
def Hx_1(xi, eta):
    return 1.5 * (coefs[5]['a'] * P5(xi, eta) - coefs[8]['a'] * P8(xi, eta))

def Hxx_1(xi, eta):
    return coefs[5]['b'] * P5(xi, eta) + coefs[8]['b'] * P8(xi, eta)

def Hxy_1(xi, eta):
    return N1(xi, eta) - coefs[5]['c'] * P5(xi, eta) - coefs[8]['c'] * P8(xi, eta)

# Node 2 uses edges 6 and 5
def Hx_2(xi, eta):
    return 1.5 * (coefs[6]['a'] * P6(xi, eta) - coefs[5]['a'] * P5(xi, eta))

def Hxx_2(xi, eta):
    return coefs[6]['b'] * P6(xi, eta) + coefs[5]['b'] * P5(xi, eta)

def Hxy_2(xi, eta):
    return N2(xi, eta) - coefs[6]['c'] * P6(xi, eta) - coefs[5]['c'] * P5(xi, eta)

# Node 3 uses edges 7 and 6
def Hx_3(xi, eta):
    return 1.5 * (coefs[7]['a'] * P7(xi, eta) - coefs[6]['a'] * P6(xi, eta))

def Hxx_3(xi, eta):
    return coefs[7]['b'] * P7(xi, eta) + coefs[6]['b'] * P6(xi, eta)

def Hxy_3(xi, eta):
    return N3(xi, eta) - coefs[7]['c'] * P7(xi, eta) - coefs[6]['c'] * P6(xi, eta)

# Node 4 uses edges 8 and 7
def Hx_4(xi, eta):
    return 1.5 * (coefs[8]['a'] * P8(xi, eta) - coefs[7]['a'] * P7(xi, eta))

def Hxx_4(xi, eta):
    return coefs[8]['b'] * P8(xi, eta) + coefs[7]['b'] * P7(xi, eta)

def Hxy_4(xi, eta):
    return N4(xi, eta) - coefs[8]['c'] * P8(xi, eta) - coefs[7]['c'] * P7(xi, eta)

# DKQ interpolation functions for betay (Batoz & Tahar 1982, Eq. 34b)
# Node 1
def Hy_1(xi, eta):
    return 1.5 * (coefs[5]['d'] * P5(xi, eta) - coefs[8]['d'] * P8(xi, eta))

def Hyx_1(xi, eta):
    return -N1(xi, eta) + coefs[5]['e'] * P5(xi, eta) + coefs[8]['e'] * P8(xi, eta)

def Hyy_1(xi, eta):
    return -coefs[5]['b'] * P5(xi, eta) - coefs[8]['b'] * P8(xi, eta)

# Node 2
def Hy_2(xi, eta):
    return 1.5 * (coefs[6]['d'] * P6(xi, eta) - coefs[5]['d'] * P5(xi, eta))

def Hyx_2(xi, eta):
    return -N2(xi, eta) + coefs[6]['e'] * P6(xi, eta) + coefs[5]['e'] * P5(xi, eta)

def Hyy_2(xi, eta):
    return -coefs[6]['b'] * P6(xi, eta) - coefs[5]['b'] * P5(xi, eta)

# Node 3
def Hy_3(xi, eta):
    return 1.5 * (coefs[7]['d'] * P7(xi, eta) - coefs[6]['d'] * P6(xi, eta))

def Hyx_3(xi, eta):
    return -N3(xi, eta) + coefs[7]['e'] * P7(xi, eta) + coefs[6]['e'] * P6(xi, eta)

def Hyy_3(xi, eta):
    return -coefs[7]['b'] * P7(xi, eta) - coefs[6]['b'] * P6(xi, eta)

# Node 4
def Hy_4(xi, eta):
    return 1.5 * (coefs[8]['d'] * P8(xi, eta) - coefs[7]['d'] * P7(xi, eta))

def Hyx_4(xi, eta):
    return -N4(xi, eta) + coefs[8]['e'] * P8(xi, eta) + coefs[7]['e'] * P7(xi, eta)

def Hyy_4(xi, eta):
    return -coefs[8]['b'] * P8(xi, eta) - coefs[7]['b'] * P7(xi, eta)

# Test interpolation property: at node i, Hxx_i should equal 1 for betax interpolation
print("\nInterpolation test at nodes:")
nodes = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
Hxx = [Hxx_1, Hxx_2, Hxx_3, Hxx_4]
Hxy = [Hxy_1, Hxy_2, Hxy_3, Hxy_4]
Hyy = [Hyy_1, Hyy_2, Hyy_3, Hyy_4]
Hyx = [Hyx_1, Hyx_2, Hyx_3, Hyx_4]

for i, (xi, eta) in enumerate(nodes):
    print(f"  Node {i+1} at ({xi:2},{eta:2}):")
    for j in range(4):
        hxx = Hxx[j](xi, eta)
        hxy = Hxy[j](xi, eta)
        hyy = Hyy[j](xi, eta)
        hyx = Hyx[j](xi, eta)
        if abs(hxx) > 1e-10 or abs(hxy) > 1e-10 or abs(hyy) > 1e-10 or abs(hyx) > 1e-10:
            print(f"    Hxx_{j+1}={hxx:7.4f}, Hxy_{j+1}={hxy:7.4f}, "
                  f"Hyx_{j+1}={hyx:7.4f}, Hyy_{j+1}={hyy:7.4f}")

# Jacobian for rectangular element
J11 = a_e / 2
J22 = b_e / 2
det_J = J11 * J22

print(f"\nJacobian: J11={J11}, J22={J22}, det_J={det_J}")

# Build B matrix at a point
def get_B_matrix(xi, eta):
    """
    B matrix: curvature = B * d
    where d = [w1, betax1, betay1, w2, betax2, betay2, w3, betax3, betay3, w4, betax4, betay4]^T

    kappax = ∂betax/∂x
    kappay = ∂betay/∂y
    kappaxy = ∂betax/∂y + ∂betay/∂x
    """
    B = np.zeros((3, 12))

    # Node data structure: [(Hx, Hxx, Hxy), derivatives...]
    # We need derivatives of Hx functions for betax interpolation
    # and derivatives of Hy functions for betay interpolation

    # This requires derivatives of all H functions
    # For now, let's use numerical differentiation for testing
    h = 1e-6

    # Row 1: kappax = ∂betax/∂x = (1/J11) * ∂betax/∂xi
    # betax = Sum (Hx_i*w_i + Hxx_i*betax_i + Hxy_i*betay_i)
    Hx_funcs = [Hx_1, Hx_2, Hx_3, Hx_4]
    Hxx_funcs = [Hxx_1, Hxx_2, Hxx_3, Hxx_4]
    Hxy_funcs = [Hxy_1, Hxy_2, Hxy_3, Hxy_4]

    Hy_funcs = [Hy_1, Hy_2, Hy_3, Hy_4]
    Hyx_funcs = [Hyx_1, Hyx_2, Hyx_3, Hyx_4]
    Hyy_funcs = [Hyy_1, Hyy_2, Hyy_3, Hyy_4]

    for i in range(4):
        col = 3 * i

        # Numerical derivatives for ∂/∂xi and ∂/∂eta
        # d(Hx)/dxi
        dHx_dxi = (Hx_funcs[i](xi+h, eta) - Hx_funcs[i](xi-h, eta)) / (2*h)
        dHxx_dxi = (Hxx_funcs[i](xi+h, eta) - Hxx_funcs[i](xi-h, eta)) / (2*h)
        dHxy_dxi = (Hxy_funcs[i](xi+h, eta) - Hxy_funcs[i](xi-h, eta)) / (2*h)

        dHx_deta = (Hx_funcs[i](xi, eta+h) - Hx_funcs[i](xi, eta-h)) / (2*h)
        dHxx_deta = (Hxx_funcs[i](xi, eta+h) - Hxx_funcs[i](xi, eta-h)) / (2*h)
        dHxy_deta = (Hxy_funcs[i](xi, eta+h) - Hxy_funcs[i](xi, eta-h)) / (2*h)

        dHy_dxi = (Hy_funcs[i](xi+h, eta) - Hy_funcs[i](xi-h, eta)) / (2*h)
        dHyx_dxi = (Hyx_funcs[i](xi+h, eta) - Hyx_funcs[i](xi-h, eta)) / (2*h)
        dHyy_dxi = (Hyy_funcs[i](xi+h, eta) - Hyy_funcs[i](xi-h, eta)) / (2*h)

        dHy_deta = (Hy_funcs[i](xi, eta+h) - Hy_funcs[i](xi, eta-h)) / (2*h)
        dHyx_deta = (Hyx_funcs[i](xi, eta+h) - Hyx_funcs[i](xi, eta-h)) / (2*h)
        dHyy_deta = (Hyy_funcs[i](xi, eta+h) - Hyy_funcs[i](xi, eta-h)) / (2*h)

        # Row 1: kappax = ∂betax/∂x = (1/J11) * ∂betax/∂xi
        B[0, col] = dHx_dxi / J11      # w_i
        B[0, col+1] = dHxx_dxi / J11   # betax_i
        B[0, col+2] = dHxy_dxi / J11   # betay_i

        # Row 2: kappay = ∂betay/∂y = (1/J22) * ∂betay/∂eta
        B[1, col] = dHy_deta / J22     # w_i
        B[1, col+1] = dHyx_deta / J22  # betax_i
        B[1, col+2] = dHyy_deta / J22  # betay_i

        # Row 3: kappaxy = ∂betax/∂y + ∂betay/∂x = (1/J22)*∂betax/∂eta + (1/J11)*∂betay/∂xi
        B[2, col] = dHx_deta / J22 + dHy_dxi / J11
        B[2, col+1] = dHxx_deta / J22 + dHyx_dxi / J11
        B[2, col+2] = dHxy_deta / J22 + dHyy_dxi / J11

    return B

# Test B matrix at center
print("\nB matrix at center (xi=0, eta=0):")
B_center = get_B_matrix(0, 0)
print(B_center)

print("\nB matrix at Gauss point 1 (xi=-1/sqrt3, eta=-1/sqrt3):")
B_gp1 = get_B_matrix(-1/np.sqrt(3), -1/np.sqrt(3))
print(B_gp1)

# Material properties
E = 35000e6  # Pa (35000 MPa)
nu = 0.15
t = 0.1  # m

# Constitutive matrix for bending
D = E * t**3 / (12 * (1 - nu**2)) * np.array([
    [1, nu, 0],
    [nu, 1, 0],
    [0, 0, (1-nu)/2]
])

print(f"\nConstitutive matrix D (for t={t}, E={E/1e6}MPa, nu={nu}):")
print(D)

# Element stiffness matrix using 2x2 Gauss quadrature
def compute_K_element():
    K = np.zeros((12, 12))

    # 2x2 Gauss points
    gp = 1/np.sqrt(3)
    gauss_pts = [(-gp, -gp), (gp, -gp), (gp, gp), (-gp, gp)]
    weights = [1, 1, 1, 1]

    for (xi, eta), w in zip(gauss_pts, weights):
        B = get_B_matrix(xi, eta)
        K += w * det_J * B.T @ D @ B

    return K

K_e = compute_K_element()

print("\nElement stiffness matrix K_e (12x12):")
print("Diagonal elements:")
print(np.diag(K_e))

print("\nChecking symmetry:")
print(f"Max asymmetry: {np.max(np.abs(K_e - K_e.T))}")

print("\nChecking eigenvalues (should be non-negative for positive semi-definite):")
eigenvalues = np.linalg.eigvalsh(K_e)
print(f"Eigenvalues: {eigenvalues}")
print(f"Number of zero eigenvalues: {np.sum(np.abs(eigenvalues) < 1e-6)}")
print(f"Number of negative eigenvalues: {np.sum(eigenvalues < -1e-6)}")

if np.any(eigenvalues < -1e-6):
    print("\nWARNING: Matrix has negative eigenvalues - NOT positive definite!")
    print("This explains the Calcpad error 'Matrix is not positive definite'")
