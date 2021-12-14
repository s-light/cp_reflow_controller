import profiles

"""TestDev Profile"""


class TestDev_Profile(profiles.Profile):
    """TestDev Profile"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "TestDev_Profile"
        self.title = "TestDev Profile"
        self.title_short = "TestDev Profil"
        self.alloy = "Sn96,5Ag3,0Cu0,5"
        self.melting_point = 220
        self.reference = "https://www.felder.de/files/felder/pdf/DE_23-Clear.pdf"
        self.steps = [
            {
                "stage": "preheat",
                "duration": 5,
                "temp_target": 150,
            },
            {
                "stage": "soak",
                "duration": 5,
                "temp_target": 200,
            },
            {
                "stage": "reflow",
                "duration": 5,
                "temp_target": 245,
            },
            {
                "stage": "cool",
                "duration": 5,
                "temp_target": 0,
            },
        ]
