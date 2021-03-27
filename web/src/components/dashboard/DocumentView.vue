<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		Document view
	</b-card-header>
	<div class="d-block">
		<b-input-group>
			<b-form-select
        v-model="focused"
        :options="selected"
        text-field="file_name"
        value-field="id"></b-form-select>
			<b-input-group-append>
				<b-button 
					size="sm"
					title="Unsellect all documents"
					variant="outline-danger"
          @click="setFocused(null); setSelected([]);">
					<font-awesome-icon size="sm" :icon="['fas', 'times']"/>
				</b-button>
			</b-input-group-append>
		</b-input-group>
	</div>
	<div id="displaCy" class="mt-3" v-html="displaCy_NER"></div>
</b-card>
</template>

<script>
import { mapMutations, mapState } from 'vuex';

export default {
	name: 'DocumentView',
	computed: {
		displaCy_NER: function() {
			let objRef = this;
			return this.corpus.find(
				doc => doc.id == objRef.focused
			)?.svg ?? "<center>Please select a document<center/>";
		},
    focused: {
      get() {
        return this.$store.state.session.focused;
      },
      set(id) {
        this.setFocused(id);
      }
    },
    selected() {
      let selected = this.$store.state.session.selected;
      return this.corpus.filter((doc) => selected.includes(doc.id));
    },
    ...mapState("userData", ["corpus"])
	},
  methods: {
    ...mapMutations("session", ["setFocused", "setSelected"])
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
#displaCy
	overflow-y: scroll
	padding: 5px
	font-size: small
	word-break: normal
</style>
