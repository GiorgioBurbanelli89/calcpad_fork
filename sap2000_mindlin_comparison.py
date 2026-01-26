"""
SAP2000 API Script: Mindlin Plate Comparison
Creates a 4x4m simply supported plate with 4x4 mesh
Same parameters as Calcpad FEA example
Uses AddByCoord for more reliable element creation
"""

import os
import sys
import comtypes.client

def create_mindlin_plate_model():
    # Model parameters (same as Calcpad)
    a = 4.0  # m - plate dimension x
    b = 4.0  # m - plate dimension y
    t = 0.4  # m - thickness
    q = 10.0  # kN/m² - uniform load
    E = 30000000  # kPa (30000 MPa)
    nu = 0.2  # Poisson's ratio
    n_div = 4  # mesh divisions

    # Connect to existing SAP2000 instance using COM
    sap_object = None

    try:
        sap_object = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        if sap_object is not None:
            print("Connected to existing SAP2000 instance via GetActiveObject")
    except Exception as e:
        print(f"GetActiveObject failed: {e}")

    if sap_object is None:
        try:
            helper = comtypes.client.CreateObject('SAP2000v1.Helper')
            helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
            sap_object = helper.GetObject("CSI.SAP2000.API.SapObject")
            if sap_object is not None:
                print("Connected to existing SAP2000 instance via Helper")
        except Exception as e:
            print(f"Helper.GetObject failed: {e}")

    if sap_object is None:
        print("Starting new SAP2000 instance...")
        helper = comtypes.client.CreateObject('SAP2000v1.Helper')
        helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
        sap_object = helper.CreateObject(r"C:\Program Files\Computers and Structures\SAP2000 24\SAP2000.exe")
        sap_object.ApplicationStart()

    sap_model = sap_object.SapModel

    # Initialize new model (kN-m units)
    ret = sap_model.InitializeNewModel(6)  # 6 = kN_m_C
    print(f"InitializeNewModel: {ret}")

    # Create new blank model
    ret = sap_model.File.NewBlank()
    print(f"New model created: {ret}")

    # Define material
    ret = sap_model.PropMaterial.SetMaterial("CONC", 2)  # 2 = Concrete
    print(f"SetMaterial: {ret}")
    ret = sap_model.PropMaterial.SetMPIsotropic("CONC", E, nu, 0.0000099)
    print(f"SetMPIsotropic: {ret}")

    # Define area section (Shell-Thick for Mindlin behavior)
    # ShellType: 1=Shell-Thin, 2=Shell-Thick, 3=Membrane, 4=Plate-Thin, 5=Plate-Thick
    ret = sap_model.PropArea.SetShell_1("PLATE_THICK", 5, True, "CONC", 0, t, t, -1, "", "")
    print(f"SetShell_1: {ret}")

    # Create shell elements using AddByCoord (creates points automatically)
    dx = a / n_div
    dy = b / n_div
    shell_names = {}  # Store actual shell names assigned by SAP2000

    print(f"\nCreating {n_div ** 2} shell elements using AddByCoord...")
    for i in range(n_div):
        for j in range(n_div):
            # Corner coordinates for this element (counterclockwise)
            x0, y0 = i * dx, j * dy
            x1, y1 = (i + 1) * dx, j * dy
            x2, y2 = (i + 1) * dx, (j + 1) * dy
            x3, y3 = i * dx, (j + 1) * dy

            x_coords = [x0, x1, x2, x3]
            y_coords = [y0, y1, y2, y3]
            z_coords = [0.0, 0.0, 0.0, 0.0]

            user_name = f"SHELL_{i}_{j}"
            name = ""  # Will be filled with actual name

            ret = sap_model.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, name, "PLATE_THICK", user_name)
            shell_names[(i, j)] = user_name

            if ret != 0:
                print(f"  Error creating {user_name}: ret={ret}")

    print(f"Shell elements created: {n_div ** 2}")

    # Get all point names created by SAP2000
    # First count them
    num_points_result = sap_model.PointObj.Count()
    print(f"\nTotal points created: {num_points_result}")

    # Apply boundary conditions to edge points
    # We need to get all point objects and check if they're on the edge
    print("\nApplying boundary conditions to edge points...")

    # Get all point names
    num_points = 0
    point_names = []
    result = sap_model.PointObj.GetNameList(num_points, point_names)
    num_points = result[0]
    point_names = result[1]

    print(f"Retrieved {num_points} point names")

    edge_count = 0
    for pt_name in point_names:
        # Get coordinates of this point
        x = 0.0
        y = 0.0
        z = 0.0
        result = sap_model.PointObj.GetCoordCartesian(pt_name, x, y, z)
        x = result[0]
        y = result[1]
        z = result[2]

        # Check if on edge (with small tolerance)
        tol = 0.001
        is_edge = (abs(x) < tol or abs(x - a) < tol or
                   abs(y) < tol or abs(y - b) < tol)

        if is_edge:
            # Simply supported: restrain UZ only
            restraint = [False, False, True, False, False, False]
            ret = sap_model.PointObj.SetRestraint(pt_name, restraint)
            edge_count += 1
            if ret != 0:
                print(f"  Restraint error on {pt_name}: ret={ret}")

    print(f"Boundary conditions applied to {edge_count} edge points")

    # Define load pattern
    ret = sap_model.LoadPatterns.Add("UNIFORM", 1)  # 1 = Dead
    print(f"\nLoad pattern added: {ret}")

    # Apply uniform load to all shell elements
    print("Applying loads...")
    for i in range(n_div):
        for j in range(n_div):
            name = shell_names[(i, j)]
            # Uniform load in -Z direction (gravity)
            # Dir: 6 = Local 3 (normal to shell)
            ret = sap_model.AreaObj.SetLoadUniform(name, "UNIFORM", -q, 6)
            if ret != 0:
                print(f"  Load error on {name}: ret={ret}")

    print("Uniform load applied")

    # Refresh the view to show the model
    ret = sap_model.View.RefreshView(0, False)
    print(f"RefreshView: {ret}")

    # Save model
    model_path = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\Mindlin_Plate_4x4.sdb"
    ret = sap_model.File.Save(model_path)
    print(f"Model saved to {model_path}: {ret}")

    # Set the model to run only for the UNIFORM load case
    ret = sap_model.Analyze.SetRunCaseFlag("DEAD", False)
    print(f"\nDisable DEAD case: {ret}")
    ret = sap_model.Analyze.SetRunCaseFlag("UNIFORM", True)
    print(f"Enable UNIFORM case: {ret}")

    # Run analysis
    print("\nRunning analysis...")
    ret = sap_model.Analyze.RunAnalysis()
    print(f"Analysis complete: {ret}")

    # ========== GET RESULTS ==========
    # Select output case
    sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = sap_model.Results.Setup.SetCaseSelectedForOutput("UNIFORM")
    print(f"\nSetCaseSelectedForOutput('UNIFORM'): {ret}")

    # Find center point (at x=2, y=2)
    center_point = None
    for pt_name in point_names:
        result = sap_model.PointObj.GetCoordCartesian(pt_name, 0.0, 0.0, 0.0)
        x = result[0]
        y = result[1]
        if abs(x - a/2) < 0.001 and abs(y - b/2) < 0.001:
            center_point = pt_name
            break

    print(f"\n=== RESULTS ===")
    print(f"Center point: {center_point}")

    # Get displacement at center
    ObjectElm = 0  # 0 = ObjectElm type
    w_center = 0

    if center_point:
        result = sap_model.Results.JointDispl(center_point, ObjectElm, 0, [], [], [], [], [], [], [], [], [], [], [])
        NumberResults = result[0]
        if NumberResults > 0:
            U3_results = result[9]  # U3 is at index 9
            w_center = U3_results[0]
            print(f"Vertical displacement (w): {w_center * 1000:.4f} mm")
        else:
            print(f"No displacement results at center. NumberResults={NumberResults}")
    else:
        print("Center point not found!")

    # Get shell forces (moments) at center shell
    center_shell = shell_names[(n_div // 2 - 1, n_div // 2 - 1)]
    print(f"\nCenter shell element: {center_shell}")

    result = sap_model.Results.AreaForceShell(center_shell, ObjectElm, 0,
            [], [], [], [], [], [],
            [], [], [], [], [], [], [],
            [], [], [], [], [], [],
            [], [], [], [])

    NumberResults = result[0]
    m11_avg = 0
    m22_avg = 0
    if NumberResults > 0:
        M11_results = result[17]  # M11 position in tuple
        M22_results = result[18]  # M22 position in tuple
        m11_avg = sum(M11_results) / len(M11_results)
        m22_avg = sum(M22_results) / len(M22_results)
        print(f"Moment M11 (Mx): {m11_avg:.4f} kNm/m")
        print(f"Moment M22 (My): {m22_avg:.4f} kNm/m")
        print(f"Number of result points: {NumberResults}")
    else:
        print(f"No moment results found. NumberResults={NumberResults}")

    # Find maximum displacement among interior points
    max_w = w_center
    for pt_name in point_names:
        result_coord = sap_model.PointObj.GetCoordCartesian(pt_name, 0.0, 0.0, 0.0)
        x = result_coord[0]
        y = result_coord[1]

        # Check if interior point
        tol = 0.001
        is_interior = (x > tol and x < a - tol and y > tol and y < b - tol)

        if is_interior:
            result = sap_model.Results.JointDispl(pt_name, ObjectElm, 0, [], [], [], [], [], [], [], [], [], [], [])
            if result[0] > 0:
                u3_val = result[9][0]
                if abs(u3_val) > abs(max_w):
                    max_w = u3_val

    print(f"\nMaximum displacement: {max_w * 1000:.4f} mm")

    # DON'T close SAP2000 - leave it open for user to inspect
    print("\n" + "="*50)
    print("SAP2000 model left open for inspection.")
    print(f"Model file: {model_path}")
    print("="*50)

    return {
        'w_max': max_w * 1000,  # mm
        'w_center': w_center * 1000,  # mm
        'm11_center': m11_avg,
        'm22_center': m22_avg
    }

if __name__ == "__main__":
    try:
        results = create_mindlin_plate_model()

        print("\n" + "="*50)
        print("COMPARISON: Calcpad vs SAP2000 vs Analytical")
        print("="*50)
        print(f"\n{'Parameter':<25} {'Calcpad':<12} {'SAP2000':<12} {'Analytical':<12}")
        print("-"*60)
        print(f"{'Deflection w_max (mm)':<25} {'0.073':<12} {results['w_max']:.4f}{'':>5} {'0.0624':<12}")
        print(f"{'Moment Mx (kNm/m)':<25} {'6.67':<12} {results['m11_center']:.4f}{'':>5} {'7.66':<12}")
        print(f"{'Moment My (kNm/m)':<25} {'6.67':<12} {results['m22_center']:.4f}{'':>5} {'7.66':<12}")

        print("\n" + "="*50)
        print("RATIOS")
        print("="*50)
        if results['w_max'] != 0:
            print(f"SAP2000/Calcpad w_max: {results['w_max']/0.073:.4f}")
            print(f"SAP2000/Analytical w_max: {results['w_max']/0.0624:.4f}")
        if results['m11_center'] != 0:
            print(f"SAP2000/Calcpad Mx: {results['m11_center']/6.67:.4f}")
            print(f"SAP2000/Analytical Mx: {results['m11_center']/7.66:.4f}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
