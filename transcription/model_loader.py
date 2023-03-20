from torch import device, cuda
# from whisper import load_model
from faster_whisper import WhisperModel


class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        # Set the device to use the first GPU
        # input_device = device('cuda:0' if cuda.is_available() else 'cpu')
        input_device = device('cpu')

        print("Loading large model...")
        model_path = "model/whisper-large-v2-ct2-int8_float16/"
        # self.model = load_model("tiny").to(input_device)
        print("Large model loaded")
        self.model = WhisperModel(model_path, device="cpu", compute_type="int8")

    def get_model(self):
        if self.model is None:
            self.load_model()
        return self.model
