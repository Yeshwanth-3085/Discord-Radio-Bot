# Discord Radio Bot

This Discord bot streams a radio station, provides now-playing information, and allows users to connect, disconnect, and move the bot between voice channels. It fetches song metadata and displays it in an embedded message.

## Features

- **Connect** to a voice channel and stream a radio station: `$connect`
- **Disconnect** the bot from the voice channel: `$disconnect`
- **Move** the bot between voice channels: `$move`
- **Check bot latency**: `$ping`
- **Now Playing**: Display the currently playing song, album, and artist.

## Requirements

You need to have Python 3.12 installed (recommended via Microsoft Store), along with the following libraries:

- `discord.py==2.4.0`
- `PyNaCl==1.5.0`
- `yt-dlp==2024.10.22`

These libraries are listed in the `requirements.txt` file for easy installation.

## Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Under the application, create a bot and enable `MESSAGE CONTENT INTENT`.
3. Copy the bot token and replace `YOUR-BOT-TOKEN` in `Radio.py`.
4. Install `ffmpeg` and add it to `Environment Variables`.
5. Install the required dependencies (CMD):
   ```bash
   pip install -r requirements.txt
   ```
6. Run the bot (CMD):
   ```bash
   python Radio.py
   ```

## Note

This bot streams only one radio station: [107.7 Pulse FM (CISF FM)](https://listen.streamon.fm/cisffm).  
Currently, it only supports a single server, but multi-server functionality may be added in the future.  
If you encounter any bugs, feel free to reach out, and I'll work to resolve them.

**Project Link:** [Discord Radio Bot](https://github.com/Yeshwanth-3085/Discord-Radio-Bot)

## Contact

- **Email:** yeshwanthngs1r@gmail.com
- **Twitter (X):** [Yeshwanth N (@Yeshwanth_3085)](https://twitter.com/Yeshwanth_3085)
- **LinkedIn:** [Yeshwanth N](https://www.linkedin.com/in/yeshwanth-n-74966718b)
- **Discord Server:** [MARAUDER YESH](https://dsc.gg/marauder-yesh)
- **Discord Profile:** [Yeshwanth N (marauder_yesh) — (Originally known as Yeshwanth N#4663)](https://discord.com/users/761630967706157127)
- **GitHub:** [Yeshwanth N (Yeshwanth-3085)](https://github.com/Yeshwanth-3085)

## License

This project is open-source and free to use. No copyright restrictions.
