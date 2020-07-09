import numpy as np
import tensorflow as tf
import scipy.io.wavfile as wavfile
import scipy.signal
from utils import gcc_phat, gcc_gammatoneFilter
from CONFIG import *
import pickle

class DataGenerator(tf.keras.utils.Sequence):
    'Generates data for Keras'
    def __init__(self, dataFrame, features, num_classe, batch_size=32, dim=(32,32,32), n_channels=1,
                 resample=0, shuffle=True):

        'Initialization'
        self.df = dataFrame
        self.dim = dim
        self.batch_size = batch_size
        self.get_labels()
        self.list_IDs = dataFrame['audio_filename']
        self.n_channels = n_channels
        self.n_classes = num_classe
        self.shuffle = shuffle
        self.on_epoch_end()
        self.resampling = resample
        self.features = features

        self.max_tau = DISTANCE_MIC / 343.2


    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

        # Find list of IDs
        list_IDs_temp = [self.list_IDs[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(list_IDs_temp)

        return X, y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def get_labels(self):
        self.labels = {}

        for index, item in self.df.iterrows():
            self.labels[item['audio_filename']] = item['labels']

    def __data_generation(self, list_IDs_temp):
        'Generates data containing batch_size samples' # X : (n_samples, *dim, n_channels)
        # Initialization
        X = np.empty((self.batch_size, *self.dim, self.n_channels))
        y = np.empty(self.batch_size, dtype=int)

        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            if self.features == 'gammatone':
                input_x = pickle.load(open(ID.split('.wav')[0], 'rb'))
                input_x = input_x.reshape(input_x.shape[1], input_x.shape[0])
                input_x = np.expand_dims(input_x, axis=-1)

            else:
                fs, signal = wavfile.read(ID, "wb")
                signal1 = signal[:, 0]
                signal2 = signal[:, 1]

                if self.resampling:
                    nb_samples = round(len(signal1) * float(self.resampling) / fs)
                    signal1 = np.array(scipy.signal.resample(signal1, nb_samples), dtype=np.float32)
                    signal2 = np.array(scipy.signal.resample(signal2, nb_samples), dtype=np.float32)

                elif self.features == 'gcc-phat':
                    window_hanning = np.hanning(fs)
                    delay, gcc = gcc_phat(signal1 * window_hanning, signal2 * window_hanning, RESAMPLING_F, self.max_tau,
                                              n_delay=N_DELAY)
                    input_x = np.expand_dims(delay, axis=-1)
                else:
                    input_x = np.stack((signal1, signal2), axis=-1)

            # Store sample
            X[i,] = input_x

            # Store class
            y[i] = self.labels[ID]

        return X, tf.keras.utils.to_categorical(y, num_classes=self.n_classes)

