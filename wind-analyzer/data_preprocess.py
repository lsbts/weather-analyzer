import csv
from pathlib import Path


def extract_from_gzip(in_zip, out_path):
    """
    Extract the files of interest from the .gzip archive. Namely, extract the *.csv files

    Args:
        in_zip (Path): input file path
        out_path (Path): output file path
    """
    out_path.parent.mkdir(exist_ok=True, parents=True)
    with open(in_zip, 'rb') as f_in:
        content = f_in.readlines()
        with open(out_path, 'w') as f_out:
            for line in content:
                f_out.write(line.decode("utf-8"))


def simplify_inputs(in_path, out_path):
    """
    Simplify the input file, by removing some columns and changing the name of some others

    Args:
        in_path (Path): path to the input .csv, the raw extracted file
        out_path (Path): path to the output simplified .csv
    """
    out_path.parent.mkdir(exist_ok=True, parents=True)
    # Prune the file to remove some columns
    # doc comes from https://donneespubliques.meteofrance.fr/client/document/doc_parametres_synop_168.pdf
    # names = numer_sta (station id), date, dd (wind direction), ff (wind speed), t (temperature),
    # u (humidite), raf10 (rafales 10 dernieres minutes)
    dict_to_keep = {
        'numer_sta': {
            'comment': 'Station number',
            'out_name': 'station_id'
        },
        'date': {
            'comment': 'Date of acquisition, format AAAAMMDDHHMISS, UTC format',
            'out_name': 'date'
        },
        'dd': {
            'comment': 'Wind direction, in degrees',
            'out_name': 'wind_dir'
        },
        'ff': {
            'comment': 'Wind speed, in m/s',
            'out_name': 'wind_speed'
        },
        't': {
            'comment': 'Temperature, in K',
            'out_name': 'temperature'
        },
        'u': {
            'comment': 'Humidity, in percent',
            'out_name': 'humidity'
        },
        'raf10': {
            'comment': 'Gust in the last 10 minutes, in m/s',
            'out_name': 'gust_ten'
        },
    }

    with open(in_path, "r") as fir:
        input_reader = csv.reader(fir, delimiter=';')
        # newline='' needed on Windows, otherwise we have a blank line between each line
        with open(out_path, "w", newline='') as fiw:
            output_writer = csv.writer(fiw)
            for line_id, line in enumerate(input_reader):
                if line_id == 0:
                    # Get the ids of the parameters to keep, and change the headers
                    cols_id_to_keep = []
                    out_headers = []
                    for param_name, param_values in dict_to_keep.items():
                        cols_id_to_keep.append(line.index(param_name))
                        out_headers.append(param_values['out_name'])
                    output_writer.writerow(out_headers)
                else:
                    output_writer.writerow([line[col_id] for col_id in cols_id_to_keep])


def main():
    repo_dir = Path(__file__).parent.parent
    main_raw_data_dir = repo_dir / 'tmp' / 'data' / 'raw_data'
    stations_data_dir = main_raw_data_dir / 'stations'
    weather_data_dir = main_raw_data_dir / 'weather_data'

    main_processed_data_dir = repo_dir / 'tmp' / 'data' / 'processed_data'
    extracted_weather_dir = main_processed_data_dir / 'extracted_weather_data'
    simplified_weather_dir = main_processed_data_dir / 'simplified_weather_data'

    for in_path in weather_data_dir.glob('synop.*.csv.gz'):
        base_name = in_path.stem  # just *.csv
        extracted_path = extracted_weather_dir / '{}_tmp_extract.csv'.format(base_name)
        simplified_path = simplified_weather_dir / base_name
        # Extract the file from the .zip to a .csv
        extract_from_gzip(in_zip=in_path, out_path=extracted_path)
        # Simplify the file
        simplify_inputs(in_path=extracted_path, out_path=simplified_path)

    return


if __name__ == '__main__':
    main()
