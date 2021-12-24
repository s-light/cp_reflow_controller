import profiles

"""Felder ISO-Cream 'Clear' (no-clean)"""


class Felder_ISO_Cream_Clear(profiles.Profile):
    """Felder ISO-Cream 'Clear' (no-clean)"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "Felder_ISO_Cream_Clear"
        self.title = "Felder ISO-Cream 'Clear' (no-clean)"
        self.title_short = "Felder ISO-Cream"
        self.alloy = "Sn96,5Ag3,0Cu0,5"
        self.melting_point = 220
        self.reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
        self.steps = [
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
                # datasheet says 70s
                # we currently have no active cooling
                "duration": 180,
                "temp_target": 45,
            },
            # {
            #     "stage": "cool_save",
            #     "duration": 10,
            #     "temp_target": 0,
            # },
        ]
