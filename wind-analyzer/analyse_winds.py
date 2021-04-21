import csv
import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.image import NonUniformImage


def to_float(in_str):
    """
    Convert a string to a float, and returns NaN if the value is 'mq' ('manquant')

    Args:
        in_str (str): input to convert

    Returns:
        (float): the converted input
    """
    if in_str == 'mq':
        return np.nan
    else:
        return float(in_str)


def extract_data_for_single_station(station_id, in_csvs):
    """
    Extract the data for a single station id

    Args:
        station_id (int): the id for the station
        in_csvs (list[Path]): list of inputs .csv to take data from

    Returns:

    """
    data_as_dict = {
        'datetime': [],
        'wind_dir': [],
        'wind_speed': [],
        'temperature': [],
        'humidity': [],
        'gust_ten': [],
        'day': [],
        'hour': [],
    }
    for in_csv in in_csvs:
        print(in_csv)
        with open(in_csv, "r") as fir:
            input_reader = csv.reader(fir, delimiter=',')
            for line_id, line in enumerate(input_reader):
                # sometimes the header is repeated in the middle of the file, so we ignore it
                try:
                    current_id = int(line[0])
                except ValueError:
                    print('Error in row {}, line is {}'.format(line_id, line))
                    current_id = None

                if current_id == station_id:
                    current_date = datetime.datetime.strptime(line[1],
                                                              "%Y%m%d%H%M%S")  # .replace(tzinfo=datetime.timezone.utc)
                    data_as_dict['datetime'].append(current_date)
                    data_as_dict['wind_dir'].append(to_float(line[2]))
                    data_as_dict['wind_speed'].append(to_float(line[3]))
                    data_as_dict['temperature'].append(to_float(line[4]))
                    data_as_dict['humidity'].append(to_float(line[5]))
                    data_as_dict['gust_ten'].append(to_float(line[6]))
                    data_as_dict['day'].append(current_date.date())
                    data_as_dict['hour'].append(current_date.hour)

    df = pd.DataFrame.from_dict(data=data_as_dict)

    # Convert the fields to hour, so we have 1 row per day
    data_per_day = {}
    for row_id, row in df.iterrows():
        current_day = str(row['day'])
        if current_day not in data_per_day:
            data_per_day[current_day] = {}
        hour = '{:02d}'.format(row['hour'])
        data_per_day[current_day]['wind_dir_{}'.format(hour)] = row['wind_dir']
        data_per_day[current_day]['wind_speed_{}'.format(hour)] = row['wind_dir']
        data_per_day[current_day]['temperature_{}'.format(hour)] = row['wind_dir']
        data_per_day[current_day]['humidity_{}'.format(hour)] = row['wind_dir']
        data_per_day[current_day]['gust_ten_{}'.format(hour)] = row['wind_dir']

    # Create a dataframe with 1 line per date, and transform all the other in cols
    df_per_day = pd.DataFrame.from_dict(data=data_per_day, orient='index')
    print(df_per_day.columns)

    min_wind_speed = 5.0
    sub_df = df_per_day.loc[
        (df_per_day['wind_speed_06'] >= min_wind_speed) & (df_per_day['wind_speed_15'] >= min_wind_speed)]

    step_histo = 20.0
    xedges = np.arange(start=0.0, stop=360.0, step=step_histo)
    yedges = np.arange(start=0.0, stop=360.0, step=step_histo)
    hist_2d, xedges, yedges = np.histogram2d(x=sub_df['wind_dir_06'], y=sub_df['wind_dir_15'], bins=(xedges, yedges))

    fig, axes = plt.subplots(figsize=(7, 7))
    # ax = fig.add_subplot(133, title='NonUniformImage: interpolated', aspect='equal', xlim=xedges[[0, -1]],
    #                      ylim=yedges[[0, -1]])
    axes.set_xlim(xedges[[0, -1]])
    axes.set_ylim(yedges[[0, -1]])
    axes.set_xlabel('Wind dir at 6')
    axes.set_ylabel('Wind dir at 15')
    im = NonUniformImage(axes, interpolation='bilinear')

    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2
    im.set_data(xcenters, ycenters, hist_2d)
    axes.images.append(im)
    plt.show()

    return

    plt.hist(sub_df['wind_dir'], bins=np.arange(start=0.0, stop=360.0, step=10.0), alpha=0.2)

    # data_as_dict = data_as_dict(sorted(data_as_dict))
    # data_as_dict = sorted(data_as_dict, key=lambda i: i['date'])

    # plt.scatter(data_as_dict['dates'], data_as_dict['wind_speed'])
    # plt.scatter(sub_df['dates'], sub_df['wind_dir'])
    # plt.hist(sub_df['wind_speed'], bins=np.arange(start=0.0, stop=20.0, step=1.0))
    # sub_df = df.loc[(df['wind_speed'] >= 0.0) & (df['humidity'] >= 0) & (df['hour'] == 18)]
    # plt.hist(sub_df['wind_dir'], bins=np.arange(start=0.0, stop=360.0, step=10.0), alpha=0.2)
    plt.show()


def main():
    repo_dir = Path(__file__).parent.parent
    in_dir = repo_dir / 'tmp' / 'data' / 'processed_data' / 'simplified_weather_data'
    all_csv = list(in_dir.glob('*.csv'))
    # extract_data_for_single_station(station_id=7630, in_csvs=all_csv)
    extract_data_for_single_station(station_id=7481, in_csvs=all_csv)
    return


if __name__ == '__main__':
    main()
