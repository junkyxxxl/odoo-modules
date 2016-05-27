openerp.bec_salesagent = function(instance){
    var mail = instance.mail // loading the namespace of the 'sample' module

    mail.ThreadComposeMessage.include({
        on_toggle_quick_composer: function (event) {
            var self = this;
            var $input = $(event.target);
            this.compute_emails_from();
            var email_addresses = _.pluck(this.recipients, 'email_address');
            var suggested_partners = $.Deferred();

            // if clicked: call for suggested recipients
            if (event.type == 'click') {
                this.is_log = $input.hasClass('oe_compose_log');
                suggested_partners = this.parent_thread.ds_thread.call('message_get_suggested_recipients', [[this.context.default_res_id], this.context]).done(function (additional_recipients) {
                    var thread_recipients = additional_recipients[self.context.default_res_id];
                    _.each(thread_recipients, function (recipient) {
                        var parsed_email = mail.ChatterUtils.parse_email(recipient[1]);
                        if (_.indexOf(email_addresses, parsed_email[1]) == -1) {
                            self.recipients.push({
                                'checked': false,
                                'partner_id': recipient[0],
                                'full_name': recipient[1],
                                'name': parsed_email[0],
                                'email_address': parsed_email[1],
                                'reason': recipient[2],
                            })
                        }
                    });
                });
            }
            else {
                suggested_partners.resolve({});
            }

            // when call for suggested partners finished: re-render the widget
            $.when(suggested_partners).pipe(function (additional_recipients) {
                if ((!self.stay_open || (event && event.type == 'click')) && (!self.show_composer || !self.$('textarea:not(.oe_compact)').val().match(/\S+/) && !self.attachment_ids.length)) {
                    self.show_composer = !self.show_composer || self.stay_open;
                    self.reinit();
                }
                if (!self.stay_open && self.show_composer && (!event || event.type != 'blur')) {
                    self.$('textarea:not(.oe_compact):first').focus();
                }
            });

            return suggested_partners;
        },
    });

};