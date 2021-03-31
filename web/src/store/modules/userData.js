const state = {
  userId: undefined,
  corpus: [],
  sessions: [],
  isProcessed: false
};

const getters = {
  corpus_size(state) {
    return state.corpus.length;
  }
};

const actions = {};

const mutations = {
  setUserId (state, userId) {
    state.userId = userId;
  },
  setCorpus (state, corpus) {
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
    state.sessions = sessions;
  },
  clearUserData(state) {
    state.corpus = state.corpus.splice(0, state.corpus.length);
    state.sessions = state.sessions.splice(0, state.sessions.length);
  },
  setIsProcessed(state, value) {
    state.isProcessed = value;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}