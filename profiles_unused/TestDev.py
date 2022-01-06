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
                "name": "preheat",
                "duration": 5,
                "temp_target": 150,
            },
            {
                "name": "soak",
                "duration": 5,
                "temp_target": 200,
            },
            {
                "name": "reflow",
                "duration": 5,
                "temp_target": 245,
            },
            {
                "name": "cool",
                "duration": 5,
                "temp_target": 0,
            },
        ]
