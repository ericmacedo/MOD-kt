<template>
  <div id="sankeyGraph">
    <svg id="graphViewCanvas"></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import * as sankey from "d3-sankey";
import * as cloud from "d3-cloud";
import { mapState, mapMutations } from 'vuex';

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
      wordClouds: {}
    }
  },
  watch: {
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
    },
    'selection.document' : function(value) {
      if(value != null) {
        this.session
          .classed("faded", true)
          .classed("selected", false);
        this.node
          .classed("selected", d => d.docs.includes(value))
          .classed("faded", d => !d.docs.includes(value));
        this.link
          .classed("selected", d => 
            d.source.docs.includes(value) && d.target.docs.includes(value))
          .classed("faded", d => 
            !d.source.docs.includes(value) || !d.target.docs.includes(value));
      } else {
        const _node = this.selection.node,
              _link = this.selection.link,
              _session = this.selection.session;
        
        this.node
          .classed("selected",
            (_node.length == 0) ? false : d => _node.includes(d.id))
          .classed("faded",
            (_node.length == 0) ? false : d => !_node.includes(d.id));
        this.link
          .classed("selected",
            (_link.length == 0) ? false : d => _link.includes(d.id))
          .classed("faded",
            (_link.length == 0) ? false : d => !_link.includes(d.id));
        this.session
          .classed("selected",
            (_session.length == 0) ? false : d => _session.includes(d.id))
          .classed("faded",
            (_session.length == 0) ? false : d => !_session.includes(d.id));
      }
    },
  },
  computed: {
    selected_ids(){
      const _nodes = this.graphData.nodes;
      const _clusters = [...new Set(
        this.selection.node.concat(
          this.graphData.links.filter(
            d => this.selection.link.includes(d.id)
          ).flatMap(d => [d.source.id, d.target.id]))
      )];

      return [...new Set(
        _clusters.map(
          cluster_id => _nodes.find(d => d.id == cluster_id).docs
        ).flat(2)
      )];
    },
    ...mapState("userData", ["corpus"]),
    ...mapState("sankey", ["selection"]),
    ...mapState({
      graphData: ({sankey}) => sankey.graph
    })
  },
  mounted() {
    let objRef = this;
    const width = 200,
          height = 200;
    var color = d3.scaleSequential(d3.interpolateRainbow);

    // // CANVAS
    this.canvas = d3.select("#graphViewCanvas")
      .attr("width", "100%")
			.attr("height", "100%")
			.attr("viewBox", [0, 0, this.width, this.height])
      .attr('preserveAspectRatio','xMinYMin')
      .call(d3.zoom()
        .scaleExtent([0.1, 8])
        .on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}))
      .append("g");

    console.log(this.graphData);

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

    console.log(this.sankeyGraph);

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
      .on("click", this.clickNode)
      .on("mouseover", this.hover)
      .on("mousemove", this.hoverMove)
      .on("mouseout", this.hoverOut);

    this.node.data().forEach(node => {
      let words = objRef.words(node.docs);
      var xScale = d3.scaleLinear()
        .domain([0, d3.max(words, d => d.size)])
        .range([10,100]);
      
      words = words.map(d => {
        return {
          text: d.text,
          size: xScale(d.size),
          color: color(Math.random())}
      });

      cloud()
        .size([width - 10, height - 10])
        .words(words)
        .fontSize(d => d.size)
        .padding(5)
        .rotate(0)
        .spiral("rectangular")
        .font("Impact")
        .on("end", (wordCloud) => {
          objRef.wordClouds[node.id] = d3.select("#sankeyGraph").append("svg")
            .attr('id', `wordCloud-${node.id}`)
            .classed("wordCloud-popover", true)
            .attr("width", width)
            .attr("height", height + 20)
            .style("visibility", "hidden");

          objRef.wordClouds[node.id]
            .append("text")
            .style("font-size", "18px")
            .style("font-weight", "bold")
            .attr("text-anchor", "middle")
            .attr("transform", `translate(${width/2}, 15)`)
            .attr("fill", node.color)
            .text(`${node.name}`)

          objRef.wordClouds[node.id]
            .append("rect")
            .attr("width", width - 10)
            .attr("height", height - 10)
            .attr("fill", "#FFFFFF")
            .attr("rx", "20")
            .attr("ry", "20")
            .attr("transform", "translate(5, 20)")
            .style("stroke", `${node.color}`)
            .style("stroke-width", "5px")

          objRef.wordClouds[node.id]
            .append("g")
            .attr("transform", `translate(${width/2}, ${height/2 + 20})`)
            .selectAll("text")
            .data(wordCloud).join("text")
              .style("font-size", d => `${d.size}px`)
              .style("font-family", "Impact")
              .attr("text-anchor", "middle")
              .attr("transform", d => `translate(${d.x}, ${d.y + 10}) rotate(${d.rotate})`)
              .attr("fill", d => d.color)
              .text(d => d.text);
        }).start();
    });

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
      .on("click", this.clickLink)
      .on("mouseover", this.hover)
      .on("mousemove", this.hoverMove)
      .on("mouseout", this.hoverOut);

    this.link.data().forEach(link => {
      // TODO THIS
      let words = objRef.words([
        ...new Set(link.source.docs.concat(link.target.docs))
      ]);
      var xScale = d3.scaleLinear()
        .domain([0, d3.max(words, d => d.size)])
        .range([10,100]);
      
      words = words.map(d => {
        return {
          text: d.text,
          size: xScale(d.size),
          color: color(Math.random())}
      });

      cloud()
        .size([width - 10, height - 10])
        .words(words)
        .fontSize(d => d.size)
        .padding(5)
        .rotate(0)
        .spiral("rectangular")
        .font("Impact")
        .on("end", (wordCloud) => {
          objRef.wordClouds[link.id] = d3.select("#sankeyGraph").append("svg")
            .attr('id', `wordCloud-${link.id}`)
            .classed("wordCloud-popover", true)
            .attr("width", width)
            .attr("height", height + 20);

          objRef.wordClouds[link.id]
            .append("text")
            .style("font-size", "18px")
            .style("font-weight", "bold")
            .attr("text-anchor", "middle")
            .attr("transform", `translate(${width/2}, 15)`)
            .attr("fill", `url(#gradient_${link.source.id}_${link.target.id})`)
            .text(`${link.source.name} → ${link.target.name}`)

          objRef.wordClouds[link.id]
            .append("rect")
            .attr("width", width - 10)
            .attr("height", height - 10)
            .attr("fill", "#FFFFFF")
            .attr("rx", "20")
            .attr("ry", "20")
            .attr("transform", "translate(5, 20)")
            .attr("stroke", `url(#gradient_${link.source.id}_${link.target.id})`)
            .style("stroke-width", "5px");
          
          objRef.wordClouds[link.id]
            .append("g")
            .attr("transform", `translate(${width/2}, ${height/2 + 20})`)
            .selectAll("text")
            .data(wordCloud).join("text")
              .style("font-size", d => `${d.size}px`)
              .style("font-family", "Impact")
              .attr("text-anchor", "middle")
              .attr("transform", d => `translate(${d.x}, ${d.y}) rotate(${d.rotate})`)
              .attr("fill", d => d.color)
              .text(d => d.text);
        }).start();
    });

    // SESSIONS
    this.session = this.canvas.append("g")
      .classed("sessions", true)
      .selectAll("g")
      .data(this.graphData.sessions).join("g")
      .classed("session", true)
      .attr("transform", function(d, i) {
        return `translate(${(objRef.width / (objRef.graphData.sessions.length - 1) - 5) * i}, 0)`;
      })
      .on("click", this.clickSession);

    this.session.append("text")
      .classed("session-label", true)
      .attr("transform", "translate(5, -40)")
      .text(d => d.name);
    
    this.session.append("text")
      .classed("session-label", true)
      .attr("transform", "translate(5, -20)")
      .text(d => d.size);
  },
  methods: {
    words(docs) {
      let vocab  = {},
          docs_tf = this.corpus.filter(
            doc => docs.includes(doc.id)
          ).map(doc => doc?.term_frequency);

      for (let doc of docs_tf) {
        for (let word of Object.keys(doc)) {
          vocab[word] = doc[word] + (word in vocab ? vocab[word] : 0);
        }
      }
      return Object.keys(vocab).map(word => {
        return {text: word, size: vocab[word]}})
        .sort((a, b) => b.size - a.size)
        .slice(0, 50);
    },
    hover(event, element) {
      this.wordClouds[element.id]
        .classed("visible", true)
        .style("left", `${event.pageX}px`)
        .style("top", `${event.pageY-50}px`);
    },
    hoverMove (event, element) {
      this.wordClouds[element.id]
        .style("left", `${event.pageX}px`)
        .style("top", `${event.pageY-50}px`);	
    },
    hoverOut(event, element) {
      this.wordClouds[element.id]
        .classed("visible", false);
    },
    // NODE METHODS
    clickNode(event, node) {
      event.stopPropagation();
      if(event.ctrlKey) {
        this.selection.node.pushToggle(node.id);
      } else {
        this.selection.node = this.selection.node.includes(node.id) ? [] : [node.id];
      }

      this.setIndexSelection(this.selected_ids);
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
          this.selection.link.splice(index, 1);
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

      this.setIndexSelection(this.selected_ids);
    },
    // SESSION EVENTS
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
        this.selection.session.splice(0, this.selection.session.length);
        if (index != -1) {
          this.selection.link.splice(0, this.selection.link.length);
          this.selection.node.splice(0, this.selection.node.length);
        } else {
          this.selection.session.pushIfNotExist(session.id);
          session.clusters.forEach(d => objRef.selection.node.pushIfNotExist(d));
        }
      }
      this.setIndexSelection(this.selected_ids);
    },
    ...mapMutations("sankey", ["setIndexSelection"])
  },
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
      fill: #000000
      font-size: 18px
      text-anchor: middle
      cursor: pointer
    .session-counter
      font-weight: normal
      fill: #313131
      font-size: 14px
      text-anchor: middle
      cursor: pointer
    &.faded
      opacity: $session-faded
    &.selected
      opacity: $session-selected
      .session-label
        font-weight: bold

.wordCloud-popover
  position: absolute
  opacity: 0.8
  text-align: center
  pointer-events: none
  z-index: 10
  visibility: hidden
  .visible
    visibility: visible !important
</style>
