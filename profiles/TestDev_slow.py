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
        self.melting_point = 60
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
        self.steps = [
            {
                "name": "preheat",
                "duration": 20,
                "temp_target": 30,
            },
            {
                "name": "soak",
                "duration": 20,
                "temp_target": 40,
            },
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 60,
            },
            {
                "name": "cool",
                "duration": 180,
                "temp_target": 0,
            },
        ]
