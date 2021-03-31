<template>
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
          v-model="files"
          @input="onInputFieldChange">
        </b-form-file>
      <b-btn-group no-gutter>
        <b-button
          :disabled="files.length == 0"
          @click="clearUpload">Clear</b-button>
        <b-button
          variant="success"
          :disabled="files.length == 0"
          @click="callUploadDocument">
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
      v-for="(file, index) in queue"
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
</template>

<script>
import { mapActions, mapState } from 'vuex';
import Papa from 'papaparse';

export default {
  name: "UploadComponent",
  props: {
    context: {
      required: true,
      type: String
    }
  },
  data() {
    return {
      files: [],
      queue: [],
      STATUS: {
        "INVALID": 	"warning",
        "ERROR": 		"danger",
        "SUCCESS": 	"success",
        "QUEUED": 	""
      }
    }
  },
  computed: {
    ...mapState("userData", ["userId"])
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
    clearUpload: function(){
			this.files = [];
			this.files = [];
		},
		onInputFieldChange: function () {
			let objRef = this;
			this.queue = this.files.map(function(file, index){
				var format = "file-"+file.type.split('/')[1].toLowerCase();
				
				if (format === "file-plain") {
					format = "file-alt";
				}

				if (format == "file-csv") {
					const reader = new FileReader();

					reader.onload = function(event) {
						const parsed = Papa.parse(event.target.result, {
							delimiter: ",",
							header: true,
							skipEmptyLines: true
						});

						objRef.queue[index].csv.fields = parsed.meta.fields;
					};

					reader.readAsText(file);
				}

				return {
					index: index,
					name: file.name,
					status: objRef.STATUS["QUEUED"],
					format: format,
					csv: {
						fields: [],
						selected_fields: []
					}
				};
			});
		},
		callUploadDocument: async function() {
			let objRef = this;

			const promises = this.files.map(async function(file, index){
				var format = objRef.queue[index].format;
				var selected_fields = objRef.queue[index].csv.selected_fields;
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
				
				let result = await objRef.uploadDocument(formData);
				
				if (result.status == 200) {
					objRef.queue[index].status = objRef.STATUS["SUCCESS"];
				} else {
					objRef.queue[index].status = objRef.STATUS["ERROR"];
				}
				
				// SCROLLS TO CURRENT ITEM
				objRef.$refs.uploadQueue.children[index].scrollIntoView(
					{behavior: 'smooth'});
        
        const ids = result.data.newData.map(d => d.id);

        result = null;
        if(objRef.context == "MODAL") {
          return ids;
        }
			});
			
			this.makeToast(
				"Uploading files",		// title
				"Please wait...",		// content
				"warning",				// variant
				"upload_documents");	// id
			
			Promise.all(promises).then((new_docs) => {
        objRef.$bvToast.hide("upload_documents");

        const new_ids = new_docs.flat(Infinity);

        if(objRef.context == "MODAL") {
          objRef.makeToast(
            "Processing the corpus increment",  // title
            "Please wait...",		                // content
            "warning",				                  // variant
            "processing_increment");	          // id
        
          objRef.updateCorpus(new_ids).then(() => {
            objRef.$bvToast.hide("processing_increment");
            objRef.$emit("re-render")
          }).catch(() => {
            objRef.$bvToast.hide("processing_increment");
            objRef.makeToast(
              "Error",
              "Oops, looks like something went wrong",
              "danger");
          });
        }
      }).catch(() => {
        objRef.makeToast(
          "Error",
          "Oops, looks like something went wrong",
          "danger");
      });
		},
    ...mapActions(["uploadDocument", "updateCorpus"])
  },
}
</script>

<style lang="sass" scoped>
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
</style>