import datetime
from pathlib import Path

import requests


def download_file(url, out_dir, force_redownload=False):
    """
    Download a single file to the output dir.
    The out file path will be out_dir/url.name

    Args:
        url (str): the URL to download
        out_dir (Path): the output dir where the file will be stored
        force_redownload (bool): if True, will download again the file even if it exists locally
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    out_file = out_dir / url.split('/')[-1]

    if not out_file.exists() or force_redownload:
        r = requests.get(url)
        with open(out_file, 'wb') as fiw:
            fiw.write(r.content)


def get_stations_data(out_dir):
    """
    Download the data of the stations location, along with their id, from meteofrance

    Args:
        out_dir (Path): where the file will be downloaded
    """
    # Define URLs, then download the files
    csv_link = 'https://donneespubliques.meteofrance.fr/donnees_libres/Txt/Synop/postesSynop.csv'
    json_link = 'https://donneespubliques.meteofrance.fr/donnees_libres/Txt/Synop/postesSynop.json'

    download_file(csv_link, out_dir=out_dir)
    download_file(json_link, out_dir=out_dir)


def get_monthly_wind_data(date_as_str, out_dir):
    """
    Get the data for a single month on the whole France

    Args:
        date_as_str (str): format YYYYMM
        out_dir (Path): where the data will be stored
    """
    url = 'https://donneespubliques.meteofrance.fr/donnees_libres/Txt/Synop/Archive/synop.{date}.csv.gz'.format(
        date=date_as_str)
    download_file(url, out_dir=out_dir)


def get_all_wind_data(out_dir, start_date, end_date):
    """
    Get all the wind data on France between the 2 dates

    Args:
        out_dir (Path): output directory
        start_date (datetime.datetime): date to start from
        end_date (datetime.datetime): date to end at
    """
    # Cap the month to not be after today
    today = datetime.datetime.now()
    end_date = min(end_date, today)

    # Generate the list of months
    # as no 'months' attribute is available, we generate a lot of days, and remove the duplicates
    number_of_days = (end_date - start_date).days
    # take every 5 days to make it a bit faster
    day_step = 5
    date_list = [start_date + datetime.timedelta(days=day_num) for day_num in range(0, number_of_days + 1, day_step)]
    # generate the set of months in format YYYYMM
    months_as_str = list(set([date.strftime('%Y%m') for date in date_list]))
    months_as_str.sort()

    for date_id, date_to_dl in enumerate(months_as_str):
        print('Download month {}/{}: {}'.format(date_id + 1, len(months_as_str), date_to_dl))
        get_monthly_wind_data(date_to_dl, out_dir=out_dir)


def main():
    repo_dir = Path(__file__).parent.parent
    main_data_dir = repo_dir / 'tmp' / 'data' / 'raw_data'
    stations_data_dir = main_data_dir / 'stations'
    weather_data_dir = main_data_dir / 'weather_data'

    get_stations_data(out_dir=stations_data_dir)

    start_date = datetime.datetime(year=2015, month=1, day=15)
    end_date = datetime.datetime(year=2020, month=12, day=15)
    get_all_wind_data(out_dir=weather_data_dir, start_date=start_date, end_date=end_date)

    return


if __name__ == '__main__':
    main()
