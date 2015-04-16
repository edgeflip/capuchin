// http://jsfiddle.net/mekwall/sgxKJ/

$.widget("ui.autocomplete", $.ui.autocomplete, {
    options : $.extend({}, this.options, {
        multiselect: false
    }),
    _create: function(){
        this._super();

        var self = this,
            o = self.options;

        if (o.multiselect) {
            console.log('multiselect true');

            self.selectedItems = {};
            self.multiselect = $("<div></div>")
                .addClass("ui-autocomplete-multiselect ui-state-default ui-widget form-control")
                .insertBefore(self.element)
                .append(self.element)
                .bind("click.autocomplete", function(){
                    self.element.focus();
                });

            var fontSize = parseInt(self.element.css("fontSize"), 10);
            function autoSize(e){
                // Hackish autosizing
                var $this = $(this);
                $this.width(1).width(this.scrollWidth+fontSize-1);
            };

            var kc = $.ui.keyCode;
            self.element.bind({
                "keydown.autocomplete": function(e){
                    if ((this.value === "") && (e.keyCode == kc.BACKSPACE)) {
                        var prev = self.element.prev();
                        delete self.selectedItems[prev.text()];
                        prev.remove();
                    }
                },
                // TODO: Implement outline of container
                "focus.autocomplete blur.autocomplete": function(){
                    self.multiselect.toggleClass("ui-state-active");
                },
                "keypress.autocomplete change.autocomplete focus.autocomplete blur.autocomplete": autoSize
            }).trigger("change");

            if(o.values){
                for(var v in o.values){
                    var val = o.values[v];
                    var item = $("<div data-value='"+val+"'></div>")
                        .addClass("ui-autocomplete-multiselect-item")
                        .text(val)
                        .append(
                            $(" <span aria-hidden='true'> &times;</span>")
                                .click(function(){
                                    var item = $(this).parent();
                                    console.log(item);
                                    delete self.selectedItems[item.text()];
                                    console.log(self.selectedItems);
                                    o.delete(item, self);
                                    item.remove();
                                })
                        )
                        .insertBefore(self.element);

                    self.selectedItems[val] = item;
                }
            }

            // TODO: There's a better way?
            o.select = o.select || function(e, ui) {
                $("<div data-value='"+ui.item.label+"'></div>")
                    .addClass("ui-autocomplete-multiselect-item")
                    .text(ui.item.label)
                    .append(
                        $(" <span aria-hidden='true'> &times;</span>")
                            .click(function(){
                                var item = $(this).parent();
                                console.log(item);
                                delete self.selectedItems[item.text()];
                                o.delete(item, self);
                                item.remove();
                            })
                    )
                    .insertBefore(self.element);

                self.selectedItems[ui.item.label] = ui.item;
                self._value("");
                return false;
            }

            /*self.options.open = function(e, ui) {
                var pos = self.multiselect.position();
                pos.top += self.multiselect.height();
                self.menu.element.position(pos);
            }*/
        }

        return this;
    }
});
