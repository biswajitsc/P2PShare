from sknn.mlp import Regressor,Layer,Classifier
import numpy as np
import random

# X_train = np.array([[0,0],[0,1],[1,0],[1,1]])
# y_train = np.array([[0],[0],[0],[1]])
X_train = []
y_train = []
for i in range(50000):
	val1 = random.random()
	val2 = random.random()
	if val1 <= 0.2 and val2 <= 0.2:
		X_train.append(list([val1, val2]))
		y_train.append(list([0]))
	elif val1 <= 0.2 and val2 >= 0.8:
		X_train.append(list([val1, val2]))
		y_train.append(list([0]))
	elif val1 >= 0.8 and val2 <= 0.2:
		X_train.append(list([val1, val2]))
		y_train.append(list([0]))
	elif val1 >= 0.8 and val2 >= 0.8:
		X_train.append(list([val1, val2]))
		y_train.append(list([1]))
print "size of training data : ", len(X_train), len(y_train)
X_train = np.array(X_train)
y_train = np.array(y_train)
nn = Classifier(layers=[Layer("Sigmoid", units=4), Layer("Softmax", units=2)],learning_rate=0.01,n_iter=20)
# print nn.get_params()
nn.fit(X_train, y_train)
# print nn.get_parameters()
X_example = np.array([[0,0],[0,1],[1,0],[1,1]])
y_example = nn.predict(X_example)
print y_example