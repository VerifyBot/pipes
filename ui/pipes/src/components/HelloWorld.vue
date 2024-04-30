<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto">
      <div class="text-center justify-center d-flex flex-column">
        <h1 class="text-h2 font-weight-bold">🚀 Pipes</h1>
        <div class="text-body-2 font-weight-light mb-n1"><i>pipe those webhooks to Discord</i></div>
        <div class="d-flex justify-center my-2">
          <v-btn prepend-icon="mdi-github" size="small" onclick="window.open('https://github.com/VerifyBot/pipes')">github</v-btn>
        </div>
      </div>

      <div class="py-4" />

      <!-- actions -->
      <div v-if="isLoadingPipes">
        <p class="text-center mb-5">{{ loadingMessage }}</p>
        <v-progress-linear v-if="!serverDown" color="indigo" indeterminate></v-progress-linear>
        <v-img v-else style="height:30vh; object-fit: contain"
          src="https://media.giphy.com/media/hnJgISnMHGK5eMXW7p/giphy.gif">
          <template v-slot:placeholder>
            <div class="d-flex align-center justify-center fill-height">
              <v-progress-circular color="grey-lighten-4" indeterminate></v-progress-circular>
            </div>
          </template>
        </v-img>
      </div>
      <div v-else>
        <div class="d-flex my-4 justify-space-between">
          <v-btn prepend-icon="mdi-pipe" color="indigo-darken-2" @click="addPipe()">New Pipe</v-btn>
          <v-btn prepend-icon="mdi-lightbulb-question" color="pink-darken-3" @click="infoDialog = true;">Info</v-btn>
        </div>

        <!-- view pipes list (sort, filter) -->
        <v-data-table v-model:sort-by="pipesSortBy" :headers="pipesHeaders" :items="pipesArray" id="pipes-list"
          show-expand v-model:expanded="pipesExpanded">
          <!-- pause-development :: put this as an attr for v-data-able -->
          <!-- :row-props="(row) => { return { style: { color: 'white', background: !row.item.active ? 'rgba(250,0,0, .2)' : null} } }" -->
          <template v-slot:item.url="{ item }">
            <a :href="(isHttps ? 'https://' : 'http://') + item.url">{{ item.url }}</a>
          </template>

          <template v-slot:item.description="{ item }">
            <div style="max-width: 400px; line-break: anywhere">{{ item.description }}</div>
          </template>

          <template v-slot:item.last="{ item }">
            <div v-if="item.last_run">
              {{ item.last_run_human }}
              <v-tooltip text="test" location="top" activator="parent">
                {{ (new Date(item.last_run_ts * 1000) || 0).toLocaleString() }}
              </v-tooltip>
            </div>

            <div v-else>n/a</div>
          </template>

          <template v-slot:item.runs="{ item }">
            <div>{{ (item.total_runs || 0).toLocaleString() }}</div>
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
                Pipes to <b>{{ item.webhook_url }}</b>
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
        <b>{{ editedItem.description }}</b> with <b>{{ (editedItem.total_runs || 0).toLocaleString() }}</b> runs.
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
          :rules="rules.description" validate-on="submit blur" ref="descriptionField"></v-text-field>

        <v-text-field label="Discord Webhook URL *" v-model="editedItem.webhook_url" required :readonly="isCreatingPipe"
          :rules="rules.webhookUrl" validate-on="submit blur" ref="webhookUrlField"
          placeholder="https://discord.com/api/webhooks/..."></v-text-field>




        <v-switch id="hmac-switch" v-model="useHmac">
          <template v-slot:label>
            HMAC signature (optional)
            <v-tooltip width="250"
              text="To verify the authenticity of a webhook, services might send a signature header. The header contains an HMAC signature comprised of the request body and your webhook secret."
              location="top">
              <template v-slot:activator="{ props }">
                <v-icon size="small" class="ml-2" v-bind="props">mdi-help-circle</v-icon>
              </template>
            </v-tooltip>

          </template>
        </v-switch>

        <v-text-field prepend-icon="mdi-arrow-right-bottom" v-if="useHmac" label="HMAC Header *" density="compact"
          v-model="editedItem.hmac_header" :readonly="isCreatingPipe" :rules="rules.hmac_header"
          validate-on="input lazy" ref="hmacHeaderField" placeholder="X-...-Signature"></v-text-field>
        <v-text-field prepend-icon="mdi-arrow-right-bottom" v-if="useHmac" label="HMAC Secret *" density="compact"
          v-model="editedItem.hmac_secret" :readonly="isCreatingPipe" :rules="rules.hmac_secret"
          validate-on="input lazy" ref="hmacSecretField"></v-text-field>


        <v-alert v-if="pipeEditError" closable icon="mdi-message-alert" color="error" variant="tonal">{{ pipeEditError
          }}</v-alert>
      </template>

      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" @click="close" :disabled="isCreatingPipe">Cancel</v-btn>
        <v-btn color="red-darken-1" @click="save" :loading="isCreatingPipe">Save</v-btn>
        <v-spacer></v-spacer>
      </template>
    </v-card>
  </v-dialog>

  <!-- Info Dialog -->
  <v-dialog v-model="infoDialog" width="auto">
    <v-card title="🛟 Info">
      <template v-slot:text>
        <div style="max-width: 500px;">
          <div class="d-flex justify-start">
            <v-icon color="pink-darken-2" class="mr-2" size="small">mdi-file-document-alert</v-icon>
            <div>
              If a request payload is longer than 2000 characters, it will be sent as a file attachment
              to comply with <a class="a-link"
                href='https://discord.com/developers/docs/resources/webhook#:~:text=string-,the%20message%20contents%20(up%20to%202000%20characters),-one%20of%20content'
                target="_blank">Discord's limits</a>.
            </div>

          </div>

        </div>
      </template>


      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" block @click="infoDialog = false">Close</v-btn>
        <v-spacer></v-spacer>
      </template>
    </v-card>
  </v-dialog>

  <v-snackbar v-model="alertSnackbar" :timeout="3000">
    {{ alertSnackbarMessage }}
    <template v-slot:actions>
      <v-btn color="blue" variant="text" @click="alertSnackbar = false">
        Close
      </v-btn>
    </template>
  </v-snackbar>
</template>

<style>
.v-input__details:has(> #hmac-switch-messages) {
  display: none;
}

.a-link {
  color: #00BCD4;
  cursor: pointer;
}
</style>


<script>
export default {
  async created() {
    // search token in url params
    const urlParams = new URLSearchParams(window.location.search);
    const paramToken = urlParams.get('token');

    if (paramToken) {
      localStorage.setItem(this.api.tokenName, paramToken);

      // remove the token from the url
      window.history.replaceState(null, '', window.location.pathname);
    }

    const hasToken = Boolean(localStorage.getItem(this.api.tokenName))

    if (!hasToken) {
      this.redirecting = true;
      let r = await this.api.redirectToLogin();

      if (r !== 'down') return

      this.redirecting = false;
      this.serverDown = true;
      this.loadingMessage = "down" //this.loadingMessageKind.hopeless;
    }
  },

  async mounted() {
    this.isLoadingPipes = true;

    if (this.redirecting || this.serverDown) {
      return
    }



    setTimeout(() => {
      if (!this.isLoadingPipes) return
      this.loadingMessage = this.loadingMessageKind.hopeful;

      setTimeout(() => {
        if (!this.isLoadingPipes) return
        this.loadingMessage = this.loadingMessageKind.hopesemi;

        setTimeout(() => {
          if (!this.isLoadingPipes) return
          this.loadingMessage = this.loadingMessageKind.hopeless;
          this.serverDown = true;
        }, 1000 * 5);
      }, 1000 * 5);
    }, 1000 * 5);

    let js;
    try {
      js = await this.api.getPipes();
    } catch (e) {
      this.serverDown = true;
      this.loadingMessage = this.loadingMessageKind.hopeless;
      return
    }

    if (this.serverDown) return;

    this.pipesArray = js.pipes;

    this.isLoadingPipes = false;

    // this.pipesArray = [
    //   { url: "f19d3331.m.pipes.me", id: "f19d3331", description: "kabot", runs: 1420, last: "just now", lastTs: 1714322222, active: true, webhookUrl: 'https://discord.com/api/webhooks/1228741354612592771/i9XFneZAZfxlIviA4uZpbo-Jc0QhjVXjh2XcwTv39MkW__KZP3OvSJsC81L8Huy98NO_'},
    //   { url: "374753f3.m.pipes.me", id: "374753f3", description: "roybot", runs: 3234, last: "a day ago", lastTs: 1714333375, active: true, },
    //   { url: "3b231f9d.m.pipes.me", id: "3b231f9d", description: "faqbot", runs: 32, last: "2 months ago", lastTs: 1712215975, active: false },
    //   { url: "d64319bb.m.pipes.me", id: "d64319bb", description: "lis test (kabot)", runs: 0, last: null, lastTs: 1713315975, active: true },
    // ]
  },

  data() {
    return {
      isHttps: location.protocol === 'https:',

      redirecting: false,
      pipeEditError: null,

      alertSnackbar: false,
      alertSnackbarMessage: "🚀",

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

      dialog: true,
      dialogDelete: false,
      infoDialog: false,

      editedIndex: -1,
      editedItem: {
        description: '',
        webhook_url: '',
        hmac_header: '',
        hmac_secret: '',
      },

      defaultItem: {
        description: '',
        webhook_url: 'https://discord.com/api/webhooks/1234544601571000472/N_uZiHgNmE6oI2AuLvp9SSyZzFaI1FgI9kytJTBs0A8WuieKZg9twQkP-LQ3VALIPKj2',
        hmac_header: '',
        hmac_secret: '',
      },

      isLoadingPipes: true,
      loadingMessage: 'I will be ready shortly',
      serverDown: false,
      isCreatingPipe: false,
      loadingMessageKind: {
        hopeful: "The server might have morphed into a turtle... 🐢💨",
        hopesemi: "Is it a bird? A plane? Definitely not a server... 🦅🛩️",
        hopeless: "We think server got stuck in the moon, sorry... 🌑👀"
      },

      useHmac: false,



      rules: {
        // webhookUrl must be https://discord.com/api/webhooks/\d+/\w+
        webhookUrl: [
          v => !!v || 'Field is required',
          v => !!v.match(/https:\/\/discord.com\/api\/webhooks\/\d+\/\w+/) || 'Invalid Discord Webhook URL',
        ],
        description: [
          v => !!v || 'Field is required',
          v => v.length <= 500 || 'Description is too long (max 500 characters)'
        ],
        hmac_secret: [
          // if this.useHmac, then this field is required, else it's not
          v => !this.useHmac || !!v || 'Field is required',
        ],
        hmac_header: [
          // if this.useHmac, then this field is required, else it's not
          v => !this.useHmac || !!v || 'Field is required',
        ]
      }
    }
  },
  watch: {
    dialog(val) {
      if (!val) {
        this.useHmac = false;
        this.close();
      }
    },

    dialogDelete(val) {
      val || this.closeDelete()
    },

    editedItem(val) {
      this.useHmac = !!val.hmac_secret;
    },



    pipesExpanded(val) {
      // todo
    }
  },
  methods: {
    // Snackbar
    showSnackbar(message) {
      this.alertSnackbarMessage = message;
      this.alertSnackbar = true;
    },

    // Pipe Deletion
    deletePipe(item) {
      this.editedIndex = this.pipesArray.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    deleteItemConfirm() {
      this.api.deletePipe(this.editedItem);
      this.pipesArray.splice(this.editedIndex, 1)
      this.closeDelete();
      this.showSnackbar(`👋 Pipe deleted`);
    },

    closeDelete() {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    // Pipe Creating / Editing
    addPipe() {
      this.editedIndex = -1
      this.editedItem = Object.assign({}, this.defaultItem);
      this.dialog = true;
    },

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
      this.pipeEditError = null;

      let validations = [
        await this.$refs.descriptionField.validate(),
        await this.$refs.webhookUrlField.validate(),
        await this.$refs.hmacHeaderField?.validate(),
        await this.$refs.hmacSecretField?.validate(),
      ];
      if (validations.some(v => v && v.length))
        return;


      if (this.editedIndex > -1) {
        Object.assign(this.pipesArray[this.editedIndex], this.editedItem)
        this.api.editPipe(this.pipesArray[this.editedIndex]);
        this.showSnackbar(`✨ Pipe updated`);
      } else {
        this.isCreatingPipe = true;

        const js = await this.api.addPipe(this.editedItem)
        this.showSnackbar(`🚀 Pipe created`);

        if (js.error) {
          this.pipeEditError = js.error;
          this.isCreatingPipe = false;
          return
        }

        this.pipesArray.push(js)
        this.isCreatingPipe = false;
      }
      this.close()
    },

    async testPipe(item) {
      try {
        await fetch(
          item.webhook_url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: '🚀 Test Webhook from **Pipes**'
          })
        }
        ).then(async resp => {
          if (resp.status !== 204) {
            const js = await resp.json();
            throw new Error(`${js.message || js.webhook_id[0]}`);
          } else {
            this.showSnackbar('🎉 Test Webhook sent');
          }
        });
      } catch (e) {
        this.showSnackbar(`❌ Test failed: ${e.message}`);
      }


    }

  }
}
</script>
