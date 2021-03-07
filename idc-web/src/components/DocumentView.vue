<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		Document view
	</b-card-header>
	<div>
    <b-form-select v-model="focused" :options="selected"></b-form-select>
		<div id="displayCy" v-html="displaCy_NER"></div>
	</div>
</b-card>
</template>

<script>
export default {
	name: 'DocumentView',
	data() {
		return {
			session_selected: this.$session.selected,
			focused: this.$session.focused
		}
	},
	computed: {
		selected: function() {
			return this.session_selected.map(d => {
				return {
					value: d.id,
					text: d.file_name
				}
			});
		},
		displaCy_NER: function() {
			let objRef = this;
			return this.session_selected.filter(
				d => d.id == objRef.focused
			)[0].svg;
		}
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
.card
	header
		padding: 0
		text-align: center
		height: 25px

#displaCy
	max-height: 500px
    overflow-y: scroll
    padding: 5px
    font-size: small
    word-break: normal
</style>
