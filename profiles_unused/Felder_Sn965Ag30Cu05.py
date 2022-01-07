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
                "name": "prepare",
                "duration": 60,
                "temp_target": 50,
            },
            {
                "name": "preheat",
                "duration": 210,
                "temp_target": 150,
            },
            {
                "name": "soak",
                "duration": 90,
                "temp_target": 200,
            },
            # datasheet says:
            # about 40s
            # and 60-90s in liquid state -> above  ~120°C
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 220,
            },
            {
                "name": "reflow_hold",
                "duration": 60,
                "temp_target": 245,
            },
            {
                "name": "cool_set",
                "duration": 0,
                "temp_target": 45,
            },
            {
                "name": "cool",
                # datasheet says 70s
                # we currently have no active cooling
                # so we have to wait...
                "duration": 180,
                "temp_target": 45,
            },
            # {
            #     "name": "cool_save",
            #     "duration": 10,
            #     "temp_target": 0,
            # },
        ]
