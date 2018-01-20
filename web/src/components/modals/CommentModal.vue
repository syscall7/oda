<template>
  <div>
    <b-modal ref="commentModal" size="lg" @ok="ok" title="Edit Comment" no-fade @hidden="onHidden">
      <div class="form-group">
        <label for="commentInput">Comment On Address 0x{{address | hex}}</label>
        <input ref="inputField" type="text"
               v-on:keyup.enter="ok"
               class="form-control"
               id="commentInput"
               placeholder="Comment ..."
               v-model="comment">
        <!-- <small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small> -->
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {bus, SHOW_COMMENT_MODAL, MODAL_HIDDEN} from '../../bus'

  export default {
    name: 'CommentModal',
    data () {
      return {
        address: null,
        comment: null
      }
    },
    methods: {
      onHidden () {
        bus.$emit(MODAL_HIDDEN)
      },
      async ok () {
        await this.$store.dispatch('addComment', {comment: this.comment, vma: this.address})
        this.$refs.commentModal.hide()
      }
    },
    created () {
      const self = this
      bus.$on(SHOW_COMMENT_MODAL, function (event) {
        self.address = event.addr
        if (self.$store.getters.commentsByAddress[self.address]) {
          self.comment = self.$store.getters.commentsByAddress[self.address].comment
        } else {
          self.comment = ''
        }
        self.$refs.commentModal.show()
        setTimeout(() => {
          self.$refs.inputField.setSelectionRange(0, self.comment.length)
          self.$refs.inputField.focus()
        }, 1)
      })
    }
  }
</script>

<style scoped></style>

