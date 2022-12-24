# influbot
This script retrieves the [ISS](https://www.epicentro.iss.it/influenza/influnet) data on flu from the [Influnet](https://github.com/fbranda/influnet) repository.

Then, it extracts relevant information about national incidence, most affected region and age class and draws two plots and a choropleth map using the [shapefiles](https://www.istat.it/it/archivio/222527) available on ISTAT website.

Finally, it sends a toot using the [Toot CLI](https://toot.readthedocs.io/) and the Mastodon profile [@influbot@sociale.network](https://sociale.network/@influbot).


## Instructions

If you want to try influbot on your computer, please follow these steps:

1. Install [`toot`](https://toot.readthedocs.io/en/latest/index.html) and [`pandas`](https://pandas.pydata.org/), [`matplotlib`](https://matplotlib.org/), [`seaborn`](https://seaborn.pydata.org/) and [`geopandas`](https://geopandas.org/en/stable/) Python packages.

    ```pip3 install -r requirements.txt```

2. Configure `toot` with your own Mastodon account, following [these instructions](https://toot.readthedocs.io/en/latest/usage.html#authentication).

3. Download from the [ISTAT website](https://www.istat.it/it/archivio/222527) the zip archive with the shapefiles, and extract it in the script folder.

4. The plotting functions use a custom font, [FigTree](https://fonts.google.com/specimen/Figtree), which was downloaded from Google Fonts. If you want, you can install a different font or use one of the default `matplotlib` fonts. Edit the script accordingly.

5. Create an `archive.txt` file that will keep track of the weeks already processed by the script.

5. Run `influbot.py`!
