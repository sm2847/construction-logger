activities = [
    {
        "code": "A",
        "id": "ST00010",
        "activity": "Site setup",
        "planned_workers": 4,
        "planned_duration": 1.0,
        "dependencies": "-"
    },
    {
        "code": "B",
        "id": "ST00020",
        "activity": "Surveying of bridge abutments",
        "planned_workers": 2,
        "planned_duration": 2.0,
        "dependencies": "A"
    },
    {
        "code": "C",
        "id": "ST00030",
        "activity": "Fixing points into concrete substructure",
        "planned_workers": 4,
        "planned_duration": 1.0,
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
        "planned_duration": 1.0,
        "dependencies": "C, D"
    },
    {
        "code": "F",
        "id": "ST00060",
        "activity": "Fixing shell abutment details",
        "planned_workers": 2,
        "planned_duration": 1.0,
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
        "planned_duration": 1.0,
        "dependencies": "F, G"
    },
    {
        "code": "I",
        "id": "ST00090",
        "activity": "Steel delivery 1 and inspect",
        "planned_workers": 2,
        "planned_duration": 1.0,
        "dependencies": "A"
    },
    {
        "code": "J",
        "id": "ST00100",
        "activity": "Installing steel beams 1 and inspect",
        "planned_workers": 2,
        "planned_duration": 3.0,
        "dependencies": "H, I"
    },
    {
        "code": "K",
        "id": "ST00110",
        "activity": "Installing steel beams 2 and inspect",
        "planned_workers": 2,
        "planned_duration": 3.0,
        "dependencies": "H, J"
    },
    {
        "code": "L",
        "id": "ST00120",
        "activity": "Pouring concrete deck section 1",
        "planned_workers": 5,
        "planned_duration": 4.0,
        "dependencies": "K"
    },
    {
        "code": "M",
        "id": "ST00130",
        "activity": "Curing concrete deck section 1",
        "planned_workers": 1,
        "planned_duration": 24.0,
        "dependencies": "L"
    },
    {
        "code": "N",
        "id": "ST00140",
        "activity": "Pouring concrete deck section 2",
        "planned_workers": 5,
        "planned_duration": 4.0,
        "dependencies": "M"
    },
    {
        "code": "O",
        "id": "ST00150",
        "activity": "Curing concrete deck section 2",
        "planned_workers": 1,
        "planned_duration": 24.0,
        "dependencies": "N"
    },
    {
        "code": "P",
        "id": "ST00160",
        "activity": "Waterproofing bridge deck surface",
        "planned_workers": 3,
        "planned_duration": 2.0,
        "dependencies": "O"
    },
    {
        "code": "Q",
        "id": "ST00170",
        "activity": "Asphalt paving on bridge deck",
        "planned_workers": 6,
        "planned_duration": 3.0,
        "dependencies": "P"
    },
    {
        "code": "R",
        "id": "ST00180",
        "activity": "Install safety barriers and guardrails",
        "planned_workers": 4,
        "planned_duration": 2.0,
        "dependencies": "Q"
    },
    {
        "code": "S",
        "id": "ST00190",
        "activity": "Construct/install stairs and inspect",
        "planned_workers": 6,
        "planned_duration": 1.0,
        "dependencies": "-"
    },
    {
        "code": "T",
        "id": "ST00200",
        "activity": "Final site cleanup and inspection",
        "planned_workers": 4,
        "planned_duration": 1.5,
        "dependencies": "R, S"
    }
]