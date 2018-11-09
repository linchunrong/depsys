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
           layer.msg('id: ' + msg + ' 已删除！', {icon: 1})
       );
   }, function(){
       layer.msg('已取消', {
           time: 2000 //2s后自动关闭
       });
   });
};
// reset user password func
function pwd_reset(msg) {
    $.post('/users',
        {
            action: 'pwd_reset',
			name: msg
		},
		function(data,status){
			alert("数据: \n" + data + "\n状态: " + status);
		});
};