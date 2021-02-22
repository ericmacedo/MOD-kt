<template>
<div class="dashboard">
	<b-card-group columns>
		<b-card header-tag="header">
			<!-- TODO code the plain document view -->
			<template #header>Document View</template>
			<b-card-body></b-card-body>
		</b-card>
		<b-card header-tag="header">
			<template #header>WordCloud View</template>
			<b-card-body></b-card-body>
		</b-card>
		<b-card header-tag="header">
			<template #header>Cluster View</template>
			<b-card-body></b-card-body>
		</b-card>
		<b-card header-tag="header">
			<template #header>Term frequency View</template>
			<b-card-body></b-card-body>
		</b-card>
		<b-card id="graphView" header-tag="header">
			<!-- TODO code the graph view -->
			<template #header>Graph View</template>
			<b-card-body></b-card-body>
		</b-card>
	</b-card-group>
</div>
</template>

<script>
// import * as d3 from "d3";

export default {
name: 'Dashboard',
	props: {
		userData: {
			type: Object,
			required: true
		}
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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

/* #graphView {
	height: 500px;
	width: 500px;
} */
</style>
