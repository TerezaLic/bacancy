import pandas as pd


class BaseMetrics:

    def __init__(self, id_, file_path, name=None, file_type='csv', **kwargs):
        """

        :param id_: metric id
        :param file_path: input file path
        :param name: metric name
        :param file_type: file extension
        :param kwargs: other args.
        """
        self.id_ = id_
        self.name = name
        self.file_path = file_path
        self.file_type = file_type
        self.other_params = kwargs
        self.dataframe = None

    def load_data(self, **kwargs):
        """

        :param kwargs:
        :return: dataframe based on configurations
        """
        if self.file_type == 'csv':
            dataframe = pd.read_csv(self.file_path)
        elif self.file_type == 'xlsx':
            dataframe = pd.read_excel(self.file_path)
        else:
            raise Exception("The file type is unsupported.")

        self.dataframe = dataframe

        if kwargs or self.other_params:
            # Extra arguments then configure dataframe accordingly
            params = kwargs or self.other_params
            self.dataframe = self.configure_dataframe(self.dataframe, **params)

        return self.dataframe

    def configure_dataframe(self, dataframe: pd.DataFrame = None, **kwargs: dict):
        """

        :param dataframe:
        :param kwargs:
        :return: dataframe
        """

        # if dataframe is not passed then use loaded dataframe as default.
        if not isinstance(dataframe, pd.DataFrame):
            dataframe = self.dataframe

        dataframe.columns = dataframe.iloc[0]
        dataframe = dataframe.drop([0])

        if kwargs.get("filter"):

            # filter records from dataframe
            queries = []
            for key, value in kwargs.get('filter').items():
                queries.append(f"{key} == '{value}'")

            query_string = " & ".join(queries)
            dataframe = dataframe.query(query_string)

        return dataframe

