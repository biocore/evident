class NoCommonSamplesError(Exception):
    def __init__(self):
        self.message = "No common samples."
        super().__init__(self.message)
