import profiles

"""TestDev Profile"""


class TestDev_Profile_Slow(profiles.Profile):
    """TestDev Profile"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "TestDev_Profile_Slow"
        self.title = "TestDev Profile Slow "
        self.title_short = "TestDev Profile Slow"
        self.alloy = "42"
        self.melting_point = 35
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
        self.steps = [
            {
                "stage": "preheat",
                "duration": 20,
                "temp_target": 30,
            },
            {
                "stage": "soak",
                "duration": 20,
                "temp_target": 50,
            },
            {
                "stage": "reflow",
                "duration": 30,
                "temp_target": 80,
            },
            {
                "stage": "cool",
                "duration": 120,
                "temp_target": 0,
            },
        ]
