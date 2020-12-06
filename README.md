# HomeAssistant Component for IKEA IDÅSEN Sit-Standing desk

This is my -majorly hacky- way to implement the IDÅSEN desk (which is controlled via Bluetooth) in Home Assistant. Backbone is the excellent "[idasen-controller](https://github.com/rhyst/idasen-controller)" component by Rhyst, which handles all the Bluetooth interactions. The code in this repository merely provides an example wrapper (a simple Flask webhook), and an example component for integration in Home Assistant.

The current implementation only includes sitting ("off") and standing ("on") modes by design, since every interaction with the desk requires Bluetooth to pair with the desk again.

After installing the Systemd service, make sure to run the following commands.

```
sudo systemctl daemon-reload
sudo systemctl start nginx.service
```

Requires `Flask` to be installed (on top of the components required by idasen-control).