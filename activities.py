activities = [
    {
        "code": "A",
        "id": "ST00010",
        "activity": "Site setup",
        "planned_workers": 4,
        "planned_duration": 1,
        "dependencies": "-"
    },
    {
        "code": "B",
        "id": "ST00020",
        "activity": "Surveying of bridge abutments",
        "planned_workers": 2,
        "planned_duration": 2,
        "dependencies": "A"
    },
    {
        "code": "C",
        "id": "ST00030",
        "activity": "Fixing points into concrete substructure",
        "planned_workers": 4,
        "planned_duration": 1,
        "dependencies": "B"
    },
    {
        "code": "D",
        "id": "ST00040",
        "activity": "Shell abutments delivered and inspect",
        "planned_workers": 2,
        "planned_duration": 0.5,
        "dependencies": "C"
    },
    {
        "code": "E",
        "id": "ST00050",
        "activity": "Position shell abutments and inspect",
        "planned_workers": 2,
        "planned_duration": 1,
        "dependencies": "C, D"
    },
    {
        "code": "F",
        "id": "ST00060",
        "activity": "Fixing shell abutment details",
        "planned_workers": 2,
        "planned_duration": 1,
        "dependencies": "E"
    },
    {
        "code": "G",
        "id": "ST00070",
        "activity": "Capping slabs delivered and inspect",
        "planned_workers": 2,
        "planned_duration": 0.5,
        "dependencies": "F"
    },
    {
        "code": "H",
        "id": "ST00080",
        "activity": "Install capping slabs and inspect",
        "planned_workers": 2,
        "planned_duration": 1,
        "dependencies": "F, G"
    },
    {
        "code": "I",
        "id": "ST00090",
        "activity": "Steel delivery 1 and inspect",
        "planned_workers": 2,
        "planned_duration": 1,
        "dependencies": "A"
    },
    {
        "code": "J",
        "id": "ST00100",
        "activity": "Installing steel beams 1 and inspect",
        "planned_workers": 2,
        "planned_duration": 3,
        "dependencies": "H, I"
    },
    {
        "code": "K",
        "id": "ST00110",
        "activity": "Installing steel beams 2 and inspect",
        "planned_workers": 2,
        "planned_duration": 3,
        "dependencies": "H, J"
    },
    {
        "code": "S",
        "id": "ST00190",
        "activity": "Construct/install stairs and inspect",
        "planned_workers": 6,
        "planned_duration": 1,
        "dependencies": "-"
    }
]