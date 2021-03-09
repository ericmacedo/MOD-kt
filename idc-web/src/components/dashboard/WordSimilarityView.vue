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
        variant="outline-info">
        <font-awesome-icon :icon="['fas', 'search']"/>
      </b-button>
    </b-input-group>
    <div
      v-for="(item, index) in bar"
      :key="index"
      class="d-flex w-100 pr-1"
      :style="{'align-items': 'flex-end'}"
      @click="copyToClipboard(item.word)">
      <div
        class="bar mt-2 ml-1 mr-1 pl-2"
        :style="{'width': ''+(width * item.value * 0.9)+'px'}"
        >{{ item.word }}</div>
      <span
        class="ml-1"
        :style="{'color': 'steelblue'}">{{item.value * 100}}%</span>
    </div>
	</div>
</b-card>
</template>

<script>
export default {
  name: "WordSimilarity",
  data: function() {
    return {
      word_similarity: this.$session.word_similarity,
      bar: [
        {word: "eric", value: 0.5},
        {word: "macedo", value: 0.6},
        {word: "cabral", value: 1.0}
      ],
      height: 250,
      width: 485
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
.bar
  background: steelblue
  color: white
</style>