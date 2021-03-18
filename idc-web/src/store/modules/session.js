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
  setGraph({graph}, {nodes, distance, neighborhood}) {
    graph.nodes = nodes;
    graph.distance = distance;
    graph.neighborhood = neighborhood;
  },
  setLinkSelector({controls}, link_selector) {
    controls.link_selector = link_selector;
  },
  setTsne(state, tsne) {
    state.tsne = tsne;
  },
  setClusters({clusters}, {
                        cluster_k, cluster_names,
                        colors, cluster_docs, labels,
                        cluster_words
                      }) {
    clusters.cluster_k      = cluster_k;
    clusters.cluster_names  = cluster_names;
    clusters.colors         = colors;
    clusters.cluster_docs   = cluster_docs;
    clusters.cluster_words  = cluster_words;
    clusters.labels         = labels;
  },
  updateClusters({clusters}, cluster) {
    if (cluster.index == clusters.cluster_k) {
      ++clusters.cluster_k;
      
      clusters.colors.push(cluster.color);
      clusters.cluster_names.push(cluster.cluster_name);
      clusters.cluster_words.push(cluster.words);
    } else {
      clusters.colors[cluster.index] = cluster.color;
      clusters.cluster_names[cluster.index] = cluster.cluster_name;
      clusters.cluster_words[cluster.index] = cluster.words;
    }
  },
  deleteCluster({clusters}, index) {
    --clusters.cluster_k;
    clusters.cluster_names.pop(index);
    clusters.colors.pop(index);
    clusters.cluster_words.pop(index);
  },
  setControls({controls}, {
                        projection, tsne, distance,
                        n_neighbors, linkDistance,
                        charge, link_selector
                      }) {
    controls.projection     = projection;
    controls.tsne           = { perplexity: tsne.perplexity };
    controls.link_selector  = link_selector;
    controls.distance       = distance;
    controls.n_neighbors    = n_neighbors;
    controls.linkDistance   = linkDistance;
    controls.charge         = charge;
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
  setFocused(state, focused) {
    state.focused = focused;
  },
  setWordSimilarity({word_similarity}, {query, most_similar}) {
    word_similarity.query         = query;
    word_similarity.most_similar  = most_similar;
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
  nodes(state) {
    return state.graph.nodes;
  },
  links(state) {
    if (state.controls.link_selector == "Neighborhood") {
      return state.graph.neighborhood.filter((link) => 
        link.value <= state.controls.n_neighbors
      );
    } else {
      return state.graph.distance.filter((link) => 
        link.value <= state.controls.distance);
    }
  },
  index_size(state) {
    return state.index.length;
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