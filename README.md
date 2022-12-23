# influbot
This script retrieves the [ISS](https://www.epicentro.iss.it/influenza/influnet) data on flu from the [Influnet](https://github.com/fbranda/influnet) repository.

Then, it extracts relevant information about national incidence, most affected region and age class and draws two plots and a choropleth map using the [shapefiles](https://www.istat.it/it/archivio/222527) available on ISTAT website.

Finally, it sends a toot using the [Toot CLI](https://toot.readthedocs.io/) and the Mastodon profile [@influbot@sociale.network](https://sociale.network/@influbot).
