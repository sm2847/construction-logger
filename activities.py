# activities.py

activities = {
    "A": {
        "name": "Offsite setup",
        "duration": 1.5,
        "resources": 8,
        "dependencies": []
    },
    "B": {
        "name": "Steel to offsite",
        "duration": 1.5,
        "resources": 2,
        "dependencies": []
    },
    "C": {
        "name": "Attach strain gauges",
        "duration": 1.0,
        "resources": 3,
        "dependencies": ["A", "B"]
    },
    "D": {
        "name": "Connect bracing to beams",
        "duration": 1.0,
        "resources": 8,
        "dependencies": ["C"]
    },
    "E": {
        "name": "Construct temp handrail",
        "duration": 2.0,
        "resources": 3,
        "dependencies": ["A", "B"]
    },
    "F": {
        "name": "Construct temp decking",
        "duration": 2.0,
        "resources": 3,
        "dependencies": ["A", "B"]
    },
    "G": {
        "name": "Attach decking",
        "duration": 1.0,
        "resources": 3,
        "dependencies": ["D", "F"]
    },
    "H": {
        "name": "Attach permanent handrail (inc. Kickboard)",
        "duration": 4.0,
        "resources": 6,
        "dependencies": ["G"]
    },
    "I": {
        "name": "Attach temp handrail",
        "duration": 1.0,
        "resources": 5,
        "dependencies": ["E", "G"]
    },
    "J": {
        "name": "Stairs",
        "duration": 3.0,
        "resources": 3,
        "dependencies": ["A"]
    },
    "A1": {
        "name": "Wednesday",
        "duration": 6.5,
        "resources": 0,  # Not specified in sheet, defaulting to 0
        "dependencies": []
    },
    "K": {
        "name": "Site setup",
        "duration": 1.5,
        "resources": 2,
        "dependencies": []
    },
    "L": {
        "name": "Surveying of bridge abutments",
        "duration": 2.0,
        "resources": 2,
        "dependencies": ["K"]
    },
    "M": {
        "name": "Fixing points into concrete substructure",
        "duration": 1.0,
        "resources": 4,
        "dependencies": ["L", "A1"]
    },
    "N": {
        "name": "Shell abutments and capping slabs delivered and inspect",
        "duration": 0.5,
        "resources": 2,
        "dependencies": ["M"]
    },
    "O": {
        "name": "Position shell abutments and inspect",
        "duration": 0.5,
        "resources": 2,
        "dependencies": ["N"]
    },
    "Q": {
        "name": "Install capping slabs and inspect",
        "duration": 1.0,
        "resources": 2,
        "dependencies": ["O"]
    },
    "R": {
        "name": "Install stairs and inspect",
        "duration": 0.5,
        "resources": 2,
        "dependencies": ["Q"]
    },
    "U": {
        "name": "Truck leaves, Steel delivery 1",
        "duration": 1.0,
        "resources": 2,
        "dependencies": ["H", "I", "Q"]
    },
    "V": {
        "name": "Craning steel beams into place, decouple and inspect",
        "duration": 2.5,
        "resources": 2,
        "dependencies": ["U"]
    },
    "X": {
        "name": "Truck leaves, steel delivery 2 and inspect",
        "duration": 1.0,
        "resources": 2,
        "dependencies": ["V"]
    },
    "Y": {
        "name": "Installing steel beams 2 and inspect",
        "duration": 4.0,
        "resources": 2,
        "dependencies": ["X"]
    },
    "Z": {
        "name": "Photo",
        "duration": 1.0,
        "resources": 23,
        "dependencies": ["Y"]
    }
}