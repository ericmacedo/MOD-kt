from multiprocessing import Process, Queue
from scipy.spatial.distance import cdist
from dataclasses import dataclass, field
from typing import List
import numpy as np
import numbers
import pickle
import json
import os


@dataclass
class Bert:
    model_name: str
    embeddings: list = field(default_factory=list)

    def __init__(self, model_name: str = "allenai-specter"):
        self.model_name = model_name
        self.embeddings = []

    def _train(self, queue: Queue, corpus: List[str]):
        from sentence_transformers import SentenceTransformer

        transformer = SentenceTransformer(self.model_name)
        embeddings = transformer.encode(corpus).tolist()

        del transformer
        Bert.clear_memory()

        queue.put(embeddings)

    def train(self, corpus: List[str]) -> list:
        queue = Queue()
        p = Process(
            target=self._train,
            kwargs={"queue": queue, "corpus": corpus})
        p.start()
        self.embeddings = queue.get()
        p.join()

        return self.embeddings

    @classmethod
    def load(cls, path: str):
        return pickle.load(open(path, "rb"))

    @classmethod
    def clear_memory(cls):
        from gc import collect
        from torch.cuda import empty_cache, ipc_collect

        collect()
        ipc_collect()
        empty_cache()

    def save(self, path: str):
        with open(path, "wb") as pkl_file:
            pickle.dump(
                obj=self,
                file=pkl_file,
                protocol=pickle.DEFAULT_PROTOCOL,
                fix_imports=True)


class Document:
    def __init__(self, userId: str, id: str):
        self.__userId = userId
        self.id = id

        self.__path = f"./users/{self.__userId}/corpus/{self.id}.json"

        if not os.path.isfile(self.__path):
            return None

        with open(self.__path, "r") as jsonFile:
            doc = json.load(jsonFile, encoding="utf-8")
            self._file_name = doc["file_name"]
            self._content = doc["content"]
            self._processed = doc["processed"] if "processed" in doc else None
            self._term_frequency = doc["term_frequency"] if "term_frequency" in doc else None
            self._embedding = doc["embedding"] if "embedding" in doc else None
            self._uploaded_on = doc["uploaded_on"]

    # FILE NAME
    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name: str):
        self._file_name = file_name
        doc = self.as_dict()
        doc["file_name"] = file_name
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # CONTENT
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content: str):
        self._content = content
        doc = self.as_dict()
        doc["content"] = content
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # PROCESSED
    @property
    def processed(self):
        return self._processed

    @processed.setter
    def processed(self, processed: str):
        self._processed = processed
        doc = self.as_dict()
        doc["processed"] = processed
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # TERM FREQUENCY
    @property
    def term_frequency(self):
        return self._term_frequency

    @term_frequency.setter
    def term_frequency(self, term_frequency: dict):
        self._term_frequency = term_frequency
        doc = self.as_dict()
        doc["term_frequency"] = term_frequency
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # EMBEDDING
    @property
    def embedding(self):
        return self._embedding

    @embedding.setter
    def embedding(self, embedding: list):
        self._embedding = embedding
        doc = self.as_dict()
        doc["embedding"] = embedding
        with open(self.__path, "w", encoding="utf-8") as out_file:
            json.dump(doc, out_file)

    # UTILS
    def as_dict(self) -> dict:
        return dict(
            id=self.id,
            file_name=self._file_name,
            content=self._content,
            processed=self._processed,
            term_frequency=self._term_frequency,
            embedding=self._embedding,
            uploaded_on=self._uploaded_on)


def infer_doc2vec(data: str, **kwargs) -> list:
    model = kwargs.get("model", None)
    return model.infer_vector(
        data.split(" "), steps=35
    ) if model else None


class BestCMeans:
    def fit_predict(self, data, c, m, error, maxiter, init=None, seed=None):
        """
        Fuzzy c-means clustering algorithm [1].

        Parameters
        ----------
        data : 2d array, size (S, N)
            Data to be clustered.  N is the number of data sets; S is the number
            of features within each sample vector.
        c : int
            Desired number of clusters or classes.
        m : float
            Array exponentiation applied to the membership function u_old at each
            iteration, where U_new = u_old ** m.
        error : float
            Stopping criterion; stop early if the norm of (u[p] - u[p-1]) < error.
        maxiter : int
            Maximum number of iterations allowed.
        init : 2d array, size (S, N)
            Initial fuzzy c-partitioned matrix. If none provided, algorithm is
            randomly initialized.
        seed : int
            If provided, sets random seed of init. No effect if init is
            provided. Mainly for debug/testing purposes.

        Returns
        -------
        cntr : 2d array, size (S, c)
            Cluster centers.  Data for each center along each feature provided
            for every cluster (of the `c` requested clusters).
        u : 2d array, (S, N)
            Final fuzzy c-partitioned matrix.
        u0 : 2d array, (S, N)
            Initial guess at fuzzy c-partitioned matrix (either provided init or
            random guess used if init was not provided).
        d : 2d array, (S, N)
            Final Euclidian distance matrix.
        jm : 1d array, length P
            Objective function history.
        p : int
            Number of iterations run.
        fpc : float
            Final fuzzy partition coefficient.


        Notes
        -----
        The algorithm implemented is from Ross et al. [1]_.

        Fuzzy C-Means has a known problem with high dimensionality datasets, where
        the majority of cluster centers are pulled into the overall center of
        gravity. If you are clustering data with very high dimensionality and
        encounter this issue, another clustering method may be required. For more
        information and the theory behind this, see Winkler et al. [2]_.

        References
        ----------
        .. [1] Ross, Timothy J. Fuzzy Logic With Engineering Applications, 3rd ed.
            Wiley. 2010. ISBN 978-0-470-74376-8 pp 352-353, eq 10.28 - 10.35.

        .. [2] Winkler, R., Klawonn, F., & Kruse, R. Fuzzy c-means in high
            dimensional spaces. 2012. Contemporary Theory and Pragmatic
            Approaches in Fuzzy Computing Utilization, 1.
        """
        # Setup u0
        if init is None:
            if seed is not None:
                np.random.seed(seed=seed)
            n = data.shape[1]
            u0 = np.random.rand(c, n)
            u0 /= np.ones(
                (c, 1)).dot(np.atleast_2d(u0.sum(axis=0))).astype(np.float64)
            init = u0.copy()
        u0 = init
        u = np.fmax(u0, np.finfo(np.float64).eps)

        # Initialize loop parameters
        jm = np.zeros(0)
        p = 0

        # Main cmeans loop
        while p < maxiter - 1:
            u2 = u.copy()
            [cntr, u, Jjm, d] = self._cmeans0(data, u2, c, m)
            jm = np.hstack((jm, Jjm))
            p += 1

            # Stopping rule
            if np.linalg.norm(u - u2) < error:
                break

        # Final calculations
        error = np.linalg.norm(u - u2)
        fpc = self._fp_coeff(u)

        return cntr, u, u0, d, jm, p, fpc

    def _cmeans0(self, data, u_old, c, m):
        """
        Single step in generic fuzzy c-means clustering algorithm.

        Modified from Ross, Fuzzy Logic w/Engineering Applications (2010),
        pages 352-353, equations 10.28 - 10.35.

        Parameters inherited from cmeans()
        """
        # Normalizing, then eliminating any potential zero values.
        u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
        u_old = np.fmax(u_old, np.finfo(np.float64).eps)

        um = u_old ** m

        # Calculate cluster centers
        data = data.T
        cntr = um.dot(data) / (np.ones((data.shape[1],
                                        1)).dot(np.atleast_2d(um.sum(axis=1))).T)

        d = self._distance(data, cntr)
        d = np.fmax(d, np.finfo(np.float64).eps)

        jm = (um * d ** 2).sum()

        u = d ** (- 2. / (m - 1))
        u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))

        return cntr, u, jm, d

    def _distance(self, data, centers):
        """
        Euclidean distance from each point to each cluster center.

        Parameters
        ----------
        data : 2d array (N x Q)
            Data to be analyzed. There are N data points.
        centers : 2d array (C x Q)
            Cluster centers. There are C clusters, with Q features.

        Returns
        -------
        dist : 2d array (C x N)
            Euclidean distance from each point, to each cluster center.

        See Also
        --------
        scipy.spatial.distance.cdist
        """
        return cdist(data, centers, metric="cosine").T

    def _fp_coeff(self, u):
        """
        Fuzzy partition coefficient `fpc` relative to fuzzy c-partitioned
        matrix `u`. Measures 'fuzziness' in partitioned clustering.

        Parameters
        ----------
        u : 2d array (C, N)
            Fuzzy c-partitioned matrix; N = number of data points and C = number
            of clusters.

        Returns
        -------
        fpc : float
            Fuzzy partition coefficient.

        """
        n = u.shape[1]

        return np.trace(u.dot(u.T)) / float(n)

    def predict(self, test_data, cntr_trained, m, error, maxiter, init=None,
                seed=None):
        """
        Prediction of new data in given a trained fuzzy c-means framework [1].

        Parameters
        ----------
        test_data : 2d array, size (S, N)
            New, independent data set to be predicted based on trained c-means
            from ``cmeans``. N is the number of data sets; S is the number of
            features within each sample vector.
        cntr_trained : 2d array, size (S, c)
            Location of trained centers from prior training c-means.
        m : float
            Array exponentiation applied to the membership function u_old at each
            iteration, where U_new = u_old ** m.
        error : float
            Stopping criterion; stop early if the norm of (u[p] - u[p-1]) < error.
        maxiter : int
            Maximum number of iterations allowed.
        init : 2d array, size (S, N)
            Initial fuzzy c-partitioned matrix. If none provided, algorithm is
            randomly initialized.
        seed : int
            If provided, sets random seed of init. No effect if init is
            provided. Mainly for debug/testing purposes.

        Returns
        -------
        u : 2d array, (S, N)
            Final fuzzy c-partitioned matrix.
        u0 : 2d array, (S, N)
            Initial guess at fuzzy c-partitioned matrix (either provided init or
            random guess used if init was not provided).
        d : 2d array, (S, N)
            Final Euclidian distance matrix.
        jm : 1d array, length P
            Objective function history.
        p : int
            Number of iterations run.
        fpc : float
            Final fuzzy partition coefficient.

        Notes
        -----
        Ross et al. [1]_ did not include a prediction algorithm to go along with
        fuzzy c-means. This prediction algorithm works by repeating the clustering
        with fixed centers, then efficiently finds the fuzzy membership at all
        points.

        References
        ----------
        .. [1] Ross, Timothy J. Fuzzy Logic With Engineering Applications, 3rd ed.
            Wiley. 2010. ISBN 978-0-470-74376-8 pp 352-353, eq 10.28 - 10.35.
        """
        c = cntr_trained.shape[0]

        # Setup u0
        if init is None:
            if seed is not None:
                np.random.seed(seed=seed)
            n = test_data.shape[1]
            u0 = np.random.rand(c, n)
            u0 /= np.ones(
                (c, 1)).dot(np.atleast_2d(u0.sum(axis=0))).astype(np.float64)
            init = u0.copy()
        u0 = init
        u = np.fmax(u0, np.finfo(np.float64).eps)

        # Initialize loop parameters
        jm = np.zeros(0)
        p = 0

        # Main cmeans loop
        while p < maxiter - 1:
            u2 = u.copy()
            [u, Jjm, d] = self._cmeans_predict0(
                test_data, cntr_trained, u2, c, m)
            jm = np.hstack((jm, Jjm))
            p += 1

            # Stopping rule
            if np.linalg.norm(u - u2) < error:
                break

        # Final calculations
        error = np.linalg.norm(u - u2)
        fpc = self._fp_coeff(u)

        return u, u0, d, jm, p, fpc

    def _cmeans_predict0(self, test_data, cntr, u_old, c, m):
        """
        Single step in fuzzy c-means prediction algorithm. Clustering algorithm
        modified from Ross, Fuzzy Logic w/Engineering Applications (2010)
        p.352-353, equations 10.28 - 10.35, but this method to generate fuzzy
        predictions was independently derived by Josh Warner.

        Parameters inherited from cmeans()

        Very similar to initial clustering, except `cntr` is not updated, thus
        the new test data are forced into known (trained) clusters.
        """
        # Normalizing, then eliminating any potential zero values.
        u_old /= np.ones((c, 1)).dot(np.atleast_2d(u_old.sum(axis=0)))
        u_old = np.fmax(u_old, np.finfo(np.float64).eps)

        um = u_old ** m
        test_data = test_data.T

        # For prediction, we do not recalculate cluster centers. The test_data is
        # forced to conform to the prior clustering.

        d = self._distance(test_data, cntr)
        d = np.fmax(d, np.finfo(np.float64).eps)

        jm = (um * d ** 2).sum()

        u = d ** (- 2. / (m - 1))
        u /= np.ones((c, 1)).dot(np.atleast_2d(u.sum(axis=0)))

        return u, jm, d


class FuzzyCMeans(object):
    def __init__(self, training_set, k, m=2.0, distance='euclidean', userU=-1, imax=25, emax=0.01):

        self.__x = training_set
        self.__k = k
        self.m = m
        self.dist = distance
        self.userU = userU
        self.imax = imax
        self.emax = emax

        if (isinstance(userU, numbers.Number)):
            self.__mu = self.initializeFCM()
        else:
            _, N = userU.shape
            index = np.where(userU > 0)
            for j in range(index[1].size):
                userU[:, index[1][j]] = userU[:, index[1][j]] / \
                    sum(userU[:, index[1][j]])
            self.__mu = userU

        self.__obj = 0

    def __getc(self):
        return self.__c

    def __setc(self, c):
        self.__c = np.array(c).reshape(self.__c.shape)

    c = property(__getc, __setc)

    def __getmu(self):
        return self.__mu

    mu = property(__getmu, None)

    def __getx(self):
        return self.__x

    x = property(__getx, None)

    def initializeFCM(self):

        x = self.__x

        N, _ = x.shape

        U = np.random.random((self.__k, N))

        for j in range(N):
            U[:, j] = U[:, j]/sum(U[:, j])

        return U

    def centers(self):

        x = self.__x

        _, M = x.shape

        mm = self.__mu ** self.m

        tempRep = np.dot(np.ones((M, 1)),
                         np.asanyarray([np.sum(mm, axis=1)]))

        c = np.dot(mm, self.__x) / tempRep.T

        self.__c = c

        tempDist = cdist(c, x, self.dist)  # self.dist 'cosine'
        dist = tempDist**2.0
        obj = np.sum((dist**2.0)*mm)
        self.__obj = obj

        return self.__c, self.__obj

    def membership(self):

        x = self.__x
        c = self.__c
        N, _ = x.shape
        k = self.__k
        r = np.zeros((k, N))      # r will become mu
        tempDist = cdist(c, x, self.dist)  # self.dist 'cosine'
        dist = tempDist**2.0
        temp = dist**(-2.0/(self.m-1))
        tempSum = np.asanyarray([np.sum(temp, axis=0)])
        r = temp/(np.dot(np.ones((k, 1)), tempSum))

        self.__mu = r
        return self.__mu

    def step(self):
        '''
        This method runs one step of the algorithm. It might be useful to track
        the changes in the parameters.

        :Returns:
          The norm of the change in the membership values of the examples. It
          can be used to track convergence and as an estimate of the error.
        '''
        old = self.__obj
        self.centers()
        self.membership()
        return np.abs(self.__obj - old)

    def __call__(self):
        '''
        The ``__call__`` interface is used to run the algorithm until
        convergence is found.

        :Parameters:
          emax
            Specifies the maximum error admitted in the execution of the
            algorithm. It defaults to 1.e-10. The error is tracked according to
            the norm returned by the ``step()`` method.
          imax
            Specifies the maximum number of iterations admitted in the execution
            of the algorithm. It defaults to 20.

        :Returns:
          An array containing, at each line, the vectors representing the
          centers of the clustered regions.
        '''
        error = 1.0
        emax = self.emax
        imax = self.imax

        i = 0
        while error > emax and i < imax:
            error = self.step()

            if not(isinstance(self.userU, numbers.Number)):
                mu = self.__mu
                k, N = mu.shape
                index = np.where(self.userU > 0)
                for j in range(index[1].size):
                    mu[:, index[1][j]] = 0
                for j in range(index[1].size):
                    mu[index[0][j], index[1][j]
                       ] = self.userU[index[0][j], index[1][j]]
                for j in range(index[1].size):
                    mu[:, index[1][j]] = mu[:, index[1][j]] / \
                        sum(mu[:, index[1][j]])
                self.__mu = mu
            # print "obj: ", self.__obj
            i = i + 1
        return self.c
