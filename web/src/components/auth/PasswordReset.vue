<template>
  <div class="container">
    <div class="form-horizontal mt-4">
      <div class="row">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <h2>Reset Your Password</h2>
          <hr>
        </div>
      </div>
      <div class="row" v-if="details">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <div class="alert alert-success" role="alert">
            {{ details }}
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
                            {{ username_error }}
                        </span>
          </div>
        </div>
      </div>
      <div class="row" style="padding-top: 1rem">
        <div class="col-md-3"></div>
        <div class="col-md-6">
          <button type="submit" class="btn btn-success" @click="login"><i class="fa fa-sign-in"></i> Send Reset Link</button>
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
        email: 'bill.davis@syscall7.com',
        details: null
      }
    },
    methods: {
      login () {
        auth.reset(this.email).then((details) => {
          this.details = details.detail
        }).catch((e) => {
          this.password_error = _.get(e, 'response.data.non_field_errors[0]')
        })
      }
    }
  }
</script>
