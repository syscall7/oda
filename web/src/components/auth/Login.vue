<template>
  <div class="container">
    <div class="form-horizontal mt-4">
      <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <h2>Sign In To Disassembler</h2>
          <hr>
        </div>
      </div>
      <div class="row" v-if="password_error">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <div class="alert alert-danger" role="alert">
            {{ password_error }}
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3 field-label-responsive">
          <label for="name"></label>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem"><i class="fa fa-user"></i></div>
              <input type="text" name="name" class="form-control" id="name"
                     v-model="username"
                     placeholder="Username" required autofocus>
            </div>
          </div>
        </div>
        <div class="col-md-3">

        </div>
      </div>
      <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <div class="form-group">
            <label class="sr-only" for="password">Password</label>
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem"><i class="fa fa-key"></i></div>
              <input type="password" name="password" class="form-control" id="password"
                     v-model="password"
                     placeholder="Password" required v-on:keyup.enter="login">
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="form-control-feedback">
                        <span class="text-danger align-middle">

                        </span>
          </div>
        </div>
      </div>
      <!-- <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6" style="padding-top: .35rem">
          <div class="form-check mb-2 mr-sm-2 mb-sm-0">
            <label class="form-check-label">
              <input class="form-check-input" name="remember"
                     type="checkbox">
              <span style="padding-bottom: .15rem">Remember me</span>
            </label>
          </div>
        </div>
      </div>  -->
      <div class="row" style="padding-top: 1rem">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <button type="submit" class="btn btn-success" @click="login"><i class="fa fa-sign-in"></i> Login</button>
          <router-link to="PasswordReset">Forgot Your Password?</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash'

  export default {
    data () {
      return {
        username: null,
        password: null,
        password_error: null
      }
    },
    methods: {
      login () {
        this.$store.dispatch('login', {
          username: this.username,
          password: this.password
        }).then(() => {
          this.$router.push('/')
        }).catch((e) => {
          this.password_error = _.get(e, 'response.data.non_field_errors[0]')
        })
      }
    }
  }
</script>
