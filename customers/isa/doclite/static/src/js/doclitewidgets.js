openerp.doclite = function (instance) {

    instance.doclite.DocliteUrlWidget = instance.web.form.FieldUrl.extend({
        template: 'FieldUrl',

        render_value: function () {

		    var name_url = this.get('value');
		    if (name_url && typeof name_url.split  === 'function') {
		      var spl = name_url.split(",",2);
		      var fileName = spl[0];
		      var url = spl[1];
		      if (!url) {
			    this.$el.find('a').attr('href', '#').text('');
			    return;
		      }
		      var s = /(\w+):(.+)/.exec(url);
		      if (!s) {
			    url = "http://" + url;
		      }
		      this.$el.find('a').attr('href', url).attr('target','new').text(fileName);
		    }
        }
    });
    instance.web.form.widgets.add('nameandurl', 'instance.doclite.DocliteUrlWidget');
};
