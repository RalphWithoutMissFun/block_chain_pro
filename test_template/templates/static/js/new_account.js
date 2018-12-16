$(document).ready(function(){
　　$("#newer").click(function(){
　　　　user_name = $("#user_name").val()
        //alert(user_name)
        window.location.href = "/new_account/"+user_name
        //$(location).attr('href', '/new_account/'+username);
　　});
});