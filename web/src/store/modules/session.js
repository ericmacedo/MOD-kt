const state = {
  id: undefined,
  name: "Default",
  new_docs: [],
  notes: "",
  index: [],
  graph: { nodes: [], distance: [], neighborhood: [] },
  tsne: [],
  clusters: {
    cluster_k: undefined,
    cluster_names: [],
    colors: [],
    cluster_docs: [],
    cluster_words: [],
    labels: []
  },
  controls: {
    projection: undefined,
    tsne: { perplexity: undefined },
    link_selector: "Distance fn",
    distance: undefined,
    n_neighbors: undefined,
    linkDistance: undefined,
    charge: undefined
  },
  date: undefined,
  selected: [],
  focused: undefined,
  highlight: undefined,
  word_similarity: {
    query: [],
    most_similar: []
  }
};

const mutations = {
  setId(state, id) {
    state.id = id;
  },
  setName(state, name) {
    state.name = name;
  },
  setNotes(state, notes) {
    state.notes = notes;
  },
  setNewDocs(state, docs) {
    state.new_docs = docs;
  },
  setIndex(state, index) {
    state.index = index;
  },
  setGraph(state, {nodes, distance, neighborhood}) {
    state.graph.nodes = nodes;
    state.graph.distance = distance;
    state.graph.neighborhood = neighborhood;
  },
  setLinkSelector(state, link_selector) {
    state.controls.link_selector = link_selector;
  },
  setTsne(state, tsne) {
    state.tsne = tsne;
  },
  setClusters(state, {
    cluster_k, cluster_names,
    colors, cluster_docs, labels,
    cluster_words
  }) {
    state.clusters.cluster_k = cluster_k;
    state.clusters.cluster_names = cluster_names;
    state.clusters.colors = colors;
    state.clusters.cluster_docs = cluster_docs;
    state.clusters.cluster_words = cluster_words;
    state.clusters.labels = labels;
  },
  updateClusters(state, cluster) {
    if (cluster.index == state.clusters.cluster_k) {
      ++state.clusters.cluster_k;
      
      state.clusters.colors.push(cluster.color);
      state.clusters.cluster_names.push(cluster.cluster_name);
      state.clusters.cluster_words.push(cluster.words);
    } else {
      state.clusters.colors[cluster.index] = cluster.color;
      state.clusters.cluster_names[cluster.index] = cluster.cluster_name;
      state.clusters.cluster_words[cluster.index] = cluster.words;
    }
  },
  deleteCluster(state, index) {
    --state.clusters.cluster_k;
    state.clusters.cluster_names.pop(index);
    state.clusters.colors.pop(index);
    state.clusters.cluster_words.pop(index);
  },
  setControls(state, {
    projection, tsne, distance,
    n_neighbors, linkDistance,
    charge, link_selector
  }) {
    state.controls.projection = projection;
    state.controls.tsne = { perplexity: tsne.perplexity };
    state.controls.link_selector = link_selector;
    state.controls.distance = distance;
    state.controls.n_neighbors = n_neighbors;
    state.controls.linkDistance = linkDistance;
    state.controls.charge = charge;
  },
  setDate(state, date) {
    state.date = date;
  },
  setSelected(state, selected) {
    state.selected = selected;
  },
  updateSelected(state, id) {
    let index = state.selected.indexOf(id);
      
    if (index == -1) {
      state.selected.push(id);
      state.focused = id;
    } else {
      state.selected.pop(index);
      state.focused = null;
    }
  },
  setHighlight(state, cluster_name) {
    state.highlight = cluster_name;
  },
  updateHighlight(state, cluster_name) {
    state.highlight = (state.highlight == cluster_name) ? "" : cluster_name;
  },
  setFocused(state, id) {
    state.focused = id;
  },
  setWordSimilarity(state, {query, most_similar}) {
    state.word_similarity.query = query;
    state.word_similarity.most_similar = most_similar;
  }
};

const getters = {
  session(state) {
    return {
      id:               state.id,
      name:             state.name,
      notes:            state.notes,
      index:            state.index,
      graph:            state.graph,
      tsne:             state.tsne,
      clusters:         state.clusters,
      controls:         state.controls,
      date:             state.date,
      selected:         state.selected,
      focused:          state.focused,
      highlight:        state.highlight,
      word_similarity:  state.word_similarity
    }
  },
  nodes({graph}) {
    return graph.nodes;
  },
  links({controls, graph}) {
    if (controls.link_selector == "Neighborhood") {
      return graph.neighborhood.filter((link) => 
        link.value <= controls.n_neighbors
      );
    } else {
      return graph.distance.filter((link) => 
        link.value <= controls.distance);
    }
  },
  index_size({index}) {
    return index.length;
  },
};

const actions = {};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};