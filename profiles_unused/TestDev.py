import profiles

"""TestDev Profile"""


class TestDev_Profile(profiles.Profile):
    """TestDev Profile"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "TestDev_Profile"
        self.title = "TestDev Profile"
        self.title_short = "TestDev Profile"
        self.alloy = "42"
        self.melting_point = 220
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
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
