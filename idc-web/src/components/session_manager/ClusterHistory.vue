<template>
<div class="h-100 flex-column align-items-start">
  <b-list-group flush id="doc_list">
    <b-list-group-item
      v-for="doc of doc_list"
      :key="doc"
      class="doc_list_item"
      @mouseover="hover(doc)"
      @mouseout="hoverOut">
      <div class="d-flex w-100 justify-content-between">
        <svg class="w-25"
          height="20">
          <circle
            v-for="(color, i) in index[doc]"
            :key="i"
            :fill="color"
            :cx="10 + (12 * i)"
            cy="10"
            r="5"/>
        </svg>
        <span class="w-75 ml-1">{{ corpus.find(d => d.id == doc).file_name }}</span>
      </div>
    </b-list-group-item>
  </b-list-group>
</div>
</template>

<script>
import {mapState} from "vuex";

export default {
  name: "ClusterHistory",
  computed: {
    document: {
      get() {
        console.log(this.$store.state.sankey.selection);
        return this.$store.state.sankey.selection.document;
      },
      set(document) {
        this.$store.state.sankey.selection.document = document;
      }
    },
    doc_list() {
      let objRef = this,
          result = Object.keys(this.index);
      
      if(this.selection_index.length > 0) {
        result = result.filter(d => objRef.selection_index.includes(d));
      }
      return result
    },
    ...mapState({
      corpus: ({userData}) => userData.corpus,
      index: ({sankey}) => sankey.graph.index,
      selection_index: ({sankey}) => sankey.selection.index
    })
  },
  methods: {
    hover(doc) {
      this.document = doc
    },
    hoverOut() {
      this.document = null;
    }
  }
}
</script>

<style lang="sass">
#doc_list
  .doc_list_item
    background: none
    &.active
      background: steelblue !important
    &:hover
      background: lightgrey
</style>