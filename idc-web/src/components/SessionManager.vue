<template>
<div class="session-manager h-100 w-100">
  <Promised :promise="sankeyData">
    <template v-slot:pending>
      <b-col id="Spinner" col>
        <b-spinner variant="primary" label="Spinning"></b-spinner>
      </b-col>
    </template>
    <template v-slot:default>
      <b-container fluid>
        <b-row>
          <b-col cols="12" sm="12" md="9" lg="9">
            <svg id="sankey"></svg>
          </b-col>
          <b-col cols="12" sm="12" md="3" lg="3">
            
          </b-col>
        </b-row>
      </b-container>
    </template>
    <template v-slot:rejected>
      <p>oops, something went wrong!</p>
    </template>
  </Promised>
</div>
</template>

<script>
// import * as d3 from "d3";
// import * as sankey from "d3-sankey";

export default {
  name: "SessionManager",
  data() {
    return {
      sankeyData: undefined,
      canvas: undefined,
      node: undefined,
      link: undefined,
      height: 600,
      width: 900,
      dataGraph: {
        nodes: [
          {id: "1", name: "node1", session: 1},
          {id: "2", name: "node2", session: 1},
          {id: "3", name: "node3", session: 1},
          {id: "4", name: "node4", session: 2},
          {id: "5", name: "node5", session: 2}
        ],
        links: [
          {source: "1", target: "4"},
          {source: "3", target: "5"}
        ],
      },
      sankeyGraph: {}
    }
  },
  mounted() {
    let objRef = this;
    console.log(objRef);

    // // CANVAS
		// this.canvas = d3.select("#graphViewCanvas")
		// 	.attr("width", this.width)
		// 	.attr("height", this.height)
		// 	.attr("viewBox", [0, 0, this.width, this.height])
		// 	.call(d3.zoom()
		// 		.scaleExtent([0.1, 8])
		// 		.on("zoom", (e) => {objRef.canvas.attr("transform", e.transform)}))
		// 	.append("g");

    // this.sankey = d3.sankey()
    //   .nodeId(d => `${d.session}_${d.name}`)
    //   .nodeAlign(d3[`sankey${align[0].toUpperCase()}${align.slice(1)}`])
    //   .nodeSort(inputOrder ? null : undefined)
    //   .nodeWidth(15)
    //   .nodePadding(10)
    //   .extent([[1, 5], [this.width, this.height]]);

    // this.sankeyGraph = this.sankey(this.graph);

    // this.node = this.canvas.append("g")
    //   .attr("stroke", "#000")
    //   .selectAll("rect")
    //   .data(this.sankeyGraph.nodes).join("rect")
    //   .attr("x", d => d.x0)
    //   .attr("y", d => d.y0)
    //   .attr("height", d => d.y1 - d.y0)
    //   .attr("width", d => d.x1 - d.x0)
    //   .attr("fill", color)
    //   .append("title").text(d => d.name);

  //   this.link = this.canvas.append("g")
  //     .attr("fill", "none")
  //     .attr("stroke-opacity", 0.5)
  //     .selectAll("g")
  //     .data(this.sankeyGraph.links).join("g")
  //     .style("mix-blend-mode", "multiply");
  //   this.link.append("title").text(d => `${d.source.name} → ${d.target.name}`);

  //   this.link.append("path")
  //     .attr("d", d3.sankeyLinkHorizontal())
  //     .attr("stroke", d => edgeColor === "none" ? "#aaa"
  //         : edgeColor === "path" ? d.uid 
  //         : edgeColor === "input" ? color(d.source) 
  //         : color(d.target))
  //     .attr("stroke-width", d => Math.max(1, d.width));
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass" scoped></style>