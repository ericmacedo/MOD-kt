<template>
<b-card no-body>
	<b-card-header header-tag="header" class="text-center">
		Cluster Manager
	</b-card-header>
	<b-container fluid id="clusterManagerWrapper">
		<b-row cols="4" class="p-1">
			<b-col
				v-for="(cluster, index) in clusters.cluster_names"
				:key="index"
				class="mb-1 p-0">
				<b-card no-body class="cluster-card text-center"
					:id="'cluster_card_'+index"
					text-variant="white"
          :class="['cluster-card', 'text-center', cluster==highlight?'highlighted':'' ]"
					title="Double click to edit this cluster"
					@dblclick="launchEditor(index)"
          @click="updateHighlight(cluster)">
					<b-card-header
						header-tag="header"
						:style="[{'background': clusters.colors[index]}]">
						<strong>{{ cluster }}</strong>
					</b-card-header>
					<b-list-group>
						<b-list-group-item
							class="cluster-card"
							v-for="word in clusters.cluster_words[index]"
							:key="word.word"
							:variant="word.weight > 0 ? 'success' :'danger'">
						{{ word.word }}
						</b-list-group-item>
					</b-list-group>
				</b-card>
			</b-col>
		</b-row>
    <b-row>
      <b-button
        size="sm"
        variant="outline-dark"
        class="mx-auto mb-2"
        title="Click to create a new cluster"
        @click="launchEditor()">
        <font-awesome-icon 
          size="sm"
          :icon="['fas', 'plus']"/>
      </b-button>
    </b-row>
	</b-container>

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
						:disabled="modal.index == clusters.cluster_k && validClusterName(modal.cluster_name)"
						@click="callDeleteCluster">
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
									@click="modal.words.splice(index, 1)">
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
				class="mx-auto mt-1"
				@click="addWord">
				<small><font-awesome-icon :icon="['fas', 'plus']"/></small>
			</b-button>
		</div>
	</b-modal>
</b-card>
</template>

<script>
import { mapState, mapMutations } from "vuex";
import * as d3 from "d3";

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
  computed: {
    ...mapState("session", ["highlight", "clusters"])
  },
	methods: {
		validClusterName(cluster_name) {
			let modal = this.modal;

			// Check for:
			//	* Empty inputs
			//	* If it is editing a existing cluster (index  < cluster_k)
			//		* Filter the clustering being edited
			//		* Checks if the new name is unique among the remaining clusters
			//	* If it is a new cluster (index == cluster_k)
			//		* Checks if the new name is unique among the older clusters
			return modal.cluster_name?.length > 0 && ( 
				(
					modal.index < this.clusters.cluster_k &&
					!this.clusters.cluster_names.filter((d, i) => i != modal.index).includes(cluster_name)
				) || (
					modal.index == this.clusters.cluster_k &&
					!this.clusters.cluster_names.includes(cluster_name)
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
			let clusters = JSON.parse(JSON.stringify(this.clusters));

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
			this.updateClusters(this.modal);

			d3.select(`#cluster_card_${this.modal.index} header`)
				.style("background", this.modal.color);

			this.$forceUpdate();
		},
		callDeleteCluster() {
			if (confirm(`You're about to delete cluster ${this.modal.cluster_name}, are you sure?`)) {
				this.deleteCluster(this.modal.index)

				this.$refs['cluster-editor'].hide();
			}
		},
    ...mapMutations("session", [
      "updateClusters", "deleteCluster", "updateHighlight"])
	},
}
</script>

<style lang="sass">
.cluster-card
	padding: 0 !important
	white-space: normal
	word-wrap: break-word
	max-width: 120px !important
	color: #000
	cursor: pointer
	font-size: small
  user-select: none
  -ms-user-select: none
  -moz-user-select: none
  -khtml-user-select: none
  -webkit-user-select: none
  -webkit-touch-callout: none
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
		height: 20px !important
		text-align: center

.highlighted
  border: 2px solid red !important

#clusterManagerWrapper
  overflow-y: auto
</style>