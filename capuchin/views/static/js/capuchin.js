$(document).ready(function () {
    /* Anchors with rel="external" open their href in a new window.
     */
    $('body').on('click', 'a[rel=external]', function (event) {
        event.preventDefault();
        window.open(this.href);
    });
}).ready(function () {
    /* Table rows with the data-url attribute act like anchors.
    */
    $('body').on('click', '.table > tbody > tr[data-url]', function (event) {
        if ($(event.target).data('toggle') !== 'modal') {
            window.location.href = $(event.currentTarget).data('url');
        }
    });
}).ready(function () {
    /* Table header and "pager" anchors, and table-mutating buttons, load new table
     * data and trigger event "capuchin.table.load".
     */
    function insertResult (result) {
        var id = this.data('id'),
            oldTable = $('#' + id),
            newTable = $(result);

        oldTable.replaceWith(newTable);
        newTable.trigger('capuchin.table.load');
    }
    $('body').on('click', '.pager, .table_sort, .table-change', function (event) {
        event.preventDefault();
        var target = $(event.target),
            url = target.data('refresh') || target.attr('href');

        $.ajax({url: url, success: insertResult.bind(target)});
    });
}).ready(function () {
    /* Enable an "intermediary" modal to pass its invoking DOM element's
     * attribute data to its target modal via the intermediary's "show" event.
     */
    $('.modal-intermediary').on('show.bs.modal', function (event) {
        $(this).find('[data-toggle=modal]').data('showEvent', event);
    });
}).ready(function () {
    /* Transform notification modals for individual posts and segments.
     */
    function parseOptions (event, attrs, keys) {
        var caller = $(event.relatedTarget),
            intermediateEvent = caller.data('showEvent'),
            remainder = [];

        if (attrs === undefined) attrs = {};
        if (keys === undefined) keys = ['title', 'post', 'segment'];

        var index, key, value;
        for (index = 0; index < keys.length; index++) {
            key = keys[index];
            value = caller.data(key);
            if (value) {
                attrs[key] = value;
            } else {
                remainder.push(key);
            }
        }

        // Continue (even if remainder empty) so as to discover call chain initiator.
        if (intermediateEvent) {
            return parseOptions(intermediateEvent, attrs, remainder);
        }

        // We've exhausted the call chain.
        attrs.initiator = caller;
        return attrs;
    }

    var Modal = function (modal) {
        var root = $(modal),
            lastValues = root.data('lastValues');

        if (!lastValues) {
            lastValues = {};
            root.data('lastValues', lastValues);
        }

        return {
            root: root,
            lastValues: lastValues,
            title: root.find('.modal-title'),
            // posts
            posts: root.find('[name=posts]'),
            postBooster: root.find('.post-booster'),
            boostedPost: root.find('.boosted-post'),
            postDefaults: root.find('.engagement'),
            // segments
            segments: root.find('[name=segments]'),
            segmentEngager: root.find('.segment-engager'),
            engagedSegment: root.find('.engaged-segment'),
            segmentDefault: root.find('.audience')
        };
    };

    function truncate (text, size) {
        var clean = text.trim();
        if (clean.length <= size) {
            return clean;
        } else {
            return clean.substring(0, size - 2).trim() + " \u2026"; 
        }
    }

    $('.modal-notification')
    .on('show.bs.modal', function (event) {
        /* Configure modal content given calling button's custom options
         */
        var modal = Modal(this),
            attrs = parseOptions(event),
            postSnippet,
            segmentName;

        if (attrs.title) {
            modal.lastValues.title = modal.title.text();
            modal.title.text(attrs.title);
        } else {
            modal.lastValues.title = null;
        }

        if (attrs.post) {
            // Set selected post text and set its id in the true form input
            modal.lastValues.post = modal.posts.val();
            modal.posts.val(attrs.post);

            postSnippet = modal.posts.find('option[value="' + attrs.post + '"]').text();
            if (!postSnippet) {
                // Post isn't in default list;
                // try to grab snippet from button's row in table
                postSnippet = attrs.initiator.closest('tr').find('.post-detail').text();
            }
            modal.boostedPost.text(truncate(postSnippet, 70));

            modal.postDefaults.removeClass('on');
            modal.postBooster.addClass('on');
        } else {
            modal.lastValues.post = null;
        }

        if (attrs.segment) {
            // Set the selected segment text and set its id in the true form input
            modal.lastValues.segment = modal.segments.val();
            modal.segments.val(attrs.segment);

            segmentName = modal.segments.find('option[value="' + attrs.segment + '"]').text();
            modal.engagedSegment.text(segmentName);

            modal.segmentDefault.removeClass('on');
            modal.segmentEngager.addClass('on');
        } else {
            modal.lastValues.segment = null;
        }
    })
    .on('hidden.bs.modal', function () {
        /* Revert modal to initial state
         */
        var modal = Modal(this);

        if (modal.lastValues.title) {
            modal.title.text(modal.lastValues.title);
        }
        if (modal.lastValues.post) {
            modal.posts.val(modal.lastValues.post);
        }
        if (modal.lastValues.segment) {
            modal.segments.val(modal.lastValues.segment);
        }

        modal.postBooster.add(modal.segmentEngager).removeClass('on');
        modal.postDefaults.add(modal.segmentDefault).addClass('on');
    });
}).ready(function () {
    /* Transform deletion modals for individual objects.
     */
    $('.modal-remove')
    .on('show.bs.modal', function (event) {
        var modal = $(this),
            caller = $(event.relatedTarget),
            object = caller.closest('[data-object]'),
            objectId = object.data('object'),
            columns = object.find('td'),
            name = columns.first().text(),
            table = caller.closest('[data-source]'),
            refreshUrl = table.data('source'),
            tableWrapper = table.closest('[id^=table]'),
            tableId = tableWrapper.attr('id');

        modal.find('.object-name').text(name);
        modal.find('[data-action=delete-object]').data({
            target: objectId,

            // Below data attrs for .table-change handler:
            id: tableId,
            refresh: refreshUrl
        });
    })
    .on('hidden.bs.modal', function () {
        var modal = $(this);

        modal.find('.object-name').text('');
        modal.find('[data-action=delete-object]').data({
            target: '',
            id: '',
            refresh: ''
        });
    });

    function hideModal () {
        /* Close modal
         */
        this.closest('.modal-remove').modal('hide');
    }

    $('[data-action=delete-object]').click(function () {
        var $this = $(this),
            objectId = $this.data('target'),
            postUrl = objectId && '/audience/segment/' + objectId + '/delete';

        if (objectId) {
            // FIXME: Would be better, e.g., to pause only event propagation, until this
            // (async) call is complete, rather than lock the entire process (sync).
            $.ajax(postUrl, {async: false, method: 'POST', complete: hideModal.bind($this)});
        }
        // table refresh will be taken care of by .table-change handler
    });
}).ready(function () {
    /* self-delivery forms submit their contents asynchronously and deliver the results to their target.
    */
    // Functional helpers //
    function getControlByName (controlName) {
        // Bound to native form
        return this.elements[controlName];
    }

    function unsatisfactory (control) {
        return ! $(control).val();
    }

    function controlName (control) {
        return control.name;
    }

    function showErrors (_index, element) {
        // Bound to array of names of controls with erroneous input
        var $element = $(element), // current form error element
            target = $element.data('error'), // its form control
            on = this.indexOf(target) > -1; // its error status

        $element.toggleClass('on', on);
        $element.closest('.form-group').toggleClass('has-error', on);
    }

    function startRequest () {
        // bound to jQuery wrapper of form
        this.find('[type=submit]').prop('disabled', true);
    }

    function endRequest () {
        // bound to jQuery wrapper of form
        this.find('[type=submit]').prop('disabled', false);
    }

    function showResult (data) {
        // bound to jQuery wrapper of form
        $(this.data('target')).html(data);
    }

    function deliver (event) {
        var form = this,
            $form = $(this),
            requireSpec = $form.data('require'),
            requiredControls = requireSpec && requireSpec.split(/ +/).map(getControlByName, form),
            errorControls = requiredControls && requiredControls.filter(unsatisfactory),
            errorNames = errorControls && errorControls.map(controlName);

        if (errorNames && errorNames.length > 0) {
            $form.find('[data-error]').each(showErrors.bind(errorNames));
        } else {
            $form.find('[data-error]').removeClass('on');
            startRequest.call($form);
            $.ajax(form.action, {
                data: $form.serialize(),
                method: form.method
            })
            .done(showResult.bind($form))
            .always(endRequest.bind($form));
        }

        event.preventDefault();
    }

    // TODO: upon type, remove errors?
    $('.self-delivery').submit(deliver);
});

(function () {

    function insertReachCharts (result) {
        var data = result.data,
            element, key, values, value, valueBox, barValue, barBox;

        for (var index = 0; index < this.length; index++) {
            element = this.eq(index),
            key = 'post.' + element.data('post') + '.post_impressions_unique.lifetime',
            values = data[key],
            value = values ? values['post_impressions_unique'] : undefined;

            if (value === undefined) {
                element.addClass('text-center').html("&ndash;");
                continue;
            }

            valueBox = $('<span></span>', {'class': 'reach-value', 'text': value});

            barValue = $('<span></span>', {'class': 'bar-value'}).css({
                display: 'inline-block',
                height: '100%',
                width: (2 * Math.atan(value / 1000) / Math.PI) * 100 + '%' // TODO: tweak? according to global?
            });

            barBox = $('<span></span>', {'class': 'bar'}).css({
                'float': 'right',
                'min-height': '1px',
                'text-align': 'left',
            }).append(barValue);

            element.addClass('text-right').html(valueBox).append(barBox);
        }
    }

    $(document).on('capuchin.table.load ready', function (event) {
        var target = $(event.target);

        /* Can't delegate tooltip(), so reset each time a table is loaded.
         */
        target.find('[data-toggle=tooltip]').tooltip({
            html: 'true',
            container: 'body',
            placement: 'bottom'
        });

        /* Fill in post tables' "Reach" column with data from the "post reach"
        * dashboard chart endpoint.
        */
        var reachCharts = target.find('.post-reach-chart');
        if (reachCharts.length > 0) {
            $.getJSON(
                '/chart/post_reach',
                {
                    fbid: reachCharts.map(function () {
                        return $(this).data('post');
                    }).get()
                },
                insertReachCharts.bind(reachCharts)
            );
        }
    });

})();

function notify(cls, message){
    $("#notifications").html("<div class=\"alert alert-"+cls+" alert-dismissible\" role=\"alert\"> \
        <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button> \
        <p id=\"notification\">"+message+"</p> \
    </div>");
    setTimeout(function(){
        $(".alert").remove();
    }, 5000);
}

var capuchin = {};
