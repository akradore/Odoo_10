odoo.define('biztech_report_template.biz_color', function(require) {
    "use strict";

    var core = require('web.core');
    var form_widgets = require('web.form_widgets');
    var _t = core._t;

    // for colorpicker library import
    var colpick = window.colpick;

    core.search_widgets_registry.add('biz_color', 'instance.web.search.CharField');

    var BizColorPicker = form_widgets.FieldChar.extend({
        template: 'BizColorPicker',
        widget_class: 'oe_form_biz_color_picker',
        store_dom_value: function() {
            if (!this.get('effective_readonly') && this.$('input').length && this.is_syntax_valid()) {
                this.internal_set_value(
                    this.parse_value(
                        this.$('input').val()));
            }
        },
        is_syntax_valid: function() {
            var $input = this.$('input');
            if (!this.get("effective_readonly") && $input.size() > 0) {
                var val = $input.val();
                var isOk = /^#[0-9A-F]{6}$/i.test(val);
                if (!isOk) {
                    return false;
                }
                try {
                    this.parse_value(this.$('input').val(), '');
                    return true;
                } catch (e) {
                    return false;
                }
            }
            return true;
        },
        render_value: function() {
            var show_value = this.format_value(this.get('value'), '');
            if (!this.get("effective_readonly")) {
                var $input = this.$el.find('input');
                $input.val(show_value);
                $input.css("background-color", show_value)
                $input.colpick({
                    onSubmit:function(hsb,hex,rgb,el,bySetColor) {
                        $(el).val('#'+hex);
                        $(el).colpickHide();
                    },
                    onChange:function(hsb,hex,rgb,el,bySetColor) {
                        $(el).val('#'+hex);
                        $input.css('backgroundColor', '#' + hex);
                    },
                });
            } else {
                this.$(".oe_form_char_content").text(show_value);
                this.$('div').css("background-color", show_value)
            }
        }
    });

    core.form_widget_registry.add('biz_color', BizColorPicker);

});