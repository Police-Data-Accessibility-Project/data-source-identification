from dataclasses import dataclass

import pandas as pd


@dataclass
class TrainTestDataframes:
    train: pd.DataFrame
    test: pd.DataFrame

    def get_as_list(self):
        return [self.train, self.test]
