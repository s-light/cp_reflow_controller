import profiles

"""Plastic"""


class Plastic(profiles.Profile):
    """Plastic"""

    def config(self):
        # __name__ must be the same as the class name
        self.__name__ = "Plastic"
        self.title = "Plastic 59°C"
        self.title_short = "Plastic 59°C"
        self.alloy = "42"
        self.melting_point = 59
        self.reference = "https://blog.s-light.eu/hot-plate-smd-soldering/"
        # runtime = 40 + 40 + 30 + 30 + 30 + 230 = 400 = 6,7min
        self.steps = [
            {
                "name": "prepare",
                "duration": 3,
                "temp_target": 59,
            },
            {
                "name": "reflow",
                "duration": 30 * 60,
                "temp_target": 59,
            },
        ]
