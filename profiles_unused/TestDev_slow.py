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
        self.melting_point = 110
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
        # runtime = 40 + 40 + 30 + 30 + 30 + 230 = 400 = 6,7min
        self.steps = [
            {
                "name": "prepare40",
                "duration": 40,
                "temp_target": 40,
            },
            {
                "name": "wait40",
                "duration": 40,
                "temp_target": 40,
            },
            {
                "name": "soak",
                "duration": 30,
                "temp_target": 70,
            },
            {
                "name": "wait70",
                "duration": 30,
                "temp_target": 70,
            },
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 110,
            },
            {
                "name": "cool_set",
                "duration": 0,
                "temp_target": 40,
            },
            {
                "name": "cool",
                "duration": 230,
                "temp_target": 0,
            },
        ]
