<template>
<div>
	<b-row>
		<b-col class="upload-wrapper"
			sm="12" md="6" lg="6">
			<upload-component context="CORPUS"></upload-component>
		</b-col>

		<!-- TOOLBAR + TABLE -->
		<b-col id="tableCol" sm="12" md="6" lg="6">
			<!-- TOOLBAR -->
			<b-button-toolbar id="corpusToolbar">
				<b-button-group size="sm" class="mx-1">
					<b-button disabled
						variant="outline-secondary">
							{{ corpus_size }}
						</b-button>
					<b-button @click="reloadTable">
						<font-awesome-icon :icon="['fas', 'sync']"/>
					</b-button>
				</b-button-group>
				<b-button-group class="mx-1">
					<b-button
						size="sm"
						:disabled="corpus_size==0"
						@click="selectAllRows">
						Select all
					</b-button>
					<b-button
						size="sm"
						@click="clearSelected"
						:disabled="table.selection.length == 0">
						Unselect all
					</b-button>
					<b-button
						size="sm"
						variant="danger"
						:disabled="table.selection.length == 0"
						@click="callDeleteDocument">
						<font-awesome-icon :icon="['fas', 'trash']"/>
						Delete documents
					</b-button>
				</b-button-group>

				<!-- TODO create modal to confirm redirect to Dashboard? -->
				<b-dropdown
					class="mx-1"
					variant="info"
					text="Process corpus"
          right
					:disabled="corpus_size == 0 || processingCorpus">
					<b-dropdown-item-button
						@click="callProcessCorpus('HIGH')">
            <font-awesome-icon :icon="['fas', 'server']"/>&nbsp;High performance<br/>
            <small>
              &nbsp; Document encoder: S-BERT<br/>
              &nbsp; Word embeddings: FastText
            </small>
          </b-dropdown-item-button>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item-button
						@click="callProcessCorpus('LOW')">
            <font-awesome-icon :icon="['fas', 'desktop']"/>&nbsp;Low performance<br/>
            <small>
              &nbsp; Document encoder: Doc2Vec<br/>
              &nbsp; Word embeddings: Word2Vec
            </small>
          </b-dropdown-item-button>
				</b-dropdown>

			</b-button-toolbar>

			<!-- TABLE -->
			<b-table
				id="corpusTable"
				hover selectable show-empty
				:fields="table.fields"
				:items="corpus"
				select-mode="multi"
				responsive="sm"
				ref="corpusTable"
				@row-selected="onRowSelected">
				
				<!-- IS SELECTED -->
				<template #cell(selected)="{ rowSelected }">
					<template v-if="rowSelected">
						<span aria-hidden="true">&check;</span>
						<span class="sr-only">Selected</span>
					</template>
					<template v-else>
						<span aria-hidden="true">&nbsp;</span>
						<span class="sr-only">Not selected</span>
					</template>
				</template>

				<!-- SHOW CONTENT -->
				<template #cell(show_details)="row">
					<b-button size="sm" @click="row.toggleDetails" class="mr-2">
						<font-awesome-icon
							:icon="['fas', (row.detailsShowing) ? 'eye-slash' : 'eye']"/>
					</b-button>
				</template>

				<!-- DETAILS CARD -->
				<template #row-details="row">
					<b-card>
						<b-row class="mb-2">
							<p>{{ row.item.content }}</p>
						</b-row>
						<b-button size="sm" @click="row.toggleDetails">Hide Conent</b-button>
					</b-card>
				</template>

			</b-table>
		</b-col>
	</b-row>
	<b-modal
		ref="dashboard-redirect-modal"
		id="dashboard-redirect-modal"
		size="md"
		header-bg-variant="dark"
		header-text-variant="light"
		title="Corpus processed"
		centered
		hide-footer>
		<div class="d-block text-center">
			<h6>You corpus was processed succesfully, do you want to proceed to the <strong>Dashboard</strong> and start exploring you corpus?</h6>
		</div>
		<b-button
			class="mt-3"
			variant="outline-success"
			block
			@click="$bvModal.hide('dashboard-redirect-modal')"
			to="/dashboard">
				<font-awesome-icon :icon="['fas', 'tachometer-alt']"/>&nbsp;
				Yes, take me to the <strong>Dashboard</strong>!
		</b-button>
	</b-modal>
</div>
</template>

<script>
import { mapGetters, mapState, mapActions } from 'vuex';
import UploadComponent from "./UploadComponent";

export default {
  name: 'Corpus',
  components: {
    "upload-component": UploadComponent
  },
	data: function() {
		return {
			table: {
				fields: ["selected", "file_name", "uploaded_on", "show_details"],
				selection: []
			},
			processingCorpus: false
		}
	},
	computed: {
		all_selected: function () {
			return (this.table.selection.length == this.corpus_size);
		},
    ...mapState({
      corpus: state => state.userData.corpus,
      userId: state => state.userData.userId
    }),
    ...mapGetters('userData', ["corpus_size"])
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
		get_userData() {
			let objRef = this;
      
      this.userData = this.getUserData(this.userId);

      this.userData.then(function() {
        objRef.makeToast(
					"Success",					  // title
					"User data reloaded",	// content
					"success");					  // variant
      }).catch(function() {
        objRef.makeToast(
					"Oops, something went wrong!",// title
					"Try reloading the page",	  	// content
					"danger");						        // variant
      });
		},
		reloadTable() {
			this.get_userData();
			this.table.selection = [];
		},
		onRowSelected: function (selection) {
			this.table.selection = selection;
		},
		selectAllRows: function () {
			this.$refs.corpusTable.selectAllRows();
		},
		clearSelected: function () {
			this.$refs.corpusTable.clearSelected();
		},
		callDeleteDocument: async function() {
			let objRef = this;

			const to_remove = this.table.selection.map((d) => d.id);
      
      this.deleteDocument({
        to_remove: to_remove,
        RESET_FLAG: this.all_selected
      }).then(function() {
				objRef.makeToast(
					"Success!",						// title
					"Files deleted successfully!",	// content
					"success");						// variant
			}).catch(function() {
				objRef.makeToast(
					"Oops, something went wrong!",	// title
					"Try reloading the page",		// content
					"danger");						// variant
			});
		},
		callProcessCorpus: async function(performance) {
			let objRef = this;
			
      this.makeToast(
				"Processing corpus",	// title
				"Please wait...",		// content
				"warning",				// variant
				"process_corpus");		// id
			this.processingCorpus = true;
			
      this.processCorpus(performance)
        .then(function() {
          objRef.get_userData(objRef.userId)
          objRef.$bvModal.show('dashboard-redirect-modal');
        }).catch(function() {
          objRef.makeToast(
            "Oops, something went wrong",	// title
            "Internal error",				// content
            "danger");						// variant
        }).then(() => {
          objRef.$bvToast.hide("process_corpus");
          objRef.processingCorpus = false;});
		},
    ...mapActions(["deleteDocument", "processCorpus", "getUserData"])
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass" scoped>
*
	box-sizing: border-box
	-moz-box-sizing: border-box
	-webkit-box-sizing: border-box
  
.upload-wrapper
	text-align: center
	padding: 10px 50px 0px 50px

	& > .container
		background-color: #f9f9f9
		padding: 20px
		border-radius: 10px
		position: -webkit-sticky
		position: sticky
		top: 60px

#corpusTable
	overflow-y: scroll
	overflow-x: auto
	max-height: 800px

#tableCol
	padding-top: 10px

#corpusToolbar
  justify-content: center
  padding-bottom: 5px
  position: -webkit-sticky
  position: sticky
  top: 60px
</style>
