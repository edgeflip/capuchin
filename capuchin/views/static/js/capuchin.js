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
    /* Transform the boost modal for individual posts.
     */
    var modal = $('#boost-modal'),
        // posts
        posts = $('#posts'),
        boostedPost = $('#boosted-post'),
        postBooster = boostedPost.closest('.form-group'),
        postDefaults = $('#engagement').children().not(postBooster),
        // segments
        segments = $('#segments'),
        engagedSegment = $('#engaged-segment'),
        segmentEngager = engagedSegment.closest('.form-group'),
        segmentDefault = segments.closest('.form-group');

    postBooster.hide();
    segmentEngager.hide();

    if (modal.length === 0) {
        return;
    }

    var modalTitle = $('#boost-title'),
        options = ['title', 'post', 'segment'],
        optionParser = function (attrs, key) {
            attrs[key] = this.data(key);
            return attrs;
        },
        lastValues = {};

    function truncate (text, size) {
        var clean = text.trim();
        if (clean.length <= size) {
            return clean;
        } else {
            return clean.substring(0, size - 2).trim() + " \u2026"; 
        }
    }

    modal
    .on('show.bs.modal', function (event) {
        /* Configure modal content given calling button's custom options
         */
        var button = $(event.relatedTarget),
            attrs = options.reduce(optionParser.bind(button), {}),
            postSnippet,
            segmentName;

        if (attrs.title) {
            lastValues.title = modalTitle.text();
            modalTitle.text(attrs.title);
        } else {
            lastValues.title = null;
        }

        if (attrs.post) {
            // Set selected post text and set its id in the true form input
            lastValues.post = posts.val();
            posts.val(attrs.post);
            postSnippet = posts.find('option[value="' + attrs.post + '"]').text();
            if (!postSnippet) {
                // Post isn't in default list;
                // try to grab snippet from button's row in table
                postSnippet = button.closest('tr').find('.post-detail').text();
            }
            boostedPost.text(truncate(postSnippet, 70));
            postDefaults.hide();
            postBooster.show();
        } else {
            lastValues.post = null;
        }

        if (attrs.segment) {
            // Set the selected segment text and set its id in the true form input
            lastValues.segment = segments.val();
            segments.val(attrs.segment);
            segmentName = segments.find('option[value="' + attrs.segment + '"]').text();
            engagedSegment.text(segmentName);
            segmentDefault.hide();
            segmentEngager.show();
        } else {
            lastValues.segment = null;
        }
    })
    .on('hidden.bs.modal', function () {
        /* Revert modal to initial state
         */
        if (lastValues.title) {
            modalTitle.text(lastValues.title);
        }
        if (lastValues.post) {
            posts.val(lastValues.post);
        }
        if (lastValues.segment) {
            segments.val(lastValues.segment);
        }
        postBooster.hide();
        postDefaults.show();
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
