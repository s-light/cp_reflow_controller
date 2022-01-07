import profiles

"""TestDev Profile"""


class TestDev_60(profiles.Profile):
    """TestDev Profile 60°C"""

    def config(self):
        # __name__ msut be the same as the class name
        self.__name__ = "TestDev_60"
        self.title = "TestDev Profile 60°C"
        self.title_short = "TestDev 60°C"
        self.alloy = "42"
        self.melting_point = 60
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
        # runtime = 40 + 40 + 30 + 30 + 30 + 230 = 400 = 6,7min
        self.steps = [
            {
                "name": "prepare30",
                "duration": 40,
                "temp_target": 30,
            },
            {
                "name": "wait30",
                "duration": 40,
                "temp_target": 30,
            },
            {
                "name": "soak40",
                "duration": 30,
                "temp_target": 40,
            },
            {
                "name": "wait40",
                "duration": 30,
                "temp_target": 40,
            },
            {
                "name": "reflow",
                "duration": 30,
                "temp_target": 60,
            },
            {
                "name": "cool_set",
                "duration": 0,
                "temp_target": 25,
            },
            {
                "name": "cool",
                "duration": 230,
                "temp_target": 25,
            },
        ]
