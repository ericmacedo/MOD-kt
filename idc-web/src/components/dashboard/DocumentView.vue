<template>
<b-card no-body>
    <b-card-header header-tag="header" class="text-center">
		Document view
	</b-card-header>
	<div class="d-block">
		<b-input-group>
			<b-form-select
        v-model="focused.id"
        :options="selected"></b-form-select>
			<b-input-group-append>
				<b-button 
					size="sm"
					title="Unsellect all documents"
					variant="outline-danger"
          @click="session_selected.splice(0, session_selected.length)">
					<font-awesome-icon size="sm" :icon="['fas', 'times']"/>
				</b-button>
			</b-input-group-append>
		</b-input-group>
	</div>
	<div id="displaCy" class="mt-3" v-html="displaCy_NER"></div>
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
				d => d.id == objRef.focused.id
			)[0]?.svg ?? "<center>Please select a document<center/>";
		}
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
#displaCy
	overflow-y: auto
	padding: 5px
	font-size: small
	word-break: normal
</style>
