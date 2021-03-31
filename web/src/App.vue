<template>
<div id="app" ref="app" class="w-100 h-100">
  <b-navbar small
    id="navbar"
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
            <b-button-group size="sm">
              <b-button
                id="fab-btn"
                class="mr-1"
                variant="info"
                v-b-modal.upload-modal>
                <font-awesome-icon :icon="['fas', 'plus']"/>&nbsp;
              </b-button>
              <b-button
                size="sm"
                title="Cluster the corpus with the given configuration on 'Cluster Manager'"
                variant="success"
                @click="callCluster">
                <strong>Cluster</strong>&nbsp;
                <font-awesome-icon :icon="['fas', 'play']"/>
              </b-button>
            </b-button-group>
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
                    {{ session_name }}
                  </b-button>
                  <b-button
                    v-b-modal.session-save-modal
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
              <em>{{ userId }}</em>
            </template>
            <!-- TODO add "clear user data" with modal confirm -->
            <b-dropdown-item @click="callClearUserData">
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
      <transition>
        <keep-alive>
          <router-view
            id="mainView"
            :dashboardKey="keys.dashboard"
            :corpusKey="keys.corpus"
            :sessionKey="keys.session"
            class="h-100 w-100 container-fluid"/>
        </keep-alive>
      </transition>
    </template>
    <template v-slot:rejected>
      <p>oops, something went wrong!</p>
    </template>
  </Promised>
  
  <b-modal
		ref="session-save-modal"
		id="session-save-modal"
		size="lg"
		header-bg-variant="dark"
		header-text-variant="light"
		:title="'Saving session '+session_name+'...'"
		centered
    scrollable
		no-close-on-backdrop
		no-close-on-esc
    @ok="callSaveSession">
		<div class="d-block">
      <label for="session-name">Name:</label>
      <b-form-input
        id="session-name"
        v-model="session_name"
        placeholder="Enter a name for your session"></b-form-input>
      <label
        class="mt-2"
        for="session-notes">Notes:</label>
      <b-form-textarea
        v-model="notes"
        rows="10"
				max-rows="10"
        size="md"
        placeholder="Notes"></b-form-textarea>
		</div>
	</b-modal>

  <b-modal
		ref="upload-modal"
		id="upload-modal"
		size="lg"
		header-bg-variant="dark"
		header-text-variant="light"
		title="Upload new documents"
		centered
    scrollable
    hide-footer
		no-close-on-backdrop
		no-close-on-esc>
		<upload-component
      v-on:re-render="incremented()"
      context="MODAL"></upload-component>
	</b-modal>
</div>
</template>

<script>
import NotesWidget from './components/dashboard/NotesWidget';
import UploadComponent from "./components/UploadComponent";
import { mapState, mapActions } from "vuex";

export default {
  name: 'App',
  components: {
    "notes-widget": NotesWidget,
    "upload-component": UploadComponent
  },
  data: function() {
    return {
      title: "Vis-Kt",
      userData: undefined,
      keys: {
        corpus: 0,
        dashboard: 0,
        session: 0
      },
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
  computed: {
    session_name: {
      get() {
        return this.$store.state.session.name;
      },
      set(name) {
        this.$store.commit("session/setName", name);
      }
    },
    notes: {
      get() {
        return this.$store.state.session.notes;
      },
      set(notes) {
        this.$store.commit("session/setNotes", notes);
      }
    },
    ...mapState("userData", ["userId"])
  },
  created() {
    let objRef = this;

    const userId = prompt("Please enter your Username");

    this.userData = this.getUserData(userId);

    this.userData.then(function() {
      objRef.makeToast(
        "Logged in successfully!",
        "Welcome, "+objRef.$store.state.userData.userId,
        "success");
    }).catch(function() {
      alert("No such user exists!");
      window.location.reload();
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
      
      this.userData = this.getUserData(this.userId);

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
    callClearUserData() {
      let objRef = this;

      if(confirm("You're about to erase all of your data, are you sure?")) {
        this.clearUserData()
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
    callCluster() {
      let objRef = this;

      objRef.makeToast(
          "Clustering your data",
          "Please wait",
          "warning",
          "cluster-data");
			
			this.sessionData = this.cluster();

      this.sessionData.then(() => {
        objRef.incremented();
      }).catch(() => {
        objRef.makeToast(
          "Oops, something went wrong!",
          "Please, try again",
          "danger");
      }).then(() => objRef.$bvToast.hide("cluster-data"));
    },
    callSaveSession() {
      let objRef = this;

      this.makeToast(
        `Saving session "${this.session_name}"`,
        "Please wait",
        "warning",
        "save-session");
			
			this.saveSession()
        .then(() => {
          objRef.makeToast(
            "Success",
            "Your session was successfully saved",
            "success");
            objRef.getUserData(objRef.userId);
        })
        .catch(() => {
          objRef.makeToast(
            "Oops, something went wrong!",
            "Please, try again",
            "danger");
        }).then(() => objRef.$bvToast.hide("save-session"));
    },
    updateDashboard() {
      this.keys.dashboard++;
    },
    ...mapActions([
      "cluster", "getUserData", "clearUserData", "saveSession"])
  }
}
</script>

<style lang="sass">
body, html
  padding-top: 30px
  height: 100% !important
  width: 100% !important

#app
  position: relative
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
