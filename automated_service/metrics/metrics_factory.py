import yaml
from base_metrics import BaseMetrics
from typing import List, Dict
from dashboard_working import process_raw_data, line_chart
import altair as alt
import streamlit as st

class MetricsFactory:
    """
    selected format for yaml file to load metrics:
    metrics:
      - metric:
          id: unique_metric_id
          name: Name of Metrics
          type: line
          data:
            input_file:/root/sample.csv
            type: csv
            # additional configurations such as limit, header row can be added in the future
    """

    def __init__(self, data: dict):
        """

        :param data: dict
        """
        self.data = data

    def __call__(self):
        metrics = self.load_metrics(self.data['metrics'])
        return metrics

    def load_metrics(self, data: List = []) -> List[BaseMetrics] | BaseMetrics:
        """

        :param data: List[Dict]
        :return: BaseMetrics object(s)
        """
        if not data:
            data = self.data

        metrics = []
        for metric_rec in data:
            metric_rec = metric_rec['metric']
            _obj = BaseMetrics(
                id_=metric_rec['id'],
                file_path=metric_rec['data']['input_file'],
                file_type=metric_rec['data'].get('type'),
                name=metric_rec.get('name'),
                **metric_rec['data']
            )
            metrics.append(_obj)

        return metrics


def read_configurations(file_path: str = "") -> Dict:
    """

    :param file_path: yaml file path
    :return: dict
    """
    with open(file_path, 'r') as f:
        configurations = yaml.safe_load(f)
    return configurations


if __name__ == "__main__":
    config = read_configurations("/home/bacancy/DevangiRami/projects/Calon/code/bacancy/automated_service/data/test_dashboard_configure.yml")
    mf = MetricsFactory(config)
    objs = mf()
    for mf_obj in objs:
        mf_obj.load_data()
        print(mf_obj.id_, mf_obj.dataframe.shape)
        print(mf_obj.dataframe.head())

    print("start...")
    # Fields input - will take from YML
    invoice_date = "primary_datetime_dimension_value"
    revenue = "metric_value"
    region = "dimension_1_string_value"

    fields = {
        'x' : invoice_date,
        'y' : revenue,
        'pivot_column' : region
    }
    
    fields1 = {
        'x' : invoice_date,
        'y' : revenue,
    }
    
    
    obj1 = objs[0]
    processed_response = process_raw_data(obj1.dataframe, fields)
    chart = line_chart(processed_response, fields1)
    
    st.set_page_config(layout='wide')
    st.title("Line Chart from Excel Data")
    st.altair_chart(chart, use_container_width=True)
