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
            layer.msg('结果： ' + result, {icon: 1});
            return false;
        }
    )
        .fail(function () {
            layer.msg('发生错误！', {icon: 2});
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