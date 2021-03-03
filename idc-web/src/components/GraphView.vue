<template>
<b-card no-body footer-tag="footer">
	<b-tabs
		v-model="projection"
		no-key-nav
		small
		align="right"
		@change="updateLayout">
		<b-tab
			v-for="item of graph"
			:key="item.name"
			:title="item.name">
			<svg :id="item.id"
				:width="width" :height="height"
				class="graphViewCanvas"></svg>
		</b-tab>
	</b-tabs>
	<template id="graphViewControls" #footer>
		<b-container fluid>
			<b-row>
				<b-col col-sm-6>
					<b-row>
						<template v-if="$session.controls.projection == 't-SNE'">
							<b-input-group
								prepend="Neighborhood"
								size="sm">
								<b-form-input
										class="col-9"
										v-model="$session.controls.n_neighbors"
										size="sm"
										@change="updateLayout"
										:state="parameterState($session.controls.n_neighbors, 0, corpus_size)"
										type="number" step="1"
										min="0" :max="$session.corpus_size"></b-form-input>
							</b-input-group>
						</template>
						<template v-else>
							<b-input-group
								prepend="Distance"
								size="sm">
								<b-form-input
									size="sm"
									v-model="$session.controls.distance"
									type="range"
									step="0.01" min="0.0" max="1.0"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="$session.controls.distance"
										size="sm"
										@change="updateLayout"
										:state="parameterState($session.controls.distance, 0.0, 1.0)"
										type="number" step="0.01"
										min="0.0" max="1.0"></b-form-input>
								</b-input-group-append>
							</b-input-group>
						</template>
					</b-row>
					<b-row id="graph_counter">
						<b-button-toolbar>
							<b-button-group size="sm" class="mx-1">
								<b-button disabled variant="secondary">Docs</b-button>
								<b-button disabled
									variant="outline-secondary">{{nodes.length}}</b-button>
							</b-button-group>
							<b-button-group size="sm" class="mx-1">
								<b-button disabled variant="secondary">Links</b-button>
								<b-button disabled
									variant="outline-secondary">{{links.length}}</b-button>
							</b-button-group>
						</b-button-toolbar>
					</b-row>
				</b-col>
				<b-col sm="6">
					<template v-if="$session.controls.projection == 't-SNE'">
						<b-input-group
							prepend="Perplexity"
							size="sm">
								<b-form-input
									class="col-9"
									v-model="$session.controls.tsne.perplexity"
									size="sm"
									:state="parameterState($session.controls.tsne.perplexity, 5, 50)"
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
					<template v-else>
						<b-row>
							<b-input-group
								prepend="Charge"
								size="sm">
								<b-form-input
									size="sm"
									v-model="$session.controls.charge"
									type="range"
									min="-200" max=50 step="1"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="$session.controls.charge"
										size="sm"
										:state="parameterState($session.controls.charge, -200, 50)"
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
									v-model="$session.controls.linkDistance"
									type="range"
									step="1" min="0" max="200"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="$session.controls.linkDistance"
										size="sm"
										:state="parameterState($session.controls.linkDistance, 0, 200)"
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
			width: 545,
			height: 450,
			projection_list: ["t-SNE", "DAG"],
			projection: 0,
			graph: [
				{
					id: "GraphViewTSNE",
					name: "t-SNE",
					canvas: undefined,
					node: undefined,
					link: undefined,
					transform: undefined,
					simulation: undefined,
				},
				{
					id: "GraphViewDAG",
					name: "DAG",
					canvas: undefined,
					node: undefined,
					link: undefined,
					transform: undefined,
					simulation: undefined,
				}
			],
		}
	},
	watch: {
		projection(value) {
			this.$session.controls.projection = this.graph[value].name;
			this.updateLayout();
		}
	},
	computed: {
		node: {
			get() {
				return this.graph[this.projection].node;
			},
			set(value) {
				this.graph[this.projection].node = value;
			}
		},
		nodes() {
			return this.$session.graph.nodes;
		},
		link: {
			get() {
				return this.graph[this.projection].link;
			},
			set(value) {
				this.graph[this.projection].link = value;
			}
		},
		links() {
			if (this.$session.controls.projection == "t-SNE") {
				return this.$session.graph.neighborhood.filter((link) => 
					link.value <= this.$session.controls.n_neighbors
				);
			} else {
				return this.$session.graph.dist.filter((link) => 
					link.value <= this.$session.controls.distance);
			}
		},
		simulation() {
			return this.graph[this.projection].simulation;
		},
		corpus_size() {
			return this.$session.index.length;
		}
	},
	mounted() {
		this.graph.forEach((graph) => {
			// SIMULATION ENGINE
			graph.simulation = this.$d3.forceSimulation()
				.force('link', 		this.$d3.forceLink())
				.force("charge", 	this.$d3.forceManyBody())
				.force("center", 	this.$d3.forceCenter())
				.on("tick", function() {
					graph.node
						.attr("cx", d => d.x)
						.attr("cy", d => d.y);
			
					graph.link
						.attr("x1", d => d.source.x)
						.attr("y1", d => d.source.y)
						.attr("x2", d => d.target.x)
						.attr("y2", d => d.target.y);
				});

			// CANVAS
			graph.canvas = this.$d3.select(`#${graph.id}`)
				.attr("width", this.width)
				.attr("height", this.height)
				.attr("viewBox", [0, 0, this.width, this.height])
				.call(this.$d3.zoom()
					.scaleExtent([0.1, 8])
					.on("zoom", (e) => {graph.canvas.attr("transform", e.transform)}))
				.append("g");

			// 	LINKS
			graph.link = graph.canvas.append("g")
				.attr("class", "link")
				.attr("stroke", "#999")
				.attr("stroke-opacity", 0.5)
				.selectAll("line");

			// 	NODES
			graph.node = graph.canvas.append("g")
				.attr("class", "node")
				.selectAll("circle");
		});

		this.updateLayout();
	},
	methods: {
		parameterState(value, min, max) {
			return (value > max) || (value < min) ? false : null;
		},
		updateLayout() {
			const objRef = this,
						_links = this.links,
						_nodes = this.nodes,
						_projection = (this.projection == this.projection_list.indexOf("DAG"));

			// NODES
			this.node = this.node.data(_nodes).join("circle")
				.style("pointer-events", "all")
				.attr("r", 4)
				.attr("cx", d => d.x)
				.attr("cy", d => d.y)
				.attr("opacity", 1)
				.call(this.$d3.drag()
					.on("start", function(e, d) {
						if (_projection) {
							if (!e.active) objRef.simulation.alphaTarget(0.3).restart();
							d.fx = d.x;
							d.fy = d.y;
					}})
					.on("drag", function(e, d) {
						if (_projection) {
							d.fx = e.x;
							d.fy = e.y;
					}})
					.on("end", function(e, d) {
						if (_projection) {
							if (e.active) objRef.simulation.alphaTarget(0.0001);
							d.fx = null;
							d.fy = null;
					}}));
			this.node.append("title").text(d => d.name);
			
			// LINKS
			this.link = this.link.data(_links).join("line")
				.attr("stroke", "#999")
				.attr("opacity", 0.8);

			// SIMULATION FORCES
			this.simulation
				.nodes(_nodes)
				.force("link").links(_links);

			if(!_projection) {
				const _emb = this.$session.tsne;

				_emb.forEach((row, index) => {
					_nodes[index].x = (row[0] + this.width/11) * 6;
					_nodes[index].y = (row[1] + this.height/11) * 6;});

				this.node
					.attr("cx", d => d.x)
					.attr("cy", d => d.y);

				this.link
					.attr("stroke-width", 1)
					.attr("x1", d => (_emb[d.source.index][0] + this.width/11) * 6)
					.attr("y1", d => (_emb[d.source.index][1] + this.height/11) * 6)
					.attr("x2", d => (_emb[d.target.index][0] + this.width/11) * 6)
					.attr("y2", d => (_emb[d.target.index][1] + this.height/11) * 6);
			} else {
				this.link.attr("stroke-width", (d) => 1 - d.value)
			}

			// FORCE CENTER
			this.simulation.force("center")
        .x(this.width / 2)
        .y(this.height / 2);

			// FORCE CHARGE
			this.simulation.force("charge")
				.strength(this.$session.controls.charge * (_projection ? 1 : 0))
				.distanceMin(1)
				.distanceMax(200);

			// LINK FORCE
			this.simulation.force("link")
				.distance(this.$session.controls.linkDistance)
				.iterations(1);

			if(_projection) {
				this.simulation.alphaTarget(1).restart();
			} else {
				this.simulation.alpha(0).stop();
			}
		}
	},
}
</script>

<style lang="sass" scoped>
#graphView
	width: 550px
	max-width: 550px
	height: 575px
	max-height: 575px
	margin: 0 25px 0 25px
	padding: 1px

	header
		padding: 1px
		text-align: center
		height: 25px

	footer
		display: flex
		vertical-align: middle
		justify-content: center
		justify-items: center
		align-content: center
		align-items: center
		padding: 10px 5px 5px 5px
		z-index: 2

.graphViewCanvas
	z-index: 1
	width: 545px
	max-width: 545px
	height: 450px
	max-height: 450px

#projectionToggler
	position: absolute
	z-index: 2
	top: 30px
	right: 5px

#graphViewControls
	margin: 1px
	border: 1px
	padding: 10px 1px 1px 1px

svg
  flex-basis: 100%

#metricsPanel
	margin: 0

#graph_counter
	padding-top: 5px

.link
	path
		stroke: #999
		stroke-opacity: 0.3
		fill: none

.node
	circle
		stroke: #fff
		stroke-width: 1.5px
</style>