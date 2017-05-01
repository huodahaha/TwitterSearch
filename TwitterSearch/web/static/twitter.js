$(function () {
    // calendar listener
    $('.input-daterange input').each(function () {
        $(this).datetimepicker({
            format: 'yyyy-mm-dd',
            minView: '2'
        });
    });

    // submit listener for twitter search
    $(".left_up .submit-btn").click(function () {

        $(".related_users_score").hide();
        $(".score_board").hide();
        $(".related_users").empty();
        $(".details").empty();
        $(".related_users").show();
        $(".details").show();
        var username = $(this).parent().find(".username").val()
        var begin_date = $(this).parent().find(".begin_date").data("datetimepicker").getDate();
        var end_date = $(this).parent().find(".end_date").data('datetimepicker').getDate();
        var related_num = $(this).parent().find(".words").val();
        var search_text = $(this).parent().find(".keyword").val();

        begin_date_str = begin_date.toLocaleDateString();
        end_date_str = end_date.toLocaleDateString();

        if (begin_date.valueOf() > end_date.valueOf())
            alert("Please choose a reasonable time range.");
        else if (search_text.length == 0)
            alert("Please input search text.");
        else if (username.length == 0)
            alert("Please input user name.")
        else {

            $(".loading").show();
            $.ajax({
                type: "GET",
                url: "/SearchTwitter",
                dataType: 'json',
                data: {
                    "user_name": username,
                    "begin_date": begin_date_str,
                    "end_date": end_date_str,
                    "related_user_cnt": related_num,
                    "search_text": search_text
                },
                success: function (res) {
                    $(".loading").hide();
                    if (res.errcode == 1)
                        alert(res.errmsg);
                    else {
                        if (res.result.length == 0)
                            $(".details").append(
                                "<p style= 'font-size: 16px; color:#0084B4;'>No result returned.<br><br> Note that, TwitterSearch only support Tweet in English. Also, stop word (we /you /if / and....)and is elimated.</p>"
                            )
                        else {
                            $.each(res.result, function (i, item) {
                                $(".details").append(
                                    "<div class='item'><span class='user'>" + item.user_name + "</span><span class='twitter-time'>" + item.ts + "</span><p class='text'>" + item.raw_test + "</p><span class='score' style= 'background: #40bbc2; border-radius: 5px;color: #fff; padding: 5px;'>" + "score:&nbsp;&nbsp;" + item.score + "</span></div>"
                                )
                            })
                            $(".related_users").append(
                               "<span style= 'font-size: 19px;color: #0084B4;'>Relevent Users: &nbsp;&nbsp</span>"
                            )
                            $.each(res.related_users, function (i, item) {
                                $(".related_users").append(
                                    "<span style = 'background:#0084B4; color: #fff; margin-right: 20px; padding:5px; font-size: 18px; border-radius: 5px; margin-bottom: 10px;'>" + item + "</span>"
                                )
                            })
                        }
                    }
                }
            })
        }
    })

    // submit listener for score board
    $(".left_down .submit-btn").click(function () {


        $(".related_users").hide()
        $(".details").hide();
        $(".score_board").empty();
        $(".related_users_score").empty();
        $(".score_board").show();
        $(".related_users_score").show()

        // $(this).attr("disabled",true); 

        var username = $(this).parent().find(".username").val()
        var begin_date = $(this).parent().find(".begin_date").data("datetimepicker").getDate();
        var end_date = $(this).parent().find(".end_date").data('datetimepicker').getDate();
        var related_num = $(this).parent().find(".words").val();

        begin_date_str = begin_date.toLocaleDateString();
        end_date_str = end_date.toLocaleDateString();

        if (begin_date.valueOf() > end_date.valueOf())
            alert("Please choose a reasonable time range.");
        else if (username.length == 0)
            alert("Please input user name.")
        else {

            $(".loading").show();
            $.ajax({
                type: "GET",
                url: "/Keyword",
                dataType: 'json',
                data: {
                    "user_name": username,
                    "begin_date": begin_date_str,
                    "end_date": end_date_str,
                    "related_user_cnt": related_num
                },
                success: function (res) {
                    // $(this).attr("disabled",false);
                    $(".loading").hide();
                    if (res.errcode == 1)
                        alert(res.errmsg);
                    else {

                        if (res.result.length == 0)
                            $(".score_board").append(
                                "<p style= 'font-size: 16px; color:#0084B4;'>No result returned.<br> <br>Note that, TwitterSearch only support Tweet in English. Also, stop word (we /you /if / and....) and is elimated.</p>"
                            )
                        else {
                            $(".score_board").append(
                                "<div class = 'title' style = 'margin-left: 50px;margin-bottom: 30px;font-size:" + 30 + "px; color:#0084B4; font-weight:bold'>" + "<span class = 'score' style = 'margin-right: 160px; font-weight: bold'>" + "Score" + "</span>" + "Keyword" + "</div>"
                            )
                            $.each(res.result, function (i, item) {
                                var size = 40 - i * 0.8;
                                var name = item[0];
                                var score = item[1];

                                $(".score_board").append(
                                    "<div class = 'word' style = 'margin-left: 55px;margin-bottom: 15px;font-size:" + 20 + "px; color:#1da1f2'>" + "<span class = 'score' style = 'margin-right: 200px;'>" + score + "</span>" + name + "</div>"
                                )
                            })
                            $(".related_users_score").append(
                               "<span style= 'font-size: 19px;color: #0084B4;'>Relevent Users: &nbsp;&nbsp</span>"
                            )
                            $.each(res.related_users, function (i, item) {
                                $(".related_users_score").append(
                                    "<span style = 'background:#0084B4; color: #fff; margin-right: 20px; padding:5px; font-size: 18px; border-radius: 5px; margin-bottom: 10px;'>" + item + "</span>"
                                )
                            })
                        }

                    }

                }
            })
        }
    })


    function getRandomColor() {
        return '#' +
            (function (color) {
                return (color += '0123456789abcdef'[Math.floor(Math.random() * 16)])
                    && (color.length == 6) ? color : arguments.callee(color);
            })('');
    }

})