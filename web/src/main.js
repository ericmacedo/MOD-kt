import Vue from 'vue'
import App from './App.vue'
import store from "./store";
import router from "./router";

// FONT AWESOME
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
library.add(fas)
Vue.component('font-awesome-icon', FontAwesomeIcon)

// BOOTSTRAP
import BootstrapVue from "bootstrap-vue";
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
Vue.use(BootstrapVue);

// PAPA PARSE
import VuePapaParse from "vue-papa-parse";
Vue.use(VuePapaParse);

// VUE PROMISED
import { Promised } from 'vue-promised';
Vue.component('Promised', Promised);

Vue.config.productionTip = false;

new Vue({
	render: h => h(App),
	router: router,
	components: {App},
  store: store
}).$mount('#app');
