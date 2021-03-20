import Vue from 'vue';
import Vuex from 'vuex';
import axios from "axios";

import userData from './modules/userData';
import session from './modules/session';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    userData, session
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
          commit("userData/setUserId",      data.userData.userId);
          commit("userData/setCorpus",      data.userData.corpus);
          commit("userData/setSessions",    data.userData.sessions);
          commit("userData/setIsProcessed", data.userData.isProcessed);
          resolve(data);
          data = null;
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
          data = null;
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
          result = null;
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
          
          commit("session/setId",             session.id);
          commit("session/setName",           session.name);
          commit("session/setNotes",          session.notes);
          commit("session/setIndex",          session.index);
          commit("session/setGraph",          session.graph);
          commit("session/setLinkSelector",   session.link_selector);
          commit("session/setTsne",           session.tsne);
          commit("session/setClusters",       session.clusters);
          commit("session/setControls",       session.controls);
          commit("session/setDate",           session.date);
          commit("session/setSelected",       session.selected);
          commit("session/setFocused",        session.focused);
          commit("session/setHighlight",      session.highlight);
          commit("session/setWordSimilarity", session.word_similarity);

          resolve(data);
          data = null;
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
          
          data = null;
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
          const session = data.sessionData;
          
          commit("session/setId",             session.id);
          commit("session/setName",           session.name);
          commit("session/setNotes",          session.notes);
          commit("session/setIndex",          session.index);
          commit("session/setGraph",          session.graph);
          commit("session/setLinkSelector",   session.link_selector);
          commit("session/setTsne",           session.tsne);
          commit("session/setClusters",       session.clusters);
          commit("session/setControls",       session.controls);
          commit("session/setDate",           session.date);
          commit("session/setSelected",       session.selected);
          commit("session/setFocused",        session.focused);
          commit("session/setHighlight",      session.highlight);
          commit("session/setWordSimilarity", session.word_similarity);

          resolve(data);
          data = null;
        }).catch(error => reject(error));
      });
    },
    async getProjection({commit, state}) {
      const formData = new FormData();

			formData.set("userId", state.userData.userId);
			formData.set("projection", state.session.controls.projection);
			formData.set("index", state.session.index);
			formData.set("perplexity", state.session.controls.tsne.perplexity);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/projection", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) => {

          commit("session/setTsne", data.projection);
          resolve(data);

          data = null;
        }).catch(error => reject(error));
      });
    },
    async getMostSimilar({state, commit}) {
      const formData = new FormData();
      formData.set("userId", state.userData.userId);
      formData.set("query", state.session.word_similarity.query);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/word_similarity", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) => {
          commit("session/setWordSimilarity", {
            query: data.query,
            most_similar: data.most_similar
          });
          resolve(data)

          data = null;
        }).catch(error => reject(error));
      });
    },
    async saveSession({commit, getters, state}) {
      const formData = new FormData();
      let session = getters["session/session"];
      
      formData.set("userId", state.userData.userId);
      formData.set("sessionData", JSON.stringify(session));
      
      return new Promise((resolve, reject) => {
        axios.put(state.SERVER+"/session", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) => {
          commit("session/setId",   data.sessionData.id);
          commit("session/setDate", data.sessionData.date);
          resolve(data);

          data = null;
        }).catch(error => reject(error));
      });
    },
    async deleteSession({state}, sessionId) {
      const formData = new FormData();
      
      formData.set("userId", state.userData.userId);
      formData.set("sessionId", sessionId);
      
      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/session", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(result => {
          resolve(result);

          result = null;
        }).catch(error => reject(error));
      });
    },
    async updateCorpus({state, commit}, newData) {
      const formData = new FormData();
      
      formData.set("userId", state.userData.userId);
      formData.set("clusters", JSON.stringify(state.session.clusters));
      formData.set("new_docs", newData);

      return new Promise((resolve, reject) => {
        axios.post(state.SERVER+"/process_corpus", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(({data}) => {
          const newData = data.newData;

          // SESSION UPDATE
          commit("session/setTsne", newData.tsne);
          commit("session/setGraph", newData.graph);
          commit("session/setIndex", newData.index);
          commit("session/setNewDocs", newData.new_index);
          commit("session/setClusters", newData.clusters);

          // USER DATA UPDATE
          commit("userData/setCorpus", newData.corpus);

          resolve(data);

          data = null;
        }).catch(error => reject(error));
      });
    },
    async requestSankeyGraph({state}, userId) {
      return new Promise((resolve, reject) => {
        axios.get(state.SERVER+"/sankey", {params: {userId: userId}})
          .then(({data}) => {
            resolve(data);

            data = null;
          }).catch(error => reject(error));
      });
    }
  }
});