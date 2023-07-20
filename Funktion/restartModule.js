const Discord = require('discord.js');
const config = require('/home/kaschtelator/KaschiBot/Config/config');
const checkChannel_id = config.checkChannel_id;

let botIsConnected = false;
let client; // Discord.js-Client hinzufügen

const restartModule = {
    start: (discordClient) => { // Den Discord.js-Client als Argument übergeben
        client = discordClient; // Den Client setzen

        client.on('ready', () => {
            botIsConnected = true;

            setInterval(() => {
                if (!botIsConnected) {
                    console.log('Der Bot hat die Verbindung getrennt und überprüft den Kanalstatus...');
                    restartModule.checkChannel();
                }
            }, 1800000);
        });

        client.on('disconnect', () => {
            botIsConnected = false;
        });

        client.on('message', msg => {
            if (msg.content === '!restart') {
                restartModule.restartBot(msg);
            }
        });
    },
    checkChannel: () => {
        const channel = client.channels.find(ch => ch.id === checkChannel_id); // Den Client verwenden
        if (channel) {
            channel.send("Der Bot ist getrennt und versucht, die Verbindung wiederherzustellen...")
                .then(() => restartModule.restartBot())
                .catch(console.error);
        } else {
            console.log("Kanal kann nicht erreicht werden, Bot wird neu gestartet...");
            restartModule.restartBot();
        }
    },
    restartBot: (message) => {
        message.channel.send("KaschiBot wird neugestartet...")
            .then(() => process.exit())
            .then(() => client.login(config.token))
            .catch(console.error);
    }
};

module.exports = restartModule;
