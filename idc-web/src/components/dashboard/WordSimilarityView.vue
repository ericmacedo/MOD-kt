<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		Word Similarity
	</b-card-header>
	<div class="d-block">
    <b-input-group size="sm">
      <b-form-tags
        size="sm"
        v-model="word_similarity.query"
        input-id="query-words"
        separator=" "
        placeholder="Enter new words separated by space"
        remove-on-delete
        no-add-on-enter></b-form-tags>
      <b-button
        size="sm"
        title="Search for similar words within this corpus"
        variant="outline-info"
        @click="requestMostSimilar">
        <font-awesome-icon :icon="['fas', 'search']"/>
      </b-button>
    </b-input-group>
    <div
      v-for="(item, index) in word_similarity.most_similar"
      :key="index"
      class="d-flex w-100 pr-1"
      :style="{'align-items': 'flex-end'}"
      @click="copyToClipboard(item.word)">
      <div
        class="bar mt-2 ml-1 mr-1 pl-2"
        :style="{'width': ''+(width * item.value * 0.9)+'px'}"
        >{{ item.word }}</div>
      <span class="ml-1 percentage">
        {{ (item.value * 100).toFixed(2) }}%
      </span>
    </div>
	</div>
</b-card>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  name: "WordSimilarity",
  data: function() {
    return {
      height: 250,
      width: 485
    }
  },
  computed: {
    ...mapState({
      word_similarity: state => state.session.word_similarity
    })
  },
  methods: {
    clipboardToast(word) {
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
    copyToClipboard(word) {
      let objRef = this;
      
      navigator.permissions.query({name: "clipboard-write"}).then(result => {
        if (result.state == "granted" || result.state == "prompt") {
          navigator.clipboard.writeText(word).then(
            () => objRef.clipboardToast(word));
        } else {
          var dummy = document.createElement("input");
          document.body.appendChild(dummy);                 // Add it to the document
          dummy.setAttribute("id", "dummy_id");             // Set its ID
          document.getElementById("dummy_id").value = word; // Output the array into it
          dummy.select();                                   // Select it
          document.execCommand("copy");                     // Copy its contents
          document.body.removeChild(dummy);                 // Remove it as its not needed anymore

          objRef.clipboardToast(word);
        }
      });
    },
    requestMostSimilar() {
      let objRef = this;

      this.makeToast(
        "Calculating word similarity",  // title
        "Please wait...",               // content
        "warning",                      // variant
        "word_similarity"); 	          // id

      this.getMostSimilar()
        .catch(function() {
          objRef.makeToast(
            "Oops, looks like something went wrong",
            "Please, try it again",
            "danger");
        }).then(() => objRef.$bvToast.hide("word_similarity"));
    },
    ...mapActions(["getMostSimilar"])
  },
}
</script>

<style lang="sass">
.bar
  background: steelblue
  color: white

.percentage
  color: steelblue
  font-size: smaller
</style>