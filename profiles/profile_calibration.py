import profiles

"""Calibration Profile"""


class ProfileCalibration(profiles.Profile):
    """Calibration Profile"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "ProfileCalibration"
        self.title = "Calibration Profile"
        self.title_short = "Calibration Profil"
        self.alloy = "-"
        self.melting_point = 220
        self.reference = "-"
        self.steps = [
            {
                "stage": "set30",
                "duration": 0,
                "temp_target": 30,
            },
            {
                "stage": "hold30",
                "duration": 60,
                "temp_target": 30,
            },
            # {
            #     "stage": "heatup100",
            #     "duration": 10,
            #     "temp_target": 100,
            # },
            # {
            #     "stage": "hold100",
            #     "duration": 10,
            #     "temp_target": 100,
            # },
            # {
            #     "stage": "cool",
            #     "duration": 5,
            #     "temp_target": 0,
            # },
        ]
