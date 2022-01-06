import profiles

"""Felder ISO-Cream 'Clear' (no-clean) FAST"""


class Felder_ISO_Cream_Clear_FAST(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean) FAST"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "Felder_ISO_Cream_Clear_FAST"
        self.title = "Felder ISO-Cream 'Clear' (no-clean) FAST"
        self.title_short = "Felder ISO-Cream FAST"
        self.alloy = "Sn96,5Ag3,0Cu0,5"
        self.melting_point = 220
        self.reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
        self.steps = [
            {
                "name": "preheat",
                "duration": 120,
                "temp_target": 150,
            },
            {
                "name": "soak",
                "duration": 50,
                "temp_target": 200,
            },
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 248,
            },
            {
                "name": "cool",
                "duration": 120,
                "temp_target": 0,
            },
        ]
