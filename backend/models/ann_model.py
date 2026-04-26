import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


# Generate training data
def generate_data():
    X = []
    y = []

    for _ in range(500):
        similarity = np.random.rand()
        skill_match = np.random.rand()

        score = 0.6 * similarity + 0.4 * skill_match

        X.append([similarity, skill_match])
        y.append(score)

    return np.array(X), np.array(y)


# Train ANN model
def train_model():
    X, y = generate_data()

    model = Sequential([
        Dense(8, activation='relu', input_shape=(2,)),
        Dense(4, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=50, verbose=0)

    return model


# Predict score
def predict_score(model, similarity, skill_match):
    input_data = np.array([[similarity, skill_match]])
    prediction = model.predict(input_data, verbose=0)
    return float(prediction[0][0])


# Test independently
if __name__ == "__main__":
    print("Testing ANN independently...")

    model = train_model()
    print("Model trained")

    test_score = predict_score(model, 0.5, 0.5)
    print("Test ANN Score:", test_score)