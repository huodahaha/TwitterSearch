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
        $(".related_users_score").hide()
        $(".score_board").hide();
        $(".related_users").show()
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
                if (res.errcode == 1)
                    alert(res.errmsg);
                else {
                    $.each(res.result, function (i, item) {
                        $(".details").append(
                            "<div class='item'><span class='user'>" + item.user_name + "</span><span class='twitter-time'>" + item.ts + "</span><p class='text'>" + item.raw_test + "</p><span class='score'>" + item.score + "</span></div>"
                        )
                    })
                    $.each(res.related_users, function (i, item) {
                        $(".related_users").append(
                            "<span>" + item + "</span>"
                        )
                    })
                }
            }
        })
    })

    // submit listener for score board
    $(".left_down .submit-btn").click(function () {
      
        $(".related_users").hide()
        $(".details").hide();
        $(".score_board").show();
        $(".related_users_score").show()
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

        $.ajax({
            type: "GET",
            url: "/Keyword",
            dataType: 'json',
            data: {
                "user_name": username,
                "begin_date": begin_date_str,
                "end_date": end_date_str,
                "related_user_cnt": related_num,
                "search_text": search_text
            },
            success: function (res) {
                if (res.errcode == 1)
                    alert(res.errmsg);
                else {

                    $.each(res.result, function (i, item) {
                        $(".score_board").append(
                            "<div class = 'word'>" + item + "</div>"
                        )
                    })
                    $.each(res.related_users, function (i, item) {
                        $(".related_users_score").append(
                            "<span>" + item + "</span>"
                        )
                    })
                }

            }
        })
    })












})