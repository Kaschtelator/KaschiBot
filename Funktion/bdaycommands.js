const fs = require('fs');

module.exports = {
    addCommand: function (client) {
        client.on('message', message => {
            if (message.author.bot) return; // Ignoriere nachrichten vom Bot.
            if (!message.content.startsWith('!addgeburtstag')) return; // Nachrichten ignorieren, die nicht beginnen mit "!addgeburtstag"
            var input = message.content.split(" ");
            if (input.length !== 3) {
                message.channel.send("Du hast addgeburtstag genutzt aber Falsch, bitte nutze es so wie hier beschrieben !addgeburtstag [Name] [TT-MM] & deine eingabe wird nach 20 Sek Gelöscht weil Sicherheit und so :shushing_face: ").then(sentMessage => {
                    console.log('!addgeburtstag wurde Falsch vom Nutzer verwendet oder nicht genug daten eingegeben');
                    setTimeout(() => {
                        message.delete();
                        sentMessage.delete();
                    }, 20000);
                });
                return;
            }
            var name = input[1];
            var date = input[2]; // Das format vom Datum ist TT-MM

            var heute = new Date();
            var jahr = heute.getFullYear() - 1; //ermittel das letzte jahr damit dieses abgespeichert werden kann
            // nicht dieses jahr, da der geburtstag noch dieses jahr sein kann!

            addBirthday(name, date, jahr);
            message.channel.send("Geburtstag hinzugefügt! Deine Eingaben werden nach 20 Sek Gelöscht dein Geburtstag bleibt erstmal unser Geheimnis :shushing_face: ").then(sentMessage => {
                setTimeout(() => {
                    message.delete();
                    sentMessage.delete();
                }, 20000);
            });
            console.log('Geburtstag von Nutzer hinzugefügt!');
        });
        function addBirthday(name, date, jahr) {
            var birthdays;
            try {
                birthdays = JSON.parse(fs.readFileSync('/home/kaschtelator/KaschiBot/Datenbank/birthdays.json', 'utf-8'));
            } catch (err) {
                birthdays = [];
                fs.writeFileSync('/home/kaschtelator/KaschiBot/Datenbank/birthdays.json', JSON.stringify(birthdays));
            }
            // das jahr mit abspeichern
            birthdays.push({ name, date, jahr });
            fs.writeFileSync('/home/kaschtelator/KaschiBot/Datenbank/birthdays.json', JSON.stringify(birthdays));
        }
    }
}