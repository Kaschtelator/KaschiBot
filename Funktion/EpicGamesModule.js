const config = require('/home/kaschtelator/KaschiBot/Config/config');
const fs = require('fs');
const axios = require('axios');
const Discord = require('discord.js');
const discord_channel_id = config.freegames_discord_channel_id;
let lastGames = [];
var moduleEnabled = true; // Starten Sie das Modul standardmäßig aktiviert
var debugbot = true;

let interval;

const epicModule = {
  checkForNewFreeGames: (client) => {
    client.on('message', message => {
      if (message.content === '!epic') {
        checkForNewFreeGames();
      }

      if (message.content === '!epicoff') {
        // Deaktivieren Sie das Modul, wenn !epicoff eingegeben wird
        moduleEnabled = false;
        clearInterval(interval); // Stoppen Sie das Intervall
        message.channel.send("Das Epic-Modul wurde deaktiviert.");
        console.log('Das Epic-Modul wurde deaktiviert.');
      }

      if (message.content === '!epicon') {
        // Aktivieren Sie das Modul, wenn !epicon eingegeben wird
        moduleEnabled = true;
        // Dieser Timer in Millisekunden löst eine Suche aus, wenn er abgelaufen ist.
        // 10800000 ms sind 3 Stunden
        // 7200000 ms sind 2 Stunden
        // 3600000 ms sind 1 Stunde
        // 1800000 ms sind 30 Minuten.
        // 1200000 ms sind 20 Minuten
        // 600000  ms sind 10 Minuten
        interval = setInterval(checkForNewFreeGames, 600000); // Starten Sie das Intervall erneut
        message.channel.send("Das Epic-Modul wurde aktiviert.");
        console.log('Das Epic-Modul wurde aktiviert.');
      }
    });

    function checkForNewFreeGames() {
      if (!moduleEnabled) {
        console.log('Das Epic-Modul ist deaktiviert.');
        return;
      }
      if (!fs.existsSync('/home/kaschtelator/KaschiBot/Datenbank/lastEpicGames.json')) {
        fs.writeFileSync('/home/kaschtelator/KaschiBot/Datenbank/lastEpicGames.json', '[]');
      }

      try {
        lastGames = JSON.parse(fs.readFileSync('/home/kaschtelator/KaschiBot/Datenbank/lastEpicGames.json'));
      } catch (err) {
        console.log('lastEpicGames.json nicht gefunden');
      }

      const url = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=de-DE&country=DE&allowCountries=DE';
      axios.get(url)
        .then(response => {
          const promotions = response.data?.data?.Catalog?.searchStore;
          if (!promotions) {
            if (debugbot) {
              console.log('Keine neuen Spiele gefunden.');
            }
            return;
          }

          const freeGames = promotions.elements.filter(game => {
            const hasPromotion = game.promotions?.promotionalOffers?.length > 0;
            const discountPercentage = game.promotions?.promotionalOffers[0]?.promotionalOffers[0]?.discountSetting?.discountPercentage || 0;
            return hasPromotion && discountPercentage === 0;
          });

          if (freeGames.length === 0) {
            if (debugbot) {
              console.log('Keine neuen kostenlosen Spiele gefunden.');
            }
            return;
          }
          freeGames.forEach(game => {
            const gameTitle = game.title;
            const pageSlug = game.catalogNs && game.catalogNs.mappings && game.catalogNs.mappings[0] ? game.catalogNs.mappings[0].pageSlug : null;

            if (pageSlug) {
              // Sie können pageSlug hier sicher verwenden
            } else {
              // Behandeln Sie den Fall, in dem pageSlug null oder undefiniert ist
            }
            const gameUrl = `https://www.epicgames.com/store/de/p/${pageSlug}`;
            const existingGame = lastGames.find(g => g.id === game.id);
            if (existingGame) {
              if (debugbot) {
                console.log(`Spiel ${game.id} (${gameTitle}) wurde bereits gepostet.`);
              }
              return;
            }
            lastGames.push({ id: game.id });
            console.log(`Spiel ${game.id} (${gameTitle}) - URL: ${gameUrl}`);



            const gameImage = game.keyImages[0]?.url;
            const gameDescription = game.description;
            const originalPrice = game.price?.totalPrice?.originalPrice;

            if (originalPrice === 0) {
              // Spiel hat einen Originalpreis von 0, überspringe es
              if (debugbot) {
                console.log(`Spiel ${game.id} (${gameTitle}) hat keinen Originalpreis und wird übersprungen.`);
              }
              return;
            }

            const formattedPrice = `${(originalPrice / 100).toFixed(2)}€`;
            const priceText = `:moneybag: ${formattedPrice} **➜ Kostenlos!**`;

            const embed = new Discord.RichEmbed()
              .setTitle(`Kostenlos bei Epic Games:\n${gameTitle}`)
              .setDescription(`Schnappt es euch :point_right_tone1: [Epicgames.com](${gameUrl}) :point_left_tone1:`)
              .setColor('#ffb700')
              .setTimestamp()
              .setImage(gameImage)
              .addField('Beschreibung', gameDescription)
              .addField('Originalpreis', priceText);

            const channel = client.channels.find(ch => ch.id === discord_channel_id);
            channel.send('@everyone', { embed });
            if (debugbot) {
              console.log(`Spiel ${game.id} (${gameTitle}) wurde Veröffentlicht.`);
            }
          });

          fs.writeFileSync('/home/kaschtelator/KaschiBot/Datenbank/lastEpicGames.json', JSON.stringify(lastGames), err => {
            if (err) {
              console.error(err);
            }
          });
        })
        .catch(error => {
          if (debugbot) {
            console.log(error);
          }
        });
    }
  }
}

module.exports = epicModule;
