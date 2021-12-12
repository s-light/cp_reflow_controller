import profiles

"""Felder ISO-Cream 'Clear' (no-clean) SLOW"""


class Felder_ISO_Cream_Clear_SLOW(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean) SLOW"""

    title = "Felder ISO-Cream 'Clear' (no-clean) SLOW"
    alloy = "Sn96,5Ag3,0Cu0,5"
    melting_point = 220
    reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
    profile = [
        {
            "stage": "preheat",
            "duration": 210,
            "temp_target": 150,
        },
        {
            "stage": "soak",
            "duration": 120,
            "temp_target": 200,
        },
        {
            "stage": "reflow",
            "duration": 50,
            "temp_target": 240,
        },
        {
            "stage": "cool",
            "duration": 130,
            "temp_target": 0,
        },
    ]
