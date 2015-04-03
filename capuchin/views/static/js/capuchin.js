$(document).ready(function () {
    register_table_sorting();
    register_paging();
    init_table_rows();

    // Anchors with rel="external" open their href in a new window.
    $('a[rel=external]').click(function (event) {
        event.preventDefault();
        window.open(this.href);
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
});


function notify(cls, message){
    $("#notifications").html("<div class=\"alert alert-"+cls+" alert-dismissible\" role=\"alert\"> \
        <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button> \
        <p id=\"notification\">"+message+"</p> \
    </div>");
    setTimeout(function(){
        $(".alert").remove();
    }, 5000);
}

function init_table_rows() {
    $(".table > tbody > tr[data-url]").click(function(event) {
        if ($(event.target).data('toggle') !== 'modal') {
            window.location.href = $(event.currentTarget).data('url');
        }
    });
    $('[data-toggle="tooltip"]').tooltip({
        html:'true',
        container:'body',
        placement:'bottom',
    });
};


function register_table_sorting(){
    $(".table_sort").click(function(e){
        e.preventDefault();
        var url = $(e.target).attr('href');
        var id = $(e.target).data("id");
        $.ajax({
            url: url,
            success: function(data){
                $("#"+id).replaceWith(data);
                register_table_sorting();
                register_paging();
                init_table_rows();
            }
        });
        return false;
    });
};

function register_paging(){
    $(".pager").click(function(e){
        e.preventDefault();
        var url = $(e.target).attr('href');
        var id = $(e.target).data("id");
        $.ajax({
            url: url,
            success: function(data){
                $("#"+id).replaceWith(data);
                register_table_sorting();
                register_paging();
                init_table_rows();
            }
        });
        return false;
    });
};
