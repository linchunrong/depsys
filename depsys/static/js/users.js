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
       );
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
        );
    });
}