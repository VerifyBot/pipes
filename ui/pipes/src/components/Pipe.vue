<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto">
      <div class="text-center justify-center d-flex flex-column unselectable">
        <h1 class="text-h2 font-weight-bold">
          <router-link to="/">
            <v-btn icon="mdi-home" size="large" color="blue-darken-4"></v-btn>
          </router-link>

          Pipe <u>{{ $route.params.id }}</u>
        </h1>
        <div class="text-body-2 font-weight-light mb-1"><i>{{ pipe?.description || 'Loading...' }}</i></div>
        <a :href="webProtocol + (pipe?.url || '')" style="width: min-content"
          class="mx-auto text-body-2 font-weight-light mb-n1">{{
            webProtocol + (pipe?.url || '') }}</a>
      </div>

      <div class="py-4" />

      <v-card class="mx-auto" max-width="30%" min-width="300">
        <v-card-title>
          Pipe Runs
        </v-card-title>



        <v-divider></v-divider>

        <v-empty-state v-if="!runs.length" title="No runs yet." text="Go trigger some..."></v-empty-state>
        <v-virtual-scroll :items="items" height="320" item-height="48" ref="scroll">
          <template v-slot:default="{ item }">

            <v-list-item>
              <template v-slot:title>
                <div v-if="!item?.loadMore">
                  Run #{{ item.id }}
                </div>
                <v-btn block class="my-2" variant="tonal" v-else @click="loadMoreRuns"
                  v-if="this.pipe.total_runs > this.runs.length" :loading="newRunsLoading">
                  Load more... ({{ pipe.total_runs - runs.length }} more runs)
                </v-btn>
              </template>

              <template v-slot:subtitle v-if="!item?.loadMore">
                <div style="width: min-content; white-space: pre;">
                  {{ item.sent_at_human }}
                  <v-tooltip text="test" location="left" activator="parent">
                    {{ (new Date(item.sent_at_ts * 1000) || 0).toLocaleString() }}
                  </v-tooltip>
                </div>

              </template>
              <template v-slot:prepend v-if="!item?.loadMore">
                <v-icon :color="item.success ? 'green' : 'red'">{{ item.success ? 'mdi-check-bold' : 'mdi-alert-circle'
                  }}</v-icon>
              </template>

              <template v-slot:append v-if="!item?.loadMore">
                <v-btn prepend-icon="mdi-eye" size="small" variant="tonal"
                  @click="showInfoDialog(item.id);">Info</v-btn>
              </template>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </v-card>


      <v-dialog v-model="infoDialog" width="auto" class="info-dialog">
        <v-card title="Run Details" prepend-icon="mdi-webhook">
          <template v-slot:text>
            <div style="max-width: 400px;">
              <!-- 
            we need to show...
            * run id
            * run status (if failure show run.error)
            * run sent at
            * request info
            * response info
           -->
              <v-sheet>
                <v-tabs v-model="tab" :items="tabs" align-tabs="center" color="white" height="60"
                  slider-color="#f78166">
                  <template v-slot:tab="{ item }">
                    <v-tab :value="item.value" class="text-none">
                      <template v-slot=text>
                        {{ item.text }}
                        <div class="run-status" :success="currentRun.success" v-if="item.value === 'response'">
                          {{ currentRun.response_info?.status || '...' }}
                        </div>
                      </template>
                    </v-tab>
                  </template>

                  <template v-slot:item="{ item }">
                    <v-tabs-window-item :value="item.value" class="pa-4">
                      <div v-if="item.value === 'request'">
                        ⌛ {{ currentRun.sent_at_human }} <br />
                        ☃️ ip - {{ currentRun.request_info.ip }} <br />

                        <h3 class="mt-3">Headers</h3>
                        <div class="info-codeblock">
                          <code v-for="header in Object.entries(currentRun.request_info.headers)" class="info-code">
                          <b>{{ header[0] }}</b>: {{ header[1] }} <br/>
                        </code>
                        </div>
                        <h3>Payload</h3>

                        <div class="info-codeblock">
                          <code>{{ currentRun.request_info.body || 'No payload' }}</code>
                        </div>

                      </div>

                      <div v-else>
                        <div v-if="currentRun.error && !currentRun.response_info">
                          <h3>Error</h3>
                          <code>
                            {{ currentRun.error }}
                          </code>
                        </div>
                        <div v-if="currentRun.response_info">
                          <h3>Headers</h3>
                          <div class="info-codeblock">
                            <code v-for="header in Object.entries(currentRun.response_info?.headers || [])"
                              class="info-code">
                          <b>{{ header[0] }}</b>: {{ header[1] }} <br/>
                        </code>
                          </div>
                          <h3>Payload</h3>

                          <div class="info-codeblock">
                            <code>{{ currentRun.response_info?.body || 'No response' }}</code>
                          </div>
                        </div>
                      </div>



                    </v-tabs-window-item>
                  </template>
                </v-tabs>
              </v-sheet>
            </div>
          </template>


          <template v-slot:actions>
            <v-spacer></v-spacer>
            <v-btn color="blue-darken-1" block @click="infoDialog = false">Close</v-btn>
            <v-spacer></v-spacer>
          </template>
        </v-card>
      </v-dialog>




    </v-responsive>
  </v-container>

</template>
<style>
.info-codeblock {
  padding: 8px 12px;
  margin: 8px 0;
  overflow: auto;
  font-size: 13px;
  line-height: 1.5;
  background-color: #161b22;
  border: #30363d;
  border-radius: 6px;
}

.run-status {
  padding: 4px 6px;
  border-radius: 6px;
  margin-left: 6px;
}

.run-status[success=true] {
  background-color: #238636;
}

.run-status[success=false] {
  background-color: #c53030;
}

.info-dialog .v-card-text {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
}
</style>
<script>
export default {
  data() {
    return {
      webProtocol: null,

      pipe: null,
      runs: [],
      items: [],
      scroll: null,
      newRunsLoading: false,

      currentRun: null,
      infoDialog: false,

      tab: null,
      tabs: [
        {
          text: 'Request',
          value: 'request',
        },
        {
          text: 'Response',
          value: 'response',
        },

      ],
    }
  },

  created() {
    this.webProtocol = window.location.protocol === 'https:' ? 'https://' : 'http://'
  },

  async mounted() {

    const { pipe, runs } = await this.api.getPipe({ id: this.$route.params.id });
    this.pipe = pipe;
    this.runs = runs;
    console.table(this.runs)

    this.items = [...this.runs]
    if (this.pipe.total_runs > this.runs.length) {
      this.items.push({ loadMore: true });
    }
  },

  watch: {

  },

  methods: {
    async loadMoreRuns() {
      if (this.pipe.total_runs <= this.runs.length) return;

      this.newRunsLoading = true;

      const js = await this.api.getRuns({
        pipe_id: this.pipe.id,
        offset: this.runs.length,
        limit: 15
      });

      let newRuns = js.runs

      this.runs = [...this.runs, ...newRuns];
      this.items = [...this.runs]

      if (this.pipe.total_runs > this.runs.length) {
        this.items.push({ loadMore: true });
      }

      await this.$nextTick();

      setTimeout(async () => {
        this.$refs.scroll.scrollToIndex(this.items.length - 1)
      }, 150)

      this.newRunsLoading = false;
    },

    async showInfoDialog(runId) {
      const js = await this.api.getRun({ id: runId });
      this.currentRun = js.run;
      console.log('-------------')
      console.log(this.currentRun)
      console.log('-------------')
      this.infoDialog = true;
    }
  }

  //async beforeRouteUpdate(to, from) {
  //this.id = to.params.id
  //}
}
</script>
