require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;
const VERIFY_TOKEN = process.env.FACEBOOK_VERIFY_TOKEN;
const PROCESSOR_ENDPOINT = process.env.PROCESSOR_ENDPOINT;

// Middleware
app.use(bodyParser.json());

// Webhook verification (required by Messenger)
app.get('/webhook', (req, res) => {

    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode && token === VERIFY_TOKEN) {
        console.log('Webhook Verified');
        res.status(200).send(challenge);
    } else {
        res.sendStatus(403);
    }
});

// Handling messages
app.post('/webhook', async (req, res) => {
    const body = req.body;

    if (body.object === 'page') {
        body.entry.forEach(entry => {
            const event = entry.messaging[0];
            const senderId = event.sender.id;

            if (event.message && event.message.text) {
                const userMessage = event.message.text;

                // Respond to the user
                sendMessage(senderId, userMessage);
            }
        });

        res.status(200).send('EVENT_RECEIVED');
    } else {
        res.sendStatus(404);
    }
});

// Function to send a message
const sendMessage = async (recipientId, userMessage) => {
    const url = `https://graph.facebook.com/v16.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`;

    const getMessage = await axios.post(
        PROCESSOR_ENDPOINT, 
        { 
            user: recipientId,
            query: userMessage
        });

    const payload = {
        recipient: { id: recipientId },
        message: { text: getMessage }
    };

    try {
        await axios.post(url, payload);
        console.log('Message sent!');
    } catch (error) {
        console.error('Error sending message:', error.response.data);
    }
};

// Start the server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
