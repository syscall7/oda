<template>
  <div>
    <div class="oda-sidebar-title">Structures</div>
    <form class="form-inline" role="form">
      <div class="btn-group" style="margin-right: 10px;">
        <button type="button" class="btn btn-secondary" @click="showCreateStructModal">
          <i class="fa fa-plus-square fa-lg"></i>
        </button>
      </div>
      <div class="input-group">
        <span class="input-group-addon">Filter</span>
        <input type="text" class="form-control" placeholder="Substring" ng-model="search.string">
      </div>

    </form>
    <div class="sidebar-scroll-container">
      <table class="table table-striped sidebar-table table-sm" id="structtypes-table">
        <thead>
        <tr>
          <th class="col-sm-4" style="width:1%">Type</th>
        </tr>
        </thead>
        <tbody class="scrollContent">
        <tr v-for="(struct, index) in structTypes">
          <td class="clickable" style="text-align: left; width:100%" @click="showEditStructureModal(struct, index)">
            {{ struct.name }}
          </td>
          <td>
            <button type="button" class="btn btn-secondary btn-sm" @click="deleteStruct(index)">
              <i class="fa fa-trash-o"></i>
            </button>
          </td>
        </tr>
        </tbody>
      </table>

      <div v-if="structTypes.length == 0">
        <em>No structs found in here and why not</em>
      </div>
    </div>

    <b-modal ref="createStructModal" title="Create Struct Type" @ok="createStructure">
      <div class="form-group">
        <label for="name">Structure Name:</label>
        <input type="text" id="name" class="form-control" v-model="newStructureName" />
      </div>
    </b-modal>

    <b-modal ref="editStructModal" title="Edit Structure Definition" @ok="updateStructure">
      <div class="form-group">
        <table class="table table-striped sidebar-table table-condensed" id="struct-editor-table">
          <thead>
          <tr>
            <th class="col-sm-4" style="width:1%">Name</th>
            <th class="col-sm-4" style="text-align: left; width:90%">Type</th>
            <th class="col-sm-4" style="text-align: left; width:10%"></th>
          </tr>
          </thead>
          <tbody class="scrollContent" v-if="selectedStruct">
<!--           <tr ng-repeat="f in data.fields">
            <td class="str-vma" style="text-align: left; width:45%">{{ f.name }}</td>
            <td class="string" style="text-align: left; width:45%">{{ f.type }}</td>
            <td class="string" style="text-align: left; width:10%"><button class="btn btn-primary" ng-click="deleteField($index)">Delete Field</button></td>
          </tr> -->
          <tr v-for="(f, index) in selectedStruct.fields">
            <td class="str-vma" style="text-align: left; width:45%">{{ f.name }}</td>
            <td class="string" style="text-align: left; width:45%">{{ f.type }}</td>
            <td class="string" style="text-align: left; width:10%">
              <button class="btn btn-primary" @click="deleteField(index)">Delete Field</button>
            </td>

          </tr>
          <tr>
            <td class="str-vma" style="text-align: left; width:45%">
              <input type="text" class="form-control" v-model="newfield.name" />
            </td>
            <td class="string" style="text-align: left; width:45%">
              <select class="form-control" id="select-field-type" v-model="newfield.type" name="select-field-type">
                <option v-for="ft in structFieldTypes" v-bind:value="ft.name">
                  {{ft.name}}</option>
              </select>
            </td>
            <td class="string" style="text-align: left; width:10%">
              <button class="btn btn-primary" @click="addField">Add Field</button></td>
          </tr>
          <!-- <tr>
            <td class="str-vma" style="text-align: left; width:45%">
              <input type="text" class="form-control" ng-model="newfield.name" />
            </td>
            <td class="string" style="text-align: left; width:45%">
              <select class="form-control" id="select-field-type" ng-model="newfield.type" name="select-field-type">
                <option ng-repeat="ft in data.fieldTypes">{{ft.name}}</option>
              </select>
            </td>
            <td class="string" style="text-align: left; width:10%"><button class="btn btn-primary" ng-click="addField(newfield.name,newfield.type)">Add Field</button></td>
          </tr> -->
          </tbody>
        </table>
      </div>
    </b-modal>

  </div>
</template>


<script>
  import _ from 'lodash'

  export default {
    name: 'Structures',
    data () {
      return {
        structures: [],
        newStructureName: '',

        selectedStruct: null,
        selectedStructIndex: null,

        newfield: {
          name: 'field_0',
          type: 'int32_t'
        }
      }
    },
    computed: {
      structTypes: function () {
        return this.$store.state.structTypes
      },
      structFieldTypes: function () {
        return this.$store.state.structFieldTypes
      }
    },
    methods: {
      showCreateStructModal () {
        this.newStructureName = 'StructName'
        this.$refs.createStructModal.show()
      },
      showEditStructureModal (structure, index) {
        this.selectedStruct = structure
        this.selectedStructIndex = index
        this.$refs.editStructModal.show()
        this.newfield.name = 'field_' + this.selectedStruct.fields.length
      },
      async createStructure () {
        await this.$store.dispatch('addStruct', {name: this.newStructureName})

        // show the modal to edit the new structure
        let index = _.findIndex(this.$store.state.structTypes,
                                {name: this.newStructureName})
        if (index >= 0) {
          let structure = this.$store.state.structTypes[index]
          this.selectedStruct = structure
          this.selectedStructIndex = index
          this.$refs.editStructModal.show()
        }
      },
      async updateStructure (index) {
        this.$store.dispatch('updateStruct', {index: this.selectedStructIndex, struct: this.selectedStruct})
      },
      async deleteStruct (index) {
        this.$store.dispatch('deleteStruct', {index: index})
      },
      addField () {
        this.selectedStruct.fields.push({
          name: this.newfield.name,
          type: this.newfield.type
        })
        this.newfield.name = 'field_' + this.selectedStruct.fields.length
      },
      deleteField (index) {
        this.selectedStruct.fields.splice(index, 1)
      }
    }
  }
</script>

<style scoped>
</style>
