import Vue from "vue";
import Router from "vue-router";
import Index from "@/components/Index";
import Corpus from "@/components/Corpus";
// import Dashboard from "@/components/Dashboard";
// import Sessions from "@/components/Sessions";

Vue.use(Router);

export default new Router({
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
    // {
    //   path: "/dashboard",
    //   name: "Dashboard",
    //   component: Dashboard,
    //   props: true
    // },
    // {
    //     path: "/sessions",
    //     name: "Session Manager",
    //     component: Sessions,
    //     props: true
    // }
  ]
});
