from tensorflow import keras


class Brain:
    def __init__(self, weights=None):
        self.brain = self.model()

    def model(self):
        model = keras.Sequential()
        model.add(keras.layers.Input(shape=(4,)))
        # model.add(keras.layers.Dense(4, input_shape=(4,)))
        model.add(keras.layers.Dense(1, activation="sigmoid"))
        return model

