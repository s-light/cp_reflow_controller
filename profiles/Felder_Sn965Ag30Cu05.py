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
        # duration: 600s = 10min
        self.steps = [
            # prepare for 90s
            {
                "name": "prepare",
                "duration": 70,
                "temp_target": 50,
            },
            {
                "name": "prepareHOLD",
                "duration": 20,
                "temp_target": 50,
            },
            # now all things should be at 50°C.
            # that is a good starting point.
            # datasheet recommendations:
            # START-150°C
            # 120-210s
            {
                "name": "preheat",
                "duration": 180,
                "temp_target": 150,
            },
            # datasheet recommendations:
            # 150-200°C
            # 50-120s
            {
                "name": "soak",
                "duration": 70,
                "temp_target": 200,
            },
            # datasheet recommendations:
            # 200-240°C
            # 60-90s
            # in liquid state -> above  ~217°C
            {
                "name": "reflow",
                "duration": 25,
                "temp_target": 235,
            },
            {
                "name": "reflow_hold",
                "duration": 45,
                "temp_target": 235,
            },
            {
                "name": "cool_set",
                "duration": 5,
                "temp_target": 45,
            },
            {
                "name": "cool",
                # datasheet recommendations:
                # 70s
                # we currently have no active cooling
                # so we have to wait...
                "duration": 190 - 5,
                "temp_target": 45,
            },
            # {
            #     "name": "cool_save",
            #     "duration": 10,
            #     "temp_target": 0,
            # },
        ]
