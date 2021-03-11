import Vue from 'vue'
import App from './App.vue'
import router from "./router";

// FONT AWESOME
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from "@fortawesome/free-solid-svg-icons";
import { far } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
library.add(fas, far)
Vue.component('font-awesome-icon', FontAwesomeIcon)

// BOOTSTRAP
import BootstrapVue from "bootstrap-vue";
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
Vue.use(BootstrapVue);

// AXIOS
import axios from "axios";
Vue.prototype.$axios = axios;

// PAPA PARSE
import VuePapaParse from "vue-papa-parse";
Vue.use(VuePapaParse);

// D3
import * as d3 from "d3";
Vue.prototype.$d3 = d3;

// VUE PROMISED
import { Promised } from 'vue-promised';
Vue.component('Promised', Promised);

// VUE RESIZE
import resize from "vue-resize-directive";
Vue.directive("resize", resize);


// SERVER REF
Vue.prototype.$server = "http://localhost:5000";
const SERVER = "http://localhost:5000";

// USER DATA
Vue.prototype.$userData = Object.create({
  userId: undefined,
  corpus: [],
  sessions: []
});

// SESSION HOLDER
Vue.prototype.$session = Object.create({
  _name: {text: "Default"},
  name: {
    get() { return this._name },
    set(name) { this._name.text = name }
  },
  _notes: {text: ""},
  notes: {
    get() { return this._notes },
    set(notes) { this._notes.text = notes }
  },
  _index: {ids: []},
  index: {
    get() { return this._index },
    set(index) { this._index.ids = index }
  },
  _graph: { nodes: [], distance: [], neighborhood: [] },
  graph: {
    get() { return this._graph },
    set(graph) {
      this._graph.nodes         = graph.nodes;
      this._graph.distance      = graph.distance;
      this._graph.neighborhood  = graph.neighborhood;
    }
  },
  _tsne: {embedding: []},
  tsne: {
    get() { return this._tsne },
    set(embedding) { this._tsne.embedding = embedding }
  },
  _clusters: {
    cluster_k: undefined,
    cluster_names: [],
    colors: [],
    cluster_docs: [],
    cluster_words: [],
    labels: []
  },
  clusters: {
    get() { return this._clusters },
    set(clusters) {
      this._clusters.cluster_k      = clusters.cluster_k;
      this._clusters.cluster_names  = clusters.cluster_names;
      this._clusters.colors         = clusters.colors;
      this._clusters.cluster_docs   = clusters.cluster_docs;
      this._clusters.cluster_words  = clusters.cluster_words;
      this._clusters.labels         = clusters.labels;
    }
  },
  _controls: {
    projection: undefined,
    tsne: { perplexity: undefined },
    distance: undefined,
    n_neighbors: undefined,
    linkDistance: undefined,
    charge: undefined
  },
  controls: {
    get() { return this._controls },
    set(controls) {
      this._controls.projection     = controls.projection;
      this._controls.tsne           = {
        perplexity: controls.tsne.perplexity};
      this._controls.distance       = controls.distance;
      this._controls.n_neighbors    = controls.n_neighbors;
      this._controls.linkDistance   = controls.linkDistance;
      this._controls.charge         = controls.charge;
    }
  },
  _date: undefined,
  date: {
    get() { return this._date },
    set(date) { this._date = date }
  },
  _selected: {ids:[]},
  selected: {
    get() { return this._selected },
    set(ids) { this._selected.ids = ids }
  },
  _focused: {id: undefined},
  focused: {
    get() { return this._focused },
    set(id) { this._focused.id = id }
  },
  _highlight: { cluster_name: undefined },
  highlight: {
    get() { return this._highlight },
    set(cluster_name) { this._highlight.cluster_name = cluster_name }
  },
  _word_similarity: { query: [], most_similar: []},
  word_similarity: {
    get() { return this._word_similarity },
    set(word_similarity) {
      this._word_similarity.query         = word_similarity.query;
      this._word_similarity.most_similar  = word_similarity.most_similar;
    }
  }
});

// VUEX
import Vuex from 'vuex';
Vue.use(Vuex);

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
    setSessions (state, sessions) {
      state.sessions = sessions;
    }
  },
};

const store = new Vuex.Store({
  modules: {
    userData: userData
  },
  mutations: {},
  actions: {
    async getUserData({commit}, userId) {
      const formData = new FormData();
      formData.set("userId", userId);
			
      return new Promise((resolve, reject) => {
        axios.post(SERVER+"/auth", formData, {
          headers: { "Content-Type": "multipart/form-data"
        }}).then(({data}) => {
          commit("userData/setUserId",    data.userData.userId);
          commit("userData/setCorpus",    data.userData.corpus);
          commit("userData/setSessions",  data.userData.sessions);
          resolve(data);
        }).catch(error => { reject(error) });
      });
    }
  }
})

Vue.config.productionTip = false;

new Vue({
	render: h => h(App),
	router: router,
	components: {App},
  store: store
}).$mount('#app');
