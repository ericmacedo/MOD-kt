<template>
<div class="dashboard">
	<Promised :promise="sessionData">
	<template v-slot:pending>
		<div class="h-100 text-center">
			<b-spinner
				class="m-5"
				variant="primary"></b-spinner>
		</div>
    </template>
    <template v-slot:default>
		<b-container fluid>
      <b-row no-gutters>
        <b-col cols="12" sm="12" md="6" lg="4">
          <document-view id="documentView"
            class="component h-50 w-100"></document-view>
          <word-cloud id="wordCloudView"
            class="component h-50 w-100"></word-cloud>
        </b-col>
        <b-col cols="12" sm="12" md="6" lg="4">
          <graph-view id="graphView" ref="graphView"
            class="component w-100"></graph-view>
        </b-col>
        <b-col cols="12" sm="12" md="6" lg="4">
          <cluster-manager id="clusterManagerView"
            class="component h-50 w-100"></cluster-manager>
            <word-similarity id="wordSimilarityView"
              class="component h-50 w-100"></word-similarity>
        </b-col>
      </b-row>
		</b-container>
	</template>
	<template v-slot:rejected>
    <p>oops, something went wrong!</p>
  </template>
	</Promised>

	<b-modal
		ref="dashboard-sessions-modal"
		id="dashboard-sessions-modal"
		size="lg"
		header-bg-variant="dark"
		header-text-variant="light"
		title="Select a session to load"
		scrollable
		centered
		hide-footer
		no-close-on-backdrop
		no-close-on-esc>
		<div class="d-block text-center">
			<b-list-group>
				<!-- NEW SESSION -->
				<b-list-group-item
					class="text-center"
					button
					variant="success"
					@click="callCluster">
					<font-awesome-icon :icon="['fas', 'plus']"/>&nbsp;
					Start a new session
				</b-list-group-item>
      </b-list-group>
      <br/>
      <b-list-group>
				<!-- LOADED SESSIONS -->
				<b-list-group-item
					v-for="(session, index) of sessions"
					:key="index"
					button
					variant="dark"
					class="flex-column align-items-start">
					<div class="d-flex w-100 justify-content-between">
						<h5 class="mb-1">{{ session.name }}</h5>
						<small>
              {{ session.date }}
              <b-button-group size="sm">
                <b-button
                  class="ml-2"
                  variant="outline-success"
                  @click="callGetSession(session.id)">
                  <font-awesome-icon :icon="['fas', 'download']"/>&nbsp;
                  Load session
                </b-button>
                <b-button
                  class="ml-2"
                  variant="outline-danger"
                  @click="callDeleteSession(session)">
                  <font-awesome-icon :icon="['fas', 'trash']"/>
                </b-button>
              </b-button-group>
            </small>
					</div>
					<p class="mb-1">
						{{ session.notes }}
					</p>
				</b-list-group-item>
			</b-list-group>
		</div>
	</b-modal>
  <b-modal
		ref="process-redirect-modal"
		id="process-redirect-modal"
		size="md"
		header-bg-variant="dark"
		header-text-variant="light"
		title="You need to process you corpus!"
		centered
    no-close-on-backdrop
		no-close-on-esc
		hide-footer>
		<div class="d-block text-center">
			<h6>Before you can start to explore your corpus, you need to process it! Do you want to do it now?</h6>
		</div>
		<b-button
			class="mt-3"
			variant="outline-success"
			block
			@click="$bvModal.hide('process-redirect-modal')"
			to="/corpus">
				<font-awesome-icon :icon="['fas', 'book']"/>&nbsp;
				Yes, take me to <strong>Corpus</strong>!
		</b-button>
	</b-modal>
</div>
</template>

<script>
import GraphView from './dashboard/GraphView';
import DocumentView from './dashboard/DocumentView';
import ClusterManager from './dashboard/ClusterManager';
import WordCloud from './dashboard/WordCloudView';
import WordSimilarity from './dashboard/WordSimilarityView';
import { mapState, mapActions } from "vuex";

export default {
	name: 'Dashboard',
	components: {
		"graph-view":       GraphView,
		"document-view":    DocumentView,
		"cluster-manager":  ClusterManager,
    "word-cloud":       WordCloud,
    "word-similarity":  WordSimilarity
  },
	data() {
		return {
			sessionData: undefined
		}
	},
  computed: {
    ...mapState("userData", ["userId", "sessions", "isProcessed"])
  },
	mounted() {
    if(this.isProcessed) {
      this.$bvModal.show('dashboard-sessions-modal');
    } else {
      this.$bvModal.show('process-redirect-modal');
    }
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
		callGetSession(id) {
			let objRef = this;
			
			this.$bvModal.hide('dashboard-sessions-modal');

			this.sessionData = this.getSessionById(id);

			this.sessionData.then(() => {
				objRef.makeToast(
          "Success",
          "Session retrieved",
          "success");
			}).catch(() => {
        objRef.makeToast(
          "Error",
          "Looks like something went wrong, please, try again",
          "danger");
      });
		},
		callCluster() {
			let objRef = this;
			
			this.$bvModal.hide('dashboard-sessions-modal');

			const cluster_k = prompt("Please, inform the number of clusters you want to find:");

      this.makeToast(
          "Clustering your data",
          "Please wait",
          "warning",
          "cluster-data");
			
			this.sessionData = this.cluster(cluster_k);

			this.sessionData.catch(() => {
        objRef.makeToast(
          "Oops, something went wrong!",
          "Please, try again",
          "danger");
      }).then(() => objRef.$bvToast.hide("cluster-data"));
		},
    callDeleteSession(session) {
      let objRef = this;
      
      if (confirm(`You're about to delete session "${session.name}", are you sure?`)) {
        this.deleteSession(session.id)
          .then(() => {
            objRef.makeToast(
              "Success",
              "Your session was successfully deleted",
              "success");
            objRef.getUserData(objRef.userId);
          })
          .catch(() => {
            objRef.makeToast(
              "Oops, something went wrong!",
              "Please, try again",
              "danger");
          });
      }
    },
    ...mapActions(["getSessionById", "cluster", "deleteSession", "getUserData"])
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
.dashboard
	padding: 5px
	border: 0!important
	margin: 0!important

.component
	border: 1px solid #c3c3c3

.card
	header
		padding: 0
		text-align: center
		height: 25px

#documentView
  height: 45vh !important

#wordCloudView
  height: 45vh !important

#graphView
  margin: 0
  height: 90vh !important

#clusterManagerView
  height: 40vh !important

#wordSimilarityView
  height: 50vh !important
</style>
