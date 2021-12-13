import profiles

"""Felder ISO-Cream 'Clear' (no-clean) FAST"""


class Felder_ISO_Cream_Clear_FAST(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean) FAST"""

    # __name__ msut be the same as the class name
    __name__ = "Felder_ISO_Cream_Clear_FAST"
    title = "Felder ISO-Cream 'Clear' (no-clean) FAST"
    title_short = "Felder ISO-Cream FAST"
    alloy = "Sn96,5Ag3,0Cu0,5"
    melting_point = 220
    reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
    profile = [
        {
            "stage": "preheat",
            "duration": 120,
            "temp_target": 150,
        },
        {
            "stage": "soak",
            "duration": 50,
            "temp_target": 200,
        },
        {
            "stage": "reflow",
            "duration": 30,
            "temp_target": 248,
        },
        {
            "stage": "cool",
            "duration": 120,
            "temp_target": 0,
        },
    ]
