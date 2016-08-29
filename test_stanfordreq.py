from stanfordreq import extract_courses, parse_course


def test_extract_courses():
    # see Github issue 1 for AP scores bug
    chem31x = ("Prerequisites: AP chemistry score of _ or passing score on chemistry placement test, "
               "and AP Calculus AB score of _ or Math 20 or Math 41")
    cs106b = "Prerequisite: 106A or equivalent."
    cs107 = "Prerequisites: 106B or X, or consent of instructor."
    cs110 = "Prerequisite: 107."
    cs142 = "Prerequisites: CS 107 and CS 108."
    econ50 = "Prerequisites: Econ 1 or 1V, and Math 51 or CME 100 or CME 100A."
    math171 = "Prerequisite: 51H or 115 or consent of the instructor."
    music127 = "Prerequisite: 23."
    physics120 = "Prerequisites: PHYSICS 43 or PHYS 63; MATH 52 and MATH 53"

    assert extract_courses(chem31x, "CHEM") == ["MATH 20", "MATH 41"]
    assert extract_courses(cs106b, "CS") == ["CS 106A"]
    assert extract_courses(cs107, "CS") == ["CS 106B", "CS 106X"]
    assert extract_courses(cs110, "CS") == ["CS 107"]
    assert extract_courses(cs142, "CS") == ["CS 107", "CS 108"]
    assert extract_courses(econ50, "ECON") == ["ECON 1", "ECON 1V", "MATH 51", "CME 100", "CME 100A"]
    assert extract_courses(math171, "MATH") == ["MATH 51H", "MATH 115"]
    assert extract_courses(music127, "MUSIC") == ["MUSIC 23"]
    assert extract_courses(physics120, "PHYSICS") == ["PHYSICS 43", "PHYSICS 63", "MATH 52", "MATH 53"]


def test_parse_course():
    physics120 = """
Vector analysis. Electrostatic fields, including boundary-value problems and multipole expansion.
Dielectrics, static and variable magnetic fields, magnetic materials. Maxwell's equations.
Prerequisites: PHYSICS 43 or PHYS 63; MATH 52 and MATH 53.
Pre- or corequisite: MATH 131P or MATH 173. Recommended corequisite: PHYS 112.
"""
    ee222 = """
Emphasis is on applications in modern devices and systems. Topics include: Schr&ouml;dinger's equation,
eigenfunctions and eigenvalues, solutions of simple problems including quantum wells and tunneling,
quantum harmonic oscillator, coherent states, operator approach to quantum mechanics, Dirac notation,
angular momentum, hydrogen atom, calculation techniques including matrix diagonalization, perturbation theory,
variational method, and time-dependent perturbation theory with applications to optical absorption,
nonlinear optical coefficients, and Fermi's golden rule. Prerequisites: MATH 52 and 53, EE 65 or
PHYSICS 65 (or PHYSICS 43 and 45).
"""

    assert parse_course(physics120, "PHYSICS 120") == {
        'code': 'PHYSICS 120',
        'prereq': ['PHYSICS 43', 'PHYSICS 63', 'MATH 52', 'MATH 53'],
        'coreq': ['MATH 131P', 'MATH 173'],
        'recommend': ['PHYSICS 112']
    }

    assert parse_course(ee222, "EE 222") == {
        'code': 'EE 222',
        'prereq': ['MATH 52', 'MATH 53', 'EE 65', 'PHYSICS 65', 'PHYSICS 43', 'PHYSICS 45'],
        'coreq': [],
        'recommend': []
    }
