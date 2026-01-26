"""
DKQ Element Simple Test
Check if element stiffness matrix is correct
"""

import numpy as np

# Test with same parameters as Calcpad
a_e = 1.0  # Element dimensions (for 1x1 element)
b_e = 1.0

# Material
E = 35000e6  # Pa
nu = 0.15
t = 0.1  # m

# Constitutive matrix
D = E * t**3 / (12 * (1 - nu**2)) * np.array([
    [1, nu, 0],
    [nu, 1, 0],
    [0, 0, (1-nu)/2]
])

print(f"D matrix for t={t}m, E={E/1e6}MPa, nu={nu}:")
print(f"  D[0,0] = {D[0,0]:.6e}")
print(f"  D[0,1] = {D[0,1]:.6e}")
print(f"  D[1,1] = {D[1,1]:.6e}")
print(f"  D[2,2] = {D[2,2]:.6e}")

# For Calcpad: D_b = E*t^3/(12*(1 - nu^2))*[1; nu; 0|nu; 1; 0|0; 0; (1 - nu)/2]
# With E=35000 MPa = 35000e3 kN/m^2, t=0.1m, nu=0.15:
E_kN = 35000e3  # kN/m^2
D_kN = E_kN * t**3 / (12 * (1 - nu**2))
print(f"\nIn Calcpad units (kN, m):")
print(f"  E*t^3/(12*(1-nu^2)) = {D_kN:.6f} kN*m")
print(f"  D[0,0] = D[1,1] = {D_kN:.6f} kN*m")
print(f"  D[0,1] = D[1,0] = {D_kN*nu:.6f} kN*m")
print(f"  D[2,2] = {D_kN*(1-nu)/2:.6f} kN*m")

# Jacobian
J11 = a_e / 2
J22 = b_e / 2
det_J = J11 * J22

print(f"\nJacobian: J11={J11}, J22={J22}, det_J={det_J}")

# Edge coefficients for rectangular element
print("\nDKQ coefficients for rectangular element:")
print("  Edge 5 (1->2, x=a_e, y=0): a5=-6/a_e, b5=0, c5=-1, d5=-2, e5=0")
print("  Edge 6 (2->3, x=0, y=b_e): a6=0, b6=0, c6=2, d6=1, e6=0")
print("  Edge 7 (3->4, x=-a_e, y=0): a7=6/a_e, b7=0, c7=-1, d7=-2, e7=0")
print("  Edge 8 (4->1, x=0, y=-b_e): a8=0, b8=0, c8=2, d8=1, e8=0")

print(f"\nFor a_e=b_e={a_e}:")
a5 = -6/a_e
a7 = 6/a_e
c5 = c7 = -1
c6 = c8 = 2
d5 = d7 = -2
d6 = d8 = 1
print(f"  a5={a5}, a7={a7}")
print(f"  c5=c7={c5}, c6=c8={c6}")
print(f"  d5=d7={d5}, d6=d8={d6}")

# Simple check: compute a single B matrix entry at center
print("\n" + "="*50)
print("CHECK: B matrix at center (xi=0, eta=0)")
print("="*50)

# At center, P functions:
# P5(0,0) = (1-0^2)(1-0)/4 = 1/4 = 0.25
# P6(0,0) = (1+0)(1-0^2)/4 = 1/4 = 0.25
# P7(0,0) = (1-0^2)(1+0)/4 = 1/4 = 0.25
# P8(0,0) = (1-0)(1-0^2)/4 = 1/4 = 0.25

P5_0 = P6_0 = P7_0 = P8_0 = 0.25
print(f"P5=P6=P7=P8 at center = {P5_0}")

# Hx_1(0,0) = 1.5 * (a5*P5 - a8*P8) = 1.5 * (-6*0.25 - 0) = -2.25
Hx1_0 = 1.5 * (a5 * P5_0 - 0)
print(f"Hx_1(0,0) = 1.5*(a5*P5 - a8*P8) = 1.5*({a5}*{P5_0} - 0) = {Hx1_0}")

# Check interpolation at node 1 (-1,-1)
print("\n" + "="*50)
print("INTERPOLATION TEST at node 1 (xi=-1, eta=-1)")
print("="*50)

# P functions at node 1:
# P5(-1,-1) = (1-1)(1-(-1))/4 = 0*2/4 = 0
# P6(-1,-1) = (1+(-1))(1-1)/4 = 0*0/4 = 0
# P7(-1,-1) = (1-1)(1+(-1))/4 = 0*0/4 = 0
# P8(-1,-1) = (1-(-1))(1-1)/4 = 2*0/4 = 0

P5_n1 = 0
P6_n1 = 0
P7_n1 = 0
P8_n1 = 0
print(f"P5(-1,-1)={P5_n1}, P6={P6_n1}, P7={P7_n1}, P8={P8_n1}")

# N1(-1,-1) = (1-(-1))(1-(-1))/4 = 2*2/4 = 1
N1_n1 = 1
print(f"N1(-1,-1) = {N1_n1}")

# Hxy_1(-1,-1) = N1 - c5*P5 - c8*P8 = 1 - (-1)*0 - 2*0 = 1
Hxy1_n1 = N1_n1 - c5*P5_n1 - c8*P8_n1
print(f"Hxy_1(-1,-1) = N1 - c5*P5 - c8*P8 = {N1_n1} - {c5}*{P5_n1} - {c8}*{P8_n1} = {Hxy1_n1}")

# Hxx_1(-1,-1) = b5*P5 + b8*P8 = 0*0 + 0*0 = 0
print(f"Hxx_1(-1,-1) = b5*P5 + b8*P8 = 0*0 + 0*0 = 0")

print("\n" + "="*50)
print("PROBLEM IDENTIFIED!")
print("="*50)
print("At node 1, we need Hxx_1=1 to interpolate betax correctly")
print("But we get Hxx_1=0 and Hxy_1=1")
print("")
print("This means the naming convention in Batoz paper is:")
print("  - Hxy_i interpolates the SAME rotation (diagonal entry)")
print("  - Hxx_i interpolates cross-coupling")
print("")
print("In standard FE convention, DOF order is [w, thetax, thetay]")
print("where thetax = dw/dy (rotation about x-axis)")
print("      thetay = -dw/dx (rotation about y-axis)")
print("")
print("The Batoz formulation uses betax, betay differently!")
