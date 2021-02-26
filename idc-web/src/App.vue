<template>
<div id="app">
  <b-navbar sticky
    class="w-100"
    toggleable="lg"
    type="dark" variant="dark">
    <b-navbar-brand to="/" >{{ title }}</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <!-- Right aligned nav items -->
      <b-col cols="4">
        <b-navbar-nav>
          <b-nav-item 
            v-for="(item, index) in navbar.items"
            :key="index"
            :to="item.path"
            :active="$route.path === item.path"
            :index="index">
            <a @click="toggleRowActive(index)">
              <font-awesome-icon :icon="['fas', item.icon]"/>
              &nbsp; {{ item.name }}
            </a>
          </b-nav-item>
        </b-navbar-nav>
      </b-col>
      <b-col cols="2" >
        <b-navbar-nav
          v-if="$route.name === 'Corpus' || $route.name === 'Dashboard'"
          class="justify-content-md-center">
          <b-nav-item align="start">
            <!-- TODO implement clustering function -->
            <b-button pill size="sm" variant="success">
              <strong>Cluster</strong>&nbsp;
              <font-awesome-icon :icon="['fas', 'play']"/>
            </b-button>
          </b-nav-item>
        </b-navbar-nav>
      </b-col>
      <!-- Right aligned nav items -->
      <b-col cols="6">
        <b-navbar-nav class="ml-auto align-right">
          <b-nav-form
            v-if="$route.name === 'Dashboard'">
            <b-nav-item>
              <notes-widget></notes-widget>
            </b-nav-item>
            <b-nav-item>
              <b-input-group size="sm" prepend="Session">
                <b-form-select size="sm">
                  <template #first>
                    <b-form-select-option
                      v-model="sessionSelector.selected"
                      :options="sessionSelector.options"
                      :value="null">--&nbsp;Create new session&nbsp;--</b-form-select-option>
                  </template>
                </b-form-select>
                <b-button-group size="sm" class="navbar-item-spaced">
                  <b-button
                    variant="outline-danger">
                    <font-awesome-icon :icon="['fas', 'trash']"/>
                    Delete
                  </b-button>
                  <b-button
                    variant="outline-success">
                    <font-awesome-icon :icon="['fas', 'save']"/>
                    Save
                  </b-button>
                </b-button-group>
              </b-input-group>
            </b-nav-item>
          </b-nav-form>
          <b-nav-item-dropdown right class="navbar-item-spaced">
            <!-- Using 'button-content' slot -->
            <template #button-content>
              <font-awesome-icon :icon="['fas', 'user-circle']"/> &nbsp;
              <em>{{ $userData.userId }}</em>
            </template>
            <b-dropdown-item @click="updateUserData">
              <font-awesome-icon :icon="['fas', 'sync']"/>
              Reload user data
            </b-dropdown-item>
            <b-dropdown-item to="/logout">
              <font-awesome-icon :icon="['fas', 'sign-out-alt']"/>
              Log Out
            </b-dropdown-item>
          </b-nav-item-dropdown>
        </b-navbar-nav>
      </b-col>
      
    </b-collapse>
  </b-navbar>
  <keep-alive>
    <router-view
      id="mainView"
      v-bind:userData="userData"
      class="h-100 w-100 container-fluid"/>
  </keep-alive>
</div>
</template>

<script>
import NotesWidget from './components/NotesWidget';

export default {
  name: 'App',
  components: {
    "notes-widget": NotesWidget
  },
  created() {
    this.$userData.userId = prompt("Please enter your Username");

    const formData = new FormData();
		formData.set("userId", this.$userData.userId);

    let objRef = this;
    this.$axios.post(this.$server+"/auth", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(function(result) {
      objRef.$userData.userId = result.data.userData.userId;
      objRef.$userData.corpus	= result.data.userData.corpus;
      objRef.$userData.newDocs = result.data.userData.newData;

      objRef.makeToast(
        "success",
        "Logged in successfully!",
        "Welcome, "+objRef.$userData.userId );
    }).catch(function() {
      alert("No such user exists!");
    });
  },
  data: function() {
    return {
      title: "Vis-Kt",
      userData: this.$userData,
      navbar: {
        items: [
          {
            name: "Corpus",
            icon: "book",
            path: "/corpus"
          },
          {
            name: "Dashboard",
            icon: "tachometer-alt",
            path: "/dashboard"
          },
          {
            name: "Session Manager",
            icon: "code-branch",
            path: "/sessions"
          }
        ],
        activeIndex: -1
      },
      sessionSelector: {
        selected: null,
        options: []
      }
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
    updateUserData() {
      const formData = new FormData();

      formData.set("userId", this.$userData.userId);

      let objRef = this;
      this.$axios.post(this.$server+"/auth", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      }).then(function(result) {
        objRef.$userData.userId = result.data.userData.userId;
        objRef.$userData.corpus	= result.data.userData.corpus;
        objRef.$userData.newDocs = result.data.userData.newData;
        
        objRef.makeToast(
          "success",
          "Success!",
          "User data reloaded!");
      }).catch(function() {
        objRef.makeToast(
          "danger",
          "Oops, somethings went wrong!",
          "Try reloading the page");
      });
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
  justify-content: center;
  vertical-align: middle;
  margin: auto;
	margin: auto;
}

.navbar-item-spaced {
  /* margin-left: 5px;
  margin-right: 5px; */
  padding-left: 5px;
  padding-right: 5px;
}
.align-right {
  justify-content: flex-end;
}
</style>
