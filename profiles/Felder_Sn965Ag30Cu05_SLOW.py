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
        # duration: 820s = 14min
        self.steps = [
            # prepare for 120s
            {
                "name": "prepare",
                "duration": 80,
                "temp_target": 50,
            },
            {
                "name": "prepareHOLD",
                "duration": 40,
                "temp_target": 50,
            },
            # now all things should be at 50°C.
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
            # and 60-90s in liquid state -> above  ~220°C
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 240,
            },
            {
                "name": "reflow_hold",
                "duration": 60,
                "temp_target": 248,
            },
            {
                "name": "cool_set",
                "duration": 2,
                "temp_target": 45,
            },
            {
                "name": "cool",
                # datasheet says 70s
                # we currently have no active cooling
                # so we have to wait...
                "duration": 310 - 2,
                "temp_target": 45,
            },
            # {
            #     "name": "cool_save",
            #     "duration": 10,
            #     "temp_target": 0,
            # },
        ]
