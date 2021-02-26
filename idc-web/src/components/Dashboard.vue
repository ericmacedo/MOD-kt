<template>
<div class="dashboard h-100 w-100">
	<document-view id="documentView"
		></document-view>
	<graph-view id="graphView"
		sm="12" md="4" lg="4"></graph-view>
</div>
</template>

<script>
import GraphView from './GraphView';
import DocumentView from './DocumentView';

export default {
	name: 'Dashboard',
	props: {
		userData: {
			type: Object,
			required: true
		}
	},
	components: {
		"graph-view": GraphView,
		"document-view": DocumentView
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.dashboard {
	padding: 5px;
	border: 0!important;
	margin: 0!important;
}

.card-header {
	padding: 1px;
	text-align: center;
	height: 25px;
}
</style>
