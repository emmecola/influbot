#!/usr/bin/python3
"""This script retrieves the ISS data on flu from this GitHub repo:
https://github.com/fbranda/influnet
Then, it extracts relevant information about national incidence,
most affected region and age class and draws two plots and a
choropleth map using the shapefiles available on ISTAT website:
https://www.istat.it/it/archivio/222527
Finally, it sends a toot using the Toot CLI and the Mastodon profile
@influbot@sociale.network.
"""

# Import modules
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
import subprocess

# My variables
archive_file='archive.txt'
temp_file='temp.txt'
myfont='Figtree'
region_shapefile='Limiti01012022_g/Reg01012022_g/Reg01012022_g_WGS84.shp'
province_shapefile='Limiti01012022_g/ProvCM01012022_g/ProvCM01012022_g_WGS84.shp'

# Functions

def checkArchive(week,archive_file):
    with open(archive_file) as file:
        archive = [line.rstrip() for line in file]
    if week in archive:
        return False
    else:
        return True

def updateArchive(week,archive_file):
        o = open(archive_file,'a')
        o.write(week+"\n")
        o.close()

def cleanOutput(temp_file):
    subprocess.run("rm -rf *.png",shell=True)
    subprocess.run("> " + temp_file,shell=True)
        
def plot_incidence(df,myfont):
    palette = dict(zip(df["flu_season"].unique(), sns.color_palette('tab20', n_colors=len(df["flu_season"].unique()))))
    palette['2022-2023'] = 'black'
    sns.set_theme(style="white",font=myfont, rc={'figure.figsize':(15,10)}, font_scale=1.5)
    ax=sns.lineplot(data=df,x='week',y='incidence',hue='flu_season',linewidth=3,palette=palette)
    sns.despine()
    ax.set_xlabel('settimana',fontsize=20)
    ax.set_ylabel('casi ogni 1000 abitanti',fontsize=20)
    ax.set_title('Incidenza nel tempo', fontsize=25)
    ax.tick_params(axis='both',labelsize=15)
    ax.grid(axis='y',linestyle='dashed')
    leg = ax.legend(title="stagione", loc="upper left", bbox_to_anchor=(0.8, 1), fontsize=20)
    plt.setp(leg.get_title(),fontsize=20)
    for L in leg.get_lines():
        L.set_linewidth(3)
    plt.savefig("incidenza.png")
    plt.clf()
    
def plot_ageclass(df,last_week,myfont):
    sns.set_theme(style="white",font=myfont, rc={'figure.figsize':(15,10)}, font_scale=1.5)
    ax = sns.barplot(df)
    sns.despine()
    ax.set_xlabel('classi di età',fontsize=20)
    ax.set_ylabel('casi ogni 1000 abitanti',fontsize=20)
    ax.set_title('Incidenza per classi di età (settimana ' + last_week +')', fontsize=25)
    ax.tick_params(axis='both',labelsize=15)
    ax.grid(axis='y',linestyle='dashed')
    plt.savefig("classi_eta.png")
    plt.clf()
    
def draw_map(df,last_week,myfont):
    sns.set_theme(style="white",font=myfont, rc={'figure.figsize':(12,12)}, font_scale=1.8)
    fig, ax = plt.subplots(1, 1)
    ax = df.plot(column='incidence', ax=ax,legend=True, cmap='OrRd',missing_kwds={'color': 'lightgrey'},
             legend_kwds={'label': "casi ogni 1000 abitanti",'orientation': "vertical","shrink":.8})
    ax.set_axis_off()
    fig.axes[1].tick_params(labelsize=15)
    ax.set_title('Incidenza nelle regioni italiane (settimana ' + last_week +')', fontsize=25)
    plt.savefig("mappa.png")
    plt.clf()

def get_last_week(df):
    return df.sort_values(by='year_week')['year_week'].values[-1]

def get_previous_week(df):
    return df.sort_values(by='year_week')['year_week'].values[-2]

def get_incidence(df,week):
    return df[df['year_week']==week]['incidence'].values[0]

def get_top_region(df):
    df_sorted = df[pd.notna(df['incidence'])].sort_values(by=['incidence'],ascending=False)
    return df_sorted[['DEN_REG','incidence']].values[0]

def get_incidence_region(df,region):
    df_region = df[df['DEN_REG']==region]['incidence']
    if len(df_region) > 0:
        return df_region.values[0]
    else:
        return ''

def get_top_age(df):
    df_sorted = df.sort_values(by=[df.index[0]],axis=1,ascending=False)
    top_age = df_sorted.columns[0]
    top_age_incidence = df_sorted[top_age].values[0]
    return top_age,top_age_incidence

def get_incidence_age(df,age):
    return df[age].values[0]

def add_bolzano_trento(reg,prov):
    reg.loc[len(reg.index)] = [2,21,'Provincia Autonoma di Bolzano',
                                   prov[prov['COD_PROV']==21]['Shape_Leng'].values[0],
                                   prov[prov['COD_PROV']==21]['Shape_Area'].values[0],
                                   prov[prov['COD_PROV']==21]['geometry'].values[0]]
    reg.loc[len(reg.index)] = [2,22,'Provincia Autonoma di Trento',
                                   prov[prov['COD_PROV']==22]['Shape_Leng'].values[0],
                                   prov[prov['COD_PROV']==22]['Shape_Area'].values[0],
                                   prov[prov['COD_PROV']==22]['geometry'].values[0]]
    return reg

def preprocess_national(df):
    df['week'] = df['year_week'].str.split('-').str[1]
    sorter=['42','43','44','45','46','47','48','49','50','51','52','53',
        '01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17']
    sorterIndex = dict(zip(sorter, range(len(sorter))))
    df['week_rank'] = df['week'].map(sorterIndex)
    df.sort_values(by=['week_rank','flu_season'],inplace=True)
    df2=df[df['flu_season'].isin(['2017-2018','2018-2019','2019-2020','2020-2021','2021-2022','2022-2023'])]
    df2=df2[df2['week']!="53"]
    return df2
    
def preprocess_regional(df,reg,last_week):
    df['region'] = df['region'].replace('FriuliNAVenezia Giulia','Friuli-Venezia Giulia')
    df['region'] = df['region'].replace('Emilia Romag-','Emilia Romagna')
    df['region'] = df['region'].replace('Emilia-Romagna','Emilia Romagna')
    region_codes = {'Piedmont':1,'Aosta Valley':2,'Lombardy':3,'AP Bolzano':21,'AP Trento':22,
                    'Veneto':5,'Friuli-Venezia Giulia':6,'Liguria':7,'Emilia Romagna':8,
                    'Tuscany':9,'Umbria':10,'Marche':11,'Lazio':12,'Abruzzo':13,'Molise':14,
                    'Campania':15,'Apulia':16,'Basilicata':17,'Calabria':18,'Sicily':19,'Sardinia':20}
    df['region_code'] = df.apply(lambda row: region_codes[row['region']], axis=1)
    reg = reg.merge(df,left_on='COD_REG',right_on='region_code')
    reg = reg[reg["year_week"]==last_week]
    return reg

def df_by_age(df,last_week):
    age_columns = ['inc_0-4','inc_5-14','inc_15-64','inc_65+']
    rename_columns = {'inc_0-4': '0-4', 'inc_5-14': '5-14','inc_15-64': '15-64', 'inc_65+': '65+'}
    df_by_age = df[df['year_week']==last_week][age_columns].rename(columns=rename_columns)
    return df_by_age

def calculate_trend(last,previous):
    if previous != '':
        if last > previous:
            return 'aumento'
        elif previous > last:
            return 'calo'
        else:
            return ''
    else:
        return ''

def prepare_toot(values,temp_file):

    national_trend = calculate_trend(values['last_incidence'],values['previous_incidence'])
    regional_trend = calculate_trend(values['last_incidence_region'],values['previous_incidence_region'])
    age_trend = calculate_trend(values['last_incidence_age'],values['previous_incidence_age'])
        
    text = 'Monitoraggio influenza in Italia (settimana ' + values['last_week'] +')\n\n'
    text += 'Nella scorsa settimana, l\'incidenza dell\'influenza in Italia è stata di '
    text += str(values['last_incidence']).replace('.',',') + ' casi ogni 1000 persone'
    
    if national_trend != '':
        text += ', in ' + national_trend + ' rispetto alla settimana precedente (' + str(values['previous_incidence']).replace('.',',') + '). '
    else:
        text += '. '
    
    if values['top_region'] in ['Piemonte','Veneto','Friuli Venezia Giulia','Lazio','Molise']:
        text += 'La regione più colpita è il '
    elif values['top_region'] in ['Abruzzo']:
        text += 'La regione più colpita è l\''
    elif values['top_region'] in ['Marche']:
        text += 'La regione più colpita sono le '
    else:
        text += 'La regione più colpita è la '

    text += values['top_region'] + ', con ' + str(values['last_incidence_region']).replace('.',',') + ' casi su 1000'
        
    if regional_trend != '':
        text += ', in ' + regional_trend + ' rispetto alla settimana precedente (' + str(values['previous_incidence_region']).replace('.',',') + '). '
    else:
        text += '. '
    
    text += 'La fascia d\'età più colpita è quella '
    
    if values['top_age'] == '0-4':
        text += 'dei bambini sotto i 5 anni' 
    elif values['top_age'] == '5-14':
        text += 'tra i 5 e i 14 anni'
    elif values['top_age'] == '15-64':
        text += 'tra i 15 e 64 anni'
    elif values['top_age'] == '65+':
        text += 'degli over 65'
    else:
        pass

    text += ', con ' + str(values['last_incidence_age']).replace('.',',') + ' casi su 1000'
    
    if age_trend != '':
        text += ', in ' + age_trend + ' rispetto alla settimana precedente (' + str(values['previous_incidence_age']).replace('.',',') + ').'
    else:
        text += '. '

    with open(temp_file,'w') as f:
        f.write(text)

def toot(temp_file):
    command_string = "cat " + temp_file + " | toot post -v public -m incidenza.png -m mappa.png -m classi_eta.png"
    subprocess.run(command_string,shell=True)

def main():

    # Import data
    df = pd.read_csv("https://raw.githubusercontent.com/fbranda/influnet/main/data-aggregated/epidemiological_data/national_cases.csv")
    df_R = pd.read_csv("https://raw.githubusercontent.com/fbranda/influnet/main/data-aggregated/epidemiological_data/regional_cases.csv")

    # Load shapefiles
    reg = gpd.read_file(region_shapefile)
    prov = gpd.read_file(province_shapefile)

    # Obtain last week
    last_week = get_last_week(df)

    if checkArchive(last_week,archive_file):
    
        # Obtain previous week
        previous_week = get_previous_week(df)
    
        # Process national data
        last_incidence = get_incidence(df,last_week)
        previous_incidence = get_incidence(df,previous_week)
        df = preprocess_national(df)
    
        # Process regional data
        reg = add_bolzano_trento(reg,prov)
        reg_last = preprocess_regional(df_R,reg,last_week)
        reg_previous = preprocess_regional(df_R,reg,previous_week)
        top_region, last_incidence_region = get_top_region(reg_last)
        previous_incidence_region = get_incidence_region(reg_previous,top_region)
    
        # Process age class data
        df_age_last = df_by_age(df,last_week)
        df_age_previous = df_by_age(df, previous_week)
        top_age, last_incidence_age = get_top_age(df_age_last)
        previous_incidence_age = get_incidence_age(df_age_previous,top_age)
    
        # Write toot
        values = {'last_week':last_week,
                  'previous_week':previous_week,
                  'last_incidence':last_incidence,
                  'previous_incidence':previous_incidence,
                  'top_region':top_region,
                  'last_incidence_region':last_incidence_region,
                  'previous_incidence_region':previous_incidence_region,
                  'top_age':top_age,
                  'last_incidence_age':last_incidence_age,
                  'previous_incidence_age':previous_incidence_age}
        prepare_toot(values,temp_file)
    
        # Make plots
        plot_incidence(df,myfont)
        plot_ageclass(df_age_last,last_week,myfont)
        draw_map(reg_last,last_week,myfont)
    
        # Send toot
        toot(temp_file)
        updateArchive(last_week,archive_file)
        cleanOutput(temp_file)
        
    else:
        pass

if __name__ == "__main__":
    main()



