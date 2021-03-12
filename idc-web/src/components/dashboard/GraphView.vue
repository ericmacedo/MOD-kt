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
			<b-row h-align="center">
				<b-col col-sm-6>
					<b-row>
						<template v-if="projection == 't-SNE'">
							<b-input-group
								prepend="Neighborhood"
								size="sm">
								<b-form-input
										class="col-9"
										v-model="n_neighbors"
										size="sm"
										@change="updateLayout"
										:state="parameterState(n_neighbors, 0, index_size)"
										type="number" step="1"
										min="0" :max="index_size"></b-form-input>
							</b-input-group>
						</template>
						<template v-else>
							<b-input-group
								prepend="Distance"
								size="sm">
								<b-form-input
									size="sm"
									v-model="distance"
									type="range"
									step="0.01" min="0.0" max="1.0"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="distance"
										size="sm"
										@change="updateLayout"
										:state="parameterState(distance, 0.0, 1.0)"
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
					<template v-if="projection == 't-SNE'">
						<b-input-group
							prepend="Perplexity"
							size="sm">
								<b-form-input
									class="col-9"
									v-model="perplexity"
									size="sm"
									:state="parameterState(perplexity, 5, 50)"
									type="number"
									min="5" max="50"></b-form-input>
							<b-input-group-append>
								<b-button
									@click="requestProjection('t-SNE')"
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
									v-model="charge"
									type="range"
									min="-200" max=50 step="1"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="charge"
										size="sm"
										:state="parameterState(charge, -200, 50)"
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
									v-model="linkDistance"
									type="range"
									step="1" min="0" max="200"
									@change="updateLayout"></b-form-input>
								<b-input-group-append>
									<b-form-input
										class="col-9"
										v-model="linkDistance"
										size="sm"
										:state="parameterState(linkDistance, 0, 200)"
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
import { mapState, mapGetters, mapMutations, mapActions } from  "vuex";

export default {
  name: "GraphView",
	data() {
		return {
			width: 485,
			height: 430,
			projection_list: ["t-SNE", "DAG"],
			simulation: undefined,
			canvas: undefined,
			node: undefined,
			link: undefined
		}
	},
	watch: {
		projection() {
			this.updateLayout();
		},
		selected() {
      let objRef = this;
      
      if(this.selected.length == 0) {
        this.node.classed("selected", false);
      } else {
        this.node.classed("selected", d =>
          objRef.selected.includes(d.id));
      }
		},
    'highlight':{
      deep: true,
      handler () {
        const normal  = 0.9,
              faded   = 0.3;

        if(this.highlight == "") {
          this.node.attr("opacity", normal);
        } else {
          const doc_ids = this.clusters.cluster_docs[this.highlight];
          
          this.node.attr("opacity", 
            d => doc_ids.includes(d.id) ? normal : faded);
        }
      }
    }
	},
	computed: {
    projection: {
      get() { return this.controls.projection },
      set(projection) {
        this.$store.state.session.controls.projection = projection;
      }
    },
    n_neighbors: {
      get() { return this.controls.n_neighbors },
      set(n_neighbors) {
        this.$store.state.session.controls.n_neighbors = n_neighbors;
      }
    },
    distance: {
      get() { return this.controls.distance },
      set(distance) {
        this.$store.state.session.controls.distance = distance;
      }
    },
    perplexity: {
      get() { return this.controls.tsne.perplexity },
      set(perplexity) {
        this.$store.state.session.controls.tsne.perplexity = perplexity;
      }
    },
    charge: {
      get() { return this.controls.charge },
      set(charge) {
        this.$store.state.session.controls.charge = charge;
      }
    },
    linkDistance: {
      get() { return this.controls.linkDistance },
      set(linkDistance) {
        this.$store.state.session.controls.linkDistance = linkDistance;
      }
    },
    ...mapState("session", [
      "controls", "highlight", "selected",
      "clusters", "tsne"]),
    ...mapGetters("session", ["nodes", "links", "index_size"])
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
						_projection = (this.controls.projection == "DAG");

			// NODES
			this.node = this.node.data(_nodes).join("circle")
				.style("pointer-events", "all")
				.attr("r", 4)
				.attr("opacity", 0.9)
				.attr("cx", d => d.x)
				.attr("cy", d => d.y)
				.classed("selected", d =>
					objRef.selected.includes(d.id))
				.attr("fill", (d, i) => {
					let _label = objRef.clusters.labels[i];
					return objRef.clusters.colors[_label];})
				.on("click", function(e, d) {
					objRef.updateSelected(d.id);
					
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
				const _emb = this.tsne;

				_emb.forEach((row, index) => {
					_nodes[index].x = (row[0] + objRef.width/11) * 6;
					_nodes[index].y = (row[1] + objRef.height/11) * 6;});

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
				.strength(this.controls.charge)
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
				.distance(this.controls.linkDistance)
				.iterations(1);

			if(_projection) {
				this.simulation.alpha(1).restart();
			} else {
				this.simulation.alpha(0).stop();
			}
		},
		requestProjection(projection) {
			let objRef = this;

			this.makeToast(
					`Requesting ${projection} projection`,	// title
					"Please wait...",												// content
					"warning",															// variant
					"request_projection");									// id
          
			this.getProjection().then(() => {
				objRef.$bvToast.hide("request_projection");
				objRef.updateLayout();
			}).catch(() => {
        objRef.$bvToast.hide("request_projection");
        objRef.makeToast(
					"Error",
					"Oops, looks like something went wrong",
					"danger");
      });
    },
    ...mapMutations("session", ["updateSelected"]),
    ...mapActions(["getProjection"])
	},
}
</script>

<style lang="sass">
#graphViewControls
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