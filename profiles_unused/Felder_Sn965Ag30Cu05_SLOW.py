import profiles

"""Felder ISO-Cream 'Clear' (no-clean) SLOW"""


class Felder_ISO_Cream_Clear_SLOW(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean) SLOW"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "Felder_ISO_Cream_Clear_SLOW"
        self.title = "Felder ISO-Cream 'Clear' (no-clean) SLOW"
        self.title_short = "Felder ISO-Cream SLOW"
        self.alloy = "Sn96,5Ag3,0Cu0,5"
        self.melting_point = 220
        self.reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
        self.steps = [
            {
                "name": "preheat",
                "duration": 210,
                "temp_target": 150,
            },
            {
                "name": "soak",
                "duration": 120,
                "temp_target": 200,
            },
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 240,
            },
            {
                "name": "reflow_hold",
                "duration": 60,
                "temp_target": 245,
            },
            {
                "name": "cool",
                "duration": 130,
                "temp_target": 0,
            },
        ]
