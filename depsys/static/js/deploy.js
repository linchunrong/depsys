// show logs which deployed
function show_logs(msg) {
    layer.open({
        type: 1,
        title: '日志',
        area: ['800px', '500px'],
        shadeClose: true,
        content: '\<\pre style="padding: 20px; background-color: white; border: none">' + document.getElementById(msg).innerHTML + '\<\/pre>'
    });
}
// fill selected version
function version_select() {
    var a = $("input[name='selected']:checked").val();
    $("#branch").val(a);
}