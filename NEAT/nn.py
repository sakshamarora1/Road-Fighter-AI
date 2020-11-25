import numpy as np
import dill
import copy


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def dsigmoid(x):
    return sigmoid(x) * (1 - sigmoid(x))


class NeuralNetwork:
    def __init__(
        self, inputNum, hiddenNum, outputNum, activation=sigmoid,
    ):
        self.input_nodes = inputNum
        self.hidden_nodes = hiddenNum
        self.output_nodes = outputNum

        self.weights_ih = np.random.rand(self.hidden_nodes, self.input_nodes) * 2 - 1
        self.bias_h = np.random.rand(self.hidden_nodes, 1) * 2 - 1
        self.weights_ho = np.random.rand(self.output_nodes, self.hidden_nodes) * 2 - 1
        self.bias_o = np.random.rand(self.output_nodes, 1) * 2 - 1

        self.activation = np.vectorize(activation)

    def predict(self, input_list):
        inputs = np.asarray(input_list, float).reshape(-1, 1)

        hidden = np.matmul(self.weights_ih, inputs)
        hidden += self.bias_h
        hidden = self.activation(hidden)

        output = np.matmul(self.weights_ho, hidden)
        output += self.bias_o
        output = self.activation(output)

        return output.tolist()

    def serialize(self) -> bytes:
        return dill.dumps(self)

    @staticmethod
    def deserialize(data: bytes) -> "NeuralNetwork":
        return dill.loads(data)

    def mutate(self, func):
        func = np.vectorize(func)
        self.weights_ho = func(self.weights_ho)
        self.weights_ih = func(self.weights_ih)
        self.bias_o = func(self.bias_o)
        self.bias_h = func(self.bias_h)

    def copy(self):
        return copy.copy(self)
