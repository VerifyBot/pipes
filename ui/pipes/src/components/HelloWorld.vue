<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto">
      <div class="text-center">
        <h1 class="text-h2 font-weight-bold">🚀 Pipes</h1>
        <div class="text-body-2 font-weight-light mb-n1"><i>pipe those webhooks to Discord</i></div>
      </div>

      <div class="py-4" />

      <!-- actions -->
      <div v-if="isLoadingPipes">
        <p class="text-center mb-5">I will be ready shortly</p>
        <v-progress-linear color="indigo" indeterminate></v-progress-linear>
      </div>
      <div v-else>
        <div class="d-flex justify-start my-4">
          <v-btn prepend-icon="mdi-pipe" color="indigo-darken-2" @click="editPipe(item)">New Pipe</v-btn>
        </div>

        <!-- view pipes list (sort, filter) -->
        <v-data-table v-model:sort-by="pipesSortBy" :headers="pipesHeaders" :items="pipesArray" id="pipes-list"
          show-expand v-model:expanded="pipesExpanded">
          <!-- pause-development :: put this as an attr for v-data-able -->
          <!-- :row-props="(row) => { return { style: { color: 'white', background: !row.item.active ? 'rgba(250,0,0, .2)' : null} } }" -->
          <template v-slot:item.url="{ item }">
            <a :href="'pipe/' + item.id">{{ item.url }}</a>
          </template>

          <template v-slot:item.last="{ item }">
            <div v-if="item.last">
              {{ item.last }}
              <v-tooltip text="test" location="top" activator="parent">
                {{ (new Date(item.lastTs * 1000) || 0).toLocaleString() }}
              </v-tooltip>
            </div>

            <div v-else>n/a</div>
          </template>

          <template v-slot:item.runs="{ item }">
            <div>{{ (item.runs || 0).toLocaleString() }}</div>
          </template>

          <template v-slot:item.actions="{ item }">
            <span class="pipe-action cursor-pointer" @click="editPipe(item)"><v-icon>mdi-pencil</v-icon>
              <v-tooltip location="top" activator="parent">Edit</v-tooltip>
            </span>
            <span class="pipe-action cursor-pointer" @click="deletePipe(item)"><v-icon>mdi-delete</v-icon>
              <v-tooltip location="top" activator="parent">Delete</v-tooltip>
            </span>
            <span class="pipe-action cursor-pointer" @click="testPipe(item)"><v-icon>mdi-run</v-icon>
              <v-tooltip location="top" activator="parent">Test Webhook</v-tooltip>
            </span>
            <!-- pause-development :: add an action to pause/resume the pipe -->
            <!-- <v-icon>{{ item.active ? 'mdi-stop-circle-outline' : 'mdi-play-circle-outline' }}</v-icon> -->
          </template>

          <template v-slot:expanded-row="{ columns, item }">
            <tr>
              <td :colspan="columns.length">
                <b>{{ item.url }}</b> pipes to <b>{{ item.webhookUrl }}</b>
              </td>
            </tr>
          </template>
        </v-data-table>
      </div>




    </v-responsive>
  </v-container>

  <!-- Delete Pipe Dialog -->
  <v-dialog v-model="dialogDelete" max-width="400">
    <v-card prepend-icon="mdi-delete" title="Delete this pipe?">
      <template v-slot:text>
        <b>{{ editedItem.description }}</b> with <b>{{ (editedItem.runs || 0).toLocaleString() }}</b> runs.
      </template>
      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" @click="closeDelete">Cancel</v-btn>
        <v-btn color="red-darken-1" @click="deleteItemConfirm">Delete</v-btn>
        <v-spacer></v-spacer>
      </template>
    </v-card>
  </v-dialog>

  <!-- Create/Edit Pipe Dialog -->
  <v-dialog v-model="dialog" max-width="400" :persistent="isCreatingPipe">
    <v-card prepend-icon="mdi-pipe">
      <template v-slot:title>
        {{ this.editedIndex === -1 ? 'New Pipe' : 'Edit Pipe' }}
      </template>

      <template v-slot:text>
        <v-text-field label="Pipe Description *" v-model="editedItem.description" required :readonly="isCreatingPipe"
          :rules="[required]" ref="descriptionField"></v-text-field>

        <v-text-field label="Discord Webhook URL *" v-model="editedItem.webhookUrl" required :readonly="isCreatingPipe"
          :rules="[required]" ref="webhookUrlField"></v-text-field>
      </template>

      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" @click="close" :disabled="isCreatingPipe">Cancel</v-btn>
        <v-btn color="red-darken-1" @click="save" :loading="isCreatingPipe">Save</v-btn>
        <v-spacer></v-spacer>
      </template>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  beforeMount() {
    const hasToken = Boolean(localStorage.getItem('pipesToken'))

    if (!hasToken) {
      //this.$router.push('/login');
    }
  },

  async mounted() {
    // this.pipesArray = await this.api.getPipes();

    //await new Promise(resolve => setTimeout(resolve, 2000));

    this.pipesArray = [
      { url: "f19d3331.m.pipes.me", id: "f19d3331", description: "kabot", runs: 1420, last: "just now", lastTs: 1714322222, active: true, webhookUrl: 'https://discord.com/api/webhooks/1228741354612592771/i9XFneZAZfxlIviA4uZpbo-Jc0QhjVXjh2XcwTv39MkW__KZP3OvSJsC81L8Huy98NO_'},
      { url: "374753f3.m.pipes.me", id: "374753f3", description: "roybot", runs: 3234, last: "a day ago", lastTs: 1714333375, active: true, },
      { url: "3b231f9d.m.pipes.me", id: "3b231f9d", description: "faqbot", runs: 32, last: "2 months ago", lastTs: 1712215975, active: false },
      { url: "d64319bb.m.pipes.me", id: "d64319bb", description: "lis test (kabot)", runs: 0, last: null, lastTs: 1713315975, active: true },
    ]
    this.isLoadingPipes = false;
  },

  data() {
    return {
      pipesExpanded: [],

      pipesSortBy: [{ key: 'url', order: 'asc' }],

      pipesHeaders: [
        { title: '🚀 URL', align: 'start', sortable: false, key: 'url' },
        { title: '💬 Description', align: 'start', sortable: false, key: 'description' },
        { title: '🎉 Runs', align: 'start', sortable: true, key: 'runs' },
        { title: '📅 Last Run', align: 'start', sortable: true, key: 'last' },
        { title: '🕹️ Actions', align: 'start', sortable: false, key: 'actions' },
      ],
      pipesArray: [],

      dialog: false,
      dialogDelete: false,

      editedIndex: -1,
      editedItem: {
        description: '',
        webhookUrl: '',
      },

      defaultItem: {
        description: '',
        webhookUrl: '',
      },

      isLoadingPipes: true,
      isCreatingPipe: false,
    }
  },
  watch: {
    dialog(val) {
      val || this.close()
    },

    dialogDelete(val) {
      val || this.closeDelete()
    },

    pipesExpanded(val) {
      // todo
    }
  },
  methods: {
    // Form Utility
    required(v) {
      return !!v || 'Field is required'
    },

    // Pipe Deletion
    deletePipe(item) {
      this.editedIndex = this.pipesArray.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    deleteItemConfirm() {
      this.pipesArray.splice(this.editedIndex, 1)
      this.closeDelete()
    },

    closeDelete() {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    // Pipe Creating / Editing
    editPipe(item) {
      this.editedIndex = this.pipesArray.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    close() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    async save() {
      if (!this.editedItem.description || !this.editedItem.webhookUrl) {
        // raise the rules for the text 
        this.$refs.descriptionField.validate();
        this.$refs.webhookUrlField.validate();
        return;
      }

      if (this.editedIndex > -1) {
        Object.assign(this.pipesArray[this.editedIndex], this.editedItem)
        // this.api.editPipe(this.pipesArray[this.editedIndex]);
      } else {
        this.isCreatingPipe = true;
        await new Promise(resolve => setTimeout(resolve, 2000));
        // const pipe = await this.api.createPipe(this.editedItem)
        // this.pipesArray.push(pipe)
        this.isCreatingPipe = false;
      }
      this.close()
    },


  }
}
</script>

<style>
/* .pipe-action {
  cursor: pointer;
} */
</style>