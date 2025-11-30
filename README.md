# Books Bot

A Telegram bot that helps users search and download books for free using dBooks.org. The bot supports both direct messaging and inline mode for seamless book discovery.

## Live Demo

Try the bot on Telegram: [@MTBooks_Downloader_Bot](https://t.me/MTBooks_Downloader_Bot)

## Features

- **Book Search**: Search for books by title, author, or keywords
- **Multiple Search Modes**: 
  - Direct messaging: Send a book name to get search results
  - Inline mode: Use `@MTBooks_Downloader_Bot <search term>` in any chat
- **Direct Download Links**: Get instant download links from dBooks.org
- **Rich Book Information**: View title, authors, publisher, pages, and publication year
- **Pagination**: Browse through multiple search results with emoji-only buttons (⏩, ⏪, ⬇️, ❎)
- **User Management**: Built-in database for user tracking and statistics
- **Terms of Service**: Users must accept ToS before using the bot
- **Admin Commands**: Statistics and user management for admins
- **Logging**: Comprehensive logging for debugging and monitoring

## Technologies Used

- **Python 3.8**
- **pyTelegramBotAPI**: Telegram Bot API wrapper
- **MongoDB**: User data storage via pymongo
- **python-dotenv**: Environment variable management
- **dBooks.org API**: REST API for book search and downloads
- **Docker**: Containerized deployment


## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB database (local or cloud)
- Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/BraveRam/Books-bot.git
   cd Books-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   
   Create a `.env` file in the project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your credentials:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   MONGO_DB_URL=your_mongodb_connection_string
   ADMINS_ID=your_telegram_user_id
   ```
   
   **Note**: For multiple admins, separate IDs with commas: `ADMINS_ID=123456789,987654321`

4. **Run the bot**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t books-bot .
   ```

2. **Run the container**
   ```bash
   docker run -d books-bot
   ```

## Usage

### User Commands

- `/start` - Initialize the bot and accept Terms of Service
- `/tos` - View Terms of Service
- `/help` - Display help message
- `/stats` - View bot statistics (admin only)
- Send any text message to search for books

### Inline Mode

Type `@MTBooks_Downloader_Bot` followed by your search query in any chat to search for books inline.

Example:
```
@MTBooks_Downloader_Bot Rich dad poor dad
```

### Download Flow

1. Search for a book using text message or inline mode
2. Browse through results using ⏩ and ⏪ buttons
3. Click ⬇️ to get a download link
4. The bot will provide a direct download link to the book

## dBooks.org Integration

The bot uses the dBooks.org REST API for book search and downloads:
- Search endpoint: `https://www.dbooks.org/api/search/{query}`
- Book details: `https://www.dbooks.org/api/book/{id}`

All books are sourced from dBooks.org's free programming books collection.

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

This bot does not own any of the content available through dBooks.org. All content belongs to their respective copyright holders.

## License

This project is open source and available under the MIT License.

## Credits

Developed by [BraveRam](https://github.com/BraveRam)

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact [@BetterParrot](https://t.me/BetterParrot) on Telegram.

## Star the Project

If you find this bot useful, please give it a star on GitHub! Your support is appreciated.
