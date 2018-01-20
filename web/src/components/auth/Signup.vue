<template>
  <div class="container">
    <div class="form-horizontal mt-4" role="form">
      <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <h2>Start Disassembling Online</h2>
          <h4>The best way to reverse engineer software through the internet</h4>
          <hr>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3 field-label-responsive">
          <label for="name">Name</label>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem"><i class="fa fa-user"></i></div>
              <input type="text" name="name" class="form-control" id="name"
                     v-model="username"
                     placeholder="Your Username" required autofocus>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="form-control-feedback">
                        <span class="text-danger align-middle">
                            {{ username_error }}
                        </span>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3 field-label-responsive">
          <label for="email">E-Mail Address</label>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem"><i class="fa fa-at"></i></div>
              <input type="text" name="email" class="form-control" id="email"
                     v-model="email"
                     placeholder="you@example.com" required autofocus>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="form-control-feedback">
                        <span class="text-danger align-middle">
                            {{ email_error }}
                        </span>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3 field-label-responsive">
          <label for="password">Password</label>
        </div>
        <div class="col-md-6">
          <div class="form-group has-danger">
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem"><i class="fa fa-key"></i></div>
              <input type="password" name="password" class="form-control" id="password"
                     v-model="password1"
                     placeholder="Password" required>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="form-control-feedback" v-if="password_error">
                        <span class="text-danger align-middle">
                            <i class="fa fa-close"> {{ password_error }}</i>
                        </span>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3 field-label-responsive">
          <label for="password">Confirm Password</label>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <div class="input-group mb-2 mr-sm-2 mb-sm-0">
              <div class="input-group-addon" style="width: 2.6rem">
                <i class="fa fa-repeat"></i>
              </div>
              <input type="password" name="password-confirmation" class="form-control"
                     v-model="password2"
                     id="password-confirm" placeholder="Password" required>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <button type="submit" class="btn btn-success" @click="signup"><i class="fa fa-user-plus"></i> Register</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import * as auth from '../../api/auth'
  import _ from 'lodash'

  export default {
    data () {
      return {
        username: null,
        username_error: null,

        email: null,
        email_error: null,

        password1: null,
        password_error: null,

        password2: null

      }
    },
    methods: {
      signup () {
        auth.signup(this.username, this.email, this.password1, this.password2).then((e) => {
          this.email_error = null
          this.password_error = null
          this.username_error = null

          auth.login(this.username, this.password1).then((e) => {
            this.$router.push('/')
          })
        }).catch((e) => {
          this.email_error = _.get(e, 'response.data.email[0]')
          this.password_error = _.get(e, 'response.data.non_field_errors[0]')
          this.username_error = _.get(e, 'response.data.username[0]')
        })
      }
    }
  }
</script>

<style scoped>
  .field-label-responsive {
    padding-top: .5rem;
    text-align: right;
  }
</style>
