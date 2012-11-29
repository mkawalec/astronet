!function(a){"use strict";var b=function(b,c){this.options=c;this.$element=a(b).delegate('[data-dismiss="modal"]','click.dismiss.modal',a.proxy(this.hide,this));};b.prototype={constructor:b,toggle:function(){return this[!this.isShown?'show':'hide']();},show:function(){var b=this,c=a.Event('show');this.$element.trigger(c);if(this.isShown||c.isDefaultPrevented())return;a('body').addClass('modal-open');this.isShown=true;g.call(this);e.call(this,function(){var c=a.support.transition&&b.$element.hasClass('fade');if(!b.$element.parent().length)b.$element.appendTo(document.body);b.$element.show();if(c)b.$element[0].offsetWidth;b.$element.addClass('in');c?b.$element.one(a.support.transition.end,function(){b.$element.trigger('shown');}):b.$element.trigger('shown');});},hide:function(b){b&&b.preventDefault();var e=this;b=a.Event('hide');this.$element.trigger(b);if(!this.isShown||b.isDefaultPrevented())return;this.isShown=false;a('body').removeClass('modal-open');g.call(this);this.$element.removeClass('in');a.support.transition&&this.$element.hasClass('fade')?c.call(this):d.call(this);}};function c(){var b=this,c=setTimeout(function(){b.$element.off(a.support.transition.end);d.call(b);},500);this.$element.one(a.support.transition.end,function(){clearTimeout(c);d.call(b);});}function d(a){this.$element.hide().trigger('hidden');e.call(this);}function e(b){var c=this,d=this.$element.hasClass('fade')?'fade':'';if(this.isShown&&this.options.backdrop){var e=a.support.transition&&d;this.$backdrop=a('<div class="modal-backdrop '+d+'" />').appendTo(document.body);if(this.options.backdrop!='static')this.$backdrop.click(a.proxy(this.hide,this));if(e)this.$backdrop[0].offsetWidth;this.$backdrop.addClass('in');e?this.$backdrop.one(a.support.transition.end,b):b();}else if(!this.isShown&&this.$backdrop){this.$backdrop.removeClass('in');a.support.transition&&this.$element.hasClass('fade')?this.$backdrop.one(a.support.transition.end,a.proxy(f,this)):f.call(this);}else if(b)b();}function f(){this.$backdrop.remove();this.$backdrop=null;}function g(){var b=this;if(this.isShown&&this.options.keyboard)a(document).on('keyup.dismiss.modal',function(a){a.which==27&&b.hide();});else if(!this.isShown)a(document).off('keyup.dismiss.modal');}a.fn.modal=function(c){return this.each(function(){var d=a(this),e=d.data('modal'),f=a.extend({},a.fn.modal.defaults,d.data(),typeof c=='object'&&c);if(!e)d.data('modal',(e=new b(this,f)));if(typeof c=='string')e[c]();else if(f.show)e.show();});};a.fn.modal.defaults={backdrop:true,keyboard:true,show:true};a.fn.modal.Constructor=b;a(function(){a('body').on('click.modal.data-api','[data-toggle="modal"]',function(b){var c=a(this),d,e=a(c.attr('data-target')||(d=c.attr('href'))&&d.replace(/.*(?=#[^\s]+$)/,'')),f=e.data('modal')?'toggle':a.extend({},e.data(),c.data());b.preventDefault();e.modal(f);});});}(window.jQuery);