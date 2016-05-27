openerp.project_omniapart = function(openerp) {
    // Disables the Drag&Drop to different groups for Kanban view for projects
    openerp.web_kanban.KanbanView.include({
        on_record_moved : function(record, old_group, old_index, new_group, new_index) {
            var self = this;
            record.$el.find('[title]').tooltip('destroy');
            $(old_group.$el).add(new_group.$el).find('.oe_kanban_aggregates, .oe_kanban_group_length').hide();

            if (self.dataset.model === 'project.task') {
	            new_group.records.splice(old_index, 1);
	            new_group.records.splice(new_index, 0, record);
	            new_group.do_save_sequences();
            } else {
                this._super.apply(this, arguments);
            }

        }
    });
};
