<template>
<b-card no-body>
	<b-card-header header-tag="header" class="text-center">
		Cluster Manager
	</b-card-header>
	<b-container fluid>
		<b-row cols="4" class="p-1">
			<b-col
				v-for="(cluster, index) in $session.clusters.cluster_names"
				:key="index"
				class="mb-3 p-0">
				<b-card no-body class="cluster-card text-center"
					:id="'cluster_card_'+index"
					text-variant="white"
					title="Click to edit this cluster"
					@click="launchEditor(index)">
					<b-card-header
						header-tag="header"
						:style="[{'background': $session.clusters.colors[index]}]">
						<strong>{{ cluster }}</strong>
					</b-card-header>
					<b-list-group>
						<b-list-group-item
							class="cluster-card"
							v-for="word in $session.clusters.cluster_words[index]"
							:key="word.word"
							:variant="word.weight > 0 ? 'success' :'danger'">
						{{ word.word }}
						</b-list-group-item>
					</b-list-group>
				</b-card>
			</b-col>
		</b-row>
	</b-container>
	<b-button
		size="sm"
		variant="outline-dark"
		class="mx-auto mt-3"
		title="Click to create a new cluster"
		@click="launchEditor()">
		<font-awesome-icon 
			size="sm"
			:icon="['fas', 'plus']"/>
	</b-button>

	<b-modal
		ref="cluster-editor"
		id="cluster-editor"
		size="md"
		header-bg-variant="dark"
		header-text-variant="light"
		title="Cluster editor"
		centered
		no-close-on-backdrop
		no-close-on-esc
		@ok="submitChanges">
		<div class="d-block text-center">
			<b-input-group>
				<b-form-input
					v-model="modal.cluster_name"
					placeholder="Enter a name for your cluster"
					:state="validClusterName(modal.cluster_name)"></b-form-input>
				<b-form-input
					class="mb-1"
					v-model="modal.color"
					value="#000000"
					type="color"></b-form-input>
				<b-input-group-append>
					<small><b-button
						class="ml-2"
						size="md"
						title="Delete this cluster"
						variant="outline-danger"
						:disabled="modal.index == $session.clusters.cluster_k"
						@click="deleteCluster">
						<font-awesome-icon :icon="['fas', 'trash']"/>
					</b-button></small>
				</b-input-group-append>
			</b-input-group>
			<b-list-group>
				<b-list-group-item
					v-for="(word, index) of modal.words"
					:key="index"
					:variant="word.weight > 0 ? 'success' : 'danger'"
					class="flex-column align-items-start">
					<div
						class="d-flex w-100 justify-content-between"
						style="align-items: center;">
						<h6 class="mb-1">{{ word.word }}</h6>
						<small>
							<b-button-group size="sm">
								<b-button
									variant="outline-danger"
									@click="word.weight = -1">
									<font-awesome-icon :icon="['fas', 'minus']"/>
								</b-button>
								<b-button
									variant="outline-secondary"
									@click="modal.words.pop(index)">
									<font-awesome-icon :icon="['fas', 'trash']"/>
								</b-button>
								<b-button
									variant="outline-success"
									@click="word.weight = 1">
									<font-awesome-icon :icon="['fas', 'plus']"/>
								</b-button>
							</b-button-group>
						</small>
					</div>
				</b-list-group-item>
			</b-list-group>
			<b-button
				size="sm"
				variant="outline-dark"
				title="Add new a word to this cluster"
				class="mx-auto mt-2"
				@click="addWord">
				<small><font-awesome-icon :icon="['fas', 'plus']"/></small>
			</b-button>
		</div>
	</b-modal>
</b-card>
</template>

<script>
export default {
	name: "ClusterManager",
	data: function() {
		return {
				modal: {
					color: "#000000",
					cluster_name: "",
					words: [],
					index: 0
				}
		}
	},
	methods: {
		validClusterName(cluster_name) {
			let modal = this.modal,
					clusters = this.$session.clusters;

			// Check for:
			//	* Empty inputs
			//	* If it is editing a existing cluster (index  < cluster_k)
			//		* Filter the clustering being edited
			//		* Checks if the new name is unique among the remaining clusters
			//	* If it is a new cluster (index == cluster_k)
			//		* Checks if the new name is unique among the older clusters
			return modal.cluster_name?.length > 0 && ( 
				(
					modal.index < clusters.cluster_k &&
					!clusters.cluster_names.filter((d, i) => i != modal.index).includes(cluster_name)
				) || (
					modal.index == clusters.cluster_k &&
					!clusters.cluster_names.includes(cluster_name)
				)
			);
		},
		addWord() {
			const word = prompt("Enter a valid word to your cluster");
			const word_list = this.modal.words.map(w => w.word);
			
			if (word?.length > 0 && !word_list.includes(word)) {
				this.modal.words.push({
					word: word,
					weight: 1});
			} else {
				alert("Invalid input, please try another word");
			}
		},
		launchEditor(index=null) {
			let clusters = JSON.parse(JSON.stringify(this.$session.clusters));

			if (index != null) {
				this.modal = {
					color: clusters.colors[index],
					cluster_name: clusters.cluster_names[index],
					words: clusters.cluster_words[index],
					index: index}
			} else {
				this.modal = {
					color: "#000000",
					cluster_name: "",
					words: [],
					index: clusters.cluster_k}
			}
			this.$refs['cluster-editor'].show()
		},
		submitChanges() {
			let clusters = this.$session.clusters,
					modal = JSON.parse(JSON.stringify(this.modal));
			
			if (modal.index == clusters.cluster_k) {
				++clusters.cluster_k;
				
				clusters.colors.push(modal.color);
				clusters.cluster_names.push(modal.cluster_name);
				clusters.cluster_words.push(modal.words);
			} else {
				clusters.colors[modal.index] = modal.color;
				clusters.cluster_names[modal.index] = modal.cluster_name;
				clusters.cluster_words[modal.index] = modal.words;
			}

			this.$d3.select(`#cluster_card_${modal.index} header`)
				.style("background", modal.color);

			this.$forceUpdate();
		},
		deleteCluster() {
			if (confirm(`You're about to delete cluster ${this.modal.cluster_name}, are you sure?`)) {
				const index = this.modal.index;
				let clusters = this.$session.clusters;

				clusters.cluster_k = clusters.cluster_k - 1;
				clusters.cluster_names.pop(index);
				clusters.colors.pop(index);
				clusters.cluster_words.pop(index);

				this.$refs['cluster-editor'].hide();
				this.$forceUpdate();
			}
		}
	},
}
</script>

<style lang="sass">
.card
	header
		padding: 0
		text-align: center
		height: 25px

.cluster-card
	padding: 0 !important
	white-space: normal
	word-wrap: break-word
	max-width: 120px !important
	color: #000
	cursor: pointer
	font-size: small
	*
		margin-bottom: 0 !important
	.list-group
		height: 101px !important
		max-height: 101px
		min-height: 101px
		overflow-y: auto
		overflow-x: hidden
		-webkit-overflow-scrolling: touch
	header
		font-size: bold
		color: #FFF !important
		height: 20px
		text-align: center
</style>