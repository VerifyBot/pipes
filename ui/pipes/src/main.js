/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

const app = createApp(App)

import { PipesApi } from './api.js'

app.config.globalProperties.api = new PipesApi();
window.api = app.config.globalProperties.api;

registerPlugins(app)

app.mount('#app')
