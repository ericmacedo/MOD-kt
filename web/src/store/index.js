import Vue from 'vue';
import Vuex from 'vuex';
import axios from "axios";

import userData from './modules/userData';
import session from './modules/session';
import sankey from './modules/sankey';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    userData, session, sankey
  },
  state: {
    SERVER: `${process.env.VUE_APP_SERVER_URL}:${process.env.VUE_APP_SERVER_PORT}/api`
  },
  actions: {
    async getUserData({commit, state}, userId) {
      let formData = new FormData();
      formData.set("userId", userId);
			
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/auth", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          commit("userData/setUserId", data.userData.userId);
          commit("userData/setCorpus", data.userData.corpus.map(doc => doc));
          commit("userData/setSessions", data.userData.sessions.map(session => session));
          commit("userData/setIsProcessed", data.userData.isProcessed);
          commit("userData/setStopwords", data.userData.stop_words);
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async clearUserData({commit, state}) {
      let formData = new FormData();
      formData.set("userId", state.userData.userId);
      formData.set("RESET_FLAG", true);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/corpus", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(() =>  {
          commit("userData/clearUserData");

          resolve();
        }).catch(error => reject(error));
      });
    },
    async uploadDocument({commit, state}, formData) {
      return new Promise((resolve, reject) => {
        axios.put(state.SERVER+"/corpus", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then((result) => {
          commit("userData/pushCorpus", result.data.newData.map(d => d));
          resolve(result);
          result = null;
        }).catch(error => reject(error));
      });
    },
    async deleteDocument({commit, state}, {to_remove, RESET_FLAG}) {
      let formData = new FormData();
			formData.set("userId", state.userData.userId);
			formData.set("ids", to_remove);
			formData.set("RESET_FLAG", RESET_FLAG);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/corpus", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(() => {
          commit("userData/removeFromCorpus", to_remove);
          resolve();
        }).catch(error => reject(error));
      });
    },
    async cluster({commit, state}, cluster_k=null) {
      let formData = new FormData();
			formData.set("userId", state.userData.userId);
      formData.set("recluster", cluster_k == null);
      if (cluster_k != null) {
        formData.set("cluster_k", cluster_k);
      } else {
        formData.set("seed", JSON.stringify(state.session.clusters));
        formData.set("index", state.session.index);
      }
      
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/cluster", formData,{ 
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          let session = data.sessionData;

          if(cluster_k != null) {
            commit("session/setId", session.id);
            commit("session/setName", session.name);
            commit("session/setNotes", session.notes);
            commit("session/setIndex", session.index.map(id => id));
            commit("session/setGraph", session.graph);
            commit("session/setTsne", session.tsne.map(d => d));
            commit("session/setControls", session.controls);
            commit("session/setDate", session.date);
            commit("session/setSelected", session.selected.map(d => d));
            commit("session/setFocused", session.focused);
            commit("session/setHighlight", session.highlight);
            commit("session/setWordSimilarity", session.word_similarity);
          }          
          
          commit("session/setClusters", session.clusters);
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async processCorpus({commit, state}, performance) {
      let formData = new FormData();
			formData.set("userId", state.userData.userId);
      formData.set("performance", performance);
      formData.set("stop_words", state.userData.stop_words);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/process_corpus", formData,{ 
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          commit("userData/setUserId",      data.userData.userId);
          commit("userData/setCorpus",      data.userData.corpus.map(doc => doc));
          commit("userData/setSessions",    data.userData.sessions.map(session => session));
          commit("userData/setIsProcessed", true);
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async getSessionById({commit, state}, sessionId) {
      return new Promise((resolve, reject) => {
        axios.get(state.SERVER+"/session", {
          params: {
            userId: state.userData.userId,
            sessionId: sessionId}
        }).then(({data})=> {
          let session = data.sessionData;
          
          commit("session/setId", session.id);
          commit("session/setName", session.name);
          commit("session/setNotes", session.notes);
          commit("session/setIndex", session.index.map(id => id));
          commit("session/setGraph", session.graph);
          commit("session/setTsne", session.tsne.map(d => d));
          commit("session/setClusters", session.clusters);
          commit("session/setControls", session.controls);
          commit("session/setDate", session.date);
          commit("session/setSelected", session.selected.map(d => d));
          commit("session/setFocused", session.focused);
          commit("session/setHighlight", session.highlight);
          commit("session/setWordSimilarity", session.word_similarity);
          
          data = null;
          session = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async getProjection({commit, state}) {
      let formData = new FormData();

			formData.set("userId", state.userData.userId);
			formData.set("projection", state.session.controls.projection);
			formData.set("index", state.session.index);
			formData.set("perplexity", state.session.controls.tsne.perplexity);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/projection", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          commit("session/setTsne", data.projection.map(d => d));
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async getMostSimilar({state, commit}) {
      let formData = new FormData();
      formData.set("userId", state.userData.userId);
      formData.set("query", state.session.word_similarity.query);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/word_similarity", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          commit("session/setWordSimilarity", {
            query: data.query,
            most_similar: data.most_similar
          });
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async saveSession({commit, getters, state}) {
      let formData = new FormData();
      let session = getters["session/session"];
      
      formData.set("userId", state.userData.userId);
      formData.set("sessionData", JSON.stringify(session));
      
      return new Promise((resolve, reject) => {
        axios.put(state.SERVER+"/session", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          commit("session/setId",   data.sessionData.id);
          commit("session/setDate", data.sessionData.date);
          
          data = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async deleteSession({state}, sessionId) {
      let formData = new FormData();
      
      formData.set("userId", state.userData.userId);
      formData.set("sessionId", sessionId);
      
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/session", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(() => {resolve()
        }).catch(error => reject(error));
      });
    },
    async updateCorpus({state, commit}, newData) {
      let formData = new FormData();
      
      formData.set("userId", state.userData.userId);
      formData.set("seed", JSON.stringify(state.session.clusters));
      formData.set("new_docs", newData);

      return new Promise((resolve, reject) => {
        axios.put(state.SERVER+"/process_corpus", formData, {
          headers: {"Content-Type": "multipart/form-data"}
        }).then(({data}) => {
          let newData = data.newData;

          // SESSION UPDATE
          commit("session/setTsne", newData.tsne.map(d => d));
          commit("session/setGraph", newData.graph);
          commit("session/setIndex", newData.index.map(d => d));
          commit("session/setNewDocs", newData.new_index.map(d => d));
          commit("session/setClusters", newData.clusters);

          // USER DATA UPDATE
          commit("userData/setCorpus", newData.corpus.map(doc => doc));

          data = null;
          newData = null;
          resolve();
        }).catch(error => reject(error));
      });
    },
    async requestSankeyGraph({state, commit}, userId) {
      return new Promise((resolve, reject) => {
        axios.get(state.SERVER+"/sankey", {
          params: {userId: userId}
        }).then(({data}) => {
          commit("sankey/setGraph", data);
          resolve();
          data = null;
        }).catch(error => reject(error));
      });
    }
  }
});