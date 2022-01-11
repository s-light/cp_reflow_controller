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
            # that is a good starting point.
            # datasheet recommendations:
            # START-150°C
            # 120-210s
            {
                "name": "preheat",
                "duration": 210,
                "temp_target": 150,
            },
            # datasheet recommendations:
            # 150-200°C
            # 50-120s
            {
                "name": "soak",
                "duration": 90,
                "temp_target": 200,
            },
            # datasheet recommendations:
            # 200-240°C
            # 60-90s
            # in liquid state -> above  ~217°C
            #
            # about 40s
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 240,
            },
            {
                "name": "reflow_hold",
                "duration": 60,
                "temp_target": 240,
            },
            {
                "name": "cool_set",
                "duration": 2,
                "temp_target": 50,
            },
            {
                "name": "cool",
                # datasheet recommendations:
                # 70s
                # we currently have no active cooling
                # so we have to wait...
                "duration": 290 - 2,
                "temp_target": 40,
            },
            # {
            #     "name": "cool_save",
            #     "duration": 10,
            #     "temp_target": 0,
            # },
        ]
