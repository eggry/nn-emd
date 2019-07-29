from nn.nn_mnist import NeuralNetMLP
from nn.utils_nn_mnist import load_mnist, load_mnist_size
import numpy as np
import sys
import time


def test_nn_mnist():
    X_train, y_train = load_mnist_size('../nn/datasets/', size=2000, kind='train')
    X_test, y_test = load_mnist('../nn/datasets/', kind='t10k')
    nn = NeuralNetMLP(n_output=10,
                      n_features=X_train.shape[1],
                      n_hidden=10, # default 50
                      l2=0.1,
                      l1=0.0,
                      epochs=10, # default 1000
                      eta=0.001,
                      alpha=0.001,
                      decrease_const=0.00001,
                      minibatches=50,
                      shuffle=True,
                      random_state=1)
    nn.fit(X_train, y_train, print_progress=True)

    # plt.plot(range(len(nn.cost_)), nn.cost_)
    # plt.ylim([0, 2000])
    # plt.ylabel('Cost')
    # plt.xlabel('Epochs * 50')
    # plt.tight_layout()
    # # plt.savefig('./figures/cost.png', dpi=300)
    # plt.show()

    # batches = np.array_split(range(len(nn.cost_)), 1000)
    # cost_ary = np.array(nn.cost_)
    # cost_avgs = [np.mean(cost_ary[i]) for i in batches]
    # plt.plot(range(len(cost_avgs)), cost_avgs, color='red')
    # plt.ylim([0, 2000])
    # plt.ylabel('Cost')
    # plt.xlabel('Epochs')
    # plt.tight_layout()
    # # plt.savefig('./figures/cost2.png', dpi=300)
    # plt.show()

    y_train_pred = nn.predict(X_train)
    # print(y_train_pred)

    if sys.version_info < (3, 0):
        acc = ((np.sum(y_train == y_train_pred, axis=0)).astype('float') /
               X_train.shape[0])
    else:
        acc = np.sum(y_train == y_train_pred, axis=0) / X_train.shape[0]
    print('Training accuracy: %.2f%%' % (acc * 100))

    y_test_pred = nn.predict(X_test)

    if sys.version_info < (3, 0):
        acc = ((np.sum(y_test == y_test_pred, axis=0)).astype('float') /
               X_test.shape[0])
    else:
        acc = np.sum(y_test == y_test_pred, axis=0) / X_test.shape[0]
    print('Test accuracy: %.2f%%' % (acc * 100))

    # miscl_img = X_test[y_test != y_test_pred][:25]
    # correct_lab = y_test[y_test != y_test_pred][:25]
    # miscl_lab = y_test_pred[y_test != y_test_pred][:25]
    #
    # fig, ax = plt.subplots(nrows=5, ncols=5, sharex=True, sharey=True, )
    # ax = ax.flatten()
    # for i in range(25):
    #     img = miscl_img[i].reshape(28, 28)
    #     ax[i].imshow(img, cmap='Greys', interpolation='nearest')
    #     ax[i].set_title('%d) t: %d p: %d' % (i + 1, correct_lab[i], miscl_lab[i]))
    #
    # ax[0].set_xticks([])
    # ax[0].set_yticks([])
    # plt.tight_layout()
    # # plt.savefig('./figures/mnist_miscl.png', dpi=300)
    # plt.show()

def test_nn_mnist_secure():
    X_train, y_train = load_mnist('../nn/datasets/', kind='train')
    X_test, y_test = load_mnist('../nn/datasets/', kind='t10k')
    nn = NeuralNetMLP(n_output=10,
                      n_features=X_train.shape[1],
                      n_hidden=50,
                      l2=0.1,
                      l1=0.0,
                      epochs=5, # set 10 as test
                      eta=0.001,
                      alpha=0.001,
                      decrease_const=0.00001,
                      minibatches=50,
                      shuffle=True,
                      random_state=1,
                      sc_flag=True)
    nn.fit(X_train, y_train, print_progress=True)

    y_train_pred = nn.predict(X_train)
    print(y_train_pred)

    if sys.version_info < (3, 0):
        acc = ((np.sum(y_train == y_train_pred, axis=0)).astype('float') /
               X_train.shape[0])
    else:
        acc = np.sum(y_train == y_train_pred, axis=0) / X_train.shape[0]
    print('Training accuracy: %.2f%%' % (acc * 100))

    y_test_pred = nn.predict(X_test)

    if sys.version_info < (3, 0):
        acc = ((np.sum(y_test == y_test_pred, axis=0)).astype('float') /
               X_test.shape[0])
    else:
        acc = np.sum(y_test == y_test_pred, axis=0) / X_test.shape[0]
    print('Test accuracy: %.2f%%' % (acc * 100))


if __name__ == "__main__":
    t1 = time.time()
    test_nn_mnist()
    t2 = time.time()
    print("original cost: ")
    print(t2 - t1)
    # test_nn_mnist_secure()
    # t3 = time.time()
    # print("secure training cost: ")
    # print(t3-t2)