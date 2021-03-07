<template>
<b-card no-body footer-tag="footer">
	<b-form-group id="projectionSwitcher">
      <b-form-radio-group
        v-model="projection"
				:options="projection_list"
				button-variant="outline-dark"
				class="ml-auto"
				no-key-nav
				size="sm"
				buttons
				@change="updateLayout"
      ></b-form-radio-group>
	</b-form-group>
	<svg id="graphViewCanvas"></svg>
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
								<b-button
									@click="getProjection('t-SNE')"
									variant="info">
									<font-awesome-icon :icon="['fas', 'redo']"/>
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
			projection: "t-SNE",
			simulation: undefined,
			canvas: undefined,
			node: undefined,
			link: undefined,
			selected: this.$session.selected,
      highlight: this.$session.highlight
		}
	},
	watch: {
		projection(value) {
			this.$session.controls.projection = value;
			this.updateLayout();
		},
		selected() {
      let objRef = this;
      
      if(this.selected.length == 0) {
        this.node.classed("selected", false);
      } else {
        this.node.classed("selected", d =>
          objRef.selected
            .map(doc => doc.id)
            .includes(d.id));
      }
		},
    'highlight':{
      deep: true,
      handler () {
        const normal  = 0.9,
              faded   = 0.3;
        let clusters  =this.$session.clusters;

        if(this.highlight.cluster_name == "") {
          this.node.attr("opacity", normal);
        } else {
          const doc_ids = clusters.cluster_docs[this.highlight.cluster_name];
          
          this.node.attr("opacity", 
            d => doc_ids.includes(d.id) ? normal : faded);
        }
      }
    }
	},
	computed: {
		nodes() {
			return this.$session.graph.nodes;
		},
		links() {
			if (this.projection == "t-SNE") {
				return this.$session.graph.neighborhood.filter((link) => 
					link.value <= this.$session.controls.n_neighbors
				);
			} else {
				return this.$session.graph.dist.filter((link) => 
					link.value <= this.$session.controls.distance);
			}
		},
		corpus_size() {
			return this.$session.index.length;
		}
	},
	mounted() {
		let objRef = this;
		// SIMULATION ENGINE
		this.simulation = 	this.$d3.forceSimulation()
			.force('link', 		this.$d3.forceLink())
			.force("charge", 	this.$d3.forceManyBody())
			.force("center", 	this.$d3.forceCenter())
			.force("forceX",	this.$d3.forceX())
			.force("forceY",	this.$d3.forceY())
			.on("tick", function() {
				objRef.node
					.attr("cx", d => d.x)
					.attr("cy", d => d.y);
		
				objRef.link
					.attr("x1", d => d.source.x)
					.attr("y1", d => d.source.y)
					.attr("x2", d => d.target.x)
					.attr("y2", d => d.target.y);
			});

		// CANVAS
		this.canvas = this.$d3.select("#graphViewCanvas")
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("viewBox", [0, 0, this.width, this.height])
			.call(this.$d3.zoom()
				.scaleExtent([0.1, 8])
				.on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}))
			.append("g");

		// 	LINKS
		this.link = this.canvas.append("g")
			.attr("class", "link")
			.attr("stroke", "#999")
			.attr("stroke-opacity", 0.5)
			.selectAll("line");

		// 	NODES
		this.node = this.canvas.append("g")
			.attr("class", "node")
			.selectAll("circle");
		
		this.updateLayout();
	},
	methods: {
		makeToast(
				title,
				content,
				variant,
				id=null) {
			// Use a shorter name for this.$createElement
			const h = this.$createElement
			// Create the message
			const vProgressToast = h(
				'p', { class: ['mb-0'] },
				[h('b-spinner', { props: { small: true } }), ` ${content}`]);
			this.$bvToast.toast(
				(id) ? vProgressToast : content,
				{
					id: (id) ? id : null,
					variant: variant,
					title: title,
					toaster: "b-toaster-bottom-right",
					solid: false,
					autoHideDelay: 5000,
					noAutoHide: (id) ? true : false,
					noCloseButton: (id) ? true : false,
					appendToast: true
				});
		},
		parameterState(value, min, max) {
			return (value > max) || (value < min) ? false : null;
		},
		updateLayout() {
			const objRef = this,
						_links = this.links,
						_nodes = this.nodes,
						_projection = (this.projection == "DAG");

			// NODES
			this.node = this.node.data(_nodes).join("circle")
				.style("pointer-events", "all")
				.attr("r", 4)
				.attr("opacity", 0.9)
				.attr("cx", d => d.x)
				.attr("cy", d => d.y)
				.classed("selected", d =>
					objRef.selected
						.map(doc => doc.id)
						.includes(d.id))
				.attr("fill", (d, i) => {
					let _label = objRef.$session.clusters.labels[i];
					return objRef.$session.clusters.colors[_label];})
				.on("click", function(e, d) {
					let index = objRef.selected
						.map(doc => doc.id)
						.indexOf(d.id);
					
					if (index == -1) {
            let _doc = objRef.$userData.corpus.filter(doc => doc.id == d.id)[0];
						objRef.selected.push(_doc);
            objRef.$session.focused.id = _doc.id;
					} else {
						objRef.selected.pop(index);
            objRef.$session.focused.id = null;
					}
					
					let _ref = objRef.$d3.select(this);
					_ref.classed("selected", !_ref.classed("selected"));
				})
				.call(this.$d3.drag()
					.on("start", function(e, d) {
						if (_projection) {
							if (!e.active) objRef.simulation.alpha(1).restart();
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
							if (e.active) objRef.simulation.alpha(1);
							d.fx = null;
							d.fy = null;
					}}));
			this.node.append("title").text(d => d.name);
			
			// LINKS
			this.link = this.link.data(_links).join("line")
				.attr("stroke", "#999")
				.attr("opacity", 0.7);
			this.link.append("title").text(d => `${d.source.name} -> ${d.target.name}`);

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

			// // FORCE CHARGE
			this.simulation.force("charge")
				.strength(this.$session.controls.charge)
				.distanceMin(1)
				.distanceMax(200);

			// GRAVITY
			this.simulation.force("forceX")
				.strength(0.05)
				.x(this.width / 2);
			this.simulation.force("forceY")
				.strength(0.05)
				.y(this.height / 2);

			// LINK FORCE
			this.simulation.force("link")
				.distance(this.$session.controls.linkDistance)
				.iterations(1);

			if(_projection) {
				this.simulation.alpha(1).restart();
			} else {
				this.simulation.alpha(0).stop();
			}
		},
		getProjection(projection) {
			let objRef = this;
		
			const formData = new FormData();
			formData.set("userId", this.$userData.userId);
			formData.set("projection", projection);
			formData.set("index", this.$session.index);
			formData.set("perplexity", this.$session.controls.tsne.perplexity);

			this.makeToast(
					`Requesting ${projection} projection`,	// title
					"Please wait...",												// content
					"warning",															// variant
					"request_projection");									// id
			this.$axios.post(this.$server+"/projection", formData, {
				headers: { "Content-Type": "multipart/form-data" }
			}).then((result) => {
				objRef.$session.tsne = result.data.projection;

				objRef.$bvToast.hide("request_projection");

				objRef.updateLayout();
			});
	}
	},
}
</script>

<style lang="sass">
#graphView
	width: 550px
	max-width: 550px
	height: 575px
	max-height: 560px
	margin: 0 25px 0 25px
	padding: 0

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

#graphViewCanvas
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
	circle.selected
			stroke-width: 1px
			stroke: red

#projectionSwitcher
	margin: 5px 0 5px 5px
</style>