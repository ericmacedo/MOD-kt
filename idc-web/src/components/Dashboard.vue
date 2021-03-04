<template>
<div class="dashboard h-100 w-100">
	<!-- TODO add vue-promised for get_sessionData -->
	<Promised :promise="sessionData">
	<template v-slot:pending>
		<div class="h-100 text-center">
			<b-spinner
				class="m-5"
				variant="primary"></b-spinner>
		</div>
    </template>
    <template v-slot:default>
		<b-card-group deck>
			<document-view id="documentView"></document-view>
			<graph-view id="graphView"
				sm="12" md="4" lg="4"></graph-view>
		</b-card-group>
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
import GraphView from './GraphView';
import DocumentView from './DocumentView';

export default {
	name: 'Dashboard',
	components: {
		"graph-view": GraphView,
		"document-view": DocumentView
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
				objRef.$session.name 			= session.name;
				objRef.$session.notes			= session.notes;
				objRef.$session.index			= session.index;
				objRef.$session.graph			= session.graph;
				objRef.$session.tsne			= session.tsne;
				objRef.$session.clusters	= session.clusters;
				objRef.$session.controls	= session.controls;
				objRef.$session.date 			= session.date;
				objRef.$session.selected	= [objRef.$session.index[0]]; // the first document is focused by default
				objRef.$session.focused		= null;

				objRef.$parent.updateSessionName(session.name);
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

.card-header
	padding: 1px
	text-align: center
	height: 25px
</style>
