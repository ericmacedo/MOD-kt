<template>
<div class="session-manager h-100 w-100">
  <Promised :promise="sankeyData">
    <template v-slot:pending>
      <div class="h-100 text-center">
        <b-spinner
          class="m-5"
          variant="primary"></b-spinner>
      </div>
    </template>
    <template v-slot:default>
      <b-container fluid>
        <b-row>
          <b-col cols="12" sm="12" md="9" lg="9">
            <sankey-graph
              id="sankeyGraph"
              :width="width"
              :height="height"></sankey-graph>
          </b-col>
          <b-col cols="12" sm="12" md="3" lg="3">
            <cluster-history
              ref="corpusView"></cluster-history>
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
import { mapActions, mapState } from "vuex";
import ClusterHistory from './session_manager/ClusterHistory';
import SankeyGraph from './session_manager/SankeyGraph';

export default {
  name: "SessionManager",
  components: {
    "sankey-graph": SankeyGraph,
    "cluster-history": ClusterHistory
  },
  data() {
    return {
      sankeyData: undefined,
      height: 600,
      width: 900
    }
  },
  computed:{
    ...mapState("userData", ["userId"])
  },
  mounted() {
    this.sankeyData = this.requestSankeyGraph(this.userId);
  },
  methods: {
    ...mapActions(["requestSankeyGraph"])
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
#sankeyGraph
  position: -webkit-sticky
  position: sticky
  top: 60px
  left: 10px
</style>