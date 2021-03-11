<template>
<div>
	<b-row>
		<b-col class="upload-wrapper"
			sm="12" md="6" lg="6">
			<b-container id="uploadFrame" class="text-center">
				<h2 id="upload-title">Upload your files</h2>
				<div class="upload-container">
					<div class="border-container center-text">
						<div class="icons fa-4x">
							<font-awesome-icon 
								:icon="['fas', 'file-csv']"
								transform="shrink-3 down-2 left-6 rotate--45"/>
							<font-awesome-icon 
								:icon="['fas', 'file-pdf']"
								transform="shrink-2 up-4"/>
							<font-awesome-icon 
								:icon="['fas', 'file-alt']"
								transform="shrink-3 down-2 right-6 rotate-45"/>
						</div>
						<b-input-group class="mb-2">
							<b-form-file
								ref="files"
								id="file-upload"
								multiple
								accept=".pdf, .csv, .txt"
								drop-placeholder="Drop files here..."
								v-model="upload.files"
								@input="onInputFieldChange">
							</b-form-file>
						<b-btn-group no-gutter>
							<b-button
								:disabled="upload.files.length == 0"
								@click="clearUpload">Clear</b-button>
							<b-button
								variant="success"
								:disabled="upload.files.length == 0"
								@click="uploadFiles">
								Submit</b-button>
						</b-btn-group>
						</b-input-group>
						<p>Drag and drop files here, or browse your computer.</p>
					</div>
				</div>
				<b-list-group
					ref="uploadQueue"
					id="uploadQueue">
					<b-list-group-item
						v-for="(file, index) in upload.queue"
						:key=index
						:variant=file.status>
						<font-awesome-icon
							size="lg"
							:icon="['fas', file.format]"/>
						{{ file.name }}
						<b-form-select
							v-if="file.format == 'file-csv'"
							multiple
							v-model="file.csv.selected_fields"
							:options="file.csv.fields"
						></b-form-select>
					</b-list-group-item>
				</b-list-group>
			</b-container>
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
						@click="deleteFiles">
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
						@click="processCorpus('HIGH')">
            <font-awesome-icon :icon="['fas', 'server']"/>&nbsp;High performance<br/>
            <small>
              &nbsp; Document encoder: S-BERT<br/>
              &nbsp; Word embeddings: FastText
            </small>
          </b-dropdown-item-button>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item-button
						@click="processCorpus('LOW')">
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
				:items="$store.state.userData.corpus"
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
		size="sm"
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
import { mapGetters } from 'vuex';

export default {
  name: 'Corpus',
	data: function() {
		return {
			table: {
				fields: ["selected", "file_name", "uploaded_on", "show_details"],
				selection: []
			},
			upload: {
				files: [],
				queue: [],
				STATUS: {
					"INVALID": 	"warning",
					"ERROR": 		"danger",
					"SUCCESS": 	"success",
					"QUEUED": 	""
				}
			},
			embModel: ["Doc2Vec", "S-BERT"],
			processingCorpus: false
		}
	},
	computed: {
		all_selected: function () {
			return (this.table.selection.length == this.corpus_size);
		},
    ...mapGetters('userData', ["corpus_size", "userId"])
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
      
      this.userData = this.$store.dispatch("getUserData", this.userId);

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
		clearUpload: function(){
			this.upload.files = [];
			this.upload.files = [];
		},
		onInputFieldChange: function () {
			let objRef = this;
			this.upload.queue = this.upload.files.map(function(file, index){
				var format = "file-"+file.type.split('/')[1].toLowerCase();
				
				if (format === "file-plain") {
					format = "file-alt";
				}

				if (format == "file-csv") {
					const reader = new FileReader();

					reader.onload = function(event) {
						const parsed = objRef.$papa.parse(event.target.result, {
							delimiter: ",",
							header: true,
							skipEmptyLines: true
						});

						objRef.upload.queue[index].csv.fields = parsed.meta.fields;
					};

					reader.readAsText(file);
				}

				return {
					index: index,
					name: file.name,
					status: objRef.upload.STATUS["QUEUED"],
					format: format,
					csv: {
						fields: [],
						selected_fields: []
					}
				};
			});
		},
		uploadFiles: async function() {
			let objRef = this;

			const promises = this.upload.files.map(async function(file, index){
				var format = objRef.upload.queue[index].format;
				var selected_fields = objRef.upload.queue[index].csv.selected_fields;
				var fields = (
					format == "file-csv" && selected_fields.length > 0
				) ? selected_fields : [];
				
				// FORM
				const formData = new FormData();
				formData.set("userId", objRef.userId);
				formData.set("file", file);
				formData.set("fileName", file.name);
				formData.set("format", format);
				formData.set("fields", fields);
				
				const result = await objRef.$store.dispatch("uploadDocument", formData);
				
				if (result.status == 200) {
					objRef.upload.queue[index].status = objRef.upload.STATUS["SUCCESS"];
				} else {
					objRef.upload.queue[index].status = objRef.upload.STATUS["ERROR"];
				}
				
				// SCROLLS TO CURRENT ITEM
				objRef.$refs.uploadQueue.children[index].scrollIntoView(
					{behavior: 'smooth'});
			});				
			
			this.makeToast(
				"Uploading files",		// title
				"Please wait...",		// content
				"warning",				// variant
				"upload_documents");	// id
			
			Promise.all(promises).then(() => objRef.$bvToast.hide("upload_documents"));
				// objRef.get_userData();});
		},
		deleteFiles: async function() {
			let objRef = this;

			const to_remove = this.table.selection.map((d) => d.id);
      
      this.$store.dispatch("deleteDocument", {
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
		processCorpus: async function(performance) {
			let objRef = this;
			
      this.makeToast(
				"Processing corpus",	// title
				"Please wait...",		// content
				"warning",				// variant
				"process_corpus");		// id
			this.processingCorpus = true;
			
      this.$store.dispatch("processCorpus", performance)
        .then(function() {
          objRef.$bvModal.show('dashboard-redirect-modal');
        }).catch(function() {
          objRef.makeToast(
            "Oops, something went wrong",	// title
            "Internal error",				// content
            "danger");						// variant
        }).then(() => {
          objRef.$bvToast.hide("process_corpus");
          objRef.processingCorpus = false;});
		}
	}
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
  
#upload-title
	color: #130f40
	font-family: 'Varela Round', sans-serif
	letter-spacing: -.5px
	font-weight: 700
	padding-bottom: 10px
  
#upload-container
	background-color: rgb(239, 239, 239)
	border-radius: 6px
	padding: 10px
  
.border-container
	border: 5px dashed rgba(198, 198, 198, 0.65)
	border-radius: 6px
	padding: 20px

	p
		color: #130f40
		font-weight: 600
		font-size: 1.1em
		letter-spacing: -1px
		margin-top: 30px
		margin-bottom: 0
		opacity: 0.65
  
#file-browser
	text-decoration: none
	color: rgb(22,42,255)
	border-bottom: 3px dotted rgba(22, 22, 255, 0.85)

	&:hover
		color: rgb(0, 0, 255)
		border-bottom: 3px dotted rgba(0, 0, 255, 0.85)
  
.icons
	color: #95afc0
	opacity: 0.55

#uploadQueue
	max-height: 250px
	text-align: left
	margin-bottom: 10px
	overflow-y: scroll
	overflow-x: auto
	-webkit-overflow-scrolling: touch

#corpusTable
	overflow-y: scroll
	overflow-x: auto
	max-height: 800px

#tableCol
	padding-top: 10px

#corpusToolbar
	justify-content: center
	padding-bottom: 5px
</style>
