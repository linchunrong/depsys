// ansible verify
function verify_ansible() {
    var path = $("#ansible_path").val();
    // use ajax post data to backend
    $.post('/verify',
        {
            action: 'verify_ansible',
            path: path
        },
        function (result) {
                if (result.startsWith('Error')){
                    layer.msg(result, {time: 3000, icon: 2});
                }
                else {
                    layer.msg('结果：' + result, {icon: 1});
                }
                return false;
            }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
        });
}
// repository connect verify
function verify_repository() {
    var repo_address = $("#repo_address").val();
    var repo_user = $("#repo_user").val();
    var repo_pwd = $("#repo_pwd").val();
    // use ajax post data to backend
    $.post('/verify',
        {
            action: 'verify_repository',
            repo_address: repo_address,
            repo_user: repo_user,
            repo_pwd: repo_pwd
        },
        function (result) {
            if (result.startsWith('Error')){
                layer.msg(result, {time: 5000, icon: 2});
            }
            else {
                layer.msg('连接成功！', {icon: 1});
            }
            return false;
        }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
        });
}
// email verify
function verify_email() {
    layer.prompt({title: '输入收件人，并确认', formType: 0}, function(receiver, index){
        layer.close(index);
        // use ajax post data to backend
        $.post('/verify',
            {
                action: 'verify_email',
                receiver: receiver
            },
            function (result) {
                if (result.startsWith('Error')){
                    layer.msg(result, {time: 3000, icon: 2});
                }
                else {
                    layer.msg('发送成功！', {icon: 1});
                }
                return false;
            }
        )
            .fail(function () {
                layer.msg('发生错误！', {icon: 2});
            });
    });
}
// project name verify
function verify_project_name() {
    var name = $("#project_name").val();
    // use ajax post data to backend
    $.post('/verify',
        {
            action: 'verify_project_name',
            name: name
        },
        function (result) {
            if (result.startsWith('Error')){
                layer.msg(result, {icon: 2});
            }
            else {
                layer.msg(result, {icon: 1});
            }
            return false;
        }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
        });
}
// username verify
function verify_username() {
    var name = $("#username").val();
    // use ajax post data to backend
    $.post('/verify',
        {
            action: 'verify_username',
            name: name
        },
        function (result) {
            if (result.startsWith('Error')){
                layer.msg(result, {icon: 2});
            }
            else {
                layer.msg(result, {icon: 1});
            }
            return false;
        }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
        });
}