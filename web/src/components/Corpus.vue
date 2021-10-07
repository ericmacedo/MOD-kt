<template>
  <div>
    <b-row>
      <b-col class="upload-wrapper" cols="12" sm="12" md="6" lg="6">
        <upload-component context="CORPUS"></upload-component>
      </b-col>

      <!-- TOOLBAR + TABLE -->
      <b-col id="tableCol" cols="12" sm="12" md="6" lg="6">
        <!-- TOOLBAR -->
        <b-button-toolbar id="corpusToolbar">
          <b-button-group size="sm" class="mx-1">
            <b-button disabled variant="outline-secondary">
              {{ corpus_size }}
            </b-button>
            <b-button @click="reloadTable">
              <font-awesome-icon :icon="['fas', 'sync']" />
            </b-button>
          </b-button-group>
          <b-button-group class="mx-1" size="sm">
            <b-button
              size="sm"
              :disabled="corpus_size == 0"
              @click="selectAllRows"
            >
              Select all
            </b-button>
            <b-button
              size="sm"
              @click="clearSelected"
              :disabled="table.selection.length == 0"
            >
              Unselect all
            </b-button>
            <b-button
              size="sm"
              variant="danger"
              :disabled="table.selection.length == 0"
              @click="callDeleteDocument"
            >
              <font-awesome-icon :icon="['fas', 'trash']" />
              Delete documents
            </b-button>
          </b-button-group>

          <b-button
            size="sm"
            class="mx-1"
            variant="info"
            v-b-modal.process-corpus-modal
            :disabled="corpus_size == 0 || processingCorpus"
          >
            <font-awesome-icon :icon="['fas', 'cogs']" />
            &nbsp; Process corpus
          </b-button>
        </b-button-toolbar>

        <!-- TABLE -->
        <b-table
          id="corpusTable"
          hover
          selectable
          show-empty
          :fields="table.fields"
          :items="corpus"
          select-mode="multi"
          responsive="sm"
          ref="corpusTable"
          @row-selected="onRowSelected"
        >
          <!-- IS SELECTED -->
          <template #cell(selected)="{ rowSelected }">
            <template v-if="rowSelected">
              <span aria-hidden="true">&check;</span>
              <span class="sr-only">Selected</span>
            </template>
            <template v-else>
              <span aria-hidden="true">&nbsp;</span>
              <span class="sr-only">Not selected</span>
            </template>
          </template>

          <!-- SHOW CONTENT -->
          <template #cell(show_details)="row">
            <b-button size="sm" @click="row.toggleDetails" class="mr-2">
              <font-awesome-icon
                :icon="['fas', row.detailsShowing ? 'eye-slash' : 'eye']"
              />
            </b-button>
          </template>

          <!-- DETAILS CARD -->
          <template #row-details="row">
            <b-card>
              <b-row class="mb-2">
                <p>{{ row.item.content }}</p>
              </b-row>
              <b-button size="sm" @click="row.toggleDetails"
                >Hide Conent</b-button
              >
            </b-card>
          </template>
        </b-table>
      </b-col>
    </b-row>
    <b-modal
      ref="process-corpus-modal"
      id="process-corpus-modal"
      size="lg"
      header-bg-variant="dark"
      header-text-variant="light"
      title="Process Corpus"
      centered
      hide-footer
      no-close-on-backdrop
      no-close-on-esc
    >
      <div class="d-block">
        <b-form inline class="stopwords_wrapper" size="sm">
          <label class="mr-sm-2" for="modal-stopwords-tags">Stopwords</label>
          <b-form-file
            size="sm"
            v-model="process_corpus.stopwordsFile"
            accept=".txt"
            placeholder="Upload a 'txt' file"
            browse-text="Browse"
            @input="addStopwords"
          >
            <font-awesome-icon :icon="['fas', 'file']" />
          </b-form-file>
          <b-input-group size="sm" label="Stopwords" class="w-100">
            <b-form-tags
              size="sm"
              class="mb-2"
              id="modal-stopwords-tags"
              v-model="stopwords"
            >
              <template
                v-slot="{
                  tags,
                  inputAttrs,
                  inputHandlers,
                  tagVariant,
                  addTag,
                  removeTag,
                }"
              >
                <b-input-group class="mb-2">
                  <b-form-input
                    v-bind="inputAttrs"
                    v-on="inputHandlers"
                    placeholder="Press enter to add a stopword"
                    class="form-control"
                  ></b-form-input>
                  <b-input-group-append>
                    <b-button @click="addTag()" variant="primary">Add</b-button>
                    <b-button
                      size="sm"
                      title="Clear stopwords"
                      variant="outline-danger"
                      @click="stopwords = []"
                    >
                      <font-awesome-icon :icon="['fas', 'times']" />
                    </b-button>
                  </b-input-group-append>
                </b-input-group>
                <div class="d-inline-block" style="font-size: 1.5rem">
                  <b-form-tag
                    v-for="tag in tags"
                    @remove="removeTag(tag)"
                    :key="tag"
                    :title="tag"
                    :variant="tagVariant"
                    class="mr-1"
                    >{{ tag }}</b-form-tag
                  >
                </div>
              </template>
            </b-form-tags>
          </b-input-group>
        </b-form>
        <hr />
        <b-form target="_blank">
          <b-form-group
            label="Word model"
            label-for="modal-word-model"
            label-cols-sm="4"
            label-cols-lg="3"
            content-cols-sm
            content-cols-lg="7"
            description="Please, choose a word model for your corpus"
            @submit.stop.prevent
          >
            <b-form-radio-group
              id="modal-word-model"
              class="pt-2"
              v-model="process_corpus.selection.word"
              :options="process_corpus.models.word"
              required
            ></b-form-radio-group>
          </b-form-group>
          <hr />
          <b-form-group
            label="Document model"
            label-for="modal-document-model"
            label-cols-sm="4"
            label-cols-lg="3"
            content-cols-sm
            content-cols-lg="7"
            description="Please, choose a document model for your corpus"
            @submit.stop.prevent
          >
            <b-form-radio-group
              id="modal-document-model"
              class="pt-2"
              v-model="process_corpus.selection.document"
              :options="process_corpus.models.document"
              required
            ></b-form-radio-group>
          </b-form-group>
          <b-button
            block
            class="mt-2"
            variant="outline-primary"
            @click="callProcessCorpus"
          >
            <font-awesome-icon :icon="['fas', 'cogs']" />
            &nbsp; Process corpus
          </b-button>
        </b-form>
      </div>
    </b-modal>
    <b-modal
      ref="dashboard-redirect-modal"
      id="dashboard-redirect-modal"
      size="md"
      header-bg-variant="dark"
      header-text-variant="light"
      title="Corpus processed"
      centered
      hide-footer
    >
      <div class="d-block text-center">
        <h6>
          You corpus was processed succesfully, do you want to proceed to the
          <strong>Dashboard</strong> and start exploring you corpus?
        </h6>
      </div>
      <b-button
        class="mt-3"
        variant="outline-success"
        block
        @click="$bvModal.hide('dashboard-redirect-modal')"
        to="/dashboard"
      >
        <font-awesome-icon :icon="['fas', 'tachometer-alt']" />&nbsp; Yes, take
        me to the <strong>Dashboard</strong>!
      </b-button>
    </b-modal>
  </div>
</template>

<script>
import { mapGetters, mapState, mapActions } from "vuex";
import UploadComponent from "./UploadComponent";

export default {
  name: "Corpus",
  components: {
    "upload-component": UploadComponent,
  },
  data: function () {
    return {
      table: {
        fields: ["selected", "file_name", "uploaded_on", "show_details"],
        selection: [],
      },
      processingCorpus: false,
      process_corpus: {
        stopwordsFile: [],
        models: {
          document: ["BagOfWords", "Doc2Vec", "BERT"],
          word: ["BagOfWords", "Word2Vec", "FastText"],
        },
        selection: {
          document: undefined,
          word: undefined,
        },
      },
    };
  },
  computed: {
    all_selected: function () {
      return this.table.selection.length == this.corpus_size;
    },
    stopwords: {
      get() {
        return this.stop_words;
      },
      set(value) {
        this.$store.commit("userData/setStopwords", value);
      },
    },
    ...mapState("userData", ["corpus", "userId", "stop_words"]),
    ...mapGetters("userData", ["corpus_size"]),
  },
  methods: {
    makeToast(title, content, variant, id = null) {
      // Use a shorter name for this.$createElement
      const h = this.$createElement;
      // Create the message
      const vProgressToast = h("p", { class: ["mb-0"] }, [
        h("b-spinner", { props: { small: true } }),
        ` ${content}`,
      ]);
      this.$bvToast.toast(id ? vProgressToast : content, {
        id: id ? id : null,
        variant: variant,
        title: title,
        toaster: "b-toaster-bottom-right",
        solid: false,
        autoHideDelay: 5000,
        noAutoHide: id ? true : false,
        noCloseButton: id ? true : false,
        appendToast: true,
      });
    },
    get_userData() {
      let objRef = this;

      this.userData = this.getUserData(this.userId);

      this.userData
        .then(function () {
          objRef.makeToast(
            "Success", // title
            "User data reloaded", // content
            "success"
          ); // variant
        })
        .catch(function () {
          objRef.makeToast(
            "Oops, something went wrong!", // title
            "Try reloading the page", // content
            "danger"
          ); // variant
        });
    },
    reloadTable() {
      this.get_userData();
      this.table.selection = [];
    },
    onRowSelected: function (selection) {
      this.table.selection = selection;
    },
    selectAllRows: function () {
      this.$refs.corpusTable.selectAllRows();
    },
    clearSelected: function () {
      this.$refs.corpusTable.clearSelected();
    },
    callDeleteDocument: async function () {
      let objRef = this;

      const to_remove = this.table.selection.map((d) => d.id);

      this.deleteDocument({
        to_remove: to_remove,
        RESET_FLAG: this.all_selected,
      })
        .then(function () {
          objRef.makeToast(
            "Success!", // title
            "Files deleted successfully!", // content
            "success"
          ); // variant
        })
        .catch(function () {
          objRef.makeToast(
            "Oops, something went wrong!", // title
            "Try reloading the page", // content
            "danger"
          ); // variant
        });
    },
    callProcessCorpus: async function () {
      let objRef = this;

      this.makeToast(
        "Processing corpus", // title
        "Please wait...", // content
        "warning", // variant
        "process_corpus"
      ); // id
      this.processingCorpus = true;

      let settings = {
        document: this.process_corpus.selection.document,
        word: this.process_corpus.selection.word,
      };

      this.$bvModal.hide("process-corpus-modal");

      this.processCorpus(settings)
        .then(function () {
          objRef.get_userData(objRef.userId);
          objRef.$bvModal.show("dashboard-redirect-modal");
        })
        .catch(function () {
          objRef.makeToast(
            "Oops, something went wrong", // title
            "Internal error", // content
            "danger"
          ); // variant
        })
        .then(() => {
          objRef.$bvToast.hide("process_corpus");
          objRef.processingCorpus = false;
        });
    },
    addStopwords() {
      let objRef = this;
      this.process_corpus.stopwordsFile.text().then((txt) => {
        txt = txt.replace(/\n|\t|\r/g, " ");
        txt = txt.replace(/[^a-zA-Z ]/g, "");
        txt = txt.split(" ");
        txt = txt.filter((word) => word != "");
        txt = objRef.stop_words.concat(txt);
        txt = [...new Set(txt)];
        objRef.stopwords = txt.sort();
      });
    },
    ...mapActions(["deleteDocument", "processCorpus", "getUserData"]),
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass">
*
  box-sizing: border-box
  -moz-box-sizing: border-box
  -webkit-box-sizing: border-box

.upload-wrapper
  text-align: center
  padding: 10px 50px 0px 50px

  & > .container
    background-color: #f9f9f9
    padding: 20px
    border-radius: 10px
    position: -webkit-sticky
    position: sticky
    top: 60px

#corpusTable
  overflow-y: scroll
  overflow-x: auto
  max-height: 800px

#tableCol
  padding-top: 10px

#corpusToolbar
  justify-content: center
  padding-bottom: 5px
  position: -webkit-sticky
  position: sticky
  top: 60px

.stopwords_wrapper
  max-height: 200px !important
  overflow-y: auto
  display: block

$w: 0.0
@while $w < 1.0
  $w: $w + 0.05
  .w-#{$w * 100}
    width: percentage($w) !important
    max-width: percentage($w) !important
    min-width: percentage($w) !important

#stopwords-tags
  overflow-y: auto
  overflow-x: hidden
</style>
