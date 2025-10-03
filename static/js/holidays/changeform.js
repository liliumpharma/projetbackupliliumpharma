$(document).ready(function(){
    var id = window.location.href.split("/")[6]
    $('.object-tools').append('<a class="btn btn-block btn-primary btn-sm" href="/holidays/'+id+'">Imprimer titre de congé</a>')
})