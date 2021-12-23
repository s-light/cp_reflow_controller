import profiles

"""Test StepTime"""


class Test_StepTime(profiles.Profile):
    """Test StepTime"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "Test_StepTime"
        self.title = "Test StepTime"
        self.title_short = "Test StepTime"
        self.alloy = "-"
        self.melting_point = 220
        self.reference = "-"
        self.steps = [
            {
                "stage": "set40",
                "duration": 0,
                "temp_target": 40,
            },
            {
                "stage": "hold40",
                "duration": 120,
                "temp_target": 40,
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
