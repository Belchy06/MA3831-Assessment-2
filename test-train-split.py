from collections import namedtuple

import numpy as np
import pandas as pd
import time

import matplotlib.pyplot as plt
from sklearn import metrics

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

if __name__ == '__main__':
    data = pd.read_csv('unique_NLP_resources.csv')
    processed_features = data.iloc[:, 3].values.astype(str)
    labels = data.iloc[:, 0].values.astype(str)
    X_train, X_test, y_train, y_test = train_test_split(processed_features, labels, test_size=0.2, random_state=0)
    struct = namedtuple('struct', 'accuracies n')
    knn_structs = []
    svc_structs = []
    gnb_structs = []
    for n in range(1, 4):
        print('\nn: {}'.format(n))
        start_time = time.time()
        vectorizer = CountVectorizer(ngram_range=(1, n)).fit(X_train)
        fit_time = time.time() - start_time
        x_test = vectorizer.transform(X_test)
        x_train = vectorizer.transform(X_train)
        print('X test shape: {}'.format(x_test.shape))
        for i in range(3):
            if i == 0:
                k_range = range(1, 10)
                best_accuracy = [0, 0]
                run_times = []
                accuracies = []
                print('KNN:')
                for k in k_range:
                    start_time = time.time()
                    knn = KNeighborsClassifier(n_neighbors=k)
                    knn.fit(x_train, y_train)
                    predictions = knn.predict(x_test)
                    accuracy = accuracy_score(y_test, predictions)
                    accuracies.append(accuracy)
                    run_time = time.time() - start_time
                    run_times.append(run_time)
                    if accuracy > best_accuracy[0]:
                        best_accuracy[0] = accuracy
                        best_accuracy[1] = k
                    # print('-' * 200)
                    # print('K: {}, Accuracy: {}, Fit Time: {}, Run Time: {}'.format(k, accuracy, fit_time, run_time))
                s = struct(accuracies=accuracies, n=n)
                knn_structs.append(s)
                print('Best Accuracy: {} @ k: {}'.format(best_accuracy[0], best_accuracy[1]))
                print('Average run time: {}'.format(np.mean(run_times)))
                print('=' * 200)

            elif i == 1:
                print('SVC:')
                scoring = ['accuracy']
                clf = SVC(kernel='linear')
                scores = cross_validate(clf, x_test, y_test, scoring=scoring, cv=5, return_train_score=False)
                s = struct(accuracies=scores.get('test_accuracy'), n=n)
                svc_structs.append(s)
                print('Best Accuracy: {}'.format(np.max(scores.get('test_accuracy'))))
                print('Average run time: {}'.format(np.mean(scores.get('fit_time') + scores.get('score_time'))))
                print('=' * 200)

            elif i == 2:
                # pass
                try:
                    print('GNB:')
                    gnb = GaussianNB()
                    start_time = time.time()
                    gnb.fit(x_train.toarray(), y_train)
                    print('Fit Time: {}'.format(time.time() - start_time))
                    start_time = time.time()
                    y_pred = gnb.predict(x_test.toarray())
                    print('Pred time: {}'.format(time.time() - start_time))
                    accuracy = metrics.accuracy_score(y_test, y_pred)
                    print('Accuracy: {}'.format(accuracy))
                    print('=' * 200)
                    s = struct(accuracies=accuracy, n=n)
                    gnb_structs.append(s)
                except Exception:
                    print('not enough mem')
    dat = []
    for s in knn_structs:
        dat.append(s.accuracies)
    plt.figure(0)
    plt.boxplot(dat)
    plt.xlabel('n')
    plt.ylabel('accuracy')
    plt.title('KNN Accuracy with n-grams')
    plt.show()

    dat = []
    for s in svc_structs:
        dat.append(s.accuracies)
    plt.figure(1)
    plt.boxplot(dat)
    plt.xlabel('n')
    plt.ylabel('accuracy')
    plt.title('SVC Accuracy with n-grams')
    plt.show()

    dat = []
    for s in gnb_structs:
        dat.append(s.accuracies)
    plt.figure(2)
    plt.boxplot(dat)
    plt.xlabel('n')
    plt.ylabel('accuracy')
    plt.title('GNB Accuracy with n-grams')
    plt.show()
