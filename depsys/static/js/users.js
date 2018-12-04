// delete user func
function del_user(msg){
   layer.confirm('确定删除？', {
       btn: ['确定','取消'] //按钮
   }, function(){
       // use ajax post data to backend
       $.post('/users',
           {
               action: 'del_user',
               user_id: msg
           },
           function () {
               //window.location.reload();
               // remove the relate tr element from html
               $('#'+msg).remove();
               layer.msg('id: ' + msg + ' 已删除！', {icon: 1});
           }
       )
           .fail(function () {
                layer.msg('发生错误！', {icon: 2});
           });
   }, function(){
       layer.msg('已取消', {
           time: 2000 //2s后自动关闭
       });
   });
}
// reset user password
function pwd_reset(msg) {
    layer.prompt({title: '输入新密码，并确认', formType: 1}, function(pass, index){
        layer.close(index);
        // use ajax post data to backend
        $.post('/users',
            {
                action: 'pwd_reset',
                user_id: msg,
                password: pass
            },
            function () {
                layer.msg('id: ' + msg + ' 密码已更新！', {icon: 1});
            }
        )
            .fail(function () {
                layer.msg('发生错误！', {icon: 2});
            });
    });
}
// user enable switch
$(document).ready(function(){
    $("input[type='checkbox']").change(function() {
        // is(':checked') return true/false
        var enable = $("#" + this.id).is(':checked');
        var username = this.id;
        var user_id = this.value;
        // use ajax post data to backend
        $.post('/users',
            {
                action: 'enable_change',
                user_id: user_id,
                enable: enable
            },
            function () {
                if (enable){
                    layer.msg('用户: ' + username + ' 已启用！', {icon: 1});
                }
                else {
                    layer.msg('用户: ' + username + ' 已禁用！', {icon: 2});
                }
                return false;
            }
        )
            .fail(function () {
                layer.msg('发生错误！', {icon: 2});
            });
    });
});
// user role change,
function role_change(role_id,user_id) {
    // use ajax post data to backend
    $.post('/users',
        {
            action: 'role_change',
            user_id: user_id,
            role: role_id
        },
        function () {
            layer.msg('用户角色已更改！', {icon: 1});
            return false;
        }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
        });
}
