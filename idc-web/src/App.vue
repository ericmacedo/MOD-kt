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
                    {{ session_name.text }}
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
              <em>{{ $userData.userId }}</em>
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
      session_name: this.$session.name,
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
    // this.$userData.userId = prompt("Please enter your Username");

    // const formData = new FormData();
		// formData.set("userId", this.$userData.userId);

    // let objRef = this;
    // this.userData = this.$axios.post(this.$server+"/auth", formData, {
    //   headers: { "Content-Type": "multipart/form-data" }
    // }).then(function(result) {
    //   objRef.$userData.userId = result.data.userData.userId;
    //   objRef.$userData.corpus	= result.data.userData.corpus ?? [];
    //   objRef.$userData.sessions	= result.data.userData.sessions ?? [];

    //   objRef.makeToast(
    //     "success",
    //     "Logged in successfully!",
    //     "Welcome, "+objRef.$userData.userId );
    // }).catch(function() {
    //   alert("No such user exists!");
    //   window.location.reload();
    // });

    const userId = prompt("Please enter your Username");

    this.userData = this.$store.dispatch("getUserData", userId);

    this.userData.then(function() {
      objRef.makeToast(
        "success",
        "Logged in successfully!",
        "Welcome, "+objRef.$store.state.userData.userId);
    }).catch(function() {
      // console.log(error);
      alert("No such user exists!");
      // window.location.reload();
    });
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
    clearUserData() {
      let objRef = this;

      if(confirm("You're about to erase all of your data, are you sure?")) {
        // FORM
        const formData = new FormData();
        formData.set("userId", this.$userData.userId);
        formData.set("ids", []);
        formData.set("RESET_FLAG", true);

        this.$axios.post(this.$server+"/corpus", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        }).then(function() {
          objRef.makeToast(
            "success",
            "Success!",
            "User data cleared!");
        }).catch(function() {
          objRef.makeToast(
            "danger",
            "Oops, something went wrong!",
            "Try reloading the page");
        });
      }
    },
    toggleRowActive(index) {
      this.navbar.activeIndex = index;
    },
    cluster() {
      let objRef = this,
          session = this.$session;
		
			const formData = new FormData();
			formData.set("userId", this.$userData.userId);
			formData.set("cluster_k", session.clusters.cluster_k);
      formData.set("session", JSON.stringify({
        name: session.name.text,
        notes: session.notes.text,
        index: session.index,
        graph: session.graph,
        tsne: session.tsne,
        clusters: session.clusters,
        controls: session.controls,
        date: session.date,
        selected: session.selected,
        focused: session.focused.id,
        highlight: session.highlight.cluster_name,
        word_similarity: session.word_similarity
      }));
			
			this.sessionData = this.$axios.post(this.$server+"/cluster",
				formData, { headers: { "Content-Type": "multipart/form-data" }
			});

			this.sessionData.then((result) => {
				const session = result.data.sessionData;
				objRef.$session.name.text	  = session.name;
				objRef.$session.notes.text  = session.notes;
				objRef.$session.index			  = session.index;
				
        objRef.$session.graph.nodes	        = session.graph.nodes;
        objRef.$session.graph.distance      = session.graph.distance;
        objRef.$session.graph.neighborhood	= session.graph.neighborhood;
				
        objRef.$session.tsne			  = session.tsne;
				objRef.$session.clusters	  = session.clusters;
				objRef.$session.controls	  = session.controls;
				objRef.$session.date 			  = session.date;
				
				// the first document is focused and selected by default
				objRef.$session.selected		            = session.selected;
				objRef.$session.focused.id			        = session.focused;
        objRef.$session.highlight.cluster_name  = session.highlight;
        objRef.$session.word_similarity         = session.word_similarity
        
        objRef.$forceUpdate();
			}).catch(() => {
        objRef.makeToast(
          "danger",
          "Oops, something went wrong!",
          "Try reloading the page");
      });
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
