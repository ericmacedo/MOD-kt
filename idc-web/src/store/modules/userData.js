const state = {
  userId: undefined,
  corpus: [],
  sessions: [],
  isProcessed: false
};

const mutations = {
  setUserId (state, userId) {
    state.userId = null;
    state.userId = userId;
  },
  setCorpus (state, corpus) {
    state.corpus = null;
    state.corpus = corpus;
  },
  pushCorpus (state, newData) {
    state.corpus = state.corpus.concat(newData);
  },
  removeFromCorpus(state, to_remove) {
    state.corpus = state.corpus.filter(
      doc => !to_remove.includes(doc.id));
  },
  setSessions (state, sessions) {
    state.sessions = null;
    state.sessions = sessions;
  },
  clearUserData(state) {
    state.corpus = [];
    state.sessions = [];
  },
  setIsProcessed(state, isProcessed) {
    state.isProcessed = null;
    state.isProcessed = isProcessed;
  }
};

const getters = {
  corpus_size({corpus}) {
    return corpus.length;
  }
};

const actions = {};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}