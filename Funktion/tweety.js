const fs = require('fs'); // Importiere das Modul 'fs' zum Lesen und Schreiben von Dateien
const request = require('request'); // Importiere das Modul 'request' zum Senden von HTTP-Anfragen
const Twitter = require('twitter'); // Importiere das Modul 'twitter' für die Twitter-API
const config = require('/home/KaschiBot/Bots/KaschiBot/Config/config');
const TWITTER_API_KEY = config.TWITTER_API_KEY; // Setze deinen Twitter API Key
const TWITTER_API_SECRET_KEY = config.TWITTER_API_SECRET_KEY; // Setze deinen Twitter API Secret Key
const YT_API_KEY = config.YT_API_KEY; // Setze deinen YouTube API Key
const youtube_channel_id = config.youtube_channel_id; // Setze deine YouTube Channel ID

const oauth2 = require('oauth').OAuth2; // Importiere das Modul 'oauth' für die OAuth2-Authentifizierung
const oauth2Client = new oauth2(TWITTER_API_KEY, TWITTER_API_SECRET_KEY, 'https://api.twitter.com/', null, 'oauth2/token', null);

// Autorisierung und Zugriffstoken-Abfrage für Twitter
function authorizeTwitter() {
  oauth2Client.getOAuthAccessToken('', {
    'grant_type': 'client_credentials'
  }, function (e, access_token) {
    client = new Twitter({
      consumer_key: TWITTER_API_KEY,
      consumer_secret: TWITTER_API_SECRET_KEY,
      bearer_token: access_token
    });



    // Dieser Timer in Millisekunden löst eine Suche aus, wenn er abgelaufen ist.
    // 7200000 ms sind 2 Stunden
    // 3600000 ms sind 1 Stunde
    // 1800000 ms sind 30 Minuten.
    setInterval(checkForNewVideos, 7200000);
    console.log('Timer für die Suche nach neuen Videos gestartet.');
  });
}


function checkForNewVideos() {
  // Hier wird überprüft, ob eine JSON-Datei existiert. Wenn nicht, wird eine erstellt mit den IDs deiner letzten Videos.
  try {
    lastVideos = JSON.parse(fs.readFileSync('/home/KaschiBot/Bots/KaschiBot/Datenbank/tweetylastVideos.json'));
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
    // Hier wird überprüft, ob ein Video gefunden wurde oder nicht, um es dann in deinen Discord Channel zu posten mit der discord_channel_id
    const json = JSON.parse(body);
    if (!json.items || json.items.length === 0) {
      if (debugbot) {
        console.log('Keine neuen Videos gefunden.');
      }
      return;
    }



    // Für jedes gefundene Video überprüfen, ob es neu ist und noch nicht gepostet wurde
    json.items.forEach(video => {
      const videoTimestamp = new Date(video.snippet.publishedAt).getTime();
      const currentDate = new Date();
      const timeDifference = currentDate - videoTimestamp;
      const maxVideoAge = 1 * 24 * 60 * 60 * 1000; // 1 Tage in Millisekunden
      let alreadyPosted = false; // Flag, um zu überprüfen, ob ein Video bereits gepostet wurde

      if (timeDifference <= maxVideoAge) {
        const existingVideo = lastVideos.find(v => v.id === video.id.videoId);
        if (existingVideo && existingVideo.timestamp >= videoTimestamp) {
          console.log(`Video ${video.id.videoId} wurde bereits gepostet`);
          alreadyPosted = true; // Video wurde bereits gepostet, Flag wird auf true gesetzt
        }

        const tweetHashtags = [
          'Kaschtelator',
          'GermanMediaRT',
          'Youtube',
          'Gaming',
          'Content',
          'letsplay',
          'RetroGaming'
        ];


        if (!alreadyPosted) {
          lastVideos.push({ id: video.id.videoId, timestamp: videoTimestamp });
          const title = video.snippet.title;
          const url = `https://youtube.com/watch?v=${video.id.videoId}`;
          const author = video.snippet.channelTitle;
          const hashtags = tweetHashtags.join(' '); // Konvertiere die Hashtags in einen String mit Leerzeichen
          const tweet = `Hey Leute, ${author} hat "${title}" hochgeladen: ${url} \n${hashtags}`;

          // Tweet posten
          client.post('statuses/update', { status: tweet }, (error, tweet, response) => {
            if (!error) {
              console.log('Neuer Tweet gepostet.');
            } else {
              console.error(error);
            }
          });
        }
      }
    });


    // Hier werden gefundene Videos in eine JSON-Datei geschrieben, die zuvor vom Code erstellt wurde, um zu verfolgen, welche Videos bereits gepostet wurden.
    fs.writeFile('/home/KaschiBot/Bots/KaschiBot/Datenbank/tweetylastVideos.json', JSON.stringify(lastVideos), err => {
      if (err) {
        console.error(err);
      }
    });
  });
}

module.exports = {
  startTwitterBot: function () {
    authorizeTwitter();
  }
};
