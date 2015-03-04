$(document).ready(function(){
    register_table_sorting();
    init_create_button();
    register_paging();
});


function init_create_button(){
    $("ul.nav li a.create").click(function(e){
        $("#modal-title").html(document.title);
        $("#modal-body").html("This is the modal content for:<strong>"+ document.title +"</strong>");
        $("#modal").modal({});
    });
}

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
            }
        });
        return false;
    });
}

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
            }
        });
        return false;
    });
}
