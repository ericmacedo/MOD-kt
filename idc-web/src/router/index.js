import Vue from "vue";
import Router from "vue-router";
import Index from "@/components/Index";
import Corpus from "@/components/Corpus";
import Dashboard from "@/components/Dashboard";
import SessionManager from "@/components/SessionManager";

Vue.use(Router);

export default new Router({
  mode: "history",
  routes: [
    {
      path: "/",
      name: "Index",
      component: Index
    }, 
    {
        path: "/corpus",
        name: "Corpus",
        component: Corpus,
        props: true
    }, 
    {
      path: "/dashboard",
      name: "Dashboard",
      component: Dashboard,
      props: true
    },
    {
        path: "/sessions",
        name: "Session Manager",
        component: SessionManager,
        props: true
    }
  ]
});
