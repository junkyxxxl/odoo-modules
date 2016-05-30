(function(){
  'use strict';
  var website = openerp.website;
  var session_editor = new openerp.Session();
  var _t = openerp._t;
//  var ajax = require('web.ajax');
//var core = require('web.core');
//var base = require('web_editor.base');
//var widget = require('web_editor.widget');
//var animation = require('web_editor.snippets.animation');
//var options = require('web_editor.snippets.options');
//var snippet_editor = require('web_editor.snippet.editor');
//var website = require('website.website');
//var Model = require('web.Model');

//var _t = core._t;
//var qweb = core.qweb;
//

//options.registry.js_get_objects = options.Class.extend({
website.snippet.options.js_get_objects = website.snippet.Option.extend({
	drop_and_build_snippet: function(){
	      var self = this;
	      
	      if (!self.$target.data('snippet-view')) {    	  
	        this.$target.data("snippet-view", new website.snippet.animationRegistry.js_get_objects(this.$target));
	      }
	    },
	    clean_for_save:function(){
		      this.$target.empty();
	    }	
});

website.snippet.options.js_get_objects_in_row =  website.snippet.Option.extend({
	start:function(){
      var self = this;
      setTimeout(function(){
        var ul = self.$overlay.find(".snippet-option-js_get_objects_in_row > ul");
        if (self.$target.attr("data-objects_in_row")) {
          var in_row = self.$target.attr("data-objects_in_row");
          ul.find('li[data-objects_in_row="' + in_row + '"]').addClass("active");
        } else {
          ul.find('li[data-objects_in_row="1"]').addClass("active");
        }
      },100)
    },
    objects_in_row:function(type, value, $li){
      var self = this;
      if(type != "click"){return}
      value = parseInt(value);
      this.$target.attr("data-objects_in_row",value)
                  .data("objects_in_row",value)
                  .data('snippet-view').redrow(true);
      setTimeout(function(){
        $li.parent().find("li").removeClass("active");
        $li.addClass("active");
      },100); 
    }

});


website.snippet.options.js_get_objects_limit =  website.snippet.Option.extend({
	start:function(){
      var self = this;
      setTimeout(function(){
        var ul = self.$overlay.find(".snippet-option-js_get_objects_limit > ul");
        if (self.$target.attr("data-objects_limit")) {
          var limit = self.$target.attr("data-objects_limit");
          ul.find('li[data-objects_limit="' + limit + '"]').addClass("active");
        } else {
          ul.find('li[data-objects_limit="1"]').addClass("active");
        }
      },100)
    },
    objects_limit:function(type, value, $li){
      var self = this;
      if(type != "click"){return}
      value = parseInt(value);
      this.$target.attr("data-objects_limit",value)
                  .data("objects_limit",value)
                  .data('snippet-view').redrow(true);
      setTimeout(function(){
        $li.parent().find("li").removeClass("active");
        $li.addClass("active");
      },100); 
    }

});


website.snippet.options.js_get_objects_in_slide =  website.snippet.Option.extend({
	start:function(){
	      var self = this;
	      setTimeout(function(){
	        var ul = self.$overlay.find(".snippet-option-js_get_objects_in_slide > ul");
	        if (self.$target.attr("data-objects_in_slide")) {
	          var prd_limit = self.$target.attr("data-objects_in_slide");
	          ul.find('li[data-objects_in_slide="' + prd_limit + '"]').addClass("active");
	        } else {
	          ul.find('li[data-objects_in_slide="4"]').addClass("active");
	        }
	      },100)
	    },
	    objects_in_slide:function(type, value, $li){
	      var self = this;
	      if(type != "click"){return}
	      value = parseInt(value);
	      this.$target.attr("data-objects_in_slide",value)
	                  .data("objects_in_slide",value)
	                  .data('snippet-view').redrow(true);
	      setTimeout(function(){
	        $li.parent().find("li").removeClass("active");
	        $li.addClass("active");
	      },100); 
	    }
});

website.snippet.options.js_get_objects_selectFilter =  website.snippet.Option.extend({
	start: function() {
	      this._super();
	      var self      = this;
	      var model     =  session_editor.model('ir.filters');
	      var CategoriesList = [];

	      model
	      .call('search_read', 
	      [
			[['context','not like','group_by'],['model_id','=',self.$target.attr("data-object_name")]],
	        ['name','id']// attributes to get
	      ],  
	      {} )
	      .then(function(filters){
	        self.createfiltersList(filters)
	      }) 
	      .fail(function (e) {
	        // No data
	        var title = _t("Oops, Huston we have a problem"),
	            msg   = $("<div contenteditable='false' class='message error text-center'><h3>"+ title +"</h3><code>"+ e.data.message + "</code></div>" );
	        self.$target.append(msg)
	        return;
	      });
	    },

	    createfiltersList: function(filters){
	      var self = this;
	      var ul = null;
	      setTimeout(function(){
	        ul = self.$overlay.find(".snippet-option-js_get_objects_selectFilter > ul");
	        $(filters).each(function(){
	          var filter = $(this);
	          var li = $('<li data-filter_by_filter_id="' + filter[0].id + '"><a>' + filter[0].name + '</a></li>');
	          ul.append(li);
	        });
	        if (self.$target.attr("data-filter_by_filter_id")) {
	          var id = self.$target.attr("data-filter_by_filter_id");
	          ul.find("li[data-filter_by_filter_id=" + id  + "]").addClass("active");
	        }
	      },100)
	    },

	    filter_by_filter_id:function(type, value, $li){
	      var self = this;
	      if(type == "click"){
	        $li.parent().find("li").removeClass("active");
	        $li.addClass("active");
	        value = parseInt(value);
	        self.$target.attr("data-filter_by_filter_id",value)
	                    .data("filter_by_filter_id",value)
	                    .data('snippet-view').redrow(true); 
	      }
	    }
	  });

})();
