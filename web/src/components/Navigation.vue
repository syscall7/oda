<template>
  <b-navbar toggleable="sm" type="dark" variant="dark" class="main-nav">

    <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>

    <b-navbar-brand href="/">
      <img src="../assets/oda.png" style="position:absolute; height:50px; left: 0px; z-index:5000;"
           class="d-none d-sm-block">
      ODA
    </b-navbar-brand>

    <b-collapse is-nav id="nav_collapse">

      <b-navbar-nav>
        <b-nav-text  v-if="showingDisassembly"  >{{ projectName }}</b-nav-text>

        <!-- <b-nav-item href="#">Link</b-nav-item>
        <b-nav-item href="#" disabled>Disabled</b-nav-item> -->
      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">

        <span class="navbar-user" v-for="user in otherUsers">
          <div class="navbar-letter"
               v-bind:style="{ 'background-color': activeColor(user) }"
               v-b-tooltip.hover
               :title="user.username">{{ user.username.charAt(0).toUpperCase()}}</div>
        </span>

        <!--<b-nav-form>
          <b-form-input size="sm" class="mr-sm-2" type="text" placeholder="Search"/>
          <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>
        </b-nav-form>-->

        <b-nav-item-dropdown text="Examples" right>
          <b-dropdown-item href="/odaweb/strcpy_x86">strcpy_x86</b-dropdown-item>
          <b-dropdown-item href="/odaweb/strcpy_arm">strcpy_arm</b-dropdown-item>
          <b-dropdown-item href="/odaweb/whoami">whoami</b-dropdown-item>
          <b-dropdown-item href="/odaweb/mkdir">mkdir</b-dropdown-item>
          <b-dropdown-item href="/odaweb/cat">cat</b-dropdown-item>
          <b-dropdown-item href="/odaweb/chown">chown</b-dropdown-item>
        </b-nav-item-dropdown>

        <b-nav-item-dropdown right v-if="isActiveUser">
          <!-- Using button-content slot -->
          <template slot="button-content">
            <em>User <i class="fa fa-user"></i></em>
          </template>
          <b-dropdown-item disabled>{{ username }}</b-dropdown-item>
          <b-dropdown-item href="/user/profile">Profile</b-dropdown-item>
          <b-dropdown-item @click="logout">Signout</b-dropdown-item>

        </b-nav-item-dropdown>

        <b-button-group>

          <b-button size="sm" class="my-1 px-2 btn-primary"
                    href="/login"
                    v-if="!isActiveUser"
                    right>
            <i class="fa fa-lock"></i>
            Login
          </b-button>

          <b-button size="sm" class="my-1 px-2 btn-primary"
                    href="/signup"
                    variant="success"
                    v-if="!isActiveUser"
                    right>
            <i class="fa fa-lock"></i>
            Signup
          </b-button>

          <b-button size="sm"
                    v-if="showingDisassembly"
                    class="my-1 px-2 btn-primary" right
                    @click="showSharingDialog">
            <i class="fa fa-lock"></i>
            Share
          </b-button>

        </b-button-group>

      </b-navbar-nav>

    </b-collapse>
  </b-navbar>
</template>


<script>
  import ColorHash from 'color-hash'
  import {bus, SHOW_SHARING_MODAL} from '../bus'
  import * as auth from '../api/auth'

  export default {
    name: 'Navigation',
    data () {
      return {

      }
    },
    computed: {
      projectName () {
        return this.$store.state.projectName
      },
      username () {
        if (this.$store.state.user) {
          return this.$store.state.user.username
        }
      },
      isActiveUser () {
        return this.$store.getters.isActiveUser
      },
      otherUsers () {
        return this.$store.getters.otherUsers
      },
      showingDisassembly () {
        return (this.$route.name === 'Disassembler')
      }
    },
    methods: {
      showSharingDialog () {
        bus.$emit(SHOW_SHARING_MODAL)
      },
      logout () {
        auth.logout().then(() => {
          this.$router.push('/')
        })
      },
      activeColor (user) {
        var colorHash = new ColorHash({lightness: 0.4})
        let color = colorHash.hex(user.username)
        return color
      }
    }
  }
</script>

<style scoped>
  .main-nav {
    padding-top: 2px;
    padding-bottom: 2px;
    font-size: 0.75rem;
  }

  .main-nav .navbar-brand {
    padding: 0px 0px 0px 50px;
    font-size: 0.95rem;
  }

  .navbar-user .navbar-letter {
    font-size: 20px;
    margin: 6px 2px 4px 2px;
    padding: 1px 8px 1px 8px;
    line-height: 18px;
    font-family: Arial, Helvetica, sans-serif;
    font-weight: bold;
    color: #CCCCCC;
    border: 1px solid #a29ea2
  }

  .btn {
    padding: 2px;
    margin: 0;
    font-size: 12px;
    height: 24px;
  }

  >>> .dropdown .dropdown-menu .dropdown-item:focus {
    outline: none;
  }
</style>

