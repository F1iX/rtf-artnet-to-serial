# Broadcast DMX packages from Art-Net to Serial Device

Python script to read Art-Net data in a specified universe and send it to a serial device for physical DMX output.

## Prerequisites
- Linux
- Python
- Microcontroller with bus driver (e.g., Arduino Micro with MAX483) [running LeoDMX](https://github.com/bitfasching/leodmx)

To create a suitable virtual Python environment,
1. Run `python -m venv .venv`
1. Run `.venv/bin/pip install -r requirements.txt`

## Start
1. Run `python artnet2serial.py` (check `-h` for options)

## Autostart
### With cron
1. Adapt parameters in `runartnet2serial.sh`
1. Run `sudo crontab -e`
1. Add `@reboot sleep 5 && sh /home/pi/rtf-artnet-to-serial/runartnet2serial.sh`