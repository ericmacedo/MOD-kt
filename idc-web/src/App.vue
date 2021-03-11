<template>
<div id="app">
  <b-navbar sticky small
    fixed="top"
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
          v-if="$route.name === 'Dashboard'"
          class="justify-content-md-center">
          <b-nav-item align="start">
            <!-- TODO implement clustering function -->
            <b-button pill
              size="sm"
              title="Cluster the corpus with the given configuration on 'Cluster Manager'"
              variant="success"
              @click="cluster">
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
          size="sm"
            v-if="$route.name === 'Dashboard'">
            <b-nav-item>
                <b-button-group size="sm">
                  <notes-widget></notes-widget>
                  <b-button disabled
                    id="sessionLabel"
                    variant="dark">
                    {{ $store.state.session.name }}
                  </b-button>
                  <b-button
                    title="Delete the current session"
                    variant="outline-danger">
                    <font-awesome-icon :icon="['fas', 'trash']"/>
                    Delete
                  </b-button>
                  <b-button
                    title="Save the current session"
                    variant="outline-success">
                    <font-awesome-icon :icon="['fas', 'save']"/>
                    Save
                  </b-button>
                </b-button-group>
                <b-button-group size="sm">
                  <b-button
                    v-b-modal.dashboard-sessions-modal
                    title="Load a session"
                    class="navbar-item-spaced ml-3"
                    variant="outline-info">
                    <font-awesome-icon :icon="['fas', 'list']"/>
                  </b-button>
                </b-button-group>
            </b-nav-item>
          </b-nav-form>
          <b-nav-item-dropdown size="sm" right class="navbar-item-spaced align-vertical">
            <!-- Using 'button-content' slot -->
            <template #button-content>
              <font-awesome-icon :icon="['fas', 'user-circle']"/> &nbsp;
              <em>{{ $store.state.userData.userId }}</em>
            </template>
            <!-- TODO add "clear user data" with modal confirm -->
            <b-dropdown-item @click="clearUserData">
              <font-awesome-icon :icon="['fas', 'trash']"/>
              Clear user data
            </b-dropdown-item>
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

  <Promised :promise="userData">
    <template v-slot:pending>
      <div class="h-100 text-center">
        <b-spinner
          class="m-5"
          variant="primary"></b-spinner>
      </div>
    </template>
    <template v-slot:default>
      <keep-alive>
        <router-view
          id="mainView"
          :width="Width"
          :height="Height"
          class="h-100 w-100 container-fluid"/>
      </keep-alive>
    </template>
    <template v-slot:rejected>
      <p>oops, something went wrong!</p>
    </template>
  </Promised>
</div>
</template>

<script>
import NotesWidget from './components/dashboard/NotesWidget';

export default {
  name: 'App',
  components: {
    "notes-widget": NotesWidget
  },
  data: function() {
    return {
      title: "Vis-Kt",
      userData: undefined,
      Height: 500,
      Width: 500,
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
      }
    }
  },
  created() {
    let objRef = this;

    const userId = prompt("Please enter your Username");

    this.userData = this.$store.dispatch("getUserData", userId);

    this.userData.then(function() {
      objRef.makeToast(
        "Logged in successfully!",
        "Welcome, "+objRef.$store.state.userData.userId,
        "success");
    }).catch(function() {
      // console.log(error);
      alert("No such user exists!");
      // window.location.reload();
    });
  },
  methods: {
    makeToast(
				title,
				content,
				variant,
				id=null) {
			// Use a shorter name for this.$createElement
			const h = this.$createElement
			// Create the message
			const vProgressToast = h(
				'p', { class: ['mb-0'] },
				[h('b-spinner', { props: { small: true } }), ` ${content}`]);
			this.$bvToast.toast(
				(id) ? vProgressToast : content,
				{
					id: (id) ? id : null,
					variant: variant,
					title: title,
					toaster: "b-toaster-bottom-right",
					solid: false,
					autoHideDelay: 5000,
					noAutoHide: (id) ? true : false,
					noCloseButton: (id) ? true : false,
					appendToast: true
				});
		},
    updateUserData() {
      let objRef = this;
      
      this.userData = this.$store.dispatch(
        "getUserData",
        this.$store.state.userData.userId);

      this.userData.then(function() {
        objRef.makeToast(
          "Success!",
          "User data reloaded!",
          "success");
      }).catch(function() {
        objRef.makeToast(
          "Oops, somethings went wrong!",
          "Try reloading the page",
          "danger");
      });
    },
    clearUserData() {
      let objRef = this;

      if(confirm("You're about to erase all of your data, are you sure?")) {
        this.$store.dispatch("clearUserData")
          .then(function() {
            objRef.makeToast(
              "Success!",
              "User data cleared!",
              "success");
          }).catch(function() {
            objRef.makeToast(
              "Oops, something went wrong!",
              "Try reloading the page",
              "danger");
          });
      }
    },
    toggleRowActive(index) {
      this.navbar.activeIndex = index;
    },
    cluster() {
      let objRef = this;

      objRef.makeToast(
          "Clustering your data",
          "Please wait",
          "warning",
          "cluster-data");
			
			this.sessionData = this.$store.dispatch("cluster");

			this.sessionData.catch(() => {
        objRef.makeToast(
          "Oops, something went wrong!",
          "Please, try again",
          "danger");
      }).then(() => objRef.$bvToast.hide("cluster-data"));
    }
  }
}
</script>

<style lang="sass">
#app
  height: 100%
  width: 100%
  margin: 0
  padding: 0
  border: 0

#mainView
  justify-content: center
  vertical-align: middle
  margin: auto
  margin: auto

.align-right
  justify-content: flex-end

#sessionLabel
  white-space: normal
  word-wrap: break-word
  max-width: 300px

.align-vertical
  align-self: center
</style>
