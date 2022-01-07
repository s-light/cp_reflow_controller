import profiles

"""Calibration Profile"""


class ProfileCalibration(profiles.Profile):
    """Calibration Profile"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "ProfileCalibration"
        self.title = "Calibration Profile"
        self.title_short = "Calibration Profile"
        self.alloy = "-"
        self.melting_point = 220
        self.reference = "-"
        self.steps = [
            {
                "name": "set40",
                "duration": 0,
                "temp_target": 40,
            },
            {
                "name": "hold40",
                "duration": 60,
                "temp_target": 40,
            },
            # {
            #     "name": "heatup100",
            #     "duration": 10,
            #     "temp_target": 100,
            # },
            # {
            #     "name": "hold100",
            #     "duration": 10,
            #     "temp_target": 100,
            # },
            # {
            #     "name": "cool",
            #     "duration": 5,
            #     "temp_target": 0,
            # },
        ]
