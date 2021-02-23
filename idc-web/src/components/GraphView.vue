<template>
<b-card header-tag="header" footer-tag="footer">
	<!-- TODO code the graph view -->
	<template #header>Graph View</template>	
	<b-form-group id="projectionToggler">
		<b-form-radio-group buttons
			size="sm"
			button-variant="outline-dark"
			v-model="controls.projection"
			@change="toggleSimulation"
			:options="projections"
		></b-form-radio-group>
	</b-form-group>
	<svg id="graphViewCanvas"></svg>
	<template id="graphViewControls" #footer>
		<b-container fluid>
			<b-row>
				<b-col col-sm-6>
					<b-row>
						<b-input-group
							prepend="Cosine distance"
							size="sm">
							<b-form-input
								size="sm"
								v-model="controls.cosineDistance"
								type="range"
								min="0" max="100"
								@change="updateLayout"></b-form-input>
							<b-input-group-append>
								<b-form-input
									class="col-9"
									v-model="controls.cosineDistance"
									size="sm"
									:state="parameterState(controls.cosineDistance, 0, 100)"
									type="number"
									min="0" max="100"></b-form-input>
							</b-input-group-append>
						</b-input-group>
					</b-row>
					<b-row>
						<b-button-toolbar>
							<b-button-group size="sm" class="mx-1">
								<b-button disabled variant="secondary">Docs</b-button>
								<b-button disabled
									variant="outline-secondary">{{graph.nodes.length}}</b-button>
							</b-button-group>
							<b-button-group size="sm" class="mx-1">
								<b-button disabled variant="secondary">Links</b-button>
								<b-button disabled
									variant="outline-secondary">{{graph.links.length}}</b-button>
							</b-button-group>
						</b-button-toolbar>
					</b-row>
				</b-col>
				<b-col sm="6">
					<template v-if="controls.projection == 't-SNE'">
						<b-input-group
							prepend="Perplexity"
							size="sm">
								<b-form-input
									class="col-9"
									v-model="controls.tsne.perplexity"
									size="sm"
									:state="parameterState(controls.tsne.perplexity, 5, 50)"
									type="number"
									min="5" max="50"></b-form-input>
							<b-input-group-append>
								<b-button variant="info">
									<font-awesome-icon :icon="['fas', 'redo']"/>
									Recompute
								</b-button>
							</b-input-group-append>
						</b-input-group>
					</template>
					<template v-else-if="controls.projection == 'UMAP'">
						<b-row no-gutter>
							<b-col sm="7">
								<b-row>
									<b-input-group
										prepend="Neighbors"
										size="sm">
										<b-form-input
												class="col-9"
												v-model="controls.umap.n_neighbors"
												size="sm"
												:state="parameterState(controls.umap.n_neighbors, 5, 50)"
												type="number"
												min="5" max="50"></b-form-input>
									</b-input-group>
								</b-row>
								<b-row>
									<b-input-group
										prepend="Min. distance"
										size="sm">
										<b-form-input
												class="col-9"
												v-model="controls.umap.min_dist"
												size="sm"
												:state="parameterState(controls.umap.min_dist, 0.0, 1.0)"
												type="number"
												step="0.1" min="0.0" max="1.0"></b-form-input>
									</b-input-group>
								</b-row>
							</b-col>
							<b-col sm="5">
								<b-button class="h-100" variant="info" size="sm">
									<font-awesome-icon :icon="['fas', 'redo']"/>
									Recompute
								</b-button>
							</b-col>
						</b-row>
					</template>
					<template v-else>
						<b-row>
							<b-input-group
								prepend="Charge"
								size="sm">
								<b-form-input
									size="sm"
									v-model="controls.charge"
									type="range"
									min="-200" max=50 step="1"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="controls.charge"
										size="sm"
										:state="parameterState(controls.charge, -200, 50)"
										type="number"
										min="-200" max=50 step="1"></b-form-input>
								</b-input-group-append>
							</b-input-group>
						</b-row>
						<b-row>
							<b-input-group
								prepend="Link distance"
								size="sm">
								<b-form-input
									size="sm"
									v-model="controls.linkDistance"
									type="range"
									step="1" min="0" max="200"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="controls.linkDistance"
										size="sm"
										:state="parameterState(controls.linkDistance, 0, 200)"
										type="number"
										step="1" min="0" max="200"></b-form-input>
								</b-input-group-append>
							</b-input-group>
						</b-row>
					</template>
				</b-col>
			</b-row>
		</b-container>
	</template>
</b-card>
</template>

<script>
export default {
  name: "GraphView",
	data() {
		return {
			width: 500,
			height: 500,
			canvas: undefined,
			nodes: undefined,
			links: undefined,
			linksEnabled: true,
			zoom: undefined,
			transform: undefined,
			graph: this.$session.graph,
			simulation: this.$d3.forceSimulation(),
			projections: ["t-SNE", "UMAP", "DAG"],
			controls: this.$session.controls
		}
	},
	computed: {
		linksFiltered() {
			// TODO implement threshold filter
			return (this.linksEnabled) ? this.graph.links : [];
		}
	},
	mounted() {
		let objRef = this;

		this.canvas = this.$d3.select("#graphViewCanvas")
			.attr("viewBox", [0, 0, this.width, this.height])
			.call(this.$d3.zoom()
				.scaleExtent([0.1, 8])
				.on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}))
			.append("g");

		// 	LINKS
		this.links = this.canvas.append("g")
			.attr("class", "links")
			.selectAll("line")
			.data(this.graph.links)
			.enter().append("line")
			.attr("x1", d => d.source.x)
			.attr("y1", d => d.source.y)
			.attr("x2", d => d.target.x)
			.attr("y2", d => d.target.y)
			.attr("stroke-width", 1)
			.attr("stroke", "#aaa")
			.attr("opacity", 1);

		// 	NODES
		this.nodes = this.canvas.append("g")
      .attr("class", "nodes")
			.selectAll("circle")
			.data(this.graph.nodes)
			.enter().append("circle")
			.style("pointer-events", "all")
			.attr("r", 5)
			.attr("opacity", 1)
			.attr("cx", d => d.x)
			.attr("cy", d => d.y)
      .call(this.$d3.drag()
				.on("start", 	this.dragstarted)
				.on("drag", 	this.dragged)
				.on("end", 		this.dragended))
		this.nodes.append("title").text(d => d.id);

		// // SIMULATION ENGINE
		this.simulation.nodes(this.graph.nodes);
		this.simulation
			.force("center", 	this.$d3.forceCenter())
			.force("charge", 	this.$d3.forceManyBody())
			.force("collide", this.$d3.forceCollide())
			.force("link", 		this.$d3.forceLink());
		this.updateLayout();
		this.simulation.on("tick", this.ticked);
	},
	methods: {
		parameterState(value, min, max) {
			return (value > max) || (value < min) ? false : null;
		},
		toggleSimulation(projeciton) {
			// TODO recover t-SNE or UMAP projections and stop simulation
			if (projeciton == "DAG") {
				this.simulation.alphaTarget(0.3).restart();
			} else {
				this.simulation.stop();
			}
		},
		dragstarted(e, d) {
			if (this.controls.projection == "DAG") {
				if (!e.active) this.simulation.alphaTarget(0.3).restart();
				d.fx = d.x;
				d.fy = d.y;
			}
		},
		dragged(e, d) {
			if (this.controls.projection == "DAG") {
				d.fx = e.x;
				d.fy = e.y;
			}
		},
		dragended(e, d) {
			if (this.controls.projection == "DAG") {
				if (e.active) this.simulation.alphaTarget(0.0001);
				d.fx = null;
				d.fy = null;
			}
		},
		updateLayout() {
			// FORCE CENTER
			this.simulation.force("center")
        .x(this.width/2)
        .y(this.height/2)

			// // FORCE CHARGE
			this.simulation.force("charge")
        .strength(this.controls.charge)
        .distanceMin(1)
        .distanceMax(200);

			// // COLLISION FORCE
			this.simulation.force("collide")
        .strength(.7)
        .radius(5)
        .iterations(1);
			
			// LINK FORCE
			this.simulation.force("link")
        .id(d => d.id)
        .distance(this.controls.linkDistance)
        .iterations(1)
        .links(this.linksFiltered);

			this.simulation.alpha(1).restart();
		},
		ticked(){
			this.links
				.attr("x1", d => d.source.x)
				.attr("y1", d => d.source.y)
				.attr("x2", d => d.target.x)
				.attr("y2", d => d.target.y);

			this.nodes
				.attr("cx", d => d.x)
				.attr("cy", d => d.y);
		}
	},
}
</script>

<style scoped>
#graphView {
	width: 550px;
	height: 600px;
	margin: 0 25px 0 25px;
	padding: 1px;
}

#graphView header {
	padding: 1px;
	text-align: center;
	height: 25px;
}

#graphViewCanvas {
	z-index: 1;
}

#projectionToggler {
	position: absolute;
	z-index: 2;
	top: 30px;
	right: 5px;
}

#graphViewControls {
	margin: 1px;
	border: 1px;
	padding: 10px 1px 1px 1px;
}

#graphView footer {
	display: flex;
	vertical-align: middle;
	justify-content: center;
	justify-items: center;
	align-content: center;
	align-items: center;
	padding: 10px 5px 5px 5px;
	z-index: 2;
}

svg {
  flex-basis: 100%;
}

#metricsPanel {
	margin: 0;
}
</style>