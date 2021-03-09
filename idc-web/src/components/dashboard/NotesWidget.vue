<template>
<div>
	<b-button
		id="notes"
		size="sm"
		class="navbar-item-spaced"
		variant="outline-warning">
		<font-awesome-icon :icon="['fas', 'sticky-note']"/>
		Notes
	</b-button>
	<b-popover placement="bottom"
		target="notes" variant="warning" triggers="hover">
		<template #title>
			<b-button
				variant="outline-warning"
				size="sm"
				v-b-modal.notesModal>
				<font-awesome-icon :icon="['fas', 'expand-alt']"/>
			</b-button>
		</template>
		<b-form-textarea
			placeholder="Type some notes..."
			v-model="notes.text"
			rows="3"
			max-rows="6"
		></b-form-textarea>
	</b-popover>
	<b-modal id="notesModal" hide-footer
		header-bg-variant="warning"
		header-text-variant="light"
		body-bg-variant="warning"
		body-text-variant="light">
		<template #modal-title>
			Notes for session: {{ $session.name.text }}
		</template>
		<template #default>
			<b-form-textarea
				v-model="notes.text"
				placeholder="Type some notes..."
				rows="10"
				max-rows="10"
			></b-form-textarea>
		</template>
	</b-modal>
</div>
</template>

<script>
export default {
	name: "NotesWidget",
  data(){
    return {notes: this.$session.notes};
  }
}
</script>

<style scoped></style>