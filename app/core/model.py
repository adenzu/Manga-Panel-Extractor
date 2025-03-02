from app.core.utils import execute_with_unix_path


class Model:
    def __init__(self):
        self.model = None
        self.imported = False

    def load(self):
        if self.model is None:
            self.__load()

    def __load(self):
        if not self.imported:
            self.imported = True
            import torch
            import sys
            import os
            from app.core.utils import resource_path

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if device == "cpu":
            print(
                f"The YOLOv5 model will be run on {device}. If you think it should be able to run on cuda, reach out to the developer."
            )

        # Redirect sys.stderr to a file or a valid stream
        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w")

        # If load is called directly it throws some error that is fixed by execute_with_unix_path
        # I do not remember why, ChatGPT solved it
        self.model = execute_with_unix_path(
            lambda: (
                torch.hub.load(
                    "ultralytics/yolov5",
                    "custom",
                    path=resource_path("app/core/resources/best.pt"),
                ).to(device)
            )
        )

    def __call__(self, *args, **kwargs):
        if self.model is None:
            self.__load()
        return self.model(*args, **kwargs)


model = Model()
