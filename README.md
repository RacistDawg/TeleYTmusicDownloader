

A simple Telegram bot that downloads audio from any YouTube or YouTube Music link, embeds the correct metadata (title, artist, cover art), and sends it as an MP3 file.

## Features

-   ✅ Supports both regular YouTube and YouTube Music links.
-   🖼️ Automatically embeds the video thumbnail as album art.
-   🎤 Fills in the correct song title and artist in the MP3 tags.
-   🧹 Cleans up downloaded files from the server after sending.

## Setup & Installation

Follow these steps to get your own version of the bot running.

### Prerequisites

-   Python 3.8 or newer
-   [FFmpeg](https://ffmpeg.org/download.html): A crucial tool for processing audio. Make sure it's installed and accessible in your system's PATH.
    -   **Windows**: Download from the official site and add the `bin` folder to your PATH.
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt update && sudo apt install ffmpeg`

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Get your Telegram Bot Token:**
    -   Talk to the `@BotFather` on Telegram.
    -   Use the `/newbot` command to create a bot.
    -   He will give you a **token**. Keep it safe!

5.  **Configure your bot token:**
    -   Create a new file in the project folder named `.env`.
    -   Add your token to this file like so:
        ```
        TELEGRAM_BOT_TOKEN="wawawawa"
        ```

## Running the Bot

Once you've completed the setup, simply run the bot with this command:

```bash
python bot.py
```

Your bot should now be online and responding to messages!

