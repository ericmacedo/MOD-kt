<template>
<div class="dashboard h-100 w-100">
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
      <b-row>
        <b-col cols="12" sm="6" md="6" lg="4">
          <document-view id="documentView"
            class="component h-50"></document-view>
          <word-cloud id="wordCloudView"
            class="component h-50 w-100"></word-cloud>
        </b-col>
        <b-col cols="12" sm="6" md="6" lg="4">
          <graph-view id="graphView"
            class="component h-100 w-100"></graph-view>
        </b-col>
        <b-col cols="12" sm="6" md="6" lg="4">
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
					@click="cluster">
					<font-awesome-icon :icon="['fas', 'plus']"/>&nbsp;
					Start a new session
				</b-list-group-item>
				<!-- LOADED SESSIONS -->
				<b-list-group-item
					v-for="(session, index) of $userData.sessions"
					:key="index"
					button
					variant="dark"
					@click="getSession(session.id)"
					class="flex-column align-items-start">
					<div class="d-flex w-100 justify-content-between">
						<h5 class="mb-1">{{ session.name }}</h5>
						<small>{{ session.date }}</small>
					</div>
					<p class="mb-1">
						{{ session.notes }}
					</p>
				</b-list-group-item>
			</b-list-group>
		</div>
	</b-modal>
</div>
</template>

<script>
import GraphView from './dashboard/GraphView';
import DocumentView from './dashboard/DocumentView';
import ClusterManager from './dashboard/ClusterManager';
import WordCloud from './dashboard/WordCloudView';
import WordSimilarity from './dashboard/WordSimilarityView';

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
	mounted() {
		this.$bvModal.show('dashboard-sessions-modal');
	},
	methods: {
		getSession(id) {
			let objRef = this;
			
			this.$bvModal.hide('dashboard-sessions-modal');

			if(Object.keys(this.$session).length > 0 &&
				!confirm("Did you saved all your current work?")) {
				return;
			}

			this.sessionData = this.$axios.get(this.$server+"/session",{
					params: {
						userId: this.$userData.userId,
						sessionId: id}});

			this.sessionData.then((result) => {
				const session = result.data.sessionData;
				objRef.$session.name 			= session.name;
				objRef.$session.notes			= session.notes;
				objRef.$session.index			= session.index;
				objRef.$session.graph			= session.graph;
				objRef.$session.tsne			= session.tsne;
				objRef.$session.clusters	= session.clusters;
				objRef.$session.controls	= session.controls;
				objRef.$session.focused		= session.focused;
				objRef.$session.date 			= session.date;

				objRef.$parent.updateSessionName(session.name);
			});
		},
		cluster() {
			let objRef = this;
			
			this.$bvModal.hide('dashboard-sessions-modal');

			const cluster_k = prompt("Please, inform the number of clusters you want to find:")
		
			const formData = new FormData();
			formData.set("userId", this.$userData.userId);
			formData.set("cluster_k", cluster_k);
			
			this.sessionData = this.$axios.post(this.$server+"/cluster",
				formData, { headers: { "Content-Type": "multipart/form-data" }
			});

			this.sessionData.then((result) => {
				const session = result.data.sessionData;
				objRef.$session.name.text	  = session.name;
				objRef.$session.notes.text  = session.notes;
				objRef.$session.index			  = session.index;
				objRef.$session.graph			  = session.graph;
				objRef.$session.tsne			  = session.tsne;
				objRef.$session.clusters	  = session.clusters;
				objRef.$session.controls	  = session.controls;
				objRef.$session.date 			  = session.date;
				
				let _corpus = objRef.$userData.corpus.filter(
					d => objRef.$session.index.includes(d.id));
				
				// the first document is focused and selected by default
				objRef.$session.selected		            = [_corpus[0]];
				objRef.$session.focused.id			        = _corpus[0].id;
        objRef.$session.highlight.cluster_name  = undefined;
        objRef.$session.word_similarity         = {
          query: [],
          result: []}
			});
		}
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
	border: 2px solid #161616

.card
	header
		padding: 0
		text-align: center
		height: 25px

#documentView
  max-height: 300px !important
  #displaCy
    padding: 5px

#wordCloudView
  max-height: 300px !important

#graphView
  margin: 0

#clusterManagerView
  max-height: 300px !important

</style>
