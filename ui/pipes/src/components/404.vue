<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto">
      <v-empty-state headline="Whoops, 404" title="Page not found" text="The page you were looking for does not exist"
        image="https://i.imgur.com/F9h1qWX.png">
      
        <router-link to="/">
            <v-btn prepend-icon="mdi-home" size="large" color="blue-darken-4">Rescue me</v-btn>
          </router-link>
      </v-empty-state>
    </v-responsive>
  </v-container>
</template>