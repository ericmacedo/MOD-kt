<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		WordCloud
	</b-card-header>
	<div class="d-block">
		<b-input-group>
			<b-form-select v-model="selected">
        <b-form-select-option
          :disabled="highlight.cluster_name == ''"
          value="cluster">Cluster Word Cloud</b-form-select-option>
        <b-form-select-option
          :disabled="focused.id == null"
          value="document">Document Word Cloud</b-form-select-option>
      </b-form-select>
		</b-input-group>
    <cloud
      id="wordCloudCanvas"
      :data="words"
      nameKey="name"
      valueKey="value"
      :showTooltip="false"></cloud>
	</div>
</b-card>
</template>

<script>
import wordcloud from 'vue-wordcloud'

export default {
  name: "WordCloud",
  components: {
    'cloud': wordcloud,
  },
  data: function(){
    return {
      selected: "document",
      canvas: undefined,
      width: 400,
      height: 300,
      highlight: this.$session.highlight,
      focused: this.$session.focused
    }
  },
  mounted() {
    let objRef = this;
    
    // CANVAS
		this.canvas = this.$d3.select("#wordCloudCanvas svg")
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("viewBox", [0, 0, this.width, this.height])
			.call(this.$d3.zoom()
				.scaleExtent([0.1, 8])
				.on("zoom", (e) => {
          objRef.$d3.select("#wordCloudCanvas svg g").attr("transform", e.transform)}));
  },
  computed: {
    words() {
      let objRef = this,
          vocab  = {};

      if(this.selected == "cluster") {
        const _cluster = this.$session.clusters.cluster_docs[this.highlight.cluster_name],
              docs_tf = _cluster.map(id =>
                          objRef.$userData.corpus
                            .filter(doc => doc.id == id)[0]
                            .term_frequency);

        for (let doc of docs_tf) {
          for (let word of Object.keys(doc)) {
            vocab[word] = doc[word] + (word in vocab ? vocab[word] : 0);
          }
        }
      } else {
        vocab = this.$userData.corpus
          .filter(doc => doc.id == objRef.focused.id)[0]
          .term_frequency;
      }

      return Object.keys(vocab).map(word => {
        return {name: word, value: vocab[word]}})
        .sort((a, b) => b.value - a.value)
        .slice(0, 50)
      ?? [];
    }
  },
  methods: {
    fontSizeMapper(word) {
      return Math.log2(word.value) * 5;
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
</style>