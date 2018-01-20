<template>
  <div>
    Revision History
    <table class="table table-condensed">
      <thead>
      <th>User</th>
      <th>Operation</th>
      <th>DateTime</th>
      </thead>
      <tbody>
      <tr v-for="op in operations">
        <td v-if="op.user">
          <div v-if="op.user.is_lazy_user">
            Anonymous
          </div>
          <div v-else>
            {{ op.user.username }}
          </div>
        </td>
        <td v-else>System</td>
        <td><strong>{{op.name}}</strong><br><em>{{op.desc}}</em>
        </td>
        <td>{{op.datetime}}</td>
      </tr>
      </tbody>
    </table>

  </div>
</template>


<script>
  import {loadOperations} from '../../api/oda'

  export default {
    name: 'Operations',
    data () {
      return {
        operations: []
      }
    },
    async created () {
      this.operations = await loadOperations()
    }
  }
</script>

<style scoped>
  table {
    font-size: 0.85rem;
  }

  .table td {
    padding: 3px 8px;
  }
</style>
