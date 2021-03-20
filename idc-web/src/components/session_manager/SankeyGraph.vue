<template>
  <div>
    <svg id="graphViewCanvas"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import * as sankey from "d3-sankey";

Array.prototype.pushToggle = function(item) { 
  const index = this.indexOf(item);
  if (index == -1) {
    this.push(item);
  } else {
    this.pop(index);
  }
};

Array.prototype.pushIfNotExist = function(item) { 
  if (!this.includes(item)) {
    this.push(item);
  }
};

Array.prototype.popIfExist = function(item) { 
  const index = this.indexOf(item);
  if (index != -1) {
    this.pop(index);
  }
};

export default{
  name: "SankeyGraph",
  props:{
    width: {
      required: true,
      type: Number
    },
    height: {
      required: true,
      type: Number
    },
    graphData: {
      required: true,
      type:Object
    }
  },
  data() {
    return {
      canvas: undefined,
      sankeyGraph: undefined,
      graph: undefined,
      node: undefined,
      link: undefined,
      gradients: undefined,
      session: undefined,
      selection: {
        session: [],
        node: [],
        link: []
      }
    }
  },
  watch:{
    'selection.node': function(value) {
      this.node
        .classed("selected",
          (value.length == 0) ? false : d => value.includes(d.id))
        .classed("faded",
          (value.length == 0) ? false : d => !value.includes(d.id));
    },
    'selection.link': function(value) {
      this.link
        .classed("selected",
          (value.length == 0) ? false : d => value.includes(d.id))
        .classed("faded",
          (value.length == 0) ? false : d => !value.includes(d.id));
    },
    'selection.session': function(value) {
      this.session
        .classed("faded",
          (value.length == 0) ? false : d => !value.includes(d.id))
        .classed("selected",
          (value.length == 0) ? false : d => value.includes(d.id));
    }
  },
  mounted() {
    let objRef = this;

    // // CANVAS
    this.canvas = d3.select("#graphViewCanvas")
      .attr("width", this.width)
      .attr("height", this.height)
      .attr("viewBox", [0, 0, this.width, this.height])
      .call(d3.zoom()
        .scaleExtent([0.1, 8])
        .on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}))
      .append("g");

    // GRAPH
    this.sankeyGraph = sankey.sankey()
      .size([this.width, this.height])
      .nodeId(d => d.id)
      .nodeWidth(15)
      .nodePadding(10)
      .nodeSort((node1, node2) => node1.order < node2.order ? -1 : 1)
      .nodeAlign(node => 
        objRef.graphData.sessions
          .map(d => d.id)
          .indexOf(node.session))
      .extent([[1, 5], [this.width, this.height]]);
    this.graph = this.sankeyGraph({
      nodes: this.graphData.nodes,
      links: this.graphData.links
    });

    // NODES
    this.node = this.canvas.append("g")
      .classed("nodes", true)
      .selectAll("rect")
      .data(this.graph.nodes).join("rect")
      .classed("node", true)
      .attr("x", d => d.x0)
      .attr("y", d => d.y0)
      .attr("height", d => d.y1 - d.y0)
      .attr("width", d => d.x1 - d.x0)
      .attr("fill", d => d.color)
      .on("click", this.clickNode);

    // console.log(this.gra)
    // LINKS
    this.link = this.canvas.append("g")
      .classed("links", true)
      .selectAll("g")
      .data(this.graph.links).join("g")
      .classed("link", true)
      .classed("faded", false)
      .classed("selected", false);

    // GRADIENTS
    this.gradients = this.link
      .append("linearGradient")
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", d => d.source.x1)
      .attr("x2", d => d.target.x0)
      .attr("id", d => `gradient_${d.source.id}_${d.target.id}`);

    this.gradients.append("stop")
      .attr("offset", 0.0)
      .attr("stop-color", d => d.source.color);
    this.gradients.append("stop")
      .attr("offset", 1.0)
      .attr("stop-color", d => d.target.color);

    this.link.append("path")
      .attr("d", sankey.sankeyLinkHorizontal())
      .attr("fill", "none")
      .attr("stroke", d => `url(#gradient_${d.source.id}_${d.target.id})`)
      .attr("stroke-width", d => Math.max(1.0, d.width))
      .on("click", this.clickLink);

    this.link.append("title").text(d => `${d.source.name} → ${d.target.name}`);

    // SESSIONS
    this.session = this.canvas.append("g")
      .classed("sessions", true)
      .selectAll("g")
      .data(this.graphData.sessions).join("g")
      .classed("session", true)
      .attr("transform", function(d, i) {
        return `translate(${(objRef.width / (objRef.graphData.sessions.length - 1) - 5) * i}, 0)`;
      });

    this.session.append("text")
      .classed("session-label", true)
      .attr("transform", "translate(5,-20)")
      .text(d => d.name)
      .on("click", this.clickSession);
  },
  methods: {
    // NODE METHODS
    clickNode(event, node) {
      event.stopPropagation();
      if(event.ctrlKey) {
        this.selection.node.pushToggle(node.id);
      } else {
        this.selection.node = this.selection.node.includes(node.id) ? [] : [node.id];
      }
    },
    // LINK METHODS
    clickLink(event, link) {
      event.stopPropagation();
      let objRef = this;
      const index = this.selection.link.indexOf(link.id);

      if(index == -1) {
        if(!event.ctrlKey) {
          this.selection.link.splice(0, this.selection.link.length);
        }
        this.selection.link.push(link.id);
        this.selection.node.pushIfNotExist(link.source.id);
        this.selection.node.pushIfNotExist(link.target.id);
      } else {
        if(event.ctrlKey) {
          this.selection.link.pop(index);
          this.selection.node.popIfExist(link.source.id);
          this.selection.node.popIfExist(link.target.id);
        } else {
          this.selection.link.splice(0, this.selection.link.length);
          this.selection.node.splice(0, this.selection.node.length);
          if(this.selection.link.length > 1) {
            this.selection.link.push(link.id);
            this.selection.node.push(link.source.id);
            this.selection.node.push(link.target.id);
          }
        }
      }
      this.graphData.links
        .filter(d => objRef.selection.link.includes(d.id))
        .forEach(d => {
          objRef.selection.node.pushIfNotExist(d.source.id);
          objRef.selection.node.pushIfNotExist(d.target.id);
        });
    },
    clickSession(event, session) {
      event.stopPropagation();
      const index = this.selection.session.indexOf(session.id);

      let objRef = this;
      if(event.ctrlKey) {
        this.selection.session.pushToggle(session.id);
        session.clusters.forEach(d => objRef.selection.node[
          index == -1 ? "pushIfNotExist" : "popIfExist"
        ](d));
      } else {
        this.selection.session = index != -1  ? [] : [session.id];
        this.selection.link.splice(0, this.selection.link.length);
        this.selection.node.splice(0, this.selection.node.length);

        session.clusters.forEach(d => objRef.selection.node.pushIfNotExist(d));
      }
      console.log(this.selection.session);
    }
  }
}
</script>

<style lang="sass">
$node: 0.8
$node-faded: 0.3
$node-selected: 1.0

$link: 0.5
$link-faded: 0.2
$link-selected: 0.8

$session: 0.8
$session-faded: 0.3
$session-selected: 1.0

.links
  stroke-opacity: 0.5
  .link
    -webkit-transition: opacity .5s ease-in-out
    -moz-transition: opacity .5s ease-in-out
    -ms-transition: opacity .5s ease-in-out
    -o-transition: opacity .5s ease-in-out
    transition: opacity .5s ease-in-out
    mix-blend-mode: multiply
    opacity: $link
    &:hover
      stroke: #171717
      stroke-width: 1px
    &.faded
      opacity: $link-faded
    &.selected
      opacity: $link-selected

.nodes
  .node
    opacity: $node
    -webkit-transition: opacity .5s ease-in-out
    -moz-transition: opacity .5s ease-in-out
    -ms-transition: opacity .5s ease-in-out
    -o-transition: opacity .5s ease-in-out
    transition: opacity .5s ease-in-out
    &:hover
      stroke: #171717
      stroke-width: 2px
    &.faded
      opacity: $node-faded
    &.selected
      opacity: $node-selected

.sessions
  .session
    opacity: $session
    -webkit-transition: opacity .5s ease-in-out
    -moz-transition: opacity .5s ease-in-out
    -ms-transition: opacity .5s ease-in-out
    -o-transition: opacity .5s ease-in-out
    transition: opacity .5s ease-in-out
    .session-label
      font-weight: normal
      color: #000
      font-size: 18px
      text-anchor: middle
      cursor: pointer
    &.faded
      opacity: $session-faded
    &.selected
      opacity: $session-selected
      .session-label
        font-weight: bold
</style>
