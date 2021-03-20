<template>
<b-card no-body footer-tag="footer">
	<div
    id="projectionSwitcher"
    class="d-flex w-100 justify-content-between">
      <b-form-radio-group
        v-model="projection"
				:options="projection_list"
				button-variant="outline-dark"
				no-key-nav
				size="sm"
				buttons
				@change="updateLayout"
      ></b-form-radio-group>
      <b-button-group size="sm" class="ml-auto mr-2">
        <b-button
          size="sm"
          variant="secondary"
          title="Press it to recalculate the silhouette score"
          @click="silhouette_score = callSilhouette()">Silhouette</b-button>
        <b-button variant="outline-secondary" disabled>{{silhouette_score}}</b-button>
      </b-button-group>
	</div>
	<svg id="graphViewCanvas"></svg>
	<template id="graphViewControls" #footer>
		<b-container fluid>
			<b-row h-align="center">
				<b-col class="w-50">
					<b-row>
            <b-input-group size="sm">
              <!-- LINK FUNCTION SELECTOR -->
              <template #prepend>
                <b-dropdown
                  id="link-selector"
                  size="sm"
                  no-caret
                  variant="secondary">
                  <template #button-content>{{link_selector}}</template>
                  <b-dropdown-item
                    @click="link_selector = 'Distance fn'; updateLayout()">
                    Distance fn
                    {{ link_selector == "Distance fn" ? " &check;" : "" }}
                  </b-dropdown-item>
                  <b-dropdown-item
                    @click="link_selector = 'Neighborhood'; updateLayout()">
                    Neighborhood
                    {{ link_selector == "Neighborhood" ? " &check;" : "" }}
                  </b-dropdown-item>
                </b-dropdown>
              </template>

              <!-- LINK BY NEIGHBORHOOD -->
              <template v-if="link_selector == 'Neighborhood'">
                <b-form-input
                  class="col-9"
                  v-model="n_neighbors"
                  size="sm"
                  @change="updateLayout"
                  :state="parameterState(n_neighbors, 0, index_size)"
                  type="number" step="1"
                  min="0" :max="index_size"></b-form-input>
              </template>

              <!-- LINK BY DISTANCE FN -->
              <template v-else>
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
              </template>

            </b-input-group>
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
				<b-col class="w-50">
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
import * as d3 from "d3";
import silhouette from "@robzzson/silhouette";

Array.prototype.pushIfNotExist = function(item) { 
  if (!this.includes(item)) {
    this.push(item);
  }
};

export default {
  name: "GraphView",
	data() {
		return {
			width: 485,
			height: 430,
			projection_list: ["t-SNE", "DAG"],
			simulation: undefined,
      svg: undefined,
			canvas: undefined,
			node: undefined,
			link: undefined,
      tooltip: undefined,
      silhouette_score: 0.0
		}
	},
	watch: {
		projection() {
			this.updateLayout();
      this.silhouette_score = this.callSilhouette();
		},
    highlight:{
      deep: true,
      handler () {
        this.node
            .classed("faded", false);
          this.link
            .classed("faded", false);
        if(this.highlight == "") {
          this.node
            .classed("faded", false);
          this.link
            .classed("faded", false);
        } else {
          let doc_ids = this.clusters.cluster_docs[this.highlight];
          
          this.node.classed("faded", d => !doc_ids.includes(d.id));
          this.link.classed("faded",
            d => !(doc_ids.includes(d.source.id) || doc_ids.includes(d.target.id)));

          doc_ids = null;
        }
      }
    },
    selected: {
      deep: true,
      handler() {
        let objRef = this;

        if(this.selected.length == 0) {
          this.node
            .classed("selected", false)
            .classed("faded", false);
          this.link
            .classed("selected", false)
            .classed("faded", false);
        } else {
          let nodes = this.selected.map(d => d),
              links = [];

          this.link.data().forEach((link) => {
            if (objRef.selected.includes(link.source.id)) {
              nodes.pushIfNotExist(link.target.id);
              links.push(true);
            } else if (objRef.selected.includes(link.target.id)) {
              nodes.pushIfNotExist(link.source.id);
              links.push(true);
            } else {
              links.push(false);
            }
          });
          
          this.link
            .classed("selected", (d, i) => links[i])
            .classed("faded", (d, i) => !links[i]);
            
          this.node
            .classed("selected", d => nodes.includes(d.id))
            .classed("faded", d => !nodes.includes(d.id));

          nodes = null;
          links = null;
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
    link_selector: {
      get() { return this.controls.link_selector },
      set(link_selector) {
        this.$store.state.session.controls.link_selector = link_selector;
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
      "controls", "highlight", "selected", "focused",
      "clusters", "tsne", "index", "new_docs"]),
    ...mapState("userData", ["corpus"]),
    ...mapGetters("session", ["nodes", "links", "index_size"])
	},
	mounted() {
		let objRef = this;
		// SIMULATION ENGINE
		this.simulation = 	d3.forceSimulation()
			.force('link', 		d3.forceLink())
			.force("charge", 	d3.forceManyBody())
			.force("center", 	d3.forceCenter())
			.force("forceX",	d3.forceX())
			.force("forceY",	d3.forceY())
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
		this.svg = d3.select("#graphViewCanvas")
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("viewBox", [0, 0, this.width, this.height])
			.call(d3.zoom()
				.scaleExtent([0.1, 8])
				.on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}));

		this.canvas = this.svg.append("g");

		// 	LINKS
		this.link = this.canvas.append("g")
			.attr("class", "link")
			.selectAll("line");

		// 	NODES
		this.node = this.canvas.append("g")
			.attr("class", "node")
			.selectAll("circle");

    this.tooltip = d3.select('body')
      .append('div')
      .attr('id', 'node-tooltip');
		
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
    callSilhouette() {
      let emb = this.node.data().map(d => [d.x, d.y]),
          labels = this.clusters.labels;

      return ((emb && labels) ? silhouette(emb, labels) : 0.0).toFixed(4);
    },
		parameterState(value, min, max) {
			return (value > max) || (value < min) ? false : null;
		},
		updateLayout() {
			let objRef = this,
          _links = this.links,
          _nodes = this.nodes,
          _projection = (this.controls.projection == "DAG");

			// NODES
			this.node = this.node.data(_nodes).join("circle")
				.attr("r", 4)
				.attr("cx", d => d.x)
				.attr("cy", d => d.y)
				.classed("selected", d =>
					objRef.selected.includes(d.id))
        .classed("new_doc", d =>
					objRef.new_docs.includes(d.id))
				.attr("fill", (d, i) => {
					let _label = objRef.clusters.labels[i];
					return objRef.clusters.colors[_label];})
				.on("click", function(e, d) {
          // TODO FIX selection
          let index = objRef.selected.indexOf(d.id);
          if(e.ctrlKey) {
            objRef.updateSelected(d.id);
          } else {
            objRef.setSelected( index == -1 ? [d.id] : [] );
            objRef.setFocused(  index == -1 ? d.id : null);
          }
					
					let _ref = d3.select(this);
					_ref.classed("selected", !_ref.classed("selected"));
				})
        .on("mouseover", () => 
          objRef.tooltip.transition()
            .duration(500)
            .style("visibility", "visible"))
        .on("mousemove", (event, node) => {
          const doc = objRef.corpus.find(doc => doc.id == node.id);
          const index = objRef.index.indexOf(doc.id),
                label = objRef.clusters.labels[index],
                color = objRef.clusters.colors[label];

          let tooltip_html =
            `<strong style="color:${color};">${node.name}</strong><br/>` +
            `<br/>`;

          Object.keys(doc.term_frequency)
            .sort((a, b) => doc.term_frequency[`${b}`] - doc.term_frequency[`${a}`])
            .slice(0,5)
            .forEach((term) => tooltip_html += `${term}<br/>`);

          objRef.tooltip	
            .html(tooltip_html)
              .style("border", `2px solid ${color}`)
              .style("left", (event.pageX) + "px")		
              .style("top", (event.pageY - 28) + "px");	
          })					
        .on("mouseout", () =>
          objRef.tooltip.transition()
            .duration(500)
            .style("visibility", "hidden"))
				.call(d3.drag()
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

			// LINKS
			this.link = this.link.data(_links).join("line");

			// SIMULATION FORCES
			this.simulation
				.nodes(_nodes)
				.force("link")
          .id(d => d.id)
          .links(_links);

			this.link.append("title").text(d => `${d.source.name} → ${d.target.name}`);

			if(!_projection) {
				let _emb = this.tsne;

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

        _emb = null;
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

      _links = null;
      _nodes = null;
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
    ...mapMutations("session", ["updateSelected", "setSelected", "setFocused"]),
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
  line
    stroke: #999999
    stroke-opacity: 1.0
    fill: none
    &.selected
      stroke: #000000
      opacity: 1.0
    &.faded
      stroke: #999999
      opacity: 0.1

.node
  circle
    stroke-width: 0.5px
    stroke: #999999
    opacity: 1.0
    pointer-events: all
    &.selected
      stroke-width: 0.5px
      stroke: #000000
      opacity: 1.0
    &.faded
      stroke-width: 0.5px
      stroke: #999999
      opacity: 0.3
    &.new_doc
      stroke-width: 1px
      stroke: lime
      opacity: 1.0

#projectionSwitcher
	margin: 5px 0 5px 5px
  height: 20px

#node-tooltip
  padding: 1px
  font-size: smaller
  position: absolute
  opacity: 0.8
  max-width: 150px
  background: #f7f7f7
  text-align: center
  border-radius: 5px
  pointer-events: none
  white-space: normal
  word-wrap: break-word
  z-index: 10
  visibility: hidden
</style>