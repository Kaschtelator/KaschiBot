const config = require('/home/kaschtelator/KaschiBot/Config/config');
const checkChannel_id = config.checkChannel_id;

let botIsConnected = false;

const restartModule = {
    start: (client) => {
        client.on('ready', () => {
            botIsConnected = true;
    
            setInterval(() => {
                if (!botIsConnected) {
                    console.log('Der Bot hat die Verbindung getrennt und überprüft den Kanalstatus...');
                    checkChannel();
                }
            }, 60000);
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
        const channel = client.channels.cache.get(checkChannel_id);
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