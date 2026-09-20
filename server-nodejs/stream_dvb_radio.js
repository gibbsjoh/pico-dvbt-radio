const express = require("express");
const { spawn } = require("child_process");

const app = express();
const PORT = 3000;

const stationToURLMap = {
	"BBC 6 Music" : "http://192.168.0.20:9981/stream/channelid/1789168473?profile=audioonly",
	"BBC Asian Net" : "http://192.168.0.20:9981/stream/channelid/1304818637?profile=audioonly",
	"BBC Berkshire" : "http://192.168.0.20:9981/stream/channelid/558252868?profile=audioonly",
	"BBC Essex" : "http://192.168.0.20:9981/stream/channelid/457222855?profile=audioonly",
	"BBC R1X" : "http://192.168.0.20:9981/stream/channelid/906829287?profile=audioonly",
	"BBC R5L" : "http://192.168.0.20:9981/stream/channelid/1324135085?profile=audioonly",
	"BBC R5SX" : "http://192.168.0.20:9981/stream/channelid/423329148?profile=audioonly",
	"BBC RB 1" : "http://192.168.0.20:9981/stream/channelid/776340589?profile=audioonly",
	"BBC Radio 1" : "http://192.168.0.20:9981/stream/channelid/1088119316?profile=audioonly",
	"BBC Radio 2" : "http://192.168.0.20:9981/stream/channelid/1574393663?profile=audioonly",
	"BBC Radio 3" : "http://192.168.0.20:9981/stream/channelid/1466580832?profile=audioonly",
	"BBC Radio 4" : "http://192.168.0.20:9981/stream/channelid/921561204?profile=audioonly",
	"BBC Radio 4 Ex" : "http://192.168.0.20:9981/stream/channelid/2048850998?profile=audioonly",
	"BBC Radio London" : "http://192.168.0.20:9981/stream/channelid/2090476226?profile=audioonly",
	"BBC Surrey" : "http://192.168.0.20:9981/stream/channelid/777569649?profile=audioonly",
	"BBC Three Counties" : "http://192.168.0.20:9981/stream/channelid/18113443?profile=audioonly",
	"BBC World Sv" : "http://192.168.0.20:9981/stream/channelid/1513826557?profile=audioonly",
	"Capital" : "http://192.168.0.20:9981/stream/channelid/48061687?profile=audioonly",
	"Classic FM" : "http://192.168.0.20:9981/stream/channelid/1628426462?profile=audioonly",
	"Heart" : "http://192.168.0.20:9981/stream/channelid/1083717952?profile=audioonly",
	"LBC" : "http://192.168.0.20:9981/stream/channelid/1807396077?profile=audioonly",
	"Premier Radio" : "http://192.168.0.20:9981/stream/channelid/89334837?profile=audioonly",
	"RNIB Connect" : "http://192.168.0.20:9981/stream/channelid/9799286?profile=audioonly",
	"Smooth Radio" : "http://192.168.0.20:9981/stream/channelid/988518747?profile=audioonly",
	"talkSPORT" : "http://192.168.0.20:9981/stream/channelid/889496746?profile=audioonly"
};

app.get("/stream", (req, res) => {
    const stationName = req.query.stationName;
    console.log(stationName)
    const streamType = "audio"; //req.query.type; // "audio" or "video"
    let streamUrl = stationToURLMap[stationName];
    console.log(streamUrl);
    let ffmpegArgs;
    let theEncoder;

    if (streamType == "video"){
        theEncoder = "libx264";
        ffmpegArgs = [
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", streamUrl,
        "-c:v", theEncoder,
	    "-preset", "veryfast",
  	    "-tune", "zerolatency",
  	    "-movflags", "frag_keyframe+empty_moov+default_base_moof",
        "-b:v", "800k",
        "-c:a", "aac",
        "-b:a", "192k",
        "-f", "mp4",
        "pipe:1"
        ];
    }
    else if (streamType == "audio"){
        theEncoder = "libmp3lame";
        ffmpegArgs = [
         "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", streamUrl,
        "-c:a", theEncoder,
        "-b:a", "96",
        "-ar", "22050",
        "-f", "mp3",
        "-vn",
        "pipe:1"
        ];
    }
//    const ffmpegArgs = [
//        "-i", streamUrl,
//        "-c:v", "hevc_omx",
//        "-b:v", "800k",
//        "-c:a", "aac",
//        "-b:a", "128k",
//        "-f", "mpegts",
//        "pipe:1"
//    ];
        
    console.log(`Starting transcoding for ${streamUrl} type ${streamType}`);
    const ffmpegProcess = spawn("ffmpeg", ffmpegArgs);

    // Handle FFmpeg errors
    ffmpegProcess.stderr.on("data", (data) => {
        console.error(`FFmpeg Error: ${data}`);
    });

    // When FFmpeg process ends, log it
    ffmpegProcess.on("close", (code) => {
        console.log(`FFmpeg process ended with code ${code}`);
    });

    // Handle client disconnect and terminate FFmpeg
    req.on("close", () => {
        console.log("Client disconnected, stopping FFmpeg");
        ffmpegProcess.kill("SIGKILL");
    });

    // Set response headers and stream data

    if (streamType == "video"){
        res.setHeader("Content-Type", "video/mp4");
    }
    else if (streamType == "audio"){
        res.setHeader("Content-Type", "audio/mpeg");
    }
    ffmpegProcess.stdout.pipe(res);
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

