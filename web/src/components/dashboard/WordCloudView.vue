<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		Word Cloud
	</b-card-header>
	<div class="d-block">
		<b-input-group size="sm">
			<b-form-select v-model="option">
        <b-form-select-option
          :disabled="highlight == ''"
          value="cluster">Cluster Word Cloud</b-form-select-option>
        <b-form-select-option
          :disabled="focused == null"
          value="document">Document Word Cloud</b-form-select-option>
        <b-form-select-option
          :disabled="selected.length == 0"
          value="selection">Selection Word Cloud</b-form-select-option>
      </b-form-select>
		</b-input-group>
    <template v-if="words.length > 0">
      <cloud
        id="wordCloudCanvas"
        valueKey="value"
        nameKey="name"
        :height="height"
        :width="width"
        :data="words"
        :rotate="settings.rotate"
        :margin="settings.margin"
        :wordClick="copyToClipboard"
        :showTooltip="false"></cloud>
    </template>
    <template v-else>
      <div class="mx-auto">
        <center> 
          {{ (option == "document") ? "Select a document" : "Highlight a cluster" }} to view its WordCloud
        </center>
      </div>
    </template>
	</div>
</b-card>
</template>

<script>
import wordcloud from 'vue-wordcloud';
import { mapState } from "vuex";
import * as d3 from "d3";
 
export default {
  name: "WordCloud",
  components: {
    'cloud': wordcloud,
  },
  data: function(){
    return {
      option: "document",
      canvas: undefined,
      width: 400,
      height: 200,
      settings: {
        rotate: {
          from: 0, to: 0,
          numOfOrientation: 1
        },
        margin: {
          top: 5,
          right: 5,
          bottom: 5,
          left: 5
        }
      }
    }
  },
  mounted() {    
    // CANVAS
		this.canvas = d3.select("#wordCloudCanvas svg")
			.attr("width", "100%")
			.attr("height", "100%")
      .attr('preserveAspectRatio','xMinYMin')
			.attr("viewBox", [0, 0, this.width, this.height])
			.call(d3.zoom()
				.scaleExtent([0.1, 8])
				.on("zoom", (e) => {
          d3.select("#wordCloudCanvas svg g").attr("transform", e.transform)}));
  },
  computed: {
    words() {
      let objRef = this,
          vocab  = {};

      if(this.option == "document") {
        vocab = this.corpus
          .find(doc => doc.id == objRef.focused)?.term_frequency;
      } else {
        let docs_tf = undefined;
        if(this.option == "cluster" && this.highlight != "") {
          docs_tf = this.cluster_docs[this.highlight].map(id =>
            objRef.corpus.find(doc => doc.id == id)?.term_frequency);
        } else {
           docs_tf = this.corpus.filter(
            doc => objRef.selected.includes(doc.id)
          ).map(doc => doc?.term_frequency);
        }

        for (let doc of docs_tf) {
          for (let word of Object.keys(doc)) {
            vocab[word] = doc[word] + (word in vocab ? vocab[word] : 0);
          }
        }
      }

      if(vocab && Object.keys(vocab).length > 0) {
        return Object.keys(vocab).map(word => {
          return {name: word, value: vocab[word]}})
          .sort((a, b) => b.value - a.value)
          .slice(0, 50);
      }

      return [ {word: "", value: 0} ];
    },
    ...mapState("userData", ["corpus"]),
    ...mapState("session", ["focused", "selected", "highlight", "clusters"]),
    cluster_docs() {
      return this.clusters.cluster_docs;
    }
  },
  methods: {
    makeToast(word) {
      // Use a shorter name for this.$createElement
			const h = this.$createElement;
			// Create the message
			const copyToast = h(
				'p', { class: ['mb-0'] },
				[
          h('font-awesome-icon',{props: {icon: ['fas', 'clipboard']}}),
          ' Copied ',
          h("strong", word),
          ' to clipboard'
        ]);

      this.$bvToast.toast(
        copyToast, {
          variant: "secondary",
          toaster: "b-toaster-bottom-right",
          solid: false,
          noCloseButton: true,
          autoHideDelay: 3000});
    },
    copyToClipboard(word) {
      let objRef = this;
      
      navigator.permissions.query({name: "clipboard-write"}).then(result => {
        if (result.state == "granted" || result.state == "prompt") {
          navigator.clipboard.writeText(word).then(
            () => objRef.makeToast(word));
        } else {
          var dummy = document.createElement("input");
          document.body.appendChild(dummy);                 // Add it to the document
          dummy.setAttribute("id", "dummy_id");             // Set its ID
          document.getElementById("dummy_id").value = word; // Output the array into it
          dummy.select();                                   // Select it
          document.execCommand("copy");                     // Copy its contents
          document.body.removeChild(dummy);                 // Remove it as its not needed anymore

          objRef.makeToast(word);
        }
      });
    }
  },
}
</script>

<style lang="sass">
#wordCloudCanvas
  cursor: default
  height: 37vh !important
</style>