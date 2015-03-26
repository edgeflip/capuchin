$(document).ready(function(){
    register_table_sorting();
    init_create_button();
    register_paging();
    init_table_rows();
    // Anchors with rel="external" open their href in a new window.
    $('a[rel="external"]').click(function (event) {
        event.preventDefault();
        window.open(this.href);
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

function init_table_rows(){
    $(".table > tbody > tr").click(function(e){
        console.log(e);
        var url = $(e.currentTarget).data("url");
        console.log(url);
        window.location.href = url;
    });
    $('[data-toggle="tooltip"]').tooltip({
        html:'true',
        container:'body',
        placement:'bottom',
    });
};

function init_create_button(){
    $("ul.nav li a.create").click(function(e){
        $("#modal-title").html(document.title);
        $("#modal-body").html("This is the modal content for:<strong>"+ document.title +"</strong>");
        $("#modal").modal({});
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
