openerp.mail_message_move = function (instance) {
    instance.mail.ThreadMessage = instance.mail.ThreadMessage.extend({
        template: 'mail.thread.message',
        
        bind_events: function () {
            var self = this;
            this._super();
            this.$('.oe_attach').on('click', this.on_message_attach);
        },        
        
        on_message_attach: function (event) {
            event.stopPropagation();

           var self=this;
           var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'wizard.message.attach',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {'message_id':self.id}
		    };
		    instance.webclient.action_manager.do_action(action);            
            
            return false;
        },        
        
    });    
};
