import Vue from 'vue'
import App from './App.vue'
import store from "./store";
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

Vue.config.productionTip = false;

new Vue({
	render: h => h(App),
	router: router,
	components: {App},
  store: store
}).$mount('#app');
