<template>
<div class="session-manager h-100 w-100">
  <Promised :promise="sankeyData">
    <template v-slot:pending>
      <b-col id="Spinner" col>
        <b-spinner variant="primary" label="Spinning"></b-spinner>
      </b-col>
    </template>
    <template v-slot="data">
      <b-container fluid>
        <b-row>
          <b-col cols="12" sm="12" md="9" lg="9">
            <sankey-graph
              :graphData="data"
              :width="width"
              :height="height"></sankey-graph>
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
import { mapActions, mapState } from "vuex";
import SankeyGraph from './session_manager/SankeyGraph';

export default {
  name: "SessionManager",
  components: {
    "sankey-graph": SankeyGraph
  },
  data() {
    return {
      sankeyData: undefined,
      height: 600,
      width: 900
    }
  },
  computed:{
    ...mapState({
      userId: state => state.userData.userId
    })
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
<style lang="sass" scoped></style>