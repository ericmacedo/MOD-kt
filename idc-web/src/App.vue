<template>
<div id="app">
  <b-navbar sticky toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand to="/" >{{ title }}</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <!-- Right aligned nav items -->
      <b-navbar-nav no-gutter>
        <b-nav-item 
          v-for="(item, index) in navbar.items"
          :key="index"
          :to="item.path"
          :active="$route.path === item.path"
          :index="index"
          @click="toggleRowActive(index)">
          <font-awesome-icon :icon="['fas', item.icon]"/>
          &nbsp; {{ item.name }}
        </b-nav-item>
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-form>
          <b-form-input size="sm" class="mr-sm-2" placeholder="Search"></b-form-input>
          <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>
        </b-nav-form>

        <b-nav-item-dropdown right>
          <!-- Using 'button-content' slot -->
          <template #button-content>
            <font-awesome-icon :icon="['fas', 'user-circle']"/> &nbsp;
            <em>{{ userId }}</em>
          </template>
          <b-dropdown-item to="/logout">
            <font-awesome-icon :icon="['fas', 'sign-out-alt']"/>
            Log Out
          </b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>
  <keep-alive>
    <router-view
      id="mainView"
      :userData="userData"
      class="container"/>
  </keep-alive>
</div>
</template>

<script>
export default {
  name: 'App',
  beforeMount(){
    this.userId = prompt("Please enter your Username");

    const formData = new FormData();
		formData.set("userId", this.userId);

    let objRef = this;
    this.$axios.post(this.$server+"/auth", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(function(result) {
      console.log(result.data);
      objRef.updateUserData(result.data.userData);
      objRef.makeToast(
        "success",
        "Logged in successfully!",
        "Welcome, "+objRef.userId);
    }).catch(function() {
      alert("No such user exists!");
    });
  },
  data: function() {
    return {
      "title": "Vis-Kt",
      "userId": String,
      "userData": {},
      "navbar": {
        "items": [
          {
            "name": "Corpus",
            "icon": "book",
            "path": "/corpus"
          },
          {
            "name": "Dashboard",
            "icon": "tachometer-alt",
            "path": "/dashboard"
          },
          {
            "name": "Session Manager",
            "icon": "code-branch",
            "path": "/sessions"
          }
        ],
        "activeIndex": -1
      },
    }
  },
  methods: {
    makeToast(variant = null, title, content) {
      this.$bvToast.toast(content, {
        variant: variant,
        title: title,
        toaster: "b-toaster-bottom-right",
        solid: false,
        autoHideDelay: 5000,
      })
    },
    updateUserData: function(userData) {
      this.userData = userData;
    },
    toggleRowActive(index) {
      this.navbar.activeIndex = index;
    }
  }
}
</script>

<style>
#app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  border: 0;
}

#mainView {
  height: 100%;
  width: 100%;
  /* margin: 60px 10px 10px 10px; */
  justify-content: center;
  vertical-align: middle;
}
</style>
