<template>
<div>
  <b-jumbotron class="col-lg-10 col-md-10 col-sm-10 col-xs-10 offset-1 float-md-center">
  <template #header>Hello, {{ $store.state.userData.userId }}!</template>

    <template #lead>
      This is a simple hero unit, a simple jumbotron-style component for calling extra attention to featured content or information.
    </template>

    <hr class="my-4">

    <p>
      It uses utility classes for typography and spacing to space content out within the larger
      container.
    </p>

    <b-button variant="primary" href="#">Do Something</b-button>
    <b-button variant="success" href="#">Do Something Else</b-button>
  </b-jumbotron>
</div>
</template>

<script>
export default {
  name: 'Index'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
