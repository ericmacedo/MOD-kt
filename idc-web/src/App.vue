<template>
<div id="app">
  <b-navbar sticky toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand to="/" >{{ title }}</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <!-- Right aligned nav items -->
      <b-navbar-nav no-gutter>
        <!-- eslint-disable -->
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
        <!-- eslint-enable -->
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-form
          v-if="$route.name === 'Dashboard'">
          <notes-widget></notes-widget>
          <b-nav-item>Current session: </b-nav-item>
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
        </b-nav-form>

        <b-nav-item-dropdown right class="navbar-item-spaced">
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
      class="h-100 w-100 container"/>
  </keep-alive>
</div>
</template>

<script>
const NotesWidget = {
  name: "notes-widget",
  data(){
    return {notes: this.$session.notes};
  },
  template: `
    <div>
      <b-button rounded
        id="notes"
        rounded size="sm"
        class="navbar-item-spaced"
        variant="outline-warning">
        <font-awesome-icon :icon="['fas', 'sticky-note']"/>
        Notes
      </b-button>
      <b-popover placement="bottom"
        target="notes" variant="warning" triggers="hover">
        <template #title>
          <b-button
            variant="outline-warning"
            size="sm"
            v-b-modal.notesModal>
            <font-awesome-icon :icon="['fas', 'expand-alt']"/>
          </b-button>
        </template>
        <b-form-textarea
          placeholder="Type some notes..."
          v-model="notes"
          rows="3"
          max-rows="6"
        ></b-form-textarea>
      </b-popover>
      <b-modal id="notesModal" hide-footer
        header-bg-variant="warning"
        header-text-variant="light"
        body-bg-variant="warning"
        body-text-variant="light">
        <template #modal-title>
          Notes for session: {{ $session.name }}
        </template>
        <template #default>
          <b-form-textarea
            v-model="notes"
            placeholder="Type some notes..."
            rows="10"
            max-rows="10"
          ></b-form-textarea>
        </template>
      </b-modal>
    </div>`
}

export default {
  name: 'App',
  components: {
    "notes-widget": NotesWidget
  },
  created() {
    this.userId = prompt("Please enter your Username");

    const formData = new FormData();
		formData.set("userId", this.userId);

    let objRef = this;
    this.$axios.post(this.$server+"/auth", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    }).then(function(result) {
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
      title: "Vis-Kt",
      userId: String,
      userData: {},
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
</style>
