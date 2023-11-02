const config = require('/home/kaschtelator/KaschiBot/Config/config');
const fs = require('fs');
const YT_API_KEY = config.YT_API_KEY;
const youtube_discord_channel_id = config.youtube_discord_channel_id;
const youtube_channel_id = config.youtube_channel_id;
let lastVideos = [];
var debugbot = true;

const youtubeModule = {
    checkForNewVideos: (client) => {

        //Dieser Timer in milisekunden löst eine suche aus wenn er abgelaufen ist, 
        //7200000 ms sind 2 Stunden 
        //3600000 ms sind 1 Stunde 
        //1800000 ms sind 30 minuten.
        setInterval(checkForNewVideos, 1800000);

        //Manueler Befehl zum auslösen der Abfrage !youtube
        client.on('message', message => {
            if (message.content === '!youtube') {
                checkForNewVideos();
            }
        });


        function checkForNewVideos() {
            // Hier wird überprüft, ob eine JSON-Datei existiert. Wenn nicht, wird eine erstellt mit den IDs deiner letzten Videos.
            try {
                lastVideos = JSON.parse(fs.readFileSync('/home/kaschtelator/KaschiBot/Datenbank/lastVideos.json'));
            } catch (err) {
                console.log('lastVideos.json nicht gefunden');
            }
            const request = require('request');
            const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=${youtube_channel_id}&maxResults=1&order=date&key=${YT_API_KEY}`;
            request(url, (err, res, body) => {
                if (err) {
                    if (debugbot) {
                        console.log(err);
                    }
                    return;
                }
                const json = JSON.parse(body);
                if (!json.items || json.items.length === 0) {
                    if (debugbot) {
                        console.log('Keine neuen Videos gefunden.');
                    }
                    return;
                }
                json.items.forEach(video => {
                    const videoTimestamp = new Date(video.snippet.publishedAt);
                    const currentDate = new Date();

                    // Setzen der Uhrzeit auf Mitternacht (00:00:00)
                    videoTimestamp.setHours(0, 0, 0, 0);
                    currentDate.setHours(0, 0, 0, 0);

                    // Überprüfen, ob das Video von heute ist
                    console.log('Video Title:', video.snippet.title);
                    console.log('Video Timestamp:', videoTimestamp.toLocaleString());
                    console.log('Current Date:', currentDate.toLocaleString());
                    const isToday = videoTimestamp < new Date(currentDate.getTime() + 86400000);
                    if (isToday) {
                        const existingVideo = lastVideos.find(v => v.id === video.id.videoId);
                        if (existingVideo && existingVideo.timestamp >= videoTimestamp.getTime()) {
                            //if (debugbot) {
                               // console.log(`Video ${video.id.videoId} wurde bereits gepostet`);
                           // }
                        } else {
                            lastVideos.push({ id: video.id.videoId, timestamp: videoTimestamp.getTime() });
                            const title = video.snippet.title;
                            const url = `https://youtube.com/watch?v=${video.id.videoId}`;
                            const author = video.snippet.channelTitle;
                            const message = `Hey Leute, **${author}** hat **"${title.replace(/&amp;/g, '&')}"** hochgeladen: ${url}`;
                            const channel = client.channels.find(ch => ch.id === youtube_discord_channel_id);
                            channel.send(message);
                            if (debugbot) {
                                console.log('Neues Video gepostet.');
                            }
                        }
                    }
                });
                // Hier werden gefundene Videos in eine JSON-Datei geschrieben, die zuvor vom Code erstellt wurde, um zu verfolgen, welche Videos bereits gepostet wurden.
                fs.writeFile('/home/kaschtelator/KaschiBot/Datenbank/lastVideos.json', JSON.stringify(lastVideos), err => {
                    if (err) {
                        console.error(err);
                    }
                });
            });
        }
    }
}

module.exports = youtubeModule;
