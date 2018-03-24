import Vue from 'vue'
import Router from 'vue-router'
import Disassembler from '@/components/Disassembler'
import Login from '@/components/auth/Login'
import Signup from '@/components/auth/Signup'
import PasswordReset from '@/components/auth/PasswordReset'
import Profile from '@/components/user/Profile'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/odaweb/:shortName',
      name: 'Disassembler',
      component: Disassembler
    }, {
      path: '/login',
      name: 'Login',
      component: Login
    }, {
      path: '/signup',
      name: 'Signup',
      component: Signup
    }, {
      path: '/passwordreset',
      name: 'PasswordReset',
      component: PasswordReset
    }, {
      path: '/user/profile',
      name: 'UserProfile',
      component: Profile
    }, {
      path: '*',
      redirect: '/odaweb/strcpy_x86'
    }
  ]
})
