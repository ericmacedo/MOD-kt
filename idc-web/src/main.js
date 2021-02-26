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

// SERVER REF
Vue.prototype.$server = "http://localhost:5000";

// USER DATA
Vue.prototype.$userData = {
	userId: undefined,
	corpus: []
};

// SESSION HOLDER
Vue.prototype.$session = {
	name: "Default",
	notes: "",
	force: {
		properties: {
			charge: {
				strength: -30,
				distanceMin: 1,
				distanceMax: 2000
			},
			collide: {
				strength: .7,
				iterations: 1
			}
		}
	},
	graph: {
		nodes: [
			{id: 1},
			{id: 2},
			{id: 3},
			{id: 4}
		],
		links: [
			{source: 1, target: 2, value: 0.5}
		]
	},
	controls: {
		projection: "t-SNE",
		tsne: {perplexity: 5},
		umap: {n_neighbors: 5, min_dist: 0.1},
		cosineDistance:0,
		linkDistance: 20,
		charge: -30
	}
};

Vue.config.productionTip = false;

new Vue({
	render: h => h(App),
	router: router,
	components: {App}
}).$mount('#app');
