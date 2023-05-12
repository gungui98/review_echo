if(!window.dash_clientside) {window.dash_clientside = {};}

function draw_line(ef_boundary, color, canvas, context) {
    let height = canvas.height;
    let width = canvas.width;
    let line;
    context.lineWidth = 2;
    if (ef_boundary) {
        for (let line_idx = 0; line_idx < ef_boundary.length; line_idx++) {
            line = ef_boundary[line_idx];
            for (let i = 0; i < line.length - 1; i++) {
                context.beginPath();
                context.moveTo(line[i].x * width, line[i].y * height);
                context.lineTo(line[i + 1].x * width, line[i + 1].y * height);
                context.strokeStyle = color;
                context.stroke();
            }
        }
    } else {
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
}

function draw_point(ef_point, color, canvas, context) {
    let height = canvas.height;
    let width = canvas.width;
    const radius = 3; // Arc radius
    const startAngle = 0; // Starting point on circle
    const endAngle = 2 * Math.PI; // End point on circle
    context.font = "18px Arial";

    for (let point_idx = 0; point_idx < ef_point.length; point_idx++) {
        let x = ef_point[point_idx].x * width; // x coordinate
        let y = ef_point[point_idx].y * height; // y coordinate
        context.beginPath();
        context.strokeStyle = color;
        context.fillStyle = color;
        context.fillText((point_idx + 1).toString(), x, y - 10);
        context.arc(x, y, radius, startAngle, endAngle, true);
        context.fill();
        context.stroke();
    }

}

function draw_annotation(frame_idx, json_data, canvas, context) {
    let dicom_annotations = json_data.dicomAnnotation[frame_idx];
    if (dicom_annotations) {
        let ef_boundary = dicom_annotations.ef_boundary;
        let gls_boundary = dicom_annotations.gls_boundary;
        let ef_point = dicom_annotations.ef_point;
        let gls_point = dicom_annotations.gls_point;
        context.clearRect(0, 0, canvas.width, canvas.height);
        if (ef_boundary.length > 0) {
            draw_line(ef_boundary, '#00ff00', canvas, context);
            draw_line(gls_boundary, '#ff0000', canvas, context);
            draw_point(ef_point, '#00ff00', canvas, context);
            draw_point(gls_point, '#ff0000', canvas, context);
        }
    }
}

function parse(str) {
    var args = [].slice.call(arguments, 1),
        i = 0;

    return str.replace(/%s/g, () => args[i++]);
}

function set_star(component,id) {
    if(!id){
            return
        }
        id = parseInt(id);
        let stars = $(parse('#%s-star-rating :input',component));
        for (let i=0;i<stars.length;i++) {
            if(i>=id-1){
                $(stars[i].parentNode).css({"color":"#f2b600"});
            }else{
                $(stars[i].parentNode).css({"color":"#bbb"});

            }
        }
}

window.dash_clientside.clientside = {

    quality_star_init_callback: function(id){
        set_star("quality",id)
    },

    annotations_star_init_callback: function(id){
        set_star("annotation",id)
    },

    init_callback_annotation_review: function (json_data, frame_rate) {
        const currentFrame = $('#idx-indicator');
        let canvas = document.getElementById("annotation-canvas");
        let context = canvas.getContext('2d');
        const video = VideoFrame({
            id: 'video',
            frameRate: frame_rate,
            callback: function (frame) {
                currentFrame.html(frame);
                draw_annotation(frame,json_data, canvas, context);
            }
        });

        video.listen('frame');
        window.dash_clientside.clientside.video = video;
        window.dash_clientside.clientside.json_data = json_data;

        $('#play-pause-button').click(function () {
            if (video.video.paused) {
                video.video.play();
            } else {
                video.video.pause();
            }
        });
        $('#next-frame-button').click(function () {
            video.seekForward(1, function () {
                let frame = video.get();
                currentFrame.html(frame);
                draw_annotation(frame, json_data, canvas, context);

            })
        });

        $('#previous-frame-button').click(function () {
            video.seekBackward(1, function () {
                let frame = video.get();
                currentFrame.html(frame);
                draw_annotation(frame, json_data, canvas, context);
            })
        });
    },
    select_slider: function (frame_idx ) {
        frame_idx = frame_idx - 1;
        const currentFrame = $('#idx-indicator');
        let canvas = document.getElementById("annotation-canvas");
        let context = canvas.getContext('2d');
        const video = window.dash_clientside.clientside.video;
        const json_data = window.dash_clientside.clientside.json_data;
        if (!video.video.paused) {
                video.video.pause();
        }
        if (frame_idx === 0){
            video.seekTo({ time: '00:00:00'});
        }
        else{
            video.seekTo({ frame: frame_idx});
        }
        currentFrame.html(video.get());
        draw_annotation(frame_idx, json_data, canvas, context);
        return "";
    },
    fade_in: function (){
        $(document).ready(function(){
            $(".case-info-card").hide(0).delay(500).fadeIn(200)
        });
    }
};

