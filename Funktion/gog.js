//! Libs: node-fetch, jsdom	requried!!!
const fetch = require('node-fetch');
const { JSDOM } = require('jsdom');
const schedule = require('node-schedule');
var gamecount = 0;
/**
 * Fetches the HTML from the given URL and extracts the product tiles.
 * @param {*} url 
 * @returns void
 * @throws Error
 * @returns {Promise<Array>} Array of game data objects
 * @autor Fabian001
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchAndExtractData(url) {
  try {
    const response = await fetch(url);
    const html = await response.text();

    const dom = new JSDOM(html);
    const { document } = dom.window;

    const productTiles = document.querySelectorAll('a.product-tile.product-tile--grid');
    const products = [];

    productTiles.forEach(productTile => {
      const attributes = Array.from(productTile.attributes).reduce((acc, { name, value }) => {
        acc[name] = value;
        return acc;
      }, {});

      const productTitle = productTile.querySelector('.product-tile__title');
      if (productTitle) {
        const titleAttribute = productTitle.getAttribute('title');
        attributes.title = titleAttribute;
      }
      //? Only the title is needed the rest is for future use
      products.push(attributes);
    });

    const gameDataArray = [];

    for (const product of products) {
      const searchQuery = encodeURIComponent(product.title);
      const secondaryUrl = `https://www.gog.com/games/ajax/filtered?mediaType=game&search=${searchQuery}`;
      const secondaryResponse = await fetch(secondaryUrl);
      const jsonData = await secondaryResponse.json();
      if (jsonData.products.length === 0 || jsonData.totalResults === "0") {
        console.warn(`No results for ${product.title} (${product.href})`);
        break;
      }
      gameDataArray.push(jsonData);
    }

    return gameDataArray;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

/**
 * @function sendEmbedMessage
 * @param {*} webhookUrl 
 * @param {*} embed 
 * @description Sends the embed message to the given discord webhook URL. 
 * @returns void
 * @autor Fabian001
 */
async function sendEmbedMessage(webhookUrl, embed, notifyeveryone) {
  try {
    var response = null;

    if (notifyeveryone === true) {

      response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ embeds: [embed], content: "@here Free stuff" }),
      });
    }
    else {
      response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ embeds: [embed] }),
      });
    }

    if (!response.ok) {
      console.warn(response)
      throw new Error(`Request failed with status ${response.status}`);
    }

    console.log('Giveaway-Embed message sent successfully!');
  } catch (error) {
    console.error('Error sending the giveaway-embed message:', error);
  }
}

console.log("Motion Control: START")
// 0 17 * * 5
/// */30 * * * * *
//? Main Programm
//? Run this function every hour
schedule.scheduleJob('0 17 * * 5', () => {
  const url = 'https://www.gog.com/de/games?priceRange=0,0&discounted=true';//  <-- Kostenlose Games
  //const url = "https://www.gog.com/de/games?priceRange=0.39,0.39&discounted=true"; // <-- 0.39€ Games TESTING ONLY


  fetchAndExtractData(url)
    .then(gameDataArray => {
      //console.log('Game Data Array:', gameDataArray);
      /*
        Füge hier die Discord Webhook URL ein | Oder Ändere die Send Funktion um ^^ 
      */
      const webhookUrl = "Füge hier die Discord Webhook URL ein";
      if (gameDataArray.length == 0) { console.warn(`${new Date().toUTCString()} - No Free Games found`); return };
      //?? Optional you can also use gameData.products[0] but maybe you want to add more infos in the future
      //? Iterate over the gameDataArray
      gamecount = 0;
      // Vor der schleife gamecount auf 0 setzten 
      for (const gameData of gameDataArray) {
        //console.log(gameData.products);
        //zählen der "games" für jede gameData +1 
        gamecount = gamecount + 1;


        // 1 second delay
       //sleep (3000);

        if (gameData.length == 0) { console.warn(`${new Date().toUTCString()} - No Free Games found`); return };

        //? All important values in one object
        //
        const collectedValues = {
          "title": gameData.products[0].title,
          "oldprice": gameData.products[0].price.baseAmount,
          "amount": gameData.products[0].price.amount,
          "url": "https://gog.com" + gameData.products[0].url,
          "img": "https://images.gog-statics.com/" + gameData.products[0].image.split('/')[3] + "_product_tile_80x114_2x.webp",
        }
        //console.log(collectedValues);
        const embed = {
          title: `Kostenlos bei GOG: \m${collectedValues.title}`,
          color: 10181046,
          image: {
            url: collectedValues.img,
          },
          fields: [
            {
              name: `~~${collectedValues.oldprice} €~~  -> ${collectedValues.amount == 0.0 ? "Kostenlos!!!" : collectedValues.amount + " €"}`,
              value: `[Klick hier zum Giveaway](${collectedValues.url})`,
              inline: true,
            },
          ],
        };
        //Wenn gamecount größer 1, dann kein everyone, wenn 1 dann mit everyone
        if (gamecount === 1) {
          sendEmbedMessage(webhookUrl, embed, true);
        }
        else {
          sendEmbedMessage(webhookUrl, embed, false);
        }
      }
      console.log(`${new Date().toUTCString()} - Games found`);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  console.log('Job finished!');
});

module.exports = {
  fetchAndExtractData,
  sendEmbedMessage
};