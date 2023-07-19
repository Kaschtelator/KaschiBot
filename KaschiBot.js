// --------- VARIABLEN ----------
var debugbot = false;
const ytdl = require('ytdl-core');
const config = require('./Config/config.json');
const { Client, Intents, VoiceChannel, GUILD_VOICE_STATES } = require('discord.js');
const YouTube = require('simple-youtube-api');
const client = new Client();
client.login(config.token);
const fs = require('fs');
// Filenames der JSONS als CONST, damit diese allgemein feststehen
const SAlleComDaten = './Datenbank/AlleComDaten.json';
const SWillkommen = './Datenbank/Willkommen.json';
const SWiedersehen = './Datenbank/Wiedersehen.json';
const SStatus = './Datenbank/Status.json';
const STimeOut = './Datenbank/TimeOut.json';
const SDiceObjekt = './Datenbank/DiceObjekt.json';
const SDiceAktion = './Datenbank/DiceAktion.json';
const SMusikListe = './Datenbank/Musik.json';
//const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

//------------------------WELTHERRSCHAFT *GEPLANT*---------------------------------
//------------------------Moderations funktionen  *GEPLANT*------------------------
//------------------------Youtube und TWITCH ONLINE ERKENNUNG *GEPLANT*------------
//------------------------DISCORD VIDEO/AUDIO STREAMS *GEPLANT*--------------------
//------------------------NEUSTART BOT---------------------------------------------
const restartModule = require('./Funktion/restartModule');
console.log('restartModule erfolgreich eingelesen.');
restartModule.start(client);


client.on('ready', () => {
    console.log(`Eingeloggt als ${client.user.tag}!`);

});
//------------------------SONDERFUNKTIONEN------------------------------------------
client.on('message', (message) => {
    if (message.content === '!zeit') {
        const currentDate = new Date();
        const currentTime = currentDate.toLocaleString();
        message.channel.send(`Die aktuelle Zeit und das Datum sind: ${currentTime}`);
    }
});
//------------------------YOUTUBE NEUES VIDEO---------------------------------------


const youtubeModule = require('./Funktion/youtubeModule');
console.log('youtubeModule erfolgreich eingelesen.');
youtubeModule.checkForNewVideos(client);


//const twitterModule = require('./Funktion/tweety');
//console.log('twitterModule erfolgreich eingelesen.');
//twitterModule.startTwitterBot();
//------------------------FREE GAMES------------------------------------------------

//GOG


const { fetchAndExtractData, sendEmbedMessage } = require('./Funktion/gog.js');
console.log('gogModule erfolgreich eingelesen.');


//const gogModule = require('./Funktion/GOGModule.js');
//console.log('gogModule erfolgreich eingelesen.');
//gogModule.checkForNewFreeGames(client);

//Epic Games
const epicModule = require('./Funktion/EpicGamesModule.js');
console.log('epicModule erfolgreich eingelesen.');
epicModule.checkForNewFreeGames(client);
//------------------------GEBURTSTAGS SYSTEM----------------------------------------

const path = './Datenbank/birthdays.json';
const commands = require("./Funktion/bdaycommands");
const bday_discord_channel_id = config.bday_discord_channel_id;

commands.addCommand(client);




fs.stat(path, function (err, stat) {
    if (err == null) {
        if (debugbot) {
            console.log('birthdays.json Gefunden.');
        }


    } else if (err.code === 'ENOENT') {
        if (debugbot) {
            console.log('birthdays.json nicht Gefunden, Erstelle neue Datei...');
        }
        fs.writeFileSync(path, JSON.stringify([]));
    } else {
        if (debugbot) {
            console.log('Irgendein anderer Fehler: ', err.code);
        }
    }
});
client.on('message', message => {
    if (message.content === '!checkgeburtstag') {
        checkBirthday();
        if (debugbot) {
            console.log('Manuelle Geburtstags Prüfung');
        }
    }
});

function checkBirthday() {

    var heute = new Date();
    var jahr = heute.getFullYear();
    var monat = heute.getMonth() + 1;
    var tag = heute.getDate();

    var geburtstage = JSON.parse(fs.readFileSync(path, 'utf-8'));
    // pruefen ob dieser geburtstag dieses jahr schon mal "ermittelt" wurde
    var geburtstag = geburtstage.find(x => x.date.substring(0, 2) === tag.toString().padStart(2, "0") && x.date.substring(3) === monat.toString().padStart(2, "0") && x.jahr != jahr);

    if (geburtstag) {
        const channel = client.channels.find(ch => ch.id === bday_discord_channel_id);
        channel.send(`@everyone Heute ist der ${tag}. ${monat}.! und ${geburtstag.name} hat Heute Geburtstag! Alles Gute zum Geburtstag :tada:`);
        channel.send(`https://tenor.com/view/happy-birthday-the-office-dwight-dwight-schrute-birthday-gif-25725679 `);
        console.log('Geburtstags Event ausgelöst');

        // Das jahr richtig setzten
        geburtstag.jahr = jahr;
        var geburtstagindex = geburtstage.findIndex(x => x.date.substring(0, 2) === tag.toString().padStart(2, "0") && x.date.substring(3) === monat.toString().padStart(2, "0") && x.jahr != jahr);
        geburtstage[geburtstagindex] = geburtstag;
        // das neu gesetzte Jahr abspeichern
        fs.writeFileSync(path, JSON.stringify(geburtstage));
    }

}

//Lege ein Intervall fest, um jeden Tag nach Geburtstagen zu suchen
setInterval(checkBirthday, 10800000); // 3H in ms




//------------------------STREAM-AUDIO---------------------------------------


//---------------------------------------------------------------------------

let loop = true;
let musicplaying = false;
let radioplaying = false;
let loopcount = 1;
client.on('message', async message => {
    if (message.content.split(' ')[0].toLowerCase() == "!taverne") {

        if (!radioplaying && !musicplaying) {
            loopcount = 1;
            musicplaying = true;
            loop = true;
            if (debugbot) {
                console.log('spiele Tavernen Musik');
            }
            playmusic();
        }
        else {
            if (debugbot) {
                console.log('Spiele noch Musik/Radio Neustart nicht Möglich!!!');
                if (!message.member.voiceChannel) return message.channel.send('Spiele noch Radio/Musik Neustart nicht Möglich! Bitte nutze erst !end um die Aktuelle wiedergabe zu Beenden.');
            }
        }
    }
    if (message.content.split(' ')[0].toLowerCase() == "!end") {
        await message.member.voiceChannel.join();
        await message.guild.me.voiceChannel.leave();
        if (debugbot) {
            console.log('Beende Musik');
        }
        musicplaying = false;
        radioplaying = false;
        return loop = false;
    }
    if (message.content.split(' ')[0].toLowerCase() == "!loop") {
        if (debugbot) {
            console.log(`Loop ist ${!loop ? "An" : "Aus"}`)
        }
        return loop = !loop;
    }
    if (message.content.split(' ')[0].toLowerCase() == "!radiometal") {
        if (!radioplaying && !musicplaying) {
            radioplaying = true;

            if (debugbot) {
                console.log('spiele radio');
            }
            playradio();
        }

    }
    if (message.content.split(' ')[0].toLowerCase() == "!dunklewelle") {
        if (!radioplaying && !musicplaying) {
            radioplaying = true;

            if (debugbot) {
                console.log('spiele radio');
            }
            playradiodunklewelle();
        }

    }
    if (message.content.split(' ')[0].toLowerCase() == "!radio21") {
        if (!radioplaying && !musicplaying) {
            radioplaying = true;

            if (debugbot) {
                console.log('spiele radio');
            }
            playradio21();
        }
        else {
            if (debugbot) {
                console.log('Spiele noch Radio/Musik Neustart nicht Möglich!!!');
                if (!message.member.voiceChannel) return message.channel.send('Spiele noch Radio/Musik Neustart nicht Möglich! Bitte nutze erst !end um die Aktuelle wiedergabe zu Beenden.');
            }
        }
    }

    async function playradio() {


        const connectionradio = await message.member.voiceChannel.join();
        const dispatcherradio = await connectionradio.playStream('https://s2-webradio.rockantenne.de/heavy-metal/stream', { volume: 0.5 });
        console.log('Rock Antenne Heavy Metal');
        if (!message.member.voiceChannel) return message.channel.send('Spiele Radiosender: Rock Antenne - Heavy Metal');
        async function destroy() {
            if (debugbot) {
                console.log('Stream wird Beendet! Metal Radio')
            }
            dispatcherradio.destroy();
        }

        dispatcherradio.on('end', async () => {
            destroy();
        });
    }

    async function playradiodunklewelle() {
        try {
          const connectionradio = await message.member.voice.channel.join();
          console.log(`Connected to voice channel: ${message.member.voice.channel.name}`);
          
          const dispatcherradio = connectionradio.play('https://saurus.streampanel.net/rjmvggsr?mp=/stream', { volume: 0.5 });
          dispatcherradio.on('start', () => {
            console.log(`Started playing stream: ${dispatcherradio.streamURL}`);
          });
          dispatcherradio.on('debug', (info) => {
            console.log(`Debug info: ${info}`);
          });
          dispatcherradio.on('error', (error) => {
            console.error(`Error playing stream: ${error}`);
          });
          dispatcherradio.on('end', (reason) => {
            console.log(`Stream ended: ${reason}`);
            connectionradio.disconnect();
          });
          
          if (!message.member.voice.channel) {
            await message.channel.send('Playing radio station: Radio Dunkle Welle');
          }
          
        } catch (error) {
          console.error(`Error joining voice channel: ${error}`);
        }
      }

    

    async function playradio21() {


        const connectionradio = await message.member.voiceChannel.join();
        const dispatcherradio = await connectionradio.playStream('https://radio21.streamabc.net/radio21-wilhelmshaven-mp3-192-4130986', { volume: 0.5 });
        console.error("error".code);
        console.log('Radio 21');
        if (!message.member.voiceChannel) return message.channel.send('Spiele Radiosender: Radio 21');
        async function destroy() {
            if (debugbot) {
                
                console.log('Stream wird Beendet! Radio 21')
            }
            dispatcherradio.destroy();
        }

        dispatcherradio.on('end', async () => {
            destroy();
        });
    }





    async function playmusic() {

        const Musikliste = JSON.parse(fs.readFileSync('/home/pi/Bots/KaschiBot/Datenbank/Musik.json', 'utf-8'));
        const titlemusic = Musikliste[Math.floor(Math.random() * Musikliste.length)];

        const connectionmusic = await message.member.voiceChannel.join();
        const dispatchermusic = await connectionmusic.play('/home/pi/Bots/KaschiBot/Datenbank/Musik.json' + titlemusic, { volume: 0.3 });

        if (!message.member.voiceChannel) return msg.channel.send('Spiele Tavernen Musik ab');

        async function destroy() {
            if (debugbot) {
                console.log('Stream wird beendet! Tavernen Musik');
            }
            dispatchermusic.destroy();
        }

        dispatchermusic.on('end', async () => {
            if (loop) {
                if (debugbot) {
                    console.log('Loop ist Aktiviert! Nächster Song');
                }
                loopcount++;
                if (loopcount >= 6) {
                    return loop = false;
                }
                playmusic();
            } else {
                destroy();
            }
        });
    }
})


//-----------------------------------------------------------------------------------
const GeheimerTrenner = '; ';
// Im Aliasname wird der Text als Reg Ausdruck gespeichert den er ersetzten soll
// das /g sagt er soll wiederkehrende Worte austauschen.
const Aliasname = /member/g;

// --------- JSON ---------
// Alle Daten, sowohl Command als auch Antwort sind hier enthalten
// DEFAULT Aufbau von JSONS --- Damit mit diesen Objekten gearbeitet werden kann
var ComFunktionen =
{
    '#hilfe': '#hilfe',
    '#dice': '#dice'
}
var AlleComDaten =
{
    '#befehl': 'zeigt alle Commands an'
}
var GeheimeCommands =
{
    '#EditKaschiCommand': 'einfuegen',
    '#DeleteKaschiCommand': 'rauswerfen',
    '#GetKaschiCommand': 'ausgabe',
    '#BotKaschiCommand': 'setting',
    '#EditWillkommen': 'willkommen',
    '#EditWiedersehen': 'wiedersehen',
    '#EditDiceAktion': 'diceaddaktion',
    '#EditDiceObjekt': 'diceaddobjekt',
    '#DeleteDiceAktion': 'dicedeleteaktion',
    '#DeleteDiceObjekt': 'dicedeleteobjekt',
    '#ForceLoad': 'laden',
    '#BotPing': 'ping'
}
var TimeOutUser =
{
    "@User":
    {
        "#befehl": new Date().toISOString()
    }
}
//DEFAULT 1 Wert
var WillkommenText =
    { 0: "halli hallo member willkommen bei uns" }
//DEFAULT 1 Wert
var AufwiedersehenText =
    { 0: "User member hat den Raster verlassen" }
var StatusText =
{
    "name": "liebt deine Mama",
    "url": "https://www.google.de",
    "debugging": true,
    "channel": true
}
var DiceObjektText =
{
    0: 'eine Gl�hbirne',
    1: 'ein Einhorn'
}
var DiceAktionText =
{
    0: 'lecken',
    1: 'berühren'
}

// Musikliste
var Musikliste =
{
    0: '/home/pi/Bots/KaschiBot/Musik/13 - raven wine.mp3',
    1: ''
}


// ForceLoad mit eingebaut damit zwingend die Daten neu geladen werden anghand der Files
ForceLoad(false);
//ich bin bereit log
client.on('ready', () => {
    // Bot "Spielt Status"
    // status types: PLAYING, STREAMING, LISTENING, WATCHING
    client.user.setStatus('available');
    StatusText = ReturnJSONFile(SStatus, StatusText);
    client.user.setPresence({ game: { name: StatusText["name"], type: "streaming", url: StatusText["url"] } }).then().catch(console.error);
    // consolen log für eingelogt status als kaschibot
    // Die Debugging info setzten
    debugbot = StatusText["debugging"];

});

// --------- FUNKTIONEN ---------
function ReturnJSONFile(FileName, VergleichJSON, LogInfo = false) {
    var contents = '';
    try {
        if (FileName == '') {
            // Wenn kein Filename vorhanden ist mache nichts
            if (debugbot) {
                console.log('JSON ohne Filename laden - Fehler! - kein JSON Laden');
            }
            return VergleichJSON;
        }
        if (debugbot || LogInfo) {
            // Nur INfos fuer Log
            console.log('vor dem laden von ' + FileName + ': ' + Object.keys(VergleichJSON).length);
        }
        var getCommands = require('fs');
        if ((getCommands.existsSync(FileName))) {
            //mache nichts, wenn datei vorhanden
        }
        else {
            // Eingebaut, falls noch kein Json existert, damit es neu erstellt wird
            // und nur dann anhand des Vergleich JSON, welche aus den DEFAULT besteht
            // DEFAULT = erster Aufbau des JSONS
            SaveJSONFile(VergleichJSON, FileName);
        }

        contents = getCommands.readFileSync(FileName, 'utf8');
    }
    catch
    {
        console.log('fehler beim laden von: ' + FileName);
        contents = '';
    }
    finally { }

    // Commands sind ungleich neu laden, ansonsten nicht neu laden
    if (contents != '') {
        VergleichJSON = JSON.parse(contents);
    }

    if (debugbot || LogInfo) {
        console.log('nach dem laden von ' + FileName + ': ' + Object.keys(VergleichJSON).length);
    }

    return VergleichJSON;
}


// Gibt ein JSON Objekt zurueck, sofern es geladen werden kann, ansonsten VergleichJson = ausgabe
async function aReturnJSONFile(FileName, VergleichJSON, LogInfo = false) {
    var contents = '';
    try {
        if (FileName == '') {
            // Wenn kein Filename vorhanden ist mache nichts
            if (debugbot) {
                console.log('JSON ohne Filename laden - Fehler! - kein JSON Laden');
            }
            return VergleichJSON;
        }
        if (debugbot || LogInfo) {
            // Nur INfos fuer Log
            console.log('vor dem laden von ' + FileName + ': ' + Object.keys(VergleichJSON).length);
        }
        var getCommands = require('fs');
        if ((getCommands.existsSync(FileName))) {
            //mache nichts, wenn datei vorhanden
        }
        else {
            // Eingebaut, falls noch kein Json existert, damit es neu erstellt wird
            // und nur dann anhand des Vergleich JSON, welche aus den DEFAULT besteht
            // DEFAULT = erster Aufbau des JSONS
            SaveJSONFile(VergleichJSON, FileName);
        }

        contents = getCommands.readFileSync(FileName, 'utf8');
    }
    catch
    {
        console.log('fehler beim laden von: ' + FileName);
        contents = '';
    }
    finally { }

    // Commands sind ungleich neu laden, ansonsten nicht neu laden
    if (contents != '') {
        VergleichJSON = JSON.parse(contents);
    }

    if (debugbot || LogInfo) {
        console.log('nach dem laden von ' + FileName + ': ' + Object.keys(VergleichJSON).length);
    }

    return VergleichJSON;
}
//sichert JSON objekte
function SaveJSONFile(SaveJSON, FileName) {
    if (debugbot) {
        console.log('sichern von ' + FileName + ': ' + Object.keys(SaveJSON).length);
    }
    var fs = require('fs');
    var jsonData = JSON.stringify(SaveJSON);
    fs.writeFile(FileName, jsonData, function (err) {
        if (err && debugbot) {
            console.log(err);
        }
    });
}
// Channel auswahl definiert
function loadChanel(Channelauswahl = true) {
    if (Channelauswahl) {
        return '645295187030966303'; //testchannel
    }
    else {
        return '171323657132572682'; // schreiben channel
    }
}
// Allgemeine Textausgabe behandeln
function AusgabeText(msg, tmessage) {
    // Aus diese Anzahl an Zeichen, reduzieren wir die Nachrichten.
    maxCarL = 2000;

    if (tmessage.length > maxCarL) {
        //Splitten der Nachrichten auf Zeilenumbrüche
        var arr = tmessage.split('\n');
        var curL = 0;
        var ausgabet = "";

        if (debugbot) {
            console.log("Textausgabe mit mehr als: " + maxCarL + " Aktuelle Anzahl: " + tmessage.length);
        }

        //Ausgabe neu zusammen setzten
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].length + curL > maxCarL) {
                msg.reply(ausgabet);
                //Reset ausgabe, da die ausgabe erfolgt ist.
                ausgabet = "";
            }
            else {
                //ausgabe weiter zusammenbauen
                ausgabet = ausgabet + arr[i] + '\n';
            }
            curL = ausgabet.length;
        }
        // den Rest ausgeben!
        msg.reply(ausgabet);
    }
    else {
        if (tmessage.substr(0, 1) == '/') {
            DiscordCommandOutput(msg, tmessage)
        }
        else {
            msg.reply(tmessage);
        }
    }
}
// Behandelt den allgemeinen discord command output (TTS)
function DiscordCommandOutput(msg, outputMessage) {
    // Ein TimeOut Jsons wo alle User notiert werden, welche zuletzt einen befehl ausgeführt haben.
    TimeOutUser = ReturnJSONFile(STimeOut, TimeOutUser);

    if (msg.member == null) {
        //Sprachbefehl im Privaten Chat unterbinden, da Fehler!
        return;
    }

    // aktuelle parameter abfragen
    var id_channel = msg.channel.id;
    var username = msg.member.id;
    var befehl = msg.content.toLowerCase().replace(/#/g, '');
    var erlauben = false;
    var guildID = msg.guild.id;
    var TUser = { "#befehl": "01.01.2019" };
    var tempTUser = null;
    // wenn User noch nicht gefunden wurde, darf eine textausgabe erfolgen
    if (TimeOutUser[username] == null) {
        erlauben = true;
    }
    else {
        // wenn der befehl noch nicht genutzt wurde
        tempTUser = TimeOutUser[username];
        if (tempTUser[befehl] == null) {
            erlauben = true;
        }
        else {
            // wurde der befehl gefunden, wird ermittelt ob die zeit mitlerweile erreicht wurde,
            // die zwischen tts commands gewartet werden soll
            var aktuell = new Date().toLocaleDateString();
            var old = new Date((tempTUser[befehl])).toLocaleDateString();

            //Vergleich aktuell Tag mit OldTag und wenn dieser kleiner ist, dann erlauben wir den Sprachbefehl!
            //hier m�sste wenn eine genauere Pr�fung rein.
            if (old < aktuell) {
                erlauben = true;
            }

            //Wenn eine bestimmte Rolle gefunden wurde, die mehr darf, so erlauebn wir auch die Sprachbefehle
            //Aktuell sind die Rollen: Master / Bot Master / Kleinkind
            if (msg.member.roles.some(r => ["Master", "Bot Master", "Kleinkind"].includes(r.name))) {
                if (debugbot) {
                    console.log("Sonderrole zur Sprachausgabe");
                }
                erlauben = true;
            }
        }
    }

    // Wenn der Command genutzt werden darf
    if (erlauben) {
        // wird im aktuellen channel der Command ausgegeben
        var ComAusgabe = client.guilds.find(s => s.id == guildID).channels.get(id_channel);

        if (outputMessage.substr(0, 4) == '/tts') {
            if (debugbot) {
                console.log("Sprachbefehl gefunden und im zeitlichen Rahmen: #" + befehl);
            }
            outputMessage = outputMessage.substr(4, outputMessage.length);
            ComAusgabe.send(outputMessage, { tts: true });
        }
        else {
            ComAusgabe.send(outputMessage);
        }

        // Jsons aufbauen
        var akt = new Date().toISOString();
        if (tempTUser != null) {
            TUser = null;
            TUser = tempTUser;
        }

        TUser[befehl] = akt;


        var TUSerJson = JSON.stringify(TUser);
        vTUSerJson = TUSerJson.replace(/\\/g, '');
        TimeOutUser[username] = TUSerJson;

        TimeOutUser = JSON.parse(JSON.stringify(TimeOutUser).replace(/\\/g, '').replace(/":"{/g, '":{').replace(/"}","/g, '"},"').replace(/"}"}/, '"}}'));

        SaveJSONFile(TimeOutUser, STimeOut);
    }
    else {
        msg.reply(outputMessage);
    }
}
// laedt JSON Objekte neu
function ForceLoad(consolemsg = true) {
    // sollte ein JSON nicht geladen werden koennen, so wird wegen dem "try" nichts unternommen
    try {
        AlleComDaten = ReturnJSONFile(SAlleComDaten, AlleComDaten, consolemsg);
    }
    finally { }
    try {
        WillkommenText = ReturnJSONFile(SWillkommen, WillkommenText, consolemsg);
    }
    finally { }
    try {
        AufwiedersehenText = ReturnJSONFile(SWiedersehen, AufwiedersehenText, consolemsg);
    }
    finally { }
    try {
        StatusText = ReturnJSONFile(SStatus, StatusText, consolemsg);
    }
    finally { }
    try {
        TimeOutUser = ReturnJSONFile(STimeOut, TimeOutUser, consolemsg);
    }
    finally { }
    try {
        DiceAktionText = ReturnJSONFile(SDiceAktion, DiceAktionText, consolemsg);
    }
    finally { }
    try {
        DiceObjektText = ReturnJSONFile(SDiceObjekt, DiceObjektText, consolemsg);
    }
    finally { }
    try {
        Musikliste = ReturnJSONFile(SMusikListe, Musikliste, consolemsg);
    }
    finally { }
}
// Eine DiceRollFunktion zur Random ausgabe 2er Texte die dann in zusammenhang stehen!
function DiceRoll(msg) {
    DiceAktionText = ReturnJSONFile(SDiceAktion, DiceAktionText, false);
    DiceObjektText = ReturnJSONFile(SDiceObjekt, DiceObjektText, false);

    var aktionz = Math.floor(Math.random() * Object.keys(DiceAktionText).length);
    var objektz = Math.floor(Math.random() * Object.keys(DiceObjektText).length);

    AusgabeText(msg, DiceObjektText[objektz] + ' ' + DiceAktionText[aktionz]);
}
//eine FUnktion, die fuer einen googelt
function GetHilfe(msg) {
    // Suchtext parsen
    var suchanfrage = msg.content.substr(7, msg.content.length - 7);
    var suchtext = require('querystring').escape(suchanfrage);
    var googleURL = 'https://cse.google.de/cse?q=' + suchtext + '&sa=Suche&cx=partner-pub-0030114367999801:7ve7oxp555y';
    // URL zur�ckgeben
    AusgabeText(msg, googleURL);
}

// --------- EREIGNISSE ---------
//Ereignis beim betreten des Channels
client.on('guildMemberAdd', member => {
    console.log("guildMemberAdd call")

    // Wenn Bot... dann Nichts
    if (member.user.bot) { return; }

    // die var member ist der Client der neu drauf gejoint ist
    // WillkommenAnfangText.length = die groesse array / anzahl der elemente
    StatusText = ReturnJSONFile(SStatus, StatusText);



    var channelzumschreiben = loadChanel(StatusText.channel);
    var deinWillkommChannel = client.guilds.find(s => s.id == `171323657132572682`).channels.get(channelzumschreiben);

    // Load JSON hier machen bitte
    // damit alle Commands geladen werden
    WillkommenText = ReturnJSONFile(SWillkommen, WillkommenText);

    var myc = Object.keys(WillkommenText).length;

    var nummer = Math.floor(Math.random() * myc);
    // random gibt eine zufallszahl zur�ck zwischen 0 und 1 bsp.:0.5

    var ausgabe = "" + WillkommenText[nummer];
    if (debugbot) {
        console.log(ausgabe); //debug ausgabe
    }

    ausgabe = ausgabe.replace(Aliasname, member.user.username);
    // ausgabe des arrays anhand einer zahl / arrays fangen bei 0 an zu zaehlen
    deinWillkommChannel.send(ausgabe);
    if (debugbot) {
        console.log(nummer); //debug ausgabe
        console.log(ausgabe); //debug ausgabe
    }
});

//Ereignis beim verlassene des Channels
client.on('guildMemberRemove', member => {

    // Wenn Bot... dann Nichts
    if (member.user.bot) { return; }

    // die var member ist der Client der neu drauf gejoint ist
    StatusText = ReturnJSONFile(SStatus, StatusText);

    // AufwiedersehenAnfangText.length = die groesse array / anzahl der elemente
    var channelzumschreiben = loadChanel(StatusText.channel);
    var deinWillkommChannel = client.guilds.find(s => s.id == `171323657132572682`).channels.get(channelzumschreiben);

    // Load JSON hier machen bitte
    // damit alle Commands geladen werden

    AufwiedersehenText = ReturnJSONFile(SWiedersehen, AufwiedersehenText);

    var myc = Object.keys(AufwiedersehenText).length;

    var nummer = Math.floor(Math.random() * myc);
    // random.next(x) gibt eine zufallszahl zur�ck zwischen 1 und X

    var ausgabe = "" + AufwiedersehenText[nummer];

    if (debugbot) {
        console.log(ausgabe); //debug ausgabe
    }

    ausgabe = ausgabe.replace(Aliasname, member.user.username);
    // ausgabe des arrays anhand einer zahl / arrays fangen bei 0 an zu zaehlen
    deinWillkommChannel.send(ausgabe);
    if (debugbot) {
        console.log(nummer); //debug ausgabe
        console.log(ausgabe); //debug ausgabe
    }
});

// Allgemeines Eregnis bei Chat Unterhaltungen
client.on('message', msg => {
    if (msg.author.bot) { return; }
    else {

        //wenn es kein command ist, springe raus... commands fangen immer mit # an hier definiert
        if (msg.content.toLowerCase()[0] != "#") {
            if (msg.tts) {
                msg.reply('Ist ja gut, wir wissen es, nun ist aber mal Ruhe!!!');
            }
            return;
        }

        //Forceload ausfuehren damit immer alles neu geladen wird!
        ForceLoad(false);

        // Load JSON hier machen bitte
        // damit alle Commands geladen werden
        AlleComDaten = ReturnJSONFile(SAlleComDaten, AlleComDaten);

        var FunktionText = msg.content.toLowerCase().split(' ');

        // antworte wenn gesagt wurde...
        if (msg.content.toLowerCase() == '#befehl') {	//Alle befehle / keys aus dem json ausgeben
            var Nachricht = "\nHier sind die Commands von dem Channel\n";
            Nachricht = Nachricht + Object.keys(AlleComDaten);
            Nachricht = Nachricht.replace(/,/g, '\n');

            AusgabeText(msg, Nachricht);
        }
        else {
            //Mehr Dimminsionen finden
            try {
                //sollte es moeglich sein, das im command mehrere commands versteckt sind
                //wird hier die anzahl ermittelt
                if (AlleComDaten[msg.content.toLowerCase()][0].length == 1) {
                    gross = 0;
                }
                else {
                    var gross = Object.keys(AlleComDaten[msg.content.toLowerCase()]).length;
                }
            }
            catch
            {
                gross = 0;
            }
            finally { }

            if (gross > 1) {
                if (debugbot) {
                    console.log('Mehrfachausgabe Elemente: ' + gross);
                }
                //Object wird zwischengespeichert, damit man direkt mit diesem arbeiten kann
                var obj2 = AlleComDaten[msg.content.toLowerCase()];
                var x = Math.floor(Math.random() * Object.keys(obj2).length);

                if (debugbot) {
                    console.log('Ausgabe txt ' + x);
                }
                //Random Ausgabe ueber Dieses Object
                AusgabeText(msg, obj2[x]); // falls mehr als 2000 Zeichen gebraucht werden
                //msg.reply (obj2[x]);
            }
            else if (AlleComDaten[msg.content.toLowerCase()] != null) {
                // Wenn der Content vorhanden ist, gebe diesen aus.
                AusgabeText(msg, AlleComDaten[msg.content.toLowerCase()]); // falls mehr als 2000 Zeichen gebraucht werden
                //msg.reply (AlleComDaten[msg.content.toLowerCase()]);
            }
            // Definierte Funktionen vom BOT
            else if (ComFunktionen[FunktionText[0]] != null) {
                console.log('Sonderfunktionen werden behandelt');
                switch (FunktionText[0].toLowerCase().trim()) {
                    case ComFunktionen[0]:
                    case '#hilfe':
                        console.log('Mach Hilfe');
                        GetHilfe(msg);
                        break;
                    case ComFunktionen[1]:
                    case '#dice':
                        console.log('Mach Roll');
                        DiceRoll(msg);
                        break;
                    default:
                        break;
                }
            }
            else {
                // wahrscheinlich ein geheimer command.... Uhhhhh Geheim...
                // JSON bearbeiten und / oder speichern
                try {
                    var geheimnis = msg.content.toString().split(GeheimerTrenner)
                    // ein geheimnis wird wiefolgt eingegeben Geheimnis befehl reaktion
                    if (GeheimeCommands[geheimnis[0]] != null) {
                        if (debugbot) {
                            console.log('geheimer Command ' + geheimnis[0]);
                            console.log('geheimer Command macht ' + GeheimeCommands[geheimnis[0]]);
                        }
                        var sichern = false;
                        if (GeheimeCommands[geheimnis[0]] == 'einfuegen') {
                            if (debugbot) {
                                console.log('neuer Command einfuegen: Elemente: ' + geheimnis.length);
                            }
                            sichern = true;
                            if (geheimnis.length <= 2) {
                                msg.reply('Habe dich leider nicht verstanden!');
                            }
                            else if (geheimnis.length == 3) {
                                if (debugbot) {
                                    console.log(geheimnis[1] + ' = ' + geheimnis[2]);
                                }

                                if (geheimnis[1][0] != '#') {
                                    // f�gt ein # ein falls es fehlt
                                    geheimnis[1] = '#' + geheimnis[1];
                                }
                                if ((GeheimeCommands[geheimnis[1].toLowerCase()] != null) ||
                                    (ComFunktionen[geheimnis[1].toLowerCase()] != null)) {
                                    msg.reply('Das geht so aber nicht!');
                                }
                                else {
                                    AlleComDaten[geheimnis[1].toLowerCase()] = geheimnis[2];
                                    msg.reply('Habe verstanden! Ist erledigt Cheffe!');
                                }
                            }
                            else {
                                if (debugbot) {
                                    console.log('neue Mehrfachauswahl zu: ' + geheimnis[1]);
                                }
                                if (geheimnis[1][0] != '#') {
                                    // f�gt ein # ein falls es fehlt
                                    geheimnis[1] = '#' + geheimnis[1];
                                }
                                if ((GeheimeCommands[geheimnis[1].toLowerCase()] != null) ||
                                    (ComFunktionen[geheimnis[1].toLowerCase()] != null)) {
                                    msg.reply('Das geht so aber nicht!');
                                }
                                else {
                                    //Json Object bauen fuer die mehrfachauswahl
                                    var textMehrfach = ',\"' + geheimnis[1].toLowerCase() + '\":\{';
                                    for (i = 2; i < geheimnis.length; i++) {
                                        textMehrfach = textMehrfach + '\"' + (i - 2) + '\":\"' + geheimnis[i] + '\"';
                                        if ((i + 1) < geheimnis.length) {
                                            textMehrfach = textMehrfach + ',';
                                        }
                                        else {
                                            textMehrfach = textMehrfach + '\}';
                                        }
                                    }
                                    var jsonText = JSON.stringify(AlleComDaten);
                                    jsonText = jsonText.substr(0, jsonText.length - 1); // entfernt die letzte Klammer
                                    jsonText = jsonText + textMehrfach + '\}';
                                    AlleComDaten = JSON.parse(jsonText);
                                    msg.reply('Habe verstanden! Ist erledigt Cheffe!');
                                }
                            }
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'rauswerfen') {
                            sichern = true;
                            if (AlleComDaten[geheimnis[1].toLowerCase()] != null) {
                                if (debugbot) {
                                    console.log('l�schen von: ' + geheimnis[1]);
                                }
                                // log was gel�scht wurde um es evt wieder herstellen zu k�nnen
                                var dellog = require('fs');
                                var delnachricht = '\nBefehl: ' + geheimnis[1] + '\n'
                                    + 'mit der Ausgabe: ' + AlleComDaten[geheimnis[1].toLowerCase()] + '\n'
                                    + 'wurde herausgenommen';
                                dellog.appendFile('./logs/dellog.txt', delnachricht, function (err) {
                                    if (err) {
                                        console.log('fehler beim loggen ' + err);
                                    }
                                });
                                try {
                                    delete AlleComDaten[geheimnis[1].toLowerCase()];
                                    msg.reply('Erledigt, Schau und Bye Bye');
                                }
                                catch (error) {
                                    console.log('fehler beim delete: ' + error);
                                }
                                finally { }
                            }
                            else {
                                msg.reply('Habe dich leider nicht verstanden!');
                            }
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'ausgabe') {
                            // Aufarbeitung
                            var ausgabedaten = "Ausgabe aller Commands aus dem Channel mit Ausgabewerten\n";
                            ausgabedaten = ausgabedaten + Object.entries(AlleComDaten);
                            //Zeilenumbruch einfuegen
                            if (debugbot) {
                                console.log(ausgabedaten);
                            }
                            ausgabedaten = ausgabedaten.replace(/,/g, '=');
                            ausgabedaten = ausgabedaten.replace(/= /g, ', ');
                            ausgabedaten = ausgabedaten.replace(/=\#/g, '\n\#');
                            ausgabedaten = ausgabedaten.replace(/\[object Object\]/g, 'Random Mehrfachauswahl');

                            AusgabeText(msg, ausgabedaten);
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'setting') {

                            if (geheimnis[1].toLowerCase() == 'debug') {
                                // debugging an / aus
                                debugbot = !debugbot;
                                StatusText["debugging"] = debugbot;
                                msg.reply("Debugging is:");
                                if (debugbot) {
                                    msg.reply("Aktiv");
                                }
                                else {
                                    msg.reply("Inaktiv");
                                }
                                sichern = true;
                            }
                            else if (geheimnis[1].toLowerCase() == 'channel') {
                                StatusText["channel"] = !StatusText["channel"];
                                msg.reply("Channelausgabe auf : " + (StatusText["channel"] ? "TestChannel" : "MainChannel"));
                                sichern = true;
                            }
                            else {
                                msg.reply("Statusanpassung wird vorgenommen");
                                client.user.setPresence({ game: { name: geheimnis[1], type: "streaming", url: geheimnis[2] } }).then().catch(console.error);
                                StatusText["name"] = geheimnis[1];
                                StatusText["url"] = geheimnis[2];
                                sichern = true;
                            }

                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'willkommen') {
                            sichern = true;
                            // TODO: Erweitern des JSON... Siehe Oben
                            var myc = Object.keys(WillkommenText).length;
                            WillkommenText[myc] = geheimnis[1];
                            msg.reply("Willkommenstext erweitert");
                        }

                        else if (GeheimeCommands[geheimnis[0]] == 'wiedersehen') {
                            sichern = true;
                            // TODO: Erweitern des JSON... Siehe Oben
                            var myc = Object.keys(AufwiedersehenText).length;
                            AufwiedersehenText[myc] = geheimnis[1];
                            msg.reply("Aufwiedersehenstext erweitert");
                        }

                        else if (GeheimeCommands[geheimnis[0]] == 'laden') {

                            msg.reply('alle JSON werden neu geladen! weiteres FeedBack im LOG!');

                            console.log('---');
                            sichern = true;
                            ForceLoad();
                            //Force debugstatus setzten!
                            debugbot = StatusText["debugging"];
                            console.log('---');
                        }

                        else if (GeheimeCommands[geheimnis[0]] == 'diceaddaktion') {
                            //#EditDiceAktion; XYZ
                            sichern = true;
                            DiceAktionText[Object.keys(DiceAktionText).length] = geheimnis[1];
                            msg.reply('neue Aktion bekannt');
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'diceaddobjekt') {
                            //#EditDiceObjekt; XYZ
                            sichern = true;
                            DiceObjektText[Object.keys(DiceObjektText).length] = geheimnis[1];
                            msg.reply('neues Objekt bekannt');
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'dicedeleteaktion') {
                            //#DeleteDiceAktion; Position (0)
                            if (DiceObjektText[geheimnis[1]] != null) {
                                sichern = true;
                                delete DiceAktionText[geheimnis[1]];
                                msg.reply('Aktion herausgenommen');
                            }
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'dicedeleteobjekt') {
                            //#DeleteDiceObejkt; Position (0)
                            if (DiceObjektText[geheimnis[1]] != null) {
                                sichern = true;
                                delete DiceObjektText[geheimnis[1]];
                                msg.reply('Objekt herausgenommen');
                            }
                        }
                        else if (GeheimeCommands[geheimnis[0]] == 'ping') {
                            const used = process.memoryUsage().heapUsed / 4096 / 4096;
                            msg.reply(`\n__Ping__:\n${client.ws.ping} ms\n__Memory__:\n${Math.round(used * 100) / 100} MB`);

                        }

                        if (sichern) {
                            // sichern der angepassten commands / commandliste
                            // User wird nciht gesichert, da er aktiv gesichert wird, wenn er verwendet wird bei tts-command
                            SaveJSONFile(AlleComDaten, SAlleComDaten);
                            SaveJSONFile(WillkommenText, SWillkommen);
                            SaveJSONFile(AufwiedersehenText, SWiedersehen);
                            SaveJSONFile(StatusText, SStatus);
                            SaveJSONFile(DiceAktionText, SDiceAktion);
                            SaveJSONFile(DiceObjektText, SDiceObjekt);
                        }
                    }
                }
                finally { }
            }
        }
    }
});
