$(function (){
    // 发版总数柱形图
    var barChart = echarts.init(document.getElementById('total_bar'));
    // 显示标题，图例和空的坐标轴
    barChart.setOption({
        tooltip: {},
        legend: {
            data:['次数']
        },
        xAxis: {
            data: []
        },
        yAxis: {},
        series: [{
            name: '次数',
            type: 'bar',
            data: []
        }]
    });
    // 发版总数饼图
    var pieChart = echarts.init(document.getElementById("total_pie"));
    pieChart.setOption({
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: []
         },
        series : [
            {
                name: '次数',
                type: 'pie',
                radius : '55%',
                center: ['50%', '60%'],
                data:[],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    });

    // 异步加载数据
    barChart.showLoading();
    pieChart.showLoading();
    $(function(){
        $.get('deploy_num').done(function (data) {
        // 填入数据
            barChart.hideLoading();
            pieChart.hideLoading();
            barChart.setOption({
                xAxis: {
                    data: data.status
                },
                series: [{
                    // 根据名字对应到相应的系列
                    name: '次数',
                    data: data.amount
                }]
            });
            pieChart.setOption({
                legend: {
                    data: data.status
                },
                series: [{
                    // 根据名字对应到相应的系列
                    name: '次数',
                    data: [{value:data.amount[0],name:data.status[0]},
                        {value:data.amount[1],name:data.status[1]},
                        {value:data.amount[2],name:data.status[2]}]
                }]
            });
        });
    });
    //echarts 随屏幕缩放
    setTimeout(function () {
        window.onresize = function () {
            barChart.resize();
            pieChart.resize();
        }
    });
});

$(function () {
    // 全工程柱形图
    var barChart = echarts.init(document.getElementById('projects_status'));
    // 显示标题，图例和空的坐标轴
    barChart.setOption({
        legend: {},
        tooltip: {},
        xAxis: {type: 'category'},
        yAxis: {},
        // Declare several bar series, each will be mapped
        // to a column of dataset.source by default.
        series: [
            {type: 'bar'},
            {type: 'bar'},
            {type: 'bar'}
        ]
    });

    // 异步加载数据
    barChart.showLoading();
    $(function () {
        $.get('deploy_detail').done(function (data) {
            // 填入数据
            barChart.hideLoading();
            barChart.setOption({
                dataset: {
                    source: data
                }
            });
        });
    });

    //echarts 随屏幕缩放
    setTimeout(function () {
        window.onresize = function () {
            barChart.resize();
        }
    });
});

$(function () {
    // 发版 top
    var barChart = echarts.init(document.getElementById('deploy_top'));
    // 显示标题，图例和空的坐标车轴
    barChart.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '10%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value'
        },
        yAxis: {
            type: 'category',
            data: []
        },
        series: [
            {
                name: '次数',
                type: 'bar',
                data: []
            }
        ]
    });

    // 异步加载数据
    barChart.showLoading();
    $(function () {
        $.get('deploy_top').done(function (data) {
            // 填入数据
            barChart.hideLoading();
            barChart.setOption({
                yAxis: {
                    data: data.projects
                },
                series: {
                    name: '次数',
                    data: data.amount
                }
            });
        });
    });

    //echarts 随屏幕缩放
    setTimeout(function () {
        window.onresize = function () {
            barChart.resize();
        }
    });
});

$(function () {
    // 请求人Top
    var pieChart = echarts.init(document.getElementById("requester_top"));
    pieChart.setOption({
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: []
        },
        series: [
            {
                name: '次数',
                type: 'pie',
                radius: '55%',
                center: ['50%', '60%'],
                data: [],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    });

    // 异步加载数据
    pieChart.showLoading();
    $(function () {
        $.get('requester_top').done(function (data) {
            // 填入数据
            pieChart.hideLoading();
            pieChart.setOption({
                legend: {
                    data: data.amount.name
                },
                series: [{
                    // 根据名字对应到相应的系列
                    name: '次数',
                    data: data.amount
                }]
            });
        });
    });

    //echarts 随屏幕缩放
    setTimeout(function () {
        window.onresize = function () {
            pieChart.resize();
        }
    });
});