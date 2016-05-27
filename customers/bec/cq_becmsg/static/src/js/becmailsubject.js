openerp.cq_becmsg = function(instance) {
  var module = instance.mail;
  module.ThreadComposeMessage = module.ThreadComposeMessage.extend({
// in prima approssimazione ricopio le funzioni per applicare le modifiche segnate con ***
        bind_events: function () {
            var self = this;
            this.$('.oe_compact_inbox').on('click', self.on_toggle_quick_composer);
            this.$('.oe_compose_post').on('click', self.on_toggle_quick_composer);
            this.$('.oe_compose_log').on('click', self.on_toggle_quick_composer);
            this.$('input.oe_form_binary_file').on('change', _.bind( this.on_attachment_change, this));
            this.$('.oe_cancel').on('click', _.bind( this.on_cancel, this));
            this.$('.oe_post').on('click', self.on_message_post);
            this.$('.oe_full').on('click', _.bind( this.on_compose_fullmail, this, this.id ? 'reply' : 'comment'));
            /* stack for don't close the compose form if the user click on a button */
            this.$('.oe_msg_left, .oe_msg_center').on('mousedown', _.bind( function () { this.stay_open = true; }, this));
// ***        this.$('.oe_msg_left, .oe_msg_content').on('mouseup', _.bind( function () { this.$('textarea').focus(); }, this));
            var ev_stay = {};
            ev_stay.mouseup = ev_stay.keydown = ev_stay.focus = function () { self.stay_open = false; };
            this.$('textarea').on(ev_stay);
            this.$('textarea').autosize();

            // auto close
            this.$('textarea').on('blur', self.on_toggle_quick_composer);
            // event: delete child attachments off the oe_msg_attachment_list box
            this.$(".oe_msg_attachment_list").on('click', '.oe_delete', this.on_attachment_delete);

            this.$(".oe_recipients").on('change', 'input', this.on_checked_recipient);
       if (this.context.default_model=='res.partner') {
// se il modello e' res.partner leggo il nome del cliente/fornitore e lo metto nel context
            var model = new instance.web.Model(this.context.default_model);
            var self = this;
            model.query(['name'])
             .filter([['id', '=', this.context.default_res_id]])
             .limit(1)
             .all().then(function (xxusers) {
               self.context.nome = 'R: '+xxusers[0]['name'];
             });
        } else self.context.nome = '';
        },
        
        do_send_message_post: function (partner_ids, log) {
            var self = this;
            var values = {
                'body': this.$('textarea').val(),
                'subject': this.$('input').val(),		// *** aggiunta
                'parent_id': this.context.default_parent_id,
                'attachment_ids': _.map(this.attachment_ids, function (file) {return file.id;}),
                'partner_ids': partner_ids,
                'context': _.extend(this.parent_thread.context, {
                    'mail_post_autofollow': true,
                    'mail_post_autofollow_partner_ids': partner_ids,
                }),
                'type': 'comment',
                'content_subtype': 'plaintext',
            };
            if (log) {
                values['subtype'] = false;
            }
            else {
                values['subtype'] = 'mail.mt_comment';   
            }
            this.parent_thread.ds_thread._model.call('message_post', [this.context.default_res_id], values).done(function (message_id) {
                var thread = self.parent_thread;
                var root = thread == self.options.root_thread;
                if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
                    var thread = thread.parent_message.parent_thread;
                }
                // create object and attach to the thread object
                thread.message_fetch([["id", "=", message_id]], false, [message_id], function (arg, data) {
                    var message = thread.create_message_object( data[0] );
                    // insert the message on dom
                    thread.insert_message( message, root ? undefined : self.$el, root );
                });
                self.on_cancel();
                self.flag_post = false;
            });
        },

  });
}