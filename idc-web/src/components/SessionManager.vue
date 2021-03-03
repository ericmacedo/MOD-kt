<template>
   <div class="h-100 text-center">
      <b-spinner
        class="m-5"
        variant="primary"></b-spinner>
  </div>
</template>

<script>
export default {
  name: "SessionManager",
  props: {
    width: {
      type: Number,
      required: true
    },
    height: {
      type: Number,
      required: true
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="sass" scoped></style>