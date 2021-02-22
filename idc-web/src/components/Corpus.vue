<template>
<div>
	<b-row>
		<b-col class="upload-wrapper h-100 w-50">
			<b-container id="uploadFrame" class="text-center">
				<h2 id="upload-title">Upload your files</h2>
				<div class="upload-container">
					<div class="border-container center-text">
						<div class="icons fa-4x">
							<font-awesome-icon 
								:icon="['fas', 'file-csv']"
								transform="shrink-3 down-2 left-6 rotate--45"/>
							<font-awesome-icon 
								:icon="['fas', 'file-csv']"
								transform="shrink-2 up-4"/>
							<font-awesome-icon 
								:icon="['fas', 'file-csv']"
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
		<b-col id="tableCol" class="h-100 w-50">
			<!-- TOOLBAR -->
			<b-button-toolbar
				id="corpusToolbar"
				key-nav>
				
				<b-button-group class="mx-1">
					<b-button
						size="sm"
						:disabled="table.items.length == 0"
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

				<b-button-group class="mx-1">
					<b-button
						:disabled="table.items.length == 0">
						<font-awesome-icon :icon="['fas', 'cogs']"/>
						Process corpus
					</b-button>
				</b-button-group>

			</b-button-toolbar>

			<!-- TABLE -->
			<b-table
				id="corpusTable"
				hover selectable show-empty
				:fields="table.fields"
				:items="table.items"
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
</div>
</template>

<script>
export default {
  name: 'Corpus',
	props: {
		userData: {
			type: Object,
			required: true
		}
	},
	data: function() {
		return {
			table: {
				fields: ["selected", "file_name", "uploaded_on", "show_details"],
				items: [],
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
			}
		}
	},
	watch: {
		userData: function(data) {
			this.table.items = data.corpus
			this.table.selection = [];
		}
	},
	computed: {
		all_selected: function () {
			return (this.table.selection.length == this.table.items.length);
		}
	},
	methods: {
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
			async function PUT(objRef, formData) {
				return objRef.$axios.put(objRef.$server+"/corpus", formData, {
					headers: { "Content-Type": "multipart/form-data" }
				})
			}

			const promises = this.upload.files.map(async function(file, index){
				var format = objRef.upload.queue[index].format;
				var selected_fields = objRef.upload.queue[index].csv.selected_fields;

				var fields = (
					format == "csv" && selected_fields.lenght > 0
				) ? selected_fields : [];

				// FORM
				const formData = new FormData();
				formData.set("userId", objRef.userData.userId);
				formData.set("file", file);
				formData.set("fileName", file.name);
				formData.set("format", format);
				formData.set("fields", fields);

				const result = await PUT(objRef, formData);

				if (result.status == 200) {
					objRef.$parent.updateUserData(result.data.userData);
					objRef.upload.queue[index].status = objRef.upload.STATUS["SUCCESS"];
				} else {
					objRef.upload.queue[index].status = objRef.upload.STATUS["ERROR"];
				}

				// SCROLLS TO CURRENT ITEM
				objRef.$refs.uploadQueue.children[index].scrollIntoView(
					{behavior: 'smooth'});
			});				

			Promise.all(promises);
		},
		deleteFiles: function() {
			let objRef = this;

			// FORM
			const formData = new FormData();
			formData.set("userId", this.userData.userId);
			formData.set("ids", this.table.selection.map((d) => d.id));
			formData.set("RESET_FLAG", this.all_selected);

			this.$axios.post(this.$server+"/corpus", formData, {
				headers: { "Content-Type": "multipart/form-data" }
			}).then(function(result) {
				objRef.$parent.updateUserData(result.data.userData);
				objRef.$parent.makeToast(
					"success",
					"Files deleted successfully!",
					"");
			}).catch(function(result) {
				console.log(result);
			});
		}
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
* {
	box-sizing: border-box;
	-moz-box-sizing: border-box;
	-webkit-box-sizing: border-box;
}
  
.upload-wrapper {
	text-align: center;
}
  
.upload-wrapper > .container {
	background-color: #f9f9f9;
	padding: 20px;
	border-radius: 10px;
}
  
#upload-title {
	color: #130f40;
	font-family: 'Varela Round', sans-serif;
	letter-spacing: -.5px;
	font-weight: 700;
	padding-bottom: 10px;
}
  
#upload-container {
	background-color: rgb(239, 239, 239);
	border-radius: 6px;
	padding: 10px;
}
  
.border-container {
	border: 5px dashed rgba(198, 198, 198, 0.65);
	border-radius: 6px;
	padding: 20px;
}
  
.border-container p {
	color: #130f40;
	font-weight: 600;
	font-size: 1.1em;
	letter-spacing: -1px;
	margin-top: 30px;
	margin-bottom: 0;
	opacity: 0.65;
}
  
#file-browser {
	text-decoration: none;
	color: rgb(22,42,255);
	border-bottom: 3px dotted rgba(22, 22, 255, 0.85);
}
  
#file-browser:hover {
	color: rgb(0, 0, 255);
	border-bottom: 3px dotted rgba(0, 0, 255, 0.85);
}
  
.icons {
	color: #95afc0;
	opacity: 0.55;
}

#uploadQueue {
	max-height: 250px;
	text-align: left;
	margin-bottom: 10px;
	overflow-y: scroll;
	overflow-x: auto;
	-webkit-overflow-scrolling: touch;
}

#corpusTable {
	overflow-y: scroll;
	overflow-x: auto;
	max-height: 800px;
}

#tableCol {
	padding-top: 10px;
}

#corpusToolbar {
	justify-content: center;
	padding-bottom: 5px;
}
</style>
