import profiles


class Felder_ISO_Cream_Clear(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean)"""

    title = __doc__
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
            "duration": 90,
            "temp_target": 200,
        },
        {
            "stage": "reflow",
            "duration": 40,
            "temp_target": 245,
        },
        {
            "stage": "cool",
            "duration": 70,
            "temp_target": 0,
        },
    ]


##########################################
if __name__ == "__main__":
    import sys

    print(42 * "*")
    print("Python Version: " + sys.version)
    print(42 * "*")
    print(__doc__)
    print(42 * "*")
    print("This Module has now stand alone functionality.")
    print(42 * "*")

##########################################
