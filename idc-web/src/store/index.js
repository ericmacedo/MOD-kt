import Vue from 'vue';
import Vuex from 'vuex';
import axios from "axios";
import { mapGetters } from 'vuex';

Vue.use(Vuex);
Vue.use(mapGetters);

const userData = {
  namespaced: true,
  state: {
    userId: undefined,
    corpus: [],
    sessions: []
  },
  mutations: {
    setUserId (state, userId) {
      state.userId = userId;
    },
    setCorpus (state, corpus) {
      state.corpus = corpus;
    },
    pushCorpus ({corpus}, newData) {
      corpus.concat(newData);
    },
    removeFromCorpus(state, to_remove) {
      state.corpus = state.corpus.filter((doc) => {
        !to_remove.includes(doc.id);
      });
    },
    setSessions (state, sessions) {
      state.sessions = sessions;
    },
    clearUserData(state) {
      state.corpus = [];
      state.sessions = [];
    }
  },
  getters: {
    userId({userId}) {
      return userId;
    },
    corpus_size({corpus}) {
      return corpus.length;
    }
  }
};

const session = {
  namespaced: true,
  state: {
    name: "Default",
    notes: "",
    index: [],
    graph: { nodes: [], distance: [], neighborhood: [] },
    tsne: [],
    clusters: {
      cluster_k: undefined,
      cluster_names: [],
      colors: [],
      cluster_docs: [],
      cluster_words: [],
      labels: []
    },
    controls: {
      projection: undefined,
      tsne: { perplexity: undefined },
      distance: undefined,
      n_neighbors: undefined,
      linkDistance: undefined,
      charge: undefined
    },
    date: undefined,
    selected: [],
    focused: undefined,
    highlight: undefined,
    word_similarity: {
      query: [],
      most_similar: []
    }
  },
  mutations: {
    setName(state, name) {
      state.name = name;
    },
    setNotes(state, notes) {
      state.notes = notes;
    },
    setIndex(state, index) {
      state.index = index;
    },
    setGraph({graph}, {nodes, distance, neighborhood}) {
      graph.nodes = nodes;
      graph.distance = distance;
      graph.neighborhood = neighborhood;
    },
    setTsne(state, tsne) {
      state.tsne = tsne;
    },
    setClusters({clusters}, {
                          cluster_k, cluster_names,
                          colors, cluster_docs, labels,
                          cluster_words
                        }) {
      clusters.cluster_k      = cluster_k;
      clusters.cluster_names  = cluster_names;
      clusters.colors         = colors;
      clusters.cluster_docs   = cluster_docs;
      clusters.cluster_words  = cluster_words;
      clusters.labels         = labels;
    },
    setControls({controls}, {
                          projection, tsne, distance,
                          n_neighbors, linkDistance,
                          charge
                        }) {
      controls.projection     = projection;
      controls.tsne           = { perplexity: tsne.perplexity };
      controls.distance       = distance;
      controls.n_neighbors    = n_neighbors;
      controls.linkDistance   = linkDistance;
      controls.charge         = charge;
    },
    setDate(state, date) {
      state.date = date;
    },
    setSelected(state, selected) {
      state.selected = selected;
    },
    updateSelected(state, id) {
      let index = state.selected.indexOf(id);
					
      if (index == -1) {
        state.selected.push(id);
        state.focused = id;
      } else {
        state.selected.pop(index);
        state.focused = null;
      }
    },
    setHighlight(state, cluster_name) {
      state.highlight = cluster_name;
    },
    updateHighlight(state, cluster_name) {
      state.highlight = (state.highlight == cluster_name) ? "" : cluster_name;
    },
    setFocused(state, focused) {
      state.focused = focused;
    },
    setWordSimilarity({word_similarity}, {query, most_similar}) {
      word_similarity.query         = query;
      word_similarity.most_similar  = most_similar;
    }
  },
  getters: {
    session(state) {
      return {
        name:             state.name,
        notes:            state.notes,
        index:            state.index,
        graph:            state.graph,
        tsne:             state.tsne,
        clusters:         state.clusters,
        controls:         state.controls,
        date:             state.date,
        selected:         state.selected,
        focused:          state.focused,
        highlight:        state.highlight,
        word_similarity:  state.word_similarity
      }
    }
  }
};

export default new Vuex.Store({
  modules: {
    userData: userData,
    session: session
  },
  state: {
    SERVER: "http://localhost:5000"
  },
  actions: {
    async getUserData({commit, state}, userId) {
      const formData = new FormData();
      formData.set("userId", userId);
			
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/auth", formData, {
          headers: { "Content-Type": "multipart/form-data"
        }}).then(({data}) => {
          commit("userData/setUserId",    data.userData.userId);
          commit("userData/setCorpus",    data.userData.corpus);
          commit("userData/setSessions",  data.userData.sessions);
          resolve(data);
        }).catch(error => reject(error));
      });
    },
    async clearUserData({commit, state}) {
      const formData = new FormData();
      formData.set("userId", state.userData.userId);
      formData.set("RESET_FLAG", true);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/corpus", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) =>  {
          commit("userData/clearUserData");
          resolve(data);
        }).catch(error => reject(error));
      });
    },
    async uploadDocument({commit, state}, formData) {
      return new Promise((resolve, reject) => {
        axios.put(state.SERVER+"/corpus", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then((result) => {
          commit("userData/pushCorpus", result.data.newData)
          resolve(result);
        }).catch(error => reject(error));
      });
    },
    async deleteDocument({commit, state}, {to_remove, RESET_FLAG}) {
      const formData = new FormData();
			formData.set("userId", state.userData.userId);
			formData.set("ids", to_remove);
			formData.set("RESET_FLAG", RESET_FLAG);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/corpus", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(() => {
          commit("userData/removeFromCorpus", to_remove);
          resolve();
        }).catch(error => reject(error));
      });
    },
    async cluster({commit, getters, state}, cluster_k=null) {
      const formData = new FormData();
			formData.set("userId", state.userData.userId);
      if (cluster_k){
        formData.set("cluster_k", cluster_k);
      } else {
        formData.set("session", JSON.stringify(getters.session));
      }
      
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/cluster", formData,
          { headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) => {
          const session = data.sessionData;
          
          commit("session/setName",           session.name);
          commit("session/setNotes",          session.notes);
          commit("session/setIndex",          session.index);
          commit("session/setGraph",          session.graph);
          commit("session/setTsne",           session.tsne);
          commit("session/setClusters",       session.clusters);
          commit("session/setControls",       session.controls);
          commit("session/setDate",           session.date);
          commit("session/setSelected",       session.selected);
          commit("session/setFocused",        session.focused);
          commit("session/setHighlight",      session.highlight);
          commit("session/setWordSimilarity", session.word_similarity);

          resolve(data);
        }).catch(error => reject(error));
      });
    },
    async processCorpus({commit, state}, performance) {
      return new Promise((resolve, reject) => {
        axios.get(state.SERVER+"/process_corpus", {
          params: {
            userId: state.userData.userId,
            performance: performance}
        }).then(({data}) => {
          commit("userData/setUserId",    data.userData.userId);
          commit("userData/setCorpus",    data.userData.corpus);
          commit("userData/setSessions",  data.userData.sessions);
          resolve(data);
        }).catch(error => reject(error));
      });
    }
  }
});