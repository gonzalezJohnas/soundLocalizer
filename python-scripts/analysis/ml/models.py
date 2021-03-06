import tensorflow as tf
from tensorflow.keras.backend import squeeze
from tensorflow.keras.applications.vgg16 import VGG16
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from CONFIG import *



#########################################################################################
#                               MODELS ONE INPUT                                        #
#########################################################################################

def get_model_cnn(input_shape, output_shape, regression=False):
    activation_output = "softmax"

    if regression:
        output_shape = 1
        activation_output = "linear"

    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(input_shape),

        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(L2_REGULARIZATION)),
        tf.keras.layers.MaxPooling2D((2, 2)),



        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(output_shape, activation=activation_output)


    ])

    return model


def get_model_dense_simple(input_shape, output_shape, regression=False):
    activation_output = "softmax"

    if regression:
        output_shape = 1
        activation_output = "linear"

    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(input_shape),
        tf.keras.layers.Dense(1024, activation="relu"),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(output_shape, activation=activation_output),

    ])

    return model


def get_model_1dcnn(input_shape, output_shape):
    model = tf.keras.models.Sequential([

        tf.keras.layers.Input(input_shape),

        tf.keras.layers.Conv1D(filters=32, kernel_size=7, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(1e-2)),
        tf.keras.layers.Conv1D(filters=32, kernel_size=7, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(1e-2)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(7),

        tf.keras.layers.Conv1D(filters=64, kernel_size=5, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(1e-2)),
        tf.keras.layers.Conv1D(filters=64, kernel_size=5, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(1e-2)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(5),

        tf.keras.layers.Conv1D(filters=128, kernel_size=3, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(1e-2)),
        tf.keras.layers.BatchNormalization(),
        #
        # tf.keras.layers.Reshape((-1, 256)),
        # tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
        # tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(rate=0.4),
        tf.keras.layers.Dense(output_shape, activation="softmax")
    ])

    return model


def simple_lstm(output_dim):
    model = tf.keras.Sequential()

    # Add a LSTM layer with 128 internal units.

    model.add(tf.keras.layers.Conv1D(filters=90, kernel_size=7, activation='relu', padding='same',
                                     kernel_regularizer=tf.keras.regularizers.l2(0.0005)))
    model.add(tf.keras.layers.MaxPooling1D(2))

    model.add(tf.keras.layers.Conv1D(filters=50, kernel_size=7, activation='relu', padding='same',
                                     kernel_regularizer=tf.keras.regularizers.l2(0.0005)))

    model.add(tf.keras.layers.MaxPooling1D(2))

    model.add(tf.keras.layers.Reshape((-1, 50)))

    model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True)))

    model.add(tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)))

    model.add(tf.keras.layers.Dense(128, activation='relu'))

    model.add(tf.keras.layers.Dense(64, activation='relu'))

    model.add(tf.keras.layers.Dropout(rate=1 - 0.5))

    model.add(tf.keras.layers.Dense(output_dim, activation='softmax'))

    return model


#########################################################################################
#                               MODELS TWO INPUTS                                       #
#########################################################################################


def get_model_dense(input_shape, output_shape, reg=False):
    inputs = tf.keras.layers.Input(input_shape)

    x = tf.keras.layers.Dense(512, activation="relu")(inputs)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(rate=0.5)(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(rate=0.5)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(rate=0.5)(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.Model(inputs=inputs, outputs=x)


    # Model for head position
    input_head = tf.keras.layers.Input((1, 1))
    y = tf.keras.layers.Lambda(lambda x: tf.keras.backend.squeeze(x, 2))(input_head)

    y = tf.keras.Model(inputs=input_head, outputs=y)
    # combine the output of the two branches
    combined = tf.keras.layers.concatenate([x.output, y.output])

    # apply a FC layer and then a regression prediction on the
    # combined outputs
    z = tf.keras.layers.Dense(128, activation='relu')(combined)
    z = tf.keras.layers.Dropout(0.4)(z)
    z = tf.keras.layers.Dense(64, activation='relu')(z)
    z = tf.keras.layers.Dropout(0.4)(z)

    if reg:
        output = tf.keras.layers.Dense(1, activation="linear")(z)
    else:
        output = tf.keras.layers.Dense(output_shape, activation="softmax", name='output')(z)

    # our model will accept the inputs of the two branches and
    # then output a single value
    model = tf.keras.Model(inputs=[x.input, y.input], outputs=output)

    return model

def get_model_head_1dcnn(input_shape, output_dim=11, reg=False):

    # Model for audio
    inputs = tf.keras.layers.Input(input_shape)

    x = tf.keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(0.05))(inputs)
    x = tf.keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l2(0.05))(x)
    # x = tf.keras.layers.BatchNormalization() (x)
    x = tf.keras.layers.MaxPooling1D(3)(x)

    x = tf.keras.layers.Conv1D(filters=96, kernel_size=3, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05)) (inputs)
    x = tf.keras.layers.Conv1D(filters=96, kernel_size=3, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05))(x)
    # x = tf.keras.layers.BatchNormalization() (x)
    x = tf.keras.layers.MaxPooling1D(3) (x)

    x = tf.keras.layers.Conv1D(filters=128, kernel_size=5, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05)) (inputs)
    x = tf.keras.layers.Conv1D(filters=128, kernel_size=5, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05))(x)
    # x = tf.keras.layers.BatchNormalization() (x)
    x = tf.keras.layers.MaxPooling1D(3) (x)

    x = tf.keras.layers.Conv1D(filters=256, kernel_size=7, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05)) (inputs)
    x = tf.keras.layers.Conv1D(filters=256, kernel_size=7, activation='relu', padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(0.05))(x)
    # x = tf.keras.layers.BatchNormalization() (x)
    x = tf.keras.layers.MaxPooling1D(3) (x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.Model(inputs=inputs, outputs=x)

    # Model for head position
    input_head = tf.keras.layers.Input((1, 1))
    y = tf.keras.layers.Lambda(lambda x: tf.keras.backend.squeeze(x, 2))(input_head)

    y = tf.keras.Model(inputs=input_head, outputs=y)

    # combine the output of the two branches
    combined = tf.keras.layers.concatenate([x.output, y.output])

    # apply a FC layer and then a regression prediction on the
    # combined outputs
    z = tf.keras.layers.Dense(256, activation='relu')(combined)
    z = tf.keras.layers.Dropout(0.4)(z)
    z = tf.keras.layers.Dense(64, activation='relu')(z)
    z = tf.keras.layers.Dropout(0.4)(z)

    if reg:
        output = tf.keras.layers.Dense(1, activation="linear")(z)
    else:
        output = tf.keras.layers.Dense(output_dim, activation="softmax", name='output')(z)

    # our model will accept the inputs of the two branches and
    # then output a single value
    model = tf.keras.Model(inputs=[x.input, y.input], outputs=output)

    return model


def get_model_head_cnn(input_shape, output_dim=11, regression=False):

    # Model for audio
    inputs = tf.keras.layers.Input(input_shape)


    x = tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-2, l2=1e-2))(inputs)
    x = tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-2, l2=1e-2))(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)


    x = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)
    x = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)


    x = tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)
    x = tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)


    x = tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)
    x = tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), activation='relu', padding='same',
                               kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4))(x)


    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.Model(inputs=inputs, outputs=x)

    # Model for head position
    input_head = tf.keras.layers.Input((1, 1))
    y = tf.keras.layers.Lambda(lambda x: tf.keras.backend.squeeze(x, 2))(input_head)

    y = tf.keras.Model(inputs=input_head, outputs=y)

    # combine the output of the two branches
    combined = tf.keras.layers.concatenate([x.output, y.output])

    # apply a FC layer and then a regression prediction on the
    # combined outputs
    z = tf.keras.layers.Dense(128, activation='relu')(combined)

    z = tf.keras.layers.Dense(32, activation='relu')(z)
    z = tf.keras.layers.Dropout(0.4) (z)


    if regression:
        output = tf.keras.layers.Dense(1, activation="linear")(z)
    else:
        output = tf.keras.layers.Dense(output_dim, activation="softmax", name='output')(z)

    # our model will accept the inputs of the two branches and
    # then output a single value
    model = tf.keras.Model(inputs=[x.input, y.input], outputs=output)

    return model


def conv_net_lstm_attention(input_shape, output_dim=11):
    inputs = tf.keras.layers.Input(input_shape)

    x = tf.keras.layers.Conv2D(filters=128, kernel_size=(7, 2), activation='relu', padding='same')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Conv2D(filters=90, kernel_size=(3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Reshape((-1, 64))(x)

    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True))(x)
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True))(x)

    xFirst = tf.keras.layers.Lambda(lambda q: q[:, 128])(x)  # [b_s, vec_dim]
    query = tf.keras.layers.Dense(256)(xFirst)

    # dot product attention
    attScores = tf.keras.layers.Dot(axes=[1, 2])([query, x])
    attScores = tf.keras.layers.Softmax(name='attSoftmax')(attScores)  # [b_s, seq_len]

    # rescale sequence
    attVector = tf.keras.layers.Dot(axes=[1, 1])([attScores, x])  # [b_s, vec_dim]

    x = tf.keras.layers.Dense(256, activation='relu')(attVector)
    x = tf.keras.Model(inputs=inputs, outputs=x)

    # Model for head position
    input_head = tf.keras.layers.Input((1, 1))
    y = tf.keras.layers.Lambda(lambda x: tf.keras.backend.squeeze(x, 2))(input_head)
    y = tf.keras.Model(inputs=input_head, outputs=y)

    # combine the output of the two branches
    combined = tf.keras.layers.concatenate([x.output, y.output])
    z = tf.keras.layers.Dense(128, activation='relu')(combined)
    z = tf.keras.layers.Dropout(0.3)(z)

    output = tf.keras.layers.Dense(output_dim, activation='softmax', name='output')(z)

    model = tf.keras.Model(inputs=[x.input, y.input], outputs=output)

    return model
