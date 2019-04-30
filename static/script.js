$(document).ready(function() {
    var loading = false;
    var interval;
    $("#spinner-cont").hide();
    $("#audio-upload").on('change', function () {
        name = $("#audio-upload").val().split('\\').pop();
        $("#filename").text(name);
    });

    $("#form").submit(function(e) {
        e.preventDefault()
        $("#spinner-cont").show();
        loading = true;
        var lyrics = $("#lyrics").val().replace(/ *\([^)]*\) */g, "").replace(/ +(\W)/g, "$1").replace(/\s+(\W+)\s+/g, " ").replace(/ +(?= )/g, '').replace(/\n{2,}/g, '\n');
        var lyrics_spl = lyrics.split("\n");
        var lyrics_html = "";
        var str_to_send = "";
        var line_map = [];
        for (var i = 0; i < lyrics_spl.length; i++)
        {
            var line = lyrics_spl[i];
            var line_spl = line.split(" ");
            for (var j = 0; j < line_spl.length; j++)
            {
                var word = line_spl[j];
                var clean = word.replace(/[^0-9A-Za-z']/, '').toLowerCase();
                str_to_send += clean;
                lyrics_html += '<span style="opacity: 0.2">' + word + "</span>";
                if (j < line_spl.length - 1)
                {
                    str_to_send += " ";
                    lyrics_html += " ";
                }
                line_map.push(i);
            }
            lyrics_html += "<br>";
            str_to_send += '\n';
        }
        formdata = new FormData($(this)[0]);
        formdata.set("lyrics", str_to_send);
        $.ajax({
            type: "POST",
            url: "/upload",
            contentType: false,
            processData: false,
            data: formdata,
            success: function(data)
            {
                loading = false;
                $('#lyrics-play').css({top: "calc(50% - 40pt)"});
                $('#lyrics-play').html(lyrics_html);
                $("#playback-container").show();
                $("#playback-container").animate({opacity: 0.95}, 500, function() {
                    $("#spinner-cont").hide();
                    var reader = new FileReader();
                    var sound = document.getElementById("sound");
                    reader.onload = function(e) {
                        sound.src = this.result;
                        sound.controls = true;
                        //$("#sound").on('timeupdate', function() {
                        interval = setInterval(function() {
                            var next = 0;
                            var end = true;
                            for (var i = 0; i < data.lyrics.length; i++)
                            {
                                if (sound.currentTime < data.lyrics[i][1])
                                {
                                    next = i;
                                    end = false;
                                    break;
                                }
                            }
                            if (end)
                                next = data.lyrics.length;
                            var line_num = line_map[next];
                            $('#lyrics-play').css({top: "calc(50% - 40pt - " + line_num * 80 + "px)"});
                            var spans = $('#lyrics-play > span').each(function(index) {
                                if (index < next)
                                    $(this).css({opacity: 1.0});
                                else
                                    $(this).css({opacity: 0.2});
                            });
                        }, 50);
                    };
                    reader.readAsDataURL($("#audio-upload")[0].files[0]);
                });
            }
        });
    });

    $('#audio-upload-button').click(function(){
        $('#audio-upload').click();
    });

    $('#karaokify-button').click(function(){
        $('#submit').click();
    });

    $(document).keyup(function(e) {
        if (e.keyCode != 27)
            return;
        if (loading)
            return;
        $("#playback-container").animate({opacity: 0}, 500, function() {
            $("#playback-container").hide();
            var sound = document.getElementById("sound");
            sound.pause();
            sound.currentTime = 0;
            if (typeof interval !== 'undefined')
            {
                clearInterval(interval);
            }
        });
    });
});
