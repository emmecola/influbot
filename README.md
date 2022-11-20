# influbot
This script retrieves the ISS data on flu from this GitHub repo: [https://github.com/fbranda/influnet](https://github.com/fbranda/influnet).
Then, it extracts relevant information about national incidence, most affected region and age class and draws two plots and a choropleth map using the shapefiles available on ISTAT website: [https://www.istat.it/it/archivio/222527](https://www.istat.it/it/archivio/222527).
Finally, it sends a toot using the Toot CLI and the Mastodon profile [influbot](https://sociale.network/@influbot) at sociale.network.

The script needs [toot](https://toot.readthedocs.io/).
