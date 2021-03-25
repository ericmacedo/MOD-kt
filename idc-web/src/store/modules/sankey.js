const state = {
  graph: {
    sessions: [],
    nodes: [],
    links: [],
    index: []
  },
  selection: {
    node: [],
    link: [],
    session: [],
    index: [],
    document: null
  }
};

const getters = {};

const actions = {};

const mutations = {
  setGraph (state, {sessions, nodes, links, index}) {
    state.graph.sessions = sessions;
    state.graph.nodes = nodes;
    state.graph.links = links;
    state.graph.index = index;
  },
  setSessionSelection (state, sessions) {
    state.selection.sessions = sessions;
  },
  setNodeSelection (state, nodes) {
    state.selection.node = nodes;
  },
  setLinkSelection (state, link) {
    state.selection.link = link;
  },
  setIndexSelection (state, index) {
    state.selection.index = index;
  },
  setDocumentSelection (state, documents) {
    state.selection.document = documents;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}